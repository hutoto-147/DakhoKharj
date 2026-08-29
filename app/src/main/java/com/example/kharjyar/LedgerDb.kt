package com.example.kharjyar

import android.content.ContentValues
import android.content.Context
import android.database.Cursor
import android.database.sqlite.SQLiteDatabase
import android.database.sqlite.SQLiteOpenHelper
import org.json.JSONArray
import org.json.JSONObject

class LedgerDb(context: Context) : SQLiteOpenHelper(context, "kharjyar.db", null, 3) {
    companion object {
        private const val TAG_SEP = "\u001F"
        private val BACKUP_TABLES = listOf(
            "entries", "custom_categories", "custom_tags", "settings", "debts", "debt_history",
            "accounts", "household_members", "recurring_rules", "reminders", "installments", "bank_imports"
        )
    }

    override fun onCreate(db: SQLiteDatabase) {
        createCoreTables(db)
        createV2Tables(db)
        createV3Tables(db)
        seedDefaults(db)
    }

    private fun createCoreTables(db: SQLiteDatabase) {
        db.execSQL(
            """
            CREATE TABLE IF NOT EXISTS entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT NOT NULL,
                amount INTEGER NOT NULL,
                category TEXT NOT NULL,
                subcategory TEXT NOT NULL DEFAULT '',
                tags TEXT NOT NULL DEFAULT '',
                note TEXT NOT NULL DEFAULT '',
                occurred_at INTEGER NOT NULL,
                created_at INTEGER NOT NULL,
                account_name TEXT NOT NULL DEFAULT 'حساب اصلی',
                member_name TEXT NOT NULL DEFAULT 'من',
                source TEXT NOT NULL DEFAULT 'manual'
            )
            """.trimIndent()
        )
        db.execSQL(
            """
            CREATE TABLE IF NOT EXISTS custom_categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT NOT NULL,
                name TEXT NOT NULL,
                subcategory TEXT NOT NULL DEFAULT ''
            )
            """.trimIndent()
        )
        db.execSQL("CREATE TABLE IF NOT EXISTS custom_tags (name TEXT PRIMARY KEY)")
        db.execSQL("CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
        db.execSQL("CREATE INDEX IF NOT EXISTS idx_entries_occurred_at ON entries(occurred_at)")
        db.execSQL("CREATE INDEX IF NOT EXISTS idx_entries_type ON entries(type)")
        db.execSQL("CREATE INDEX IF NOT EXISTS idx_entries_category ON entries(category)")
    }

    private fun createV2Tables(db: SQLiteDatabase) {
        db.execSQL(
            """
            CREATE TABLE IF NOT EXISTS debts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                original_amount INTEGER NOT NULL,
                current_amount INTEGER NOT NULL,
                note TEXT NOT NULL DEFAULT '',
                occurred_at INTEGER NOT NULL,
                updated_at INTEGER NOT NULL,
                kind TEXT NOT NULL DEFAULT 'DEBT',
                due_at INTEGER NOT NULL DEFAULT 0,
                reminder_at INTEGER NOT NULL DEFAULT 0
            )
            """.trimIndent()
        )
        db.execSQL(
            """
            CREATE TABLE IF NOT EXISTS debt_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                debt_id INTEGER NOT NULL,
                amount INTEGER NOT NULL,
                occurred_at INTEGER NOT NULL
            )
            """.trimIndent()
        )
        db.execSQL("CREATE INDEX IF NOT EXISTS idx_debt_history_debt ON debt_history(debt_id)")
        db.execSQL("CREATE INDEX IF NOT EXISTS idx_debt_history_date ON debt_history(occurred_at)")
    }

    private fun createV3Tables(db: SQLiteDatabase) {
        db.execSQL(
            """
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                type TEXT NOT NULL DEFAULT 'بانکی',
                opening_balance INTEGER NOT NULL DEFAULT 0,
                icon TEXT NOT NULL DEFAULT '🏦'
            )
            """.trimIndent()
        )
        db.execSQL(
            """
            CREATE TABLE IF NOT EXISTS household_members (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            )
            """.trimIndent()
        )
        db.execSQL(
            """
            CREATE TABLE IF NOT EXISTS recurring_rules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT NOT NULL,
                amount INTEGER NOT NULL,
                category TEXT NOT NULL,
                subcategory TEXT NOT NULL DEFAULT '',
                note TEXT NOT NULL DEFAULT '',
                account_name TEXT NOT NULL DEFAULT 'حساب اصلی',
                member_name TEXT NOT NULL DEFAULT 'من',
                frequency TEXT NOT NULL DEFAULT 'MONTHLY',
                day_of_month INTEGER NOT NULL DEFAULT 1,
                next_run_at INTEGER NOT NULL,
                enabled INTEGER NOT NULL DEFAULT 1
            )
            """.trimIndent()
        )
        db.execSQL(
            """
            CREATE TABLE IF NOT EXISTS reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                note TEXT NOT NULL DEFAULT '',
                kind TEXT NOT NULL DEFAULT 'GENERAL',
                due_at INTEGER NOT NULL,
                remind_at INTEGER NOT NULL,
                enabled INTEGER NOT NULL DEFAULT 1,
                linked_id INTEGER NOT NULL DEFAULT 0
            )
            """.trimIndent()
        )
        db.execSQL(
            """
            CREATE TABLE IF NOT EXISTS installments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                installment_amount INTEGER NOT NULL,
                remaining_count INTEGER NOT NULL,
                next_due_at INTEGER NOT NULL,
                account_name TEXT NOT NULL DEFAULT 'حساب اصلی',
                note TEXT NOT NULL DEFAULT '',
                reminder_days_before INTEGER NOT NULL DEFAULT 3,
                enabled INTEGER NOT NULL DEFAULT 1
            )
            """.trimIndent()
        )
        db.execSQL(
            """
            CREATE TABLE IF NOT EXISTS bank_imports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sender TEXT NOT NULL,
                body TEXT NOT NULL,
                amount INTEGER NOT NULL DEFAULT 0,
                direction TEXT NOT NULL DEFAULT 'UNKNOWN',
                occurred_at INTEGER NOT NULL,
                created_at INTEGER NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                hash TEXT NOT NULL UNIQUE
            )
            """.trimIndent()
        )
        db.execSQL("CREATE INDEX IF NOT EXISTS idx_reminders_time ON reminders(remind_at)")
        db.execSQL("CREATE INDEX IF NOT EXISTS idx_bank_imports_status ON bank_imports(status)")
    }

    override fun onUpgrade(db: SQLiteDatabase, oldVersion: Int, newVersion: Int) {
        if (oldVersion < 2) createV2Tables(db)
        if (oldVersion < 3) {
            fun addColumn(sql: String) { runCatching { db.execSQL(sql) } }
            addColumn("ALTER TABLE entries ADD COLUMN account_name TEXT NOT NULL DEFAULT 'حساب اصلی'")
            addColumn("ALTER TABLE entries ADD COLUMN member_name TEXT NOT NULL DEFAULT 'من'")
            addColumn("ALTER TABLE entries ADD COLUMN source TEXT NOT NULL DEFAULT 'manual'")
            addColumn("ALTER TABLE debts ADD COLUMN kind TEXT NOT NULL DEFAULT 'DEBT'")
            addColumn("ALTER TABLE debts ADD COLUMN due_at INTEGER NOT NULL DEFAULT 0")
            addColumn("ALTER TABLE debts ADD COLUMN reminder_at INTEGER NOT NULL DEFAULT 0")
            createV3Tables(db)
            db.execSQL("UPDATE entries SET category = 'خودرو و تردد' WHERE category = 'رفت‌وآمد'")
            db.execSQL("UPDATE custom_categories SET name = 'خودرو و تردد' WHERE name = 'رفت‌وآمد'")
            seedDefaults(db)
        }
    }

    private fun seedDefaults(db: SQLiteDatabase) {
        val accountCount = db.rawQuery("SELECT COUNT(*) FROM accounts", null).use { if (it.moveToFirst()) it.getInt(0) else 0 }
        if (accountCount == 0) {
            insertAccount(db, Account(name = "حساب اصلی", type = "بانکی", icon = "🏦"))
            insertAccount(db, Account(name = "نقدی", type = "نقدی", icon = "💵"))
        }
        val memberCount = db.rawQuery("SELECT COUNT(*) FROM household_members", null).use { if (it.moveToFirst()) it.getInt(0) else 0 }
        if (memberCount == 0) {
            insertMember(db, "من")
            insertMember(db, "مشترک")
            insertMember(db, "هم‌خانه")
        }
    }

    private fun insertAccount(db: SQLiteDatabase, account: Account) {
        val v = ContentValues().apply {
            put("name", account.name); put("type", account.type); put("opening_balance", account.openingBalance); put("icon", account.icon)
        }
        db.insertWithOnConflict("accounts", null, v, SQLiteDatabase.CONFLICT_IGNORE)
    }

    private fun insertMember(db: SQLiteDatabase, name: String) {
        db.insertWithOnConflict("household_members", null, ContentValues().apply { put("name", name) }, SQLiteDatabase.CONFLICT_IGNORE)
    }

    fun getEntries(): List<LedgerEntry> {
        val result = mutableListOf<LedgerEntry>()
        readableDatabase.query("entries", null, null, null, null, null, "occurred_at DESC, id DESC").use { c ->
            while (c.moveToNext()) {
                result += LedgerEntry(
                    id = c.long("id"),
                    type = EntryType.valueOf(c.string("type")),
                    amount = c.long("amount"),
                    category = c.string("category"),
                    subcategory = c.string("subcategory"),
                    tags = c.string("tags").split(TAG_SEP).filter { it.isNotBlank() },
                    note = c.string("note"),
                    occurredAt = c.long("occurred_at"),
                    createdAt = c.long("created_at"),
                    accountName = c.stringOr("account_name", "حساب اصلی"),
                    memberName = c.stringOr("member_name", "من"),
                    source = c.stringOr("source", "manual")
                )
            }
        }
        return result
    }

    fun saveEntry(entry: LedgerEntry): Long {
        val v = ContentValues().apply {
            put("type", entry.type.name); put("amount", entry.amount); put("category", entry.category)
            put("subcategory", entry.subcategory); put("tags", entry.tags.joinToString(TAG_SEP)); put("note", entry.note)
            put("occurred_at", entry.occurredAt); put("created_at", entry.createdAt); put("account_name", entry.accountName)
            put("member_name", entry.memberName); put("source", entry.source)
        }
        return if (entry.id == 0L) writableDatabase.insertOrThrow("entries", null, v) else {
            writableDatabase.update("entries", v, "id = ?", arrayOf(entry.id.toString())); entry.id
        }
    }

    fun deleteEntry(id: Long) { writableDatabase.delete("entries", "id = ?", arrayOf(id.toString())) }

    fun getDebts(kind: ObligationKind? = null): List<Debt> {
        val result = mutableListOf<Debt>()
        val sel = if (kind == null) null else "kind = ?"
        val args = if (kind == null) null else arrayOf(kind.name)
        readableDatabase.query("debts", null, sel, args, null, null, "updated_at DESC, id DESC").use { c ->
            while (c.moveToNext()) {
                result += Debt(
                    id = c.long("id"), name = c.string("name"), originalAmount = c.long("original_amount"),
                    currentAmount = c.long("current_amount"), note = c.string("note"), occurredAt = c.long("occurred_at"),
                    updatedAt = c.long("updated_at"), kind = runCatching { ObligationKind.valueOf(c.stringOr("kind", "DEBT")) }.getOrDefault(ObligationKind.DEBT),
                    dueAt = c.longOr("due_at", 0L), reminderAt = c.longOr("reminder_at", 0L)
                )
            }
        }
        return result
    }

    fun saveDebt(debt: Debt): Long {
        val db = writableDatabase
        val now = System.currentTimeMillis()
        val previousAmount = if (debt.id == 0L) null else db.rawQuery(
            "SELECT current_amount FROM debts WHERE id = ?", arrayOf(debt.id.toString())
        ).use { c -> if (c.moveToFirst()) c.getLong(0) else null }
        val v = ContentValues().apply {
            put("name", debt.name.trim()); put("original_amount", debt.originalAmount); put("current_amount", debt.currentAmount)
            put("note", debt.note.trim()); put("occurred_at", debt.occurredAt); put("updated_at", now); put("kind", debt.kind.name)
            put("due_at", debt.dueAt); put("reminder_at", debt.reminderAt)
        }
        val id = if (debt.id == 0L) db.insertOrThrow("debts", null, v) else {
            db.update("debts", v, "id = ?", arrayOf(debt.id.toString())); debt.id
        }
        if (debt.id == 0L || previousAmount != debt.currentAmount) {
            db.insertOrThrow("debt_history", null, ContentValues().apply {
                put("debt_id", id); put("amount", debt.currentAmount)
                put("occurred_at", if (debt.id == 0L) debt.occurredAt else now)
            })
        }
        return id
    }

    fun deleteDebt(id: Long) {
        writableDatabase.delete("debt_history", "debt_id = ?", arrayOf(id.toString()))
        writableDatabase.delete("debts", "id = ?", arrayOf(id.toString()))
    }

    fun getDebtSnapshots(): List<DebtSnapshot> {
        val result = mutableListOf<DebtSnapshot>()
        readableDatabase.query("debt_history", null, null, null, null, null, "occurred_at ASC, id ASC").use { c ->
            while (c.moveToNext()) result += DebtSnapshot(c.long("id"), c.long("debt_id"), c.long("amount"), c.long("occurred_at"))
        }
        return result
    }

    fun addCustomCategory(type: EntryType, name: String, subcategory: String) {
        if (name.isBlank()) return
        val n = if (name.trim() == "رفت‌وآمد") "خودرو و تردد" else name.trim()
        val exists = readableDatabase.rawQuery(
            "SELECT id FROM custom_categories WHERE type = ? AND name = ? AND subcategory = ? LIMIT 1",
            arrayOf(type.name, n, subcategory.trim())
        ).use { it.moveToFirst() }
        if (!exists) writableDatabase.insertOrThrow("custom_categories", null, ContentValues().apply {
            put("type", type.name); put("name", n); put("subcategory", subcategory.trim())
        })
    }

    fun getCustomCategories(type: EntryType? = null): List<CategoryRow> {
        val rows = mutableListOf<CategoryRow>()
        val sel = if (type == null) null else "type = ?"
        val args = if (type == null) null else arrayOf(type.name)
        readableDatabase.query("custom_categories", null, sel, args, null, null, "type, name, subcategory").use { c ->
            while (c.moveToNext()) rows += CategoryRow(c.long("id"), EntryType.valueOf(c.string("type")), c.string("name"), c.string("subcategory"))
        }
        return rows
    }

    fun addCustomTag(tag: String) {
        val cleaned = tag.trim().removePrefix("#")
        if (cleaned.isNotBlank()) writableDatabase.insertWithOnConflict(
            "custom_tags", null, ContentValues().apply { put("name", cleaned) }, SQLiteDatabase.CONFLICT_IGNORE
        )
    }

    fun getCustomTags(): List<String> {
        val out = mutableListOf<String>()
        readableDatabase.query("custom_tags", arrayOf("name"), null, null, null, null, "name").use { c -> while (c.moveToNext()) out += c.getString(0) }
        return out
    }

    fun getSetting(key: String, defaultValue: String = ""): String = readableDatabase.rawQuery(
        "SELECT value FROM settings WHERE key = ? LIMIT 1", arrayOf(key)
    ).use { if (it.moveToFirst()) it.getString(0) else defaultValue }

    fun setSetting(key: String, value: String) {
        writableDatabase.insertWithOnConflict("settings", null, ContentValues().apply { put("key", key); put("value", value) }, SQLiteDatabase.CONFLICT_REPLACE)
    }

    fun getAccounts(): List<Account> {
        seedDefaults(writableDatabase)
        val out = mutableListOf<Account>()
        readableDatabase.query("accounts", null, null, null, null, null, "id").use { c ->
            while (c.moveToNext()) out += Account(c.long("id"), c.string("name"), c.string("type"), c.long("opening_balance"), c.string("icon"))
        }
        return out
    }

    fun saveAccount(account: Account): Long {
        val v = ContentValues().apply { put("name", account.name.trim()); put("type", account.type); put("opening_balance", account.openingBalance); put("icon", account.icon) }
        return if (account.id == 0L) writableDatabase.insertWithOnConflict("accounts", null, v, SQLiteDatabase.CONFLICT_IGNORE) else {
            writableDatabase.update("accounts", v, "id = ?", arrayOf(account.id.toString())); account.id
        }
    }

    fun getMembers(): List<HouseholdMember> {
        seedDefaults(writableDatabase)
        val out = mutableListOf<HouseholdMember>()
        readableDatabase.query("household_members", null, null, null, null, null, "id").use { c -> while (c.moveToNext()) out += HouseholdMember(c.long("id"), c.string("name")) }
        return out
    }

    fun addMember(name: String) {
        if (name.isNotBlank()) writableDatabase.insertWithOnConflict("household_members", null, ContentValues().apply { put("name", name.trim()) }, SQLiteDatabase.CONFLICT_IGNORE)
    }

    fun getRecurringRules(): List<RecurringRule> {
        val out = mutableListOf<RecurringRule>()
        readableDatabase.query("recurring_rules", null, null, null, null, null, "next_run_at").use { c ->
            while (c.moveToNext()) out += RecurringRule(
                id = c.long("id"), type = EntryType.valueOf(c.string("type")), amount = c.long("amount"), category = c.string("category"),
                subcategory = c.string("subcategory"), note = c.string("note"), accountName = c.string("account_name"), memberName = c.string("member_name"),
                frequency = RecurrenceFrequency.valueOf(c.string("frequency")), dayOfMonth = c.int("day_of_month"), nextRunAt = c.long("next_run_at"), enabled = c.int("enabled") == 1
            )
        }
        return out
    }

    fun saveRecurringRule(rule: RecurringRule): Long {
        val v = ContentValues().apply {
            put("type", rule.type.name); put("amount", rule.amount); put("category", rule.category); put("subcategory", rule.subcategory); put("note", rule.note)
            put("account_name", rule.accountName); put("member_name", rule.memberName); put("frequency", rule.frequency.name); put("day_of_month", rule.dayOfMonth)
            put("next_run_at", rule.nextRunAt); put("enabled", if (rule.enabled) 1 else 0)
        }
        return if (rule.id == 0L) writableDatabase.insertOrThrow("recurring_rules", null, v) else { writableDatabase.update("recurring_rules", v, "id = ?", arrayOf(rule.id.toString())); rule.id }
    }

    fun deleteRecurringRule(id: Long) { writableDatabase.delete("recurring_rules", "id = ?", arrayOf(id.toString())) }

    fun materializeRecurring(now: Long = System.currentTimeMillis()): Int {
        var count = 0
        getRecurringRules().filter { it.enabled }.forEach { rule ->
            var next = rule.nextRunAt
            var guard = 0
            while (next <= now && guard < 36) {
                saveEntry(LedgerEntry(type = rule.type, amount = rule.amount, category = rule.category, subcategory = rule.subcategory,
                    note = if (rule.note.isBlank()) "تراکنش تکرارشونده" else rule.note, occurredAt = next, accountName = rule.accountName, memberName = rule.memberName, source = "recurring"))
                next = when (rule.frequency) {
                    RecurrenceFrequency.WEEKLY -> PersianDate.addDays(next, 7)
                    RecurrenceFrequency.MONTHLY -> PersianDate.addMonths(next, 1)
                    RecurrenceFrequency.YEARLY -> PersianDate.addMonths(next, 12)
                }
                count++; guard++
            }
            if (next != rule.nextRunAt) saveRecurringRule(rule.copy(nextRunAt = next))
        }
        return count
    }

    fun getReminders(): List<ReminderItem> {
        val out = mutableListOf<ReminderItem>()
        readableDatabase.query("reminders", null, null, null, null, null, "remind_at ASC").use { c ->
            while (c.moveToNext()) out += ReminderItem(
                c.long("id"), c.string("title"), c.string("note"), ReminderKind.valueOf(c.string("kind")), c.long("due_at"), c.long("remind_at"), c.int("enabled") == 1, c.long("linked_id")
            )
        }
        return out
    }

    fun saveReminder(item: ReminderItem): Long {
        val v = ContentValues().apply { put("title", item.title); put("note", item.note); put("kind", item.kind.name); put("due_at", item.dueAt); put("remind_at", item.remindAt); put("enabled", if (item.enabled) 1 else 0); put("linked_id", item.linkedId) }
        return if (item.id == 0L) writableDatabase.insertOrThrow("reminders", null, v) else { writableDatabase.update("reminders", v, "id = ?", arrayOf(item.id.toString())); item.id }
    }

    fun deleteReminder(id: Long) { writableDatabase.delete("reminders", "id = ?", arrayOf(id.toString())) }

    fun getInstallments(): List<InstallmentPlan> {
        val out = mutableListOf<InstallmentPlan>()
        readableDatabase.query("installments", null, null, null, null, null, "next_due_at ASC").use { c ->
            while (c.moveToNext()) out += InstallmentPlan(c.long("id"), c.string("title"), c.long("installment_amount"), c.int("remaining_count"), c.long("next_due_at"), c.string("account_name"), c.string("note"), c.int("reminder_days_before"), c.int("enabled") == 1)
        }
        return out
    }

    fun saveInstallment(plan: InstallmentPlan): Long {
        val v = ContentValues().apply { put("title", plan.title); put("installment_amount", plan.installmentAmount); put("remaining_count", plan.remainingCount); put("next_due_at", plan.nextDueAt); put("account_name", plan.accountName); put("note", plan.note); put("reminder_days_before", plan.reminderDaysBefore); put("enabled", if (plan.enabled) 1 else 0) }
        return if (plan.id == 0L) writableDatabase.insertOrThrow("installments", null, v) else { writableDatabase.update("installments", v, "id = ?", arrayOf(plan.id.toString())); plan.id }
    }

    fun advanceInstallment(plan: InstallmentPlan) {
        val remaining = (plan.remainingCount - 1).coerceAtLeast(0)
        saveInstallment(plan.copy(remainingCount = remaining, nextDueAt = PersianDate.addMonths(plan.nextDueAt, 1), enabled = remaining > 0))
    }

    fun deleteInstallment(id: Long) { writableDatabase.delete("installments", "id = ?", arrayOf(id.toString())) }

    fun saveBankImport(item: BankImport): Long {
        val v = ContentValues().apply { put("sender", item.sender); put("body", item.body); put("amount", item.amount); put("direction", item.direction.name); put("occurred_at", item.occurredAt); put("created_at", item.createdAt); put("status", item.status); put("hash", item.hash) }
        return writableDatabase.insertWithOnConflict("bank_imports", null, v, SQLiteDatabase.CONFLICT_IGNORE)
    }

    fun getBankImports(status: String? = "pending"): List<BankImport> {
        val out = mutableListOf<BankImport>()
        val sel = if (status == null) null else "status = ?"
        val args = if (status == null) null else arrayOf(status)
        readableDatabase.query("bank_imports", null, sel, args, null, null, "occurred_at DESC, id DESC").use { c ->
            while (c.moveToNext()) out += BankImport(c.long("id"), c.string("sender"), c.string("body"), c.long("amount"), BankImportDirection.valueOf(c.string("direction")), c.long("occurred_at"), c.long("created_at"), c.string("status"), c.string("hash"))
        }
        return out
    }

    fun updateBankImportStatus(id: Long, status: String) { writableDatabase.update("bank_imports", ContentValues().apply { put("status", status) }, "id = ?", arrayOf(id.toString())) }

    fun getBudget(): Long = getSetting("monthly_budget", "0").toLongOrNull() ?: 0L
    fun setBudget(amount: Long) = setSetting("monthly_budget", amount.toString())

    fun exportJson(): String {
        val root = JSONObject().put("format", "kharjyar-backup").put("version", 3).put("createdAt", System.currentTimeMillis())
        BACKUP_TABLES.forEach { table -> root.put(table, dumpTable(table)) }
        return root.toString(2)
    }

    private fun dumpTable(table: String): JSONArray {
        val array = JSONArray()
        readableDatabase.query(table, null, null, null, null, null, null).use { c ->
            while (c.moveToNext()) {
                val obj = JSONObject()
                for (i in 0 until c.columnCount) {
                    when (c.getType(i)) {
                        Cursor.FIELD_TYPE_NULL -> obj.put(c.getColumnName(i), JSONObject.NULL)
                        Cursor.FIELD_TYPE_INTEGER -> obj.put(c.getColumnName(i), c.getLong(i))
                        Cursor.FIELD_TYPE_FLOAT -> obj.put(c.getColumnName(i), c.getDouble(i))
                        Cursor.FIELD_TYPE_BLOB -> Unit
                        else -> obj.put(c.getColumnName(i), c.getString(i))
                    }
                }
                array.put(obj)
            }
        }
        return array
    }

    fun importJson(json: String) {
        val root = JSONObject(json)
        require(root.optString("format") == "kharjyar-backup") { "فایل بکاپ خرج‌یار معتبر نیست." }
        val db = writableDatabase
        db.beginTransaction()
        try {
            BACKUP_TABLES.reversed().forEach { table -> db.delete(table, null, null) }
            BACKUP_TABLES.forEach { table ->
                val array = root.optJSONArray(table) ?: JSONArray()
                for (i in 0 until array.length()) {
                    val obj = array.getJSONObject(i)
                    val values = ContentValues()
                    obj.keys().forEach { key ->
                        val value = obj.opt(key)
                        when (value) {
                            null, JSONObject.NULL -> values.putNull(key)
                            is Int -> values.put(key, value)
                            is Long -> values.put(key, value)
                            is Double -> values.put(key, value)
                            is Boolean -> values.put(key, if (value) 1 else 0)
                            else -> values.put(key, value.toString())
                        }
                    }
                    db.insertWithOnConflict(table, null, values, SQLiteDatabase.CONFLICT_REPLACE)
                }
            }
            seedDefaults(db)
            db.setTransactionSuccessful()
        } finally { db.endTransaction() }
    }

    private fun Cursor.string(name: String): String = getString(getColumnIndexOrThrow(name))
    private fun Cursor.long(name: String): Long = getLong(getColumnIndexOrThrow(name))
    private fun Cursor.int(name: String): Int = getInt(getColumnIndexOrThrow(name))
    private fun Cursor.stringOr(name: String, default: String): String { val i = getColumnIndex(name); return if (i < 0 || isNull(i)) default else getString(i) }
    private fun Cursor.longOr(name: String, default: Long): Long { val i = getColumnIndex(name); return if (i < 0 || isNull(i)) default else getLong(i) }
}

class LedgerRepository(context: Context) {
    private val db = LedgerDb(context.applicationContext)

    fun entries(): List<LedgerEntry> = db.getEntries()
    fun save(entry: LedgerEntry): Long = db.saveEntry(entry)
    fun delete(id: Long) = db.deleteEntry(id)

    fun debts(kind: ObligationKind? = null): List<Debt> = db.getDebts(kind)
    fun saveDebt(debt: Debt): Long = db.saveDebt(debt)
    fun deleteDebt(id: Long) = db.deleteDebt(id)
    fun debtSnapshots(): List<DebtSnapshot> = db.getDebtSnapshots()
    fun currentDebtTotal(kind: ObligationKind = ObligationKind.DEBT): Long = db.getDebts(kind).sumOf { it.currentAmount }
    fun debtTotalAt(timeMillis: Long, kind: ObligationKind = ObligationKind.DEBT): Long {
        val allowedIds = db.getDebts(kind).map { it.id }.toSet()
        return db.getDebtSnapshots().filter { it.debtId in allowedIds && it.occurredAt <= timeMillis }
            .groupBy { it.debtId }.values.sumOf { snapshots -> snapshots.maxWithOrNull(compareBy<DebtSnapshot> { it.occurredAt }.thenBy { it.id })?.amount ?: 0L }
    }

    fun customCategories(type: EntryType? = null): List<CategoryRow> = db.getCustomCategories(type)
    fun addCategory(type: EntryType, name: String, subcategory: String) = db.addCustomCategory(type, name, subcategory)
    fun customTags(): List<String> = db.getCustomTags()
    fun addTag(tag: String) = db.addCustomTag(tag)

    fun accounts(): List<Account> = db.getAccounts()
    fun saveAccount(account: Account) = db.saveAccount(account)
    fun members(): List<HouseholdMember> = db.getMembers()
    fun addMember(name: String) = db.addMember(name)

    fun recurringRules(): List<RecurringRule> = db.getRecurringRules()
    fun saveRecurring(rule: RecurringRule) = db.saveRecurringRule(rule)
    fun deleteRecurring(id: Long) = db.deleteRecurringRule(id)
    fun materializeRecurring(): Int = db.materializeRecurring()

    fun reminders(): List<ReminderItem> = db.getReminders()
    fun saveReminder(item: ReminderItem): Long = db.saveReminder(item)
    fun deleteReminder(id: Long) = db.deleteReminder(id)

    fun installments(): List<InstallmentPlan> = db.getInstallments()
    fun saveInstallment(plan: InstallmentPlan): Long = db.saveInstallment(plan)
    fun advanceInstallment(plan: InstallmentPlan) = db.advanceInstallment(plan)
    fun deleteInstallment(id: Long) = db.deleteInstallment(id)

    fun bankImports(status: String? = "pending"): List<BankImport> = db.getBankImports(status)
    fun saveBankImport(item: BankImport): Long = db.saveBankImport(item)
    fun updateBankImportStatus(id: Long, status: String) = db.updateBankImportStatus(id, status)

    fun budget(): Long = db.getBudget()
    fun setBudget(amount: Long) = db.setBudget(amount)
    fun setting(key: String, defaultValue: String = ""): String = db.getSetting(key, defaultValue)
    fun setSetting(key: String, value: String) = db.setSetting(key, value)

    fun exportJson(): String = db.exportJson()
    fun importJson(json: String) = db.importJson(json)
}
