#!/usr/bin/env python3
from pathlib import Path
import re
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
main = root / "app/src/main/java/com/example/kharjyar/MainActivity.kt"
ledger = root / "app/src/main/java/com/example/kharjyar/LedgerDb.kt"
gradle = root / "app/build.gradle.kts"

for p in (main, ledger, gradle):
    if not p.exists():
        raise SystemExit(f"missing required file: {p}")

def sub_once(pattern: str, repl: str, text: str, label: str, flags=0) -> str:
    out, count = re.subn(pattern, repl, text, count=1, flags=flags)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly 1 match, found {count}")
    return out

def replace_between(text: str, start_marker: str, end_marker: str, replacement: str, label: str) -> str:
    start = text.find(start_marker)
    if start < 0:
        raise SystemExit(f"{label}: start marker not found")
    end = text.find(end_marker, start + len(start_marker))
    if end < 0:
        raise SystemExit(f"{label}: end marker not found")
    return text[:start] + replacement + text[end:]

# 1) Version bump only. KEEP V5 signing unchanged.
g = gradle.read_text(encoding="utf-8")
if 'applicationId = "io.github.hutoto147.dakhlokharj"' not in g:
    raise SystemExit("unexpected applicationId; refusing to patch")
if 'storeFile = file("kharjyar-v5-debug.keystore")' not in g:
    raise SystemExit("V5 debug signing config is missing; refusing to change signing identity")

if 'versionCode = 5' in g:
    g = g.replace('versionCode = 5', 'versionCode = 6', 1)
elif 'versionCode = 6' not in g:
    raise SystemExit("versionCode is neither 5 nor 6")

if 'versionName = "1.0.5"' in g:
    g = g.replace('versionName = "1.0.5"', 'versionName = "1.0.6"', 1)
elif 'versionName = "1.0.6"' not in g:
    raise SystemExit("versionName is neither 1.0.5 nor 1.0.6")

gradle.write_text(g, encoding="utf-8")

# 2) MainActivity: safe backup/restore + cleaner household member UI
m = main.read_text(encoding="utf-8")

if "var showMemberAdder by rememberSaveable" not in m:
    m = sub_once(
        r'(?m)^(\s*var memberName by remember \{ mutableStateOf\(""\) \}\s*)$',
        r'\1\n    var showMemberAdder by rememberSaveable { mutableStateOf(false) }',
        m,
        "member adder state"
    )

backup_start = '    val backupLauncher = rememberLauncherForActivityResult(ActivityResultContracts.CreateDocument("application/json"))'
xlsx_start = '    val xlsxLauncher = rememberLauncherForActivityResult('

if "restoreBackupFromUri(context, repo, uri)" not in m:
    launcher_block = r'''    val backupLauncher = rememberLauncherForActivityResult(ActivityResultContracts.CreateDocument("application/json")) { uri ->
        uri ?: return@rememberLauncherForActivityResult
        runCatching {
            val stream = context.contentResolver.openOutputStream(uri, "w")
                ?: error("امکان نوشتن فایل وجود ندارد")
            stream.writer(Charsets.UTF_8).use { it.write(repo.exportJson()) }
        }.onSuccess {
            status = "بکاپ با موفقیت ذخیره شد."
        }.onFailure {
            status = "خطا در ذخیره بکاپ: ${it.message ?: "خطای نامشخص"}"
        }
    }
    val restoreLauncher = rememberLauncherForActivityResult(ActivityResultContracts.OpenDocument()) { uri ->
        uri ?: return@rememberLauncherForActivityResult
        runCatching {
            restoreBackupFromUri(context, repo, uri)
        }.onSuccess {
            status = "بکاپ با موفقیت بازیابی شد."
            onChanged()
        }.onFailure {
            status = "بازیابی ناموفق: ${it.message ?: "خطای نامشخص"}"
        }
    }
'''
    m = replace_between(m, backup_start, xlsx_start, launcher_block, "backup launchers")

backup_section_start = '        SettingsAccordionSection("بکاپ و انتقال اطلاعات"'
bank_section_start = '        SettingsAccordionSection("اعلان بانکی و حساب‌ها"'

new_backup_section = r'''        SettingsAccordionSection("بکاپ و انتقال اطلاعات", "بکاپ، بازیابی، Excel و PDF", openSection == "backup", { openSection = if (openSection == "backup") null else "backup" }) {
            Text("بکاپ شامل تراکنش‌ها، بدهی و قرض، حساب‌ها، دسته‌ها، تگ‌ها، تنظیمات، اقساط و یادآورهاست.", modifier = Modifier.fillMaxWidth(), textAlign = TextAlign.Start, fontSize = 12.sp)
            Text("برنامه دسترسی عمومی به فایل‌های گوشی نمی‌گیرد. بکاپ در Downloads ذخیره می‌شود و برای بازیابی فقط فایلی که خودتان انتخاب می‌کنید خوانده می‌شود.", modifier = Modifier.fillMaxWidth(), textAlign = TextAlign.Start, fontSize = 11.sp)

            Button(modifier = Modifier.fillMaxWidth(), onClick = {
                val suggestedName = "DakhlKharj-Backup-${PersianDate.format(System.currentTimeMillis()).replace("/", "-")}.json"
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
                    runCatching { saveBackupToDownloads(context, repo.exportJson(), suggestedName) }
                        .onSuccess { status = "بکاپ در پوشه Downloads ذخیره شد: $it" }
                        .onFailure {
                            status = "ذخیره مستقیم ممکن نشد؛ محل ذخیره را انتخاب کنید."
                            backupLauncher.launchSafely(suggestedName) { message -> status = message }
                        }
                } else {
                    backupLauncher.launchSafely(suggestedName) { message -> status = message }
                }
            }) { Text("تهیه بکاپ") }

            OutlinedButton(modifier = Modifier.fillMaxWidth(), onClick = {
                restoreLauncher.launchSafely(arrayOf("application/json", "text/plain", "*/*")) { message -> status = message }
            }) { Text("انتخاب فایل بکاپ و بازیابی") }

            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                OutlinedButton(modifier = Modifier.weight(1f), onClick = { xlsxLauncher.launchSafely("KharjYar-Transactions.xlsx") { status = it } }) { Text("خروجی Excel") }
                OutlinedButton(modifier = Modifier.weight(1f), onClick = { pdfLauncher.launchSafely("KharjYar-Report.pdf") { status = it } }) { Text("خروجی PDF") }
            }
        }
'''
m = replace_between(m, backup_section_start, bank_section_start, new_backup_section, "backup settings section")

members_section_start = '        SettingsAccordionSection("اعضای خانواده"'
recurring_section_start = '        SettingsAccordionSection("تراکنش‌های تکرارشونده"'

new_members_section = r'''        SettingsAccordionSection("اعضای خانواده", "${members.size.toString().toPersianDigits()} عضو", openSection == "members", { openSection = if (openSection == "members") null else "members" }) {
            Text("به‌صورت پیش‌فرض فقط «من» وجود دارد. هر عضو دیگری را خودتان با نام دلخواه اضافه کنید.", modifier = Modifier.fillMaxWidth(), textAlign = TextAlign.Start, fontSize = 12.sp)

            members.forEach { member ->
                Card(Modifier.fillMaxWidth(), shape = RoundedCornerShape(14.dp)) {
                    Row(
                        Modifier.fillMaxWidth().padding(horizontal = 12.dp, vertical = 8.dp),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Column(Modifier.weight(1f)) {
                            Text(member.name, fontWeight = FontWeight.SemiBold)
                            if (member.name == "من") Text("عضو پیش‌فرض", fontSize = 11.sp)
                        }
                        if (member.name != "من") {
                            TextButton(onClick = {
                                val removed = repo.deleteMember(member.id)
                                status = if (removed) {
                                    "عضو «${member.name}» حذف شد. تراکنش‌های قبلی او بدون تغییر باقی ماندند."
                                } else {
                                    "این عضو قابل حذف نیست؛ اگر در تراکنش تکرارشونده استفاده شده، ابتدا آن مورد را حذف کنید."
                                }
                                if (removed) onChanged()
                            }) { Text("حذف") }
                        }
                    }
                }
            }

            if (showMemberAdder) {
                OutlinedTextField(
                    memberName,
                    { memberName = it },
                    Modifier.fillMaxWidth(),
                    label = { Text("نام عضو جدید") },
                    placeholder = { Text("مثلاً همسر، فرزند، هم‌خانه") },
                    singleLine = true,
                    textStyle = LocalTextStyle.current.copy(textAlign = TextAlign.Start)
                )
                Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    Button(modifier = Modifier.weight(1f), onClick = {
                        val name = memberName.trim()
                        if (name.isBlank()) {
                            status = "نام عضو را وارد کنید."
                        } else if (repo.addMember(name)) {
                            memberName = ""
                            showMemberAdder = false
                            status = "عضو جدید اضافه شد."
                            onChanged()
                        } else {
                            status = "این نام قبلاً وجود دارد."
                        }
                    }) { Text("ذخیره عضو") }

                    OutlinedButton(modifier = Modifier.weight(1f), onClick = {
                        memberName = ""
                        showMemberAdder = false
                    }) { Text("انصراف") }
                }
            } else {
                OutlinedButton(modifier = Modifier.fillMaxWidth(), onClick = {
                    showMemberAdder = true
                }) { Text("＋ افزودن عضو") }
            }
        }
'''
m = replace_between(m, members_section_start, recurring_section_start, new_members_section, "members settings section")

m = m.replace('نسخه آزمایشی ۱.۰.۵', 'نسخه آزمایشی ۱.۰.۶')

helper_anchor = 'private fun <I> ActivityResultLauncher<I>.launchSafely(input: I, onFailure: (String) -> Unit) {'
if "private fun saveBackupToDownloads(" not in m:
    helper_code = r'''private fun saveBackupToDownloads(context: android.content.Context, json: String, fileName: String): String {
    require(Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q)
    val resolver = context.contentResolver
    val values = android.content.ContentValues().apply {
        put(android.provider.MediaStore.MediaColumns.DISPLAY_NAME, fileName)
        put(android.provider.MediaStore.MediaColumns.MIME_TYPE, "application/json")
        put(android.provider.MediaStore.MediaColumns.RELATIVE_PATH, android.os.Environment.DIRECTORY_DOWNLOADS)
    }
    val uri = resolver.insert(android.provider.MediaStore.Downloads.EXTERNAL_CONTENT_URI, values)
        ?: error("امکان ساخت فایل بکاپ در Downloads وجود ندارد")
    try {
        val stream = resolver.openOutputStream(uri, "w")
            ?: error("امکان نوشتن فایل بکاپ وجود ندارد")
        stream.writer(Charsets.UTF_8).use { it.write(json) }
    } catch (t: Throwable) {
        runCatching { resolver.delete(uri, null, null) }
        throw t
    }
    return fileName
}

private fun restoreBackupFromUri(context: android.content.Context, repo: LedgerRepository, uri: Uri) {
    val json = context.contentResolver.openInputStream(uri)
        ?.bufferedReader(Charsets.UTF_8)
        ?.use { it.readText() }
        ?: error("فایل بکاپ خوانده نشد")
    repo.importJson(json)
    ReminderScheduler.scheduleAll(context)
}

'''
    if helper_anchor not in m:
        raise SystemExit("launchSafely helper anchor not found")
    m = m.replace(helper_anchor, helper_code + helper_anchor, 1)

main.write_text(m, encoding="utf-8")

# 3) LedgerDb
l = ledger.read_text(encoding="utf-8")

# Fresh install: only "من".
l = re.sub(
    r'(?m)^\s*insertMember\(db, "مشترک"\)\s*\n\s*insertMember\(db, "هم‌خانه"\)\s*\n',
    '',
    l,
    count=1
)

member_methods_start = '    fun getMembers(): List<HouseholdMember> {'
recurring_methods_start = '    fun getRecurringRules(): List<RecurringRule> {'

new_member_methods = r'''    private fun migrateLegacyHouseholdDefaults(db: SQLiteDatabase) {
        val alreadyDone = db.rawQuery(
            "SELECT value FROM settings WHERE key = ? LIMIT 1",
            arrayOf("household_defaults_v6")
        ).use { it.moveToFirst() && it.getString(0) == "1" }
        if (alreadyDone) return

        listOf("مشترک", "هم‌خانه").forEach { legacyName ->
            val usedInEntries = db.rawQuery(
                "SELECT 1 FROM entries WHERE member_name = ? LIMIT 1",
                arrayOf(legacyName)
            ).use { it.moveToFirst() }
            val usedInRecurring = db.rawQuery(
                "SELECT 1 FROM recurring_rules WHERE member_name = ? LIMIT 1",
                arrayOf(legacyName)
            ).use { it.moveToFirst() }

            if (!usedInEntries && !usedInRecurring) {
                db.delete("household_members", "name = ?", arrayOf(legacyName))
            }
        }

        db.insertWithOnConflict(
            "settings",
            null,
            ContentValues().apply {
                put("key", "household_defaults_v6")
                put("value", "1")
            },
            SQLiteDatabase.CONFLICT_REPLACE
        )
    }

    fun getMembers(): List<HouseholdMember> {
        val db = writableDatabase
        seedDefaults(db)
        migrateLegacyHouseholdDefaults(db)

        val out = mutableListOf<HouseholdMember>()
        readableDatabase.query(
            "household_members",
            null,
            null,
            null,
            null,
            null,
            "CASE WHEN name = 'من' THEN 0 ELSE 1 END, id"
        ).use { c ->
            while (c.moveToNext()) {
                out += HouseholdMember(c.long("id"), c.string("name"))
            }
        }
        return out
    }

    fun addMember(name: String): Boolean {
        val cleaned = name.trim()
        if (cleaned.isBlank()) return false
        return writableDatabase.insertWithOnConflict(
            "household_members",
            null,
            ContentValues().apply { put("name", cleaned) },
            SQLiteDatabase.CONFLICT_IGNORE
        ) != -1L
    }

    fun deleteMember(id: Long): Boolean {
        val db = writableDatabase
        val name = db.rawQuery(
            "SELECT name FROM household_members WHERE id = ? LIMIT 1",
            arrayOf(id.toString())
        ).use {
            if (it.moveToFirst()) it.getString(0) else null
        } ?: return false

        if (name == "من") return false

        val usedInRecurring = db.rawQuery(
            "SELECT 1 FROM recurring_rules WHERE member_name = ? LIMIT 1",
            arrayOf(name)
        ).use { it.moveToFirst() }

        if (usedInRecurring) return false

        return db.delete("household_members", "id = ?", arrayOf(id.toString())) > 0
    }

'''
l = replace_between(l, member_methods_start, recurring_methods_start, new_member_methods, "database member methods")

repo_members_start = '    fun members(): List<HouseholdMember> = db.getMembers()'
repo_recurring_start = '    fun recurringRules(): List<RecurringRule> = db.getRecurringRules()'

new_repo_members = r'''    fun members(): List<HouseholdMember> = db.getMembers()
    fun addMember(name: String): Boolean = db.addMember(name)
    fun deleteMember(id: Long): Boolean = db.deleteMember(id)

'''
l = replace_between(l, repo_members_start, repo_recurring_start, new_repo_members, "repository member methods")

ledger.write_text(l, encoding="utf-8")

# 4) Self-checks
g2 = gradle.read_text(encoding="utf-8")
m2 = main.read_text(encoding="utf-8")
l2 = ledger.read_text(encoding="utf-8")

checks = {
    "versionCode 6": 'versionCode = 6' in g2,
    "V5 signing preserved": 'storeFile = file("kharjyar-v5-debug.keystore")' in g2,
    "backup helper": 'private fun saveBackupToDownloads(' in m2,
    "safe restore": 'restoreBackupFromUri(context, repo, uri)' in m2,
    "member adder": 'showMemberAdder' in m2,
    "member delete": 'fun deleteMember(id: Long): Boolean' in l2,
    "fresh default only me": 'insertMember(db, "مشترک")' not in l2 and 'insertMember(db, "هم‌خانه")' not in l2,
}
failed = [name for name, ok in checks.items() if not ok]
if failed:
    raise SystemExit("post-patch self-check failed: " + ", ".join(failed))

print("V6 robust update applied successfully.")
print("- versionCode: 6")
print("- V5 signing identity preserved")
print("- backup saves to Downloads without broad storage permission")
print("- restore uses Android document picker safely")
print("- fresh installs default to only «من»")
print("- custom members can be added and removed")
