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
import android.media.AudioAttributes
import android.media.RingtoneManager
import android.os.Build
import androidx.core.app.NotificationCompat
import androidx.core.app.NotificationManagerCompat
import kotlin.math.absoluteValue

object ReminderScheduler {
    const val CHANNEL_ID = "dakhl_kharj_reminders_v2"
    private const val EXTRA_TITLE = "title"
    private const val EXTRA_NOTE = "note"
    private const val EXTRA_ID = "notification_id"
    private const val INSTALLMENT_ID_BASE = 1_000_000L

    fun schedule(context: Context, item: ReminderItem) {
        if (!item.enabled || item.remindAt <= 0L) return
        val alarm = context.getSystemService(Context.ALARM_SERVICE) as AlarmManager
        val notificationId = (item.id.takeIf { it != 0L } ?: item.title.hashCode().toLong()).toInt().absoluteValue
        val intent = Intent(context, ReminderReceiver::class.java).apply {
            putExtra(EXTRA_TITLE, item.title)
            putExtra(EXTRA_NOTE, item.note.ifBlank { "سررسید: ${PersianDate.formatDateTime(item.dueAt)}" })
            putExtra(EXTRA_ID, notificationId)
        }
        val pending = PendingIntent.getBroadcast(
            context,
            notificationId,
            intent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )
        if (Build.VERSION.SDK_INT >= 31 && alarm.canScheduleExactAlarms()) {
            alarm.setExactAndAllowWhileIdle(AlarmManager.RTC_WAKEUP, item.remindAt, pending)
        } else if (Build.VERSION.SDK_INT < 31) {
            alarm.setExactAndAllowWhileIdle(AlarmManager.RTC_WAKEUP, item.remindAt, pending)
        } else {
            alarm.setAndAllowWhileIdle(AlarmManager.RTC_WAKEUP, item.remindAt, pending)
        }
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
        pending.cancel()
    }

    fun cancelInstallment(context: Context, planId: Long) = cancel(context, INSTALLMENT_ID_BASE + planId)

    private fun scheduleInstallment(context: Context, plan: InstallmentPlan) {
        if (!plan.enabled || plan.remainingCount <= 0) {
            cancelInstallment(context, plan.id)
            return
        }
        val remindAt = PersianDate.withTime(
            PersianDate.addDays(plan.nextDueAt, -plan.reminderDaysBefore),
            plan.reminderHour,
            plan.reminderMinute
        )
        schedule(
            context,
            ReminderItem(
                id = INSTALLMENT_ID_BASE + plan.id,
                title = "قسط: ${plan.title}",
                note = "${plan.installmentAmount.asToman()} • سررسید ${PersianDate.formatDateTime(plan.nextDueAt)}",
                kind = ReminderKind.INSTALLMENT,
                dueAt = plan.nextDueAt,
                remindAt = remindAt,
                linkedId = plan.id
            )
        )
    }

    fun scheduleAll(context: Context) {
        val repo = LedgerRepository(context)
        repo.reminders()
            .filter { it.enabled && it.kind != ReminderKind.INSTALLMENT && it.remindAt > System.currentTimeMillis() }
            .forEach { schedule(context, it) }
        // Iterating all plans also cancels any alarm left by a just-completed final installment.
        repo.installments().forEach { scheduleInstallment(context, it) }
    }
}

class ReminderReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        createChannel(context)
        val title = intent.getStringExtra("title") ?: "یادآوری دخل و خرج"
        val note = intent.getStringExtra("note") ?: "یک سررسید ثبت‌شده دارید."
        val id = intent.getIntExtra("notification_id", title.hashCode().absoluteValue)
        if (Build.VERSION.SDK_INT >= 33 && context.checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS) != PackageManager.PERMISSION_GRANTED) return
        val openIntent = Intent(context, MainActivity::class.java)
        val contentPending = PendingIntent.getActivity(context, id, openIntent, PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE)
        val sound = RingtoneManager.getDefaultUri(RingtoneManager.TYPE_NOTIFICATION)
        val notification = NotificationCompat.Builder(context, ReminderScheduler.CHANNEL_ID)
            .setSmallIcon(R.drawable.ic_dakhl_kharj_notification_v2)
            .setContentTitle(title)
            .setContentText(note)
            .setStyle(NotificationCompat.BigTextStyle().bigText(note))
            .setAutoCancel(true)
            .setSound(sound)
            .setVibrate(longArrayOf(0, 250, 120, 250))
            .setPriority(NotificationCompat.PRIORITY_HIGH)
            .setCategory(NotificationCompat.CATEGORY_REMINDER)
            .setContentIntent(contentPending)
            .build()
        NotificationManagerCompat.from(context).notify(id, notification)
    }

    private fun createChannel(context: Context) {
        if (Build.VERSION.SDK_INT >= 26) {
            val manager = context.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
            val sound = RingtoneManager.getDefaultUri(RingtoneManager.TYPE_NOTIFICATION)
            val audioAttributes = AudioAttributes.Builder()
                .setUsage(AudioAttributes.USAGE_NOTIFICATION_COMMUNICATION_INSTANT)
                .setContentType(AudioAttributes.CONTENT_TYPE_SONIFICATION)
                .build()
            val channel = NotificationChannel(ReminderScheduler.CHANNEL_ID, "یادآوری‌های دخل و خرج", NotificationManager.IMPORTANCE_HIGH).apply {
                description = "اقساط، بدهی‌ها، قرض‌ها، چک‌ها و یادداشت‌های سررسیددار"
                setSound(sound, audioAttributes)
                enableVibration(true)
                vibrationPattern = longArrayOf(0, 250, 120, 250)
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
