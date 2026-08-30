#!/usr/bin/env python3
from pathlib import Path
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
main = root / "app/src/main/java/com/example/kharjyar/MainActivity.kt"
gradle = root / "app/build.gradle.kts"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly 1 match, found {count}")
    return text.replace(old, new, 1)

# --- version bump: V5 -> V6 ---
g = gradle.read_text(encoding="utf-8")
g = replace_once(g, 'versionCode = 5', 'versionCode = 6', 'versionCode')
g = replace_once(g, 'versionName = "1.0.5"', 'versionName = "1.0.6"', 'versionName')
gradle.write_text(g, encoding="utf-8")

m = main.read_text(encoding="utf-8")

# Make the SAF callbacks themselves strict about null streams, and share restore logic.
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

m = replace_once(m, old_launchers, new_launchers, 'backup/restore launchers')

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

m = replace_once(m, old_buttons, new_buttons, 'backup buttons')

# Version label in Settings.
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

m = replace_once(m, anchor, helpers, 'backup helper insertion')
main.write_text(m, encoding="utf-8")

print("V6 backup/restore fix applied successfully.")
print("- versionCode: 6")
print("- versionName: 1.0.6")
print("- direct backup to Downloads on Android 10+")
print("- latest-backup restore + safe file-picker fallback")
