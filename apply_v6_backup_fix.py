#!/usr/bin/env python3
from pathlib import Path
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
main = root / "app/src/main/java/com/example/kharjyar/MainActivity.kt"
ledger = root / "app/src/main/java/com/example/kharjyar/LedgerDb.kt"
gradle = root / "app/build.gradle.kts"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly 1 match, found {count}")
    return text.replace(old, new, 1)

# --- version bump: V5 -> V6 ---
g = gradle.read_text(encoding="utf-8")
if 'versionCode = 5' in g:
    g = replace_once(g, 'versionCode = 5', 'versionCode = 6', 'versionCode')
elif 'versionCode = 6' not in g:
    raise SystemExit('versionCode: expected V5 or V6 source')
if 'versionName = "1.0.5"' in g:
    g = replace_once(g, 'versionName = "1.0.5"', 'versionName = "1.0.6"', 'versionName')
elif 'versionName = "1.0.6"' not in g:
    raise SystemExit('versionName: expected V5 or V6 source')
gradle.write_text(g, encoding="utf-8")

m = main.read_text(encoding="utf-8")

# --- backup / restore safety ---
old_launchers = '''    val backupLauncher = rememberLauncherForActivityResult(ActivityResultContracts.CreateDocument("application/json")) { uri ->
        uri ?: return@rememberLauncherForActivityResult
        runCatching { context.contentResolver.openOutputStream(uri)?.use { it.write(repo.exportJson().toByteArray(Charsets.UTF_8)) } }
            .onSuccess { status = "بکاپ ذخیره شد. اگر Google Drive را انتخاب کرده باشید، فایل در فضای ابری شماست." }
            .onFailure { status = "خطا در ذخیره بکاپ: ${it.message}" }
    }
    val restoreLauncher = rememberLauncherForActivityResult(ActivityResultContracts.OpenDocument()) { uri ->
        uri ?: return@rememberLauncherForActivityResult
        runCatching {
            val json = context.contentResolver.openInputStream(uri)?.bufferedReader()?.use { it.readText() } ?: error("فایل خوانده نشد")
            repo.importJson(json)
            ReminderScheduler.scheduleAll(context)
        }.onSuccess { status = "بکاپ بازیابی شد."; onChanged() }.onFailure { status = "بازیابی ناموفق: ${it.message}" }
    }'''

new_launchers = '''    val backupLauncher = rememberLauncherForActivityResult(ActivityResultContracts.CreateDocument("application/json")) { uri ->
        uri ?: return@rememberLauncherForActivityResult
        runCatching {
            val stream = context.contentResolver.openOutputStream(uri) ?: error("امکان نوشتن فایل وجود ندارد")
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
            status = "بکاپ بازیابی شد."
            onChanged()
        }.onFailure {
            status = "بازیابی ناموفق: ${it.message ?: "خطای نامشخص"}"
        }
    }'''

if old_launchers in m:
    m = replace_once(m, old_launchers, new_launchers, 'backup/restore launchers')
elif new_launchers not in m:
    raise SystemExit('backup/restore launchers: source shape is unknown')

old_buttons = '''            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                Button(modifier = Modifier.weight(1f), onClick = { backupLauncher.launch("KharjYar-Backup-${PersianDate.format(System.currentTimeMillis()).replace("/", "-")}.json") }) { Text("تهیه بکاپ") }
                OutlinedButton(modifier = Modifier.weight(1f), onClick = { restoreLauncher.launch(arrayOf("application/json", "text/plain", "*/*")) }) { Text("بازیابی") }
            }
            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {'''

new_buttons = '''            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                Button(modifier = Modifier.weight(1f), onClick = {
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
                OutlinedButton(modifier = Modifier.weight(1f), onClick = {
                    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
                        runCatching {
                            val latest = findLatestBackupInDownloads(context) ?: error("فایل بکاپی در Downloads پیدا نشد")
                            restoreBackupFromUri(context, repo, latest.first)
                            latest.second
                        }.onSuccess { fileName ->
                            status = "بکاپ $fileName بازیابی شد."
                            onChanged()
                        }.onFailure {
                            status = "بازیابی خودکار انجام نشد؛ «انتخاب فایل بکاپ» را بزنید."
                        }
                    } else {
                        restoreLauncher.launchSafely(arrayOf("application/json", "text/plain", "*/*")) { message -> status = message }
                    }
                }) { Text("بازیابی آخرین بکاپ") }
            }
            OutlinedButton(modifier = Modifier.fillMaxWidth(), onClick = {
                restoreLauncher.launchSafely(arrayOf("application/json", "text/plain", "*/*")) { message -> status = message }
            }) { Text("انتخاب فایل بکاپ") }
            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {'''

if old_buttons in m:
    m = replace_once(m, old_buttons, new_buttons, 'backup buttons')
elif new_buttons not in m:
    raise SystemExit('backup buttons: source shape is unknown')

if 'نسخه آزمایشی ۱.۰.۵' in m:
    m = m.replace('نسخه آزمایشی ۱.۰.۵', 'نسخه آزمایشی ۱.۰.۶', 1)

anchor = '''private fun <I> ActivityResultLauncher<I>.launchSafely(input: I, onFailure: (String) -> Unit) {
    runCatching { launch(input) }.onFailure { onFailure("این قابلیت روی دستگاه باز نشد: ${it.message ?: "خطای نامشخص"}") }
}'''

helpers = r'''private fun saveBackupToDownloads(context: android.content.Context, json: String, fileName: String): String {
    require(Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) { "ذخیره مستقیم Downloads در این نسخه Android پشتیبانی نمی‌شود." }
    val resolver = context.contentResolver
    val values = android.content.ContentValues().apply {
        put(android.provider.MediaStore.Downloads.DISPLAY_NAME, fileName)
        put(android.provider.MediaStore.Downloads.MIME_TYPE, "application/json")
        put(android.provider.MediaStore.Downloads.RELATIVE_PATH, android.os.Environment.DIRECTORY_DOWNLOADS)
        put(android.provider.MediaStore.Downloads.IS_PENDING, 1)
    }
    val uri = resolver.insert(android.provider.MediaStore.Downloads.EXTERNAL_CONTENT_URI, values)
        ?: error("امکان ساخت فایل بکاپ در Downloads وجود ندارد")
    try {
        val stream = resolver.openOutputStream(uri, "w") ?: error("امکان نوشتن فایل بکاپ وجود ندارد")
        stream.writer(Charsets.UTF_8).use { it.write(json) }
        values.clear()
        values.put(android.provider.MediaStore.Downloads.IS_PENDING, 0)
        resolver.update(uri, values, null, null)
    } catch (t: Throwable) {
        runCatching { resolver.delete(uri, null, null) }
        throw t
    }
    return fileName
}

private fun findLatestBackupInDownloads(context: android.content.Context): Pair<Uri, String>? {
    if (Build.VERSION.SDK_INT < Build.VERSION_CODES.Q) return null
    val resolver = context.contentResolver
    val collection = android.provider.MediaStore.Downloads.EXTERNAL_CONTENT_URI
    val projection = arrayOf(
        android.provider.MediaStore.Downloads._ID,
        android.provider.MediaStore.Downloads.DISPLAY_NAME,
        android.provider.MediaStore.Downloads.DATE_MODIFIED
    )
    val selection = "${android.provider.MediaStore.Downloads.DISPLAY_NAME} LIKE ?"
    val args = arrayOf("%.json")
    val order = "${android.provider.MediaStore.Downloads.DATE_MODIFIED} DESC"
    resolver.query(collection, projection, selection, args, order)?.use { cursor ->
        val idIndex = cursor.getColumnIndexOrThrow(android.provider.MediaStore.Downloads._ID)
        val nameIndex = cursor.getColumnIndexOrThrow(android.provider.MediaStore.Downloads.DISPLAY_NAME)
        while (cursor.moveToNext()) {
            val name = cursor.getString(nameIndex) ?: continue
            val isKharjYarBackup = name.startsWith("DakhlKharj-Backup", ignoreCase = true) ||
                name.startsWith("KharjYar-Backup", ignoreCase = true)
            if (!isKharjYarBackup) continue
            val id = cursor.getLong(idIndex)
            val uri = android.content.ContentUris.withAppendedId(collection, id)
            return uri to name
        }
    }
    return null
}

private fun restoreBackupFromUri(context: android.content.Context, repo: LedgerRepository, uri: Uri) {
    val json = context.contentResolver.openInputStream(uri)?.bufferedReader(Charsets.UTF_8)?.use { it.readText() }
        ?: error("فایل بکاپ خوانده نشد")
    repo.importJson(json)
    ReminderScheduler.scheduleAll(context)
}

''' + anchor

if 'private fun saveBackupToDownloads(' not in m:
    m = replace_once(m, anchor, helpers, 'backup helper insertion')

# --- household members UI: only show add form when requested, allow removing non-primary members ---
old_member_state = '''    var accountName by remember { mutableStateOf("") }
    var memberName by remember { mutableStateOf("") }
    var categoryType by remember { mutableStateOf(EntryType.EXPENSE) }'''
new_member_state = '''    var accountName by remember { mutableStateOf("") }
    var memberName by remember { mutableStateOf("") }
    var showMemberAdder by rememberSaveable { mutableStateOf(false) }
    var categoryType by remember { mutableStateOf(EntryType.EXPENSE) }'''
if old_member_state in m:
    m = replace_once(m, old_member_state, new_member_state, 'member add form state')
elif new_member_state not in m:
    raise SystemExit('member add form state: source shape is unknown')

old_members_ui = '''        SettingsAccordionSection("اعضای خانواده", "${members.size.toString().toPersianDigits()} عضو", openSection == "members", { openSection = if (openSection == "members") null else "members" }) {
            Text("در ثبت تراکنش می‌توانید مشخص کنید تراکنش مربوط به چه کسی است.", modifier = Modifier.fillMaxWidth(), textAlign = TextAlign.Start)
            Text(members.joinToString("  •  ") { it.name }, modifier = Modifier.fillMaxWidth(), textAlign = TextAlign.Start)
            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp), verticalAlignment = Alignment.CenterVertically) {
                OutlinedTextField(memberName, { memberName = it }, Modifier.weight(1f), label = { Text("نام عضو") }, singleLine = true, textStyle = LocalTextStyle.current.copy(textAlign = TextAlign.Start))
                OutlinedButton(onClick = { if (memberName.isNotBlank()) { repo.addMember(memberName); memberName = ""; onChanged() } }) { Text("افزودن") }
            }
        }'''

new_members_ui = '''        SettingsAccordionSection("اعضای خانواده", "${members.size.toString().toPersianDigits()} عضو", openSection == "members", { openSection = if (openSection == "members") null else "members" }) {
            Text("به‌صورت پیش‌فرض فقط «من» وجود دارد. عضوهای دیگر را هر زمان خواستید اضافه یا حذف کنید.", modifier = Modifier.fillMaxWidth(), textAlign = TextAlign.Start, fontSize = 12.sp)
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
                                status = if (removed) "عضو «${member.name}» حذف شد. تراکنش‌های قبلی او بدون تغییر باقی ماندند."
                                else "این عضو قابل حذف نیست؛ اگر در تراکنش تکرارشونده استفاده شده، ابتدا آن مورد را حذف کنید."
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
                    OutlinedButton(modifier = Modifier.weight(1f), onClick = { memberName = ""; showMemberAdder = false }) { Text("انصراف") }
                }
            } else {
                OutlinedButton(modifier = Modifier.fillMaxWidth(), onClick = { showMemberAdder = true }) { Text("＋ افزودن عضو") }
            }
        }'''

if old_members_ui in m:
    m = replace_once(m, old_members_ui, new_members_ui, 'household members UI')
elif new_members_ui not in m:
    raise SystemExit('household members UI: source shape is unknown')

main.write_text(m, encoding="utf-8")

# --- database/repository household member behavior ---
l = ledger.read_text(encoding="utf-8")

old_seed = '''        val memberCount = db.rawQuery("SELECT COUNT(*) FROM household_members", null).use { if (it.moveToFirst()) it.getInt(0) else 0 }
        if (memberCount == 0) {
            insertMember(db, "من")
            insertMember(db, "مشترک")
            insertMember(db, "هم‌خانه")
        }'''
new_seed = '''        val memberCount = db.rawQuery("SELECT COUNT(*) FROM household_members", null).use { if (it.moveToFirst()) it.getInt(0) else 0 }
        if (memberCount == 0) {
            insertMember(db, "من")
        }'''
if old_seed in l:
    l = replace_once(l, old_seed, new_seed, 'default household members')
elif new_seed not in l:
    raise SystemExit('default household members: source shape is unknown')

old_members_db = '''    fun getMembers(): List<HouseholdMember> {
        seedDefaults(writableDatabase)
        val out = mutableListOf<HouseholdMember>()
        readableDatabase.query("household_members", null, null, null, null, null, "id").use { c -> while (c.moveToNext()) out += HouseholdMember(c.long("id"), c.string("name")) }
        return out
    }
    fun addMember(name: String) {
        if (name.isNotBlank()) writableDatabase.insertWithOnConflict("household_members", null, ContentValues().apply { put("name", name.trim()) }, SQLiteDatabase.CONFLICT_IGNORE)
    }'''
new_members_db = '''    private fun migrateLegacyHouseholdDefaults(db: SQLiteDatabase) {
        val alreadyDone = db.rawQuery("SELECT value FROM settings WHERE key = ? LIMIT 1", arrayOf("household_defaults_v6")).use {
            it.moveToFirst() && it.getString(0) == "1"
        }
        if (alreadyDone) return
        listOf("مشترک", "هم‌خانه").forEach { legacyName ->
            val usedInEntries = db.rawQuery("SELECT 1 FROM entries WHERE member_name = ? LIMIT 1", arrayOf(legacyName)).use { it.moveToFirst() }
            val usedInRecurring = db.rawQuery("SELECT 1 FROM recurring_rules WHERE member_name = ? LIMIT 1", arrayOf(legacyName)).use { it.moveToFirst() }
            if (!usedInEntries && !usedInRecurring) db.delete("household_members", "name = ?", arrayOf(legacyName))
        }
        db.insertWithOnConflict("settings", null, ContentValues().apply {
            put("key", "household_defaults_v6")
            put("value", "1")
        }, SQLiteDatabase.CONFLICT_REPLACE)
    }
    fun getMembers(): List<HouseholdMember> {
        val db = writableDatabase
        seedDefaults(db)
        migrateLegacyHouseholdDefaults(db)
        val out = mutableListOf<HouseholdMember>()
        readableDatabase.query("household_members", null, null, null, null, null, "CASE WHEN name = 'من' THEN 0 ELSE 1 END, id").use { c -> while (c.moveToNext()) out += HouseholdMember(c.long("id"), c.string("name")) }
        return out
    }
    fun addMember(name: String): Boolean {
        val cleaned = name.trim()
        if (cleaned.isBlank()) return false
        return writableDatabase.insertWithOnConflict(
            "household_members", null, ContentValues().apply { put("name", cleaned) }, SQLiteDatabase.CONFLICT_IGNORE
        ) != -1L
    }
    fun deleteMember(id: Long): Boolean {
        val db = writableDatabase
        val name = db.rawQuery("SELECT name FROM household_members WHERE id = ? LIMIT 1", arrayOf(id.toString())).use {
            if (it.moveToFirst()) it.getString(0) else null
        } ?: return false
        if (name == "من") return false
        val usedInRecurring = db.rawQuery("SELECT 1 FROM recurring_rules WHERE member_name = ? LIMIT 1", arrayOf(name)).use { it.moveToFirst() }
        if (usedInRecurring) return false
        return db.delete("household_members", "id = ?", arrayOf(id.toString())) > 0
    }'''
if old_members_db in l:
    l = replace_once(l, old_members_db, new_members_db, 'household member database methods')
elif new_members_db not in l:
    raise SystemExit('household member database methods: source shape is unknown')

old_repo_members = '''    fun members(): List<HouseholdMember> = db.getMembers()
    fun addMember(name: String) = db.addMember(name)'''
new_repo_members = '''    fun members(): List<HouseholdMember> = db.getMembers()
    fun addMember(name: String): Boolean = db.addMember(name)
    fun deleteMember(id: Long): Boolean = db.deleteMember(id)'''
if old_repo_members in l:
    l = replace_once(l, old_repo_members, new_repo_members, 'household member repository methods')
elif new_repo_members not in l:
    raise SystemExit('household member repository methods: source shape is unknown')

ledger.write_text(l, encoding="utf-8")

print("V6 backup/restore + household-member update applied successfully.")
print("- versionCode: 6")
print("- versionName: 1.0.6")
print("- scoped Downloads backup; no broad storage permission")
print("- safe restore picker fallback")
print("- fresh installs default to only: من")
print("- unused legacy default members are removed once")
print("- members can be added/removed; من cannot be removed")
