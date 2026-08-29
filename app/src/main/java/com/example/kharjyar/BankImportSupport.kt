package com.example.kharjyar

import android.app.Notification
import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.provider.Telephony
import android.net.Uri
import android.service.notification.NotificationListenerService
import android.service.notification.StatusBarNotification
import java.security.MessageDigest

object BankMessageParser {
    private val bankWords = listOf("بانک", "حساب", "کارت", "برداشت", "واریز", "انتقال", "خرید", "موجودی", "تراکنش", "پرداخت")
    private val creditWords = listOf("واریز", "واریزی", "بستانکار", "دریافت", "افزایش", "انتقال به")
    private val debitWords = listOf("برداشت", "خرید", "پرداخت", "کسر", "بدهکار", "انتقال از", "کم شد")
    private val ignoreWords = listOf("رمز پویا", "رمز یکبار", "رمز یک‌بار", "otp", "کد تایید", "کد تأیید")

    fun parse(sender: String, body: String, occurredAt: Long): BankImport? {
        val cleaned = body.trim()
        val lower = cleaned.lowercase()
        if (cleaned.length < 8 || ignoreWords.any { lower.contains(it) }) return null
        if (bankWords.none { lower.contains(it) }) return null
        val amount = extractAmount(cleaned) ?: return null
        val direction = when {
            creditWords.any { lower.contains(it) } -> BankImportDirection.CREDIT
            debitWords.any { lower.contains(it) } -> BankImportDirection.DEBIT
            else -> BankImportDirection.UNKNOWN
        }
        val raw = "$sender|$cleaned|$occurredAt|$amount|${direction.name}"
        val hash = MessageDigest.getInstance("SHA-256").digest(raw.toByteArray()).joinToString("") { "%02x".format(it) }
        return BankImport(sender = sender.ifBlank { "بانک" }, body = cleaned, amount = amount, direction = direction, occurredAt = occurredAt, hash = hash)
    }

    private fun extractAmount(text: String): Long? {
        val normalized = text.toEnglishDigits().replace("٬", ",")

        fun convert(raw: String, unit: String?): Long? {
            val digits = raw.replace(",", "")
            if (digits.length > 14) return null // شماره کارت/حساب را به‌عنوان مبلغ نگیریم
            val value = digits.toLongOrNull() ?: return null
            if (value < 1_000L) return null
            return if (unit == "ریال" && value >= 10_000L) value / 10L else value
        }

        // اول عددهایی که صریحاً واحد پول دارند؛ این حالت در پیامک‌های بانکی قابل‌اعتمادتر است.
        val withCurrency = Regex("""([0-9][0-9,]{2,18})\s*(ریال|تومان)""").findAll(normalized)
            .mapNotNull { convert(it.groupValues[1], it.groupValues[2]) }.toList()
        if (withCurrency.isNotEmpty()) return withCurrency.maxOrNull()

        // بعد عددی که نزدیک واژه مبلغ/برداشت/واریز/خرید/پرداخت آمده است.
        val contextual = Regex("""(?:مبلغ|به مبلغ|برداشت|واریز|واریزی|خرید|پرداخت|کسر|دریافت)\D{0,22}([0-9][0-9,]{2,18})""").findAll(normalized)
            .mapNotNull { convert(it.groupValues[1], null) }.toList()
        if (contextual.isNotEmpty()) return contextual.maxOrNull()

        // آخرین راه: بزرگ‌ترین عدد معقول؛ برای کاهش خطا اعداد خیلی بلند حذف می‌شوند.
        return Regex("""(?<!\d)([0-9][0-9,]{2,13})(?!\d)""").findAll(normalized)
            .mapNotNull { convert(it.groupValues[1], null) }
            .filterNot { it in 1300L..1600L } // سال شمسیِ تنها معمولاً مبلغ نیست
            .maxOrNull()
    }
}

object BankSmsImporter {
    fun scanExisting(context: Context, limit: Int = 250): Int {
        val repo = LedgerRepository(context)
        var count = 0
        val uri = Uri.parse("content://sms/inbox")
        val projection = arrayOf("address", "body", "date")
        val cursor = context.contentResolver.query(uri, projection, null, null, "date DESC") ?: return 0
        cursor.use { c ->
            val addressIdx = c.getColumnIndex("address")
            val bodyIdx = c.getColumnIndex("body")
            val dateIdx = c.getColumnIndex("date")
            var seen = 0
            while (c.moveToNext() && seen < limit) {
                seen++
                val sender = if (addressIdx >= 0) c.getString(addressIdx).orEmpty() else "بانک"
                val body = if (bodyIdx >= 0) c.getString(bodyIdx).orEmpty() else ""
                val date = if (dateIdx >= 0) c.getLong(dateIdx) else System.currentTimeMillis()
                val item = BankMessageParser.parse(sender, body, date) ?: continue
                if (repo.saveBankImport(item) > 0) count++
            }
        }
        return count
    }
}

class BankSmsReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        if (intent.action != Telephony.Sms.Intents.SMS_RECEIVED_ACTION) return
        val repo = LedgerRepository(context)
        Telephony.Sms.Intents.getMessagesFromIntent(intent).groupBy { it.originatingAddress.orEmpty() }.forEach { (sender, parts) ->
            val body = parts.joinToString("") { it.messageBody.orEmpty() }
            val time = parts.firstOrNull()?.timestampMillis ?: System.currentTimeMillis()
            BankMessageParser.parse(sender, body, time)?.let(repo::saveBankImport)
        }
    }
}

class BankNotificationListener : NotificationListenerService() {
    override fun onNotificationPosted(sbn: StatusBarNotification?) {
        sbn ?: return
        val extras = sbn.notification.extras ?: return
        val title = extras.getCharSequence(Notification.EXTRA_TITLE)?.toString().orEmpty()
        val text = extras.getCharSequence(Notification.EXTRA_TEXT)?.toString().orEmpty()
        val big = extras.getCharSequence(Notification.EXTRA_BIG_TEXT)?.toString().orEmpty()
        val body = listOf(title, text, big).filter { it.isNotBlank() }.distinct().joinToString("\n")
        BankMessageParser.parse(title.ifBlank { sbn.packageName }, body, sbn.postTime)?.let { LedgerRepository(this).saveBankImport(it) }
    }
}
