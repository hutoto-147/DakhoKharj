package com.example.kharjyar

import android.app.Notification
import android.content.Context
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
            if (digits.length > 14) return null
            val value = digits.toLongOrNull() ?: return null
            if (value < 1_000L) return null
            return if (unit == "ریال" && value >= 10_000L) value / 10L else value
        }

        // اولویت با عددی است که کنار واژه خود تراکنش آمده؛ نه موجودی/مانده حساب.
        val transactionWithCurrency = Regex(
            """(?:مبلغ|به مبلغ|برداشت|واریز|واریزی|خرید|پرداخت|کسر|دریافت|انتقال)\D{0,28}([0-9][0-9,]{2,18})\s*(ریال|تومان)"""
        ).findAll(normalized).mapNotNull { convert(it.groupValues[1], it.groupValues[2]) }.toList()
        if (transactionWithCurrency.isNotEmpty()) return transactionWithCurrency.first()

        val contextual = Regex(
            """(?:مبلغ|به مبلغ|برداشت|واریز|واریزی|خرید|پرداخت|کسر|دریافت|انتقال)\D{0,28}([0-9][0-9,]{2,18})"""
        ).findAll(normalized).mapNotNull { convert(it.groupValues[1], null) }.toList()
        if (contextual.isNotEmpty()) return contextual.first()

        // عددهای دارای واحد که در نزدیکی «موجودی/مانده» هستند کنار گذاشته می‌شوند.
        val currencyMatches = Regex("""([0-9][0-9,]{2,18})\s*(ریال|تومان)""").findAll(normalized).mapNotNull { match ->
            val before = normalized.substring(maxOf(0, match.range.first - 24), match.range.first).lowercase()
            if (before.contains("موجودی") || before.contains("مانده")) null else convert(match.groupValues[1], match.groupValues[2])
        }.toList()
        if (currencyMatches.isNotEmpty()) return currencyMatches.first()

        // آخرین راه: بزرگ‌ترین عدد معقول، با حذف سال شمسی و اعداد خیلی بلند.
        return Regex("""(?<!\d)([0-9][0-9,]{2,13})(?!\d)""").findAll(normalized)
            .mapNotNull { convert(it.groupValues[1], null) }
            .filterNot { it in 1300L..1600L }
            .maxOrNull()
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
