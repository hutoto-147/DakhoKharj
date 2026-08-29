package com.example.kharjyar

enum class EntryType(val titleFa: String) {
    EXPENSE("هزینه"),
    INCOME("درآمد")
}

enum class ObligationKind(val titleFa: String) {
    DEBT("بدهی"),
    LOAN("قرض داده‌شده")
}

enum class ReminderKind(val titleFa: String) {
    GENERAL("یادآوری"),
    INSTALLMENT("قسط"),
    DEBT("بدهی"),
    LOAN("قرض"),
    CHECK("چک")
}

enum class RecurrenceFrequency(val titleFa: String) {
    WEEKLY("هفتگی"),
    MONTHLY("ماهانه"),
    YEARLY("سالانه")
}

enum class BankImportDirection(val titleFa: String) {
    CREDIT("واریز"),
    DEBIT("برداشت"),
    UNKNOWN("نامشخص")
}

data class LedgerEntry(
    val id: Long = 0L,
    val type: EntryType,
    val amount: Long,
    val category: String,
    val subcategory: String = "",
    val tags: List<String> = emptyList(),
    val note: String = "",
    val occurredAt: Long,
    val createdAt: Long = System.currentTimeMillis(),
    val accountName: String = "حساب اصلی",
    val memberName: String = "من",
    val source: String = "manual"
)

data class Debt(
    val id: Long = 0L,
    val name: String,
    val originalAmount: Long,
    val currentAmount: Long,
    val note: String = "",
    val occurredAt: Long,
    val updatedAt: Long = System.currentTimeMillis(),
    val kind: ObligationKind = ObligationKind.DEBT,
    val dueAt: Long = 0L,
    val reminderAt: Long = 0L
)

data class DebtSnapshot(
    val id: Long = 0L,
    val debtId: Long,
    val amount: Long,
    val occurredAt: Long
)

data class CategoryRow(
    val id: Long = 0L,
    val type: EntryType,
    val name: String,
    val subcategory: String = ""
)

data class MonthRef(
    val year: Int,
    val month: Int,
    val label: String
) {
    val key: String get() = "%04d-%02d".format(year, month)
}

data class ChartBar(
    val label: String,
    val value: Long
)

data class ChartGroup(
    val label: String,
    val bars: List<ChartBar>
)

data class Account(
    val id: Long = 0L,
    val name: String,
    val type: String = "بانکی",
    val openingBalance: Long = 0L,
    val icon: String = "🏦"
)

data class HouseholdMember(
    val id: Long = 0L,
    val name: String
)

data class RecurringRule(
    val id: Long = 0L,
    val type: EntryType,
    val amount: Long,
    val category: String,
    val subcategory: String = "",
    val note: String = "",
    val accountName: String = "حساب اصلی",
    val memberName: String = "من",
    val frequency: RecurrenceFrequency = RecurrenceFrequency.MONTHLY,
    val dayOfMonth: Int = 1,
    val nextRunAt: Long,
    val enabled: Boolean = true
)

data class ReminderItem(
    val id: Long = 0L,
    val title: String,
    val note: String = "",
    val kind: ReminderKind = ReminderKind.GENERAL,
    val dueAt: Long,
    val remindAt: Long,
    val enabled: Boolean = true,
    val linkedId: Long = 0L
)

data class InstallmentPlan(
    val id: Long = 0L,
    val title: String,
    val installmentAmount: Long,
    val remainingCount: Int,
    val nextDueAt: Long,
    val accountName: String = "حساب اصلی",
    val note: String = "",
    val reminderDaysBefore: Int = 3,
    val reminderHour: Int = 9,
    val reminderMinute: Int = 0,
    val enabled: Boolean = true
)

data class BankImport(
    val id: Long = 0L,
    val sender: String,
    val body: String,
    val amount: Long,
    val direction: BankImportDirection,
    val occurredAt: Long,
    val createdAt: Long = System.currentTimeMillis(),
    val status: String = "pending",
    val hash: String
)
