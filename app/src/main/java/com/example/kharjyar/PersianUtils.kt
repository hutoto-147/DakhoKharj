package com.example.kharjyar

import android.icu.util.Calendar
import android.icu.util.ULocale

object PersianDate {
    private fun newPersianCalendar(): Calendar =
        Calendar.getInstance(ULocale("fa_IR@calendar=persian"))

    val monthNames = listOf(
        "فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور",
        "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند"
    )

    data class Parts(val year: Int, val month: Int, val day: Int) {
        val key: String get() = "%04d-%02d".format(year, month)
    }

    fun parts(millis: Long): Parts {
        val cal = newPersianCalendar()
        cal.timeInMillis = millis
        return Parts(
            year = cal.get(Calendar.YEAR),
            month = cal.get(Calendar.MONTH) + 1,
            day = cal.get(Calendar.DAY_OF_MONTH)
        )
    }

    fun nowParts(): Parts = parts(System.currentTimeMillis())

    fun format(millis: Long): String {
        val p = parts(millis)
        return "${p.year}/${p.month.toString().padStart(2, '0')}/${p.day.toString().padStart(2, '0')}".toPersianDigits()
    }

    fun formatMonth(millis: Long): String {
        val p = parts(millis)
        return "${monthNames[p.month - 1]} ${p.year}".toPersianDigits()
    }

    fun monthLabel(ref: MonthRef): String =
        "${monthNames[ref.month - 1]} ${ref.year}".toPersianDigits()

    fun parse(text: String): Long? {
        val normalized = text.toEnglishDigits().replace("-", "/").trim()
        val match = Regex("""^(\d{4})/(\d{1,2})/(\d{1,2})$""").matchEntire(normalized) ?: return null
        val year = match.groupValues[1].toIntOrNull() ?: return null
        val month = match.groupValues[2].toIntOrNull() ?: return null
        val day = match.groupValues[3].toIntOrNull() ?: return null
        if (month !in 1..12 || day !in 1..31) return null

        return runCatching {
            val cal = newPersianCalendar()
            cal.clear()
            cal.set(year, month - 1, day, 12, 0, 0)
            val p = Parts(cal.get(Calendar.YEAR), cal.get(Calendar.MONTH) + 1, cal.get(Calendar.DAY_OF_MONTH))
            if (p.year != year || p.month != month || p.day != day) return null
            cal.timeInMillis
        }.getOrNull()
    }

    fun dateForParts(year: Int, month: Int, day: Int): Long? = parse("$year/$month/$day")

    fun dateForMonth(ref: MonthRef, preferredDay: Int): Long {
        var day = preferredDay.coerceIn(1, 31)
        while (day >= 1) {
            val value = parse("${ref.year}/${ref.month}/$day")
            if (value != null) return value
            day--
        }
        return parse("${ref.year}/${ref.month}/1") ?: System.currentTimeMillis()
    }

    fun daysInMonth(year: Int, month: Int): Int {
        for (d in 31 downTo 28) if (parse("$year/$month/$d") != null) return d
        return 29
    }

    fun endOfMonth(ref: MonthRef): Long {
        val cal = newPersianCalendar().apply {
            clear()
            set(ref.year, ref.month - 1, 1, 23, 59, 59)
            set(Calendar.MILLISECOND, 999)
            add(Calendar.MONTH, 1)
            add(Calendar.DAY_OF_MONTH, -1)
        }
        return cal.timeInMillis
    }

    fun startOfMonth(ref: MonthRef): Long = parse("${ref.year}/${ref.month}/1") ?: 0L

    fun shiftMonth(ref: MonthRef, delta: Int): MonthRef {
        val cal = newPersianCalendar().apply {
            clear()
            set(ref.year, ref.month - 1, 1, 12, 0, 0)
            add(Calendar.MONTH, delta)
        }
        val year = cal.get(Calendar.YEAR)
        val month = cal.get(Calendar.MONTH) + 1
        return MonthRef(year, month, "${monthNames[month - 1]}\n${year.toString().toPersianDigits()}")
    }

    fun addMonths(millis: Long, count: Int): Long {
        val cal = newPersianCalendar().apply { timeInMillis = millis }
        cal.add(Calendar.MONTH, count)
        return cal.timeInMillis
    }

    fun addDays(millis: Long, count: Int): Long {
        val cal = newPersianCalendar().apply { timeInMillis = millis }
        cal.add(Calendar.DAY_OF_MONTH, count)
        return cal.timeInMillis
    }

    fun withTime(millis: Long, hour: Int, minute: Int): Long {
        val cal = newPersianCalendar().apply { timeInMillis = millis }
        cal.set(Calendar.HOUR_OF_DAY, hour.coerceIn(0, 23))
        cal.set(Calendar.MINUTE, minute.coerceIn(0, 59))
        cal.set(Calendar.SECOND, 0)
        cal.set(Calendar.MILLISECOND, 0)
        return cal.timeInMillis
    }

    fun formatTime(millis: Long): String {
        val cal = newPersianCalendar().apply { timeInMillis = millis }
        return "${cal.get(Calendar.HOUR_OF_DAY).toString().padStart(2, '0')}:${cal.get(Calendar.MINUTE).toString().padStart(2, '0')}".toPersianDigits()
    }

    fun formatDateTime(millis: Long): String = "${format(millis)}، ${formatTime(millis)}"

    fun lastMonths(count: Int, now: Long = System.currentTimeMillis()): List<MonthRef> {
        val base = newPersianCalendar().apply {
            timeInMillis = now
            set(Calendar.DAY_OF_MONTH, 1)
            set(Calendar.HOUR_OF_DAY, 12)
            set(Calendar.MINUTE, 0)
            set(Calendar.SECOND, 0)
            set(Calendar.MILLISECOND, 0)
        }

        return (count - 1 downTo 0).map { back ->
            val cal = base.clone() as Calendar
            cal.add(Calendar.MONTH, -back)
            val y = cal.get(Calendar.YEAR)
            val m = cal.get(Calendar.MONTH) + 1
            MonthRef(y, m, "${monthNames[m - 1]}\n${y.toString().toPersianDigits()}")
        }
    }

    fun selectableYears(pastYears: Int = 2, futureYears: Int = 1): List<Int> {
        val current = nowParts().year
        return (current - pastYears..current + futureYears).toList().reversed()
    }
}

/**
 * Groups the absolute amount into 3-digit clusters with the Persian thousands
 * separator U+066C. Example: 1200000 -> ۱٬۲۰۰٬۰۰۰
 */
fun Long.toGroupedPersianDigits(): String {
    val digits = kotlin.math.abs(this).toString()
    val grouped = buildString {
        for (i in digits.indices) {
            if (i > 0 && (digits.length - i) % 3 == 0) append('٬')
            append(digits[i])
        }
    }
    return grouped.toPersianDigits()
}

fun Long.asToman(): String {
    val sign = if (this < 0) "−" else ""
    return "${this.toGroupedPersianDigits()}$sign تومان"
}

fun Long.asCompactToman(): String =
    asToman()

fun String.toEnglishDigits(): String = buildString {
    this@toEnglishDigits.forEach { ch ->
        append(
            when (ch) {
                '۰', '٠' -> '0'; '۱', '١' -> '1'; '۲', '٢' -> '2'; '۳', '٣' -> '3'; '۴', '٤' -> '4'
                '۵', '٥' -> '5'; '۶', '٦' -> '6'; '۷', '٧' -> '7'; '۸', '٨' -> '8'; '۹', '٩' -> '9'
                else -> ch
            }
        )
    }
}

fun String.toPersianDigits(): String = buildString {
    this@toPersianDigits.forEach { ch ->
        append(
            when (ch) {
                '0' -> '۰'; '1' -> '۱'; '2' -> '۲'; '3' -> '۳'; '4' -> '۴'
                '5' -> '۵'; '6' -> '۶'; '7' -> '۷'; '8' -> '۸'; '9' -> '۹'
                else -> ch
            }
        )
    }
}

fun String.formatAmountInput(): String {
    val digits = toEnglishDigits().filter { it.isDigit() }
    if (digits.isEmpty()) return ""
    val normalized = digits.dropWhile { it == '0' }.ifEmpty { "0" }
    val grouped = normalized.reversed().chunked(3).joinToString("٬").reversed()
    return grouped.toPersianDigits()
}

fun String.toLongAmountOrNull(): Long? {
    val digits = toEnglishDigits().filter { it.isDigit() }
    return digits.toLongOrNull()
}

fun String.normalizedAmountCandidate(): Long? {
    val n = toEnglishDigits().replace(",", "").replace("٬", "")
    val candidates = Regex("""(?<!\d)(\d{3,16})(?!\d)""").findAll(n)
        .mapNotNull { it.groupValues[1].toLongOrNull() }
        .filter { it >= 1_000L }
        .toList()
    return candidates.maxOrNull()
}
