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

def replace_between(text: str, start_marker: str, end_marker: str, replacement: str, label: str) -> str:
    start = text.find(start_marker)
    if start < 0:
        raise SystemExit(f"{label}: start marker not found")
    end = text.find(end_marker, start + len(start_marker))
    if end < 0:
        raise SystemExit(f"{label}: end marker not found")
    return text[:start] + replacement + text[end:]

g = gradle.read_text(encoding="utf-8")
if 'applicationId = "io.github.hutoto147.dakhlokharj"' not in g:
    raise SystemExit("unexpected applicationId")
if 'storeFile = file("kharjyar-v5-debug.keystore")' not in g:
    raise SystemExit("expected persistent V5/V6 debug signing key is not configured")

if 'versionCode = 6' in g:
    g = g.replace('versionCode = 6', 'versionCode = 7', 1)
elif 'versionCode = 7' not in g:
    raise SystemExit("expected successful V6 baseline (versionCode 6)")

if 'versionName = "1.0.6"' in g:
    g = g.replace('versionName = "1.0.6"', 'versionName = "1.0.7"', 1)
elif 'versionName = "1.0.7"' not in g:
    raise SystemExit("expected successful V6 baseline (versionName 1.0.6)")

gradle.write_text(g, encoding="utf-8")

m = main.read_text(encoding="utf-8")
if "saveBackupToDownloads" not in m or "findLatestBackupInDownloads" not in m:
    raise SystemExit("V6 backup/restore fix is not present; refusing to overwrite an older baseline")

if "var showMemberAdder by rememberSaveable" not in m:
    anchor = '    var memberName by remember { mutableStateOf("") }'
    if anchor not in m:
        raise SystemExit("memberName state anchor not found")
    m = m.replace(
        anchor,
        anchor + '\n    var showMemberAdder by rememberSaveable { mutableStateOf(false) }',
        1
    )

members_start = '        SettingsAccordionSection("اعضای خانواده"'
recurring_start = '        SettingsAccordionSection("تراکنش‌های تکرارشونده"'

new_members = r'''        SettingsAccordionSection("اعضای خانواده", "${members.size.toString().toPersianDigits()} عضو", openSection == "members", { openSection = if (openSection == "members") null else "members" }) {
            Text(
                "به‌صورت پیش‌فرض فقط «من» وجود دارد. عضوهای دیگر را با نام دلخواه اضافه کنید.",
                modifier = Modifier.fillMaxWidth(),
                textAlign = TextAlign.Start,
                fontSize = 12.sp
            )

            members.forEach { member ->
                Card(Modifier.fillMaxWidth(), shape = RoundedCornerShape(14.dp)) {
                    Row(
                        Modifier.fillMaxWidth().padding(horizontal = 12.dp, vertical = 8.dp),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Column(Modifier.weight(1f)) {
                            Text(member.name, fontWeight = FontWeight.SemiBold)
                            if (member.name == "من") {
                                Text("عضو پیش‌فرض", fontSize = 11.sp)
                            }
                        }
                        if (member.name != "من") {
                            TextButton(onClick = {
                                val removed = repo.deleteMember(member.id)
                                status = if (removed) {
                                    "عضو «${member.name}» حذف شد. تراکنش‌های قبلی او حفظ شدند."
                                } else {
                                    "این عضو در یک تراکنش تکرارشونده استفاده شده و فعلاً قابل حذف نیست."
                                }
                                if (removed) onChanged()
                            }) {
                                Text("حذف")
                            }
                        }
                    }
                }
            }

            if (showMemberAdder) {
                OutlinedTextField(
                    value = memberName,
                    onValueChange = { memberName = it },
                    modifier = Modifier.fillMaxWidth(),
                    label = { Text("نام عضو جدید") },
                    placeholder = { Text("مثلاً همسر، فرزند، هم‌خانه") },
                    singleLine = true,
                    textStyle = LocalTextStyle.current.copy(textAlign = TextAlign.Start)
                )

                Row(
                    Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    Button(
                        modifier = Modifier.weight(1f),
                        onClick = {
                            val name = memberName.trim()
                            when {
                                name.isBlank() -> status = "نام عضو را وارد کنید."
                                repo.addMember(name) -> {
                                    memberName = ""
                                    showMemberAdder = false
                                    status = "عضو جدید اضافه شد."
                                    onChanged()
                                }
                                else -> status = "این نام قبلاً در اعضا وجود دارد."
                            }
                        }
                    ) {
                        Text("ذخیره عضو")
                    }

                    OutlinedButton(
                        modifier = Modifier.weight(1f),
                        onClick = {
                            memberName = ""
                            showMemberAdder = false
                        }
                    ) {
                        Text("انصراف")
                    }
                }
            } else {
                OutlinedButton(
                    modifier = Modifier.fillMaxWidth(),
                    onClick = { showMemberAdder = true }
                ) {
                    Text("＋ افزودن عضو")
                }
            }
        }
'''

m = replace_between(m, members_start, recurring_start, new_members, "members settings section")
m = m.replace('نسخه آزمایشی ۱.۰.۶', 'نسخه آزمایشی ۱.۰.۷', 1)
main.write_text(m, encoding="utf-8")

l = ledger.read_text(encoding="utf-8")

l = re.sub(
    r'(?m)^\s*insertMember\(db,\s*"مشترک"\)\s*\n\s*insertMember\(db,\s*"هم‌خانه"\)\s*\n',
    '',
    l,
    count=1
)

db_members_start = '    fun getMembers(): List<HouseholdMember> {'
db_recurring_start = '    fun getRecurringRules(): List<RecurringRule> {'

new_db_members = r'''    private fun migrateLegacyHouseholdDefaults(db: SQLiteDatabase) {
        val migrationKey = "household_defaults_v7"
        val alreadyDone = db.rawQuery(
            "SELECT value FROM settings WHERE key = ? LIMIT 1",
            arrayOf(migrationKey)
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
                put("key", migrationKey)
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
        ).use { cursor ->
            if (cursor.moveToFirst()) cursor.getString(0) else null
        } ?: return false

        if (name == "من") return false

        val usedInRecurring = db.rawQuery(
            "SELECT 1 FROM recurring_rules WHERE member_name = ? LIMIT 1",
            arrayOf(name)
        ).use { it.moveToFirst() }

        if (usedInRecurring) return false

        return db.delete(
            "household_members",
            "id = ?",
            arrayOf(id.toString())
        ) > 0
    }

'''

l = replace_between(l, db_members_start, db_recurring_start, new_db_members, "database member methods")

repo_members_start = '    fun members(): List<HouseholdMember> = db.getMembers()'
repo_recurring_start = '    fun recurringRules(): List<RecurringRule> = db.getRecurringRules()'

new_repo_members = r'''    fun members(): List<HouseholdMember> = db.getMembers()
    fun addMember(name: String): Boolean = db.addMember(name)
    fun deleteMember(id: Long): Boolean = db.deleteMember(id)

'''

l = replace_between(l, repo_members_start, repo_recurring_start, new_repo_members, "repository member methods")
ledger.write_text(l, encoding="utf-8")

g2 = gradle.read_text(encoding="utf-8")
m2 = main.read_text(encoding="utf-8")
l2 = ledger.read_text(encoding="utf-8")

checks = {
    "versionCode 7": 'versionCode = 7' in g2,
    "versionName 1.0.7": 'versionName = "1.0.7"' in g2,
    "signing key preserved": 'storeFile = file("kharjyar-v5-debug.keystore")' in g2,
    "V6 backup fix preserved": 'saveBackupToDownloads' in m2 and 'findLatestBackupInDownloads' in m2,
    "member adder UI": 'showMemberAdder' in m2,
    "delete member DB": 'fun deleteMember(id: Long): Boolean' in l2,
    "repository delete member": 'fun deleteMember(id: Long): Boolean = db.deleteMember(id)' in l2,
    "legacy migration": 'household_defaults_v7' in l2,
}
bad = [k for k, ok in checks.items() if not ok]
if bad:
    raise SystemExit("post-patch checks failed: " + ", ".join(bad))

print("V7 household-member update applied successfully.")
print("- V6 backup/restore code preserved")
print("- versionCode 7 / versionName 1.0.7")
print("- signing identity unchanged")
print("- fresh installs default to «من» only")
print("- add/remove household members enabled")
