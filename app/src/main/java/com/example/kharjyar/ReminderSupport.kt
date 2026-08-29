package com.example.kharjyar

import android.Manifest
import android.app.AlarmManager
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.media.RingtoneManager
import android.os.Build
import androidx.core.app.NotificationCompat
import androidx.core.app.NotificationManagerCompat
import kotlin.math.absoluteValue

object ReminderScheduler {
    private const val EXTRA_TITLE = "title"
    private const val EXTRA_NOTE = "note"
    private const val EXTRA_ID = "notification_id"

    fun schedule(context: Context, item: ReminderItem) {
        if (!item.enabled || item.remindAt <= 0L) return
        val alarm = context.getSystemService(Context.ALARM_SERVICE) as AlarmManager
        val notificationId = (item.id.takeIf { it != 0L } ?: item.title.hashCode().toLong()).toInt().absoluteValue
        val intent = Intent(context, ReminderReceiver::class.java).apply {
            putExtra(EXTRA_TITLE, item.title)
            putExtra(EXTRA_NOTE, item.note.ifBlank { "سررسید: ${PersianDate.format(item.dueAt)}" })
            putExtra(EXTRA_ID, notificationId)
        }
        val pending = PendingIntent.getBroadcast(
            context,
            notificationId,
            intent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )
        alarm.setAndAllowWhileIdle(AlarmManager.RTC_WAKEUP, item.remindAt, pending)
    }

    fun cancel(context: Context, id: Long) {
        val alarm = context.getSystemService(Context.ALARM_SERVICE) as AlarmManager
        val requestCode = id.toInt().absoluteValue
        val pending = PendingIntent.getBroadcast(
            context,
            requestCode,
            Intent(context, ReminderReceiver::class.java),
            PendingIntent.FLAG_NO_CREATE or PendingIntent.FLAG_IMMUTABLE
        ) ?: return
        alarm.cancel(pending)
    }

    fun scheduleAll(context: Context) {
        val repo = LedgerRepository(context)
        repo.reminders().filter { it.enabled && it.remindAt > System.currentTimeMillis() }.forEach { schedule(context, it) }
        repo.installments().filter { it.enabled && it.remainingCount > 0 }.forEach { plan ->
            val remindAt = PersianDate.addDays(plan.nextDueAt, -plan.reminderDaysBefore)
            schedule(
                context,
                ReminderItem(
                    id = 1_000_000L + plan.id,
                    title = "قسط: ${plan.title}",
                    note = "${plan.installmentAmount.asToman()} • سررسید ${PersianDate.format(plan.nextDueAt)}",
                    kind = ReminderKind.INSTALLMENT,
                    dueAt = plan.nextDueAt,
                    remindAt = remindAt,
                    linkedId = plan.id
                )
            )
        }
    }
}

class ReminderReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        createChannel(context)
        val title = intent.getStringExtra("title") ?: "یادآوری خرج‌یار"
        val note = intent.getStringExtra("note") ?: "یک سررسید ثبت‌شده دارید."
        val id = intent.getIntExtra("notification_id", title.hashCode().absoluteValue)

        if (Build.VERSION.SDK_INT >= 33 && context.checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS) != PackageManager.PERMISSION_GRANTED) return

        val openIntent = Intent(context, MainActivity::class.java)
        val contentPending = PendingIntent.getActivity(context, id, openIntent, PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE)
        val sound = RingtoneManager.getDefaultUri(RingtoneManager.TYPE_NOTIFICATION)
        val notification = NotificationCompat.Builder(context, "kharjyar_reminders")
            .setSmallIcon(android.R.drawable.ic_lock_idle_alarm)
            .setContentTitle(title)
            .setContentText(note)
            .setStyle(NotificationCompat.BigTextStyle().bigText(note))
            .setAutoCancel(true)
            .setSound(sound)
            .setPriority(NotificationCompat.PRIORITY_HIGH)
            .setContentIntent(contentPending)
            .build()
        NotificationManagerCompat.from(context).notify(id, notification)
    }

    private fun createChannel(context: Context) {
        if (Build.VERSION.SDK_INT >= 26) {
            val manager = context.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
            val channel = NotificationChannel("kharjyar_reminders", "یادآوری‌های خرج‌یار", NotificationManager.IMPORTANCE_HIGH).apply {
                description = "اقساط، بدهی‌ها، قرض‌ها، چک‌ها و یادداشت‌های سررسیددار"
                setSound(RingtoneManager.getDefaultUri(RingtoneManager.TYPE_NOTIFICATION), null)
            }
            manager.createNotificationChannel(channel)
        }
    }
}

class BootReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        if (intent.action == Intent.ACTION_BOOT_COMPLETED || intent.action == Intent.ACTION_MY_PACKAGE_REPLACED) {
            ReminderScheduler.scheduleAll(context)
        }
    }
}
