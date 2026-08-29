package com.example.kharjyar

import android.content.ContentValues
import android.content.Context
import android.net.Uri
import android.os.Build
import android.os.Environment
import android.provider.MediaStore
import java.io.File
import java.io.FileOutputStream
import java.io.OutputStream

object FileTransferSupport {
    fun saveToDownloads(
        context: Context,
        displayName: String,
        mimeType: String,
        writer: (OutputStream) -> Unit
    ): String {
        return if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            saveWithMediaStore(context, displayName, mimeType, writer)
        } else {
            saveLegacyAppExternal(context, displayName, writer)
        }
    }

    private fun saveWithMediaStore(
        context: Context,
        displayName: String,
        mimeType: String,
        writer: (OutputStream) -> Unit
    ): String {
        val resolver = context.contentResolver
        val values = ContentValues().apply {
            put(MediaStore.MediaColumns.DISPLAY_NAME, displayName)
            put(MediaStore.MediaColumns.MIME_TYPE, mimeType)
            put(MediaStore.MediaColumns.RELATIVE_PATH, "${Environment.DIRECTORY_DOWNLOADS}/DakhlKharj")
            put(MediaStore.MediaColumns.IS_PENDING, 1)
        }
        val uri = resolver.insert(MediaStore.Downloads.EXTERNAL_CONTENT_URI, values)
            ?: error("Android نتوانست فایل را در Downloads ایجاد کند.")
        try {
            val output = resolver.openOutputStream(uri, "w")
                ?: error("امکان باز کردن فایل خروجی وجود ندارد.")
            output.use(writer)

            val ready = ContentValues().apply {
                put(MediaStore.MediaColumns.IS_PENDING, 0)
            }
            resolver.update(uri, ready, null, null)
            return "Downloads/DakhlKharj/$displayName"
        } catch (t: Throwable) {
            runCatching { resolver.delete(uri, null, null) }
            throw t
        }
    }

    private fun saveLegacyAppExternal(
        context: Context,
        displayName: String,
        writer: (OutputStream) -> Unit
    ): String {
        val base = context.getExternalFilesDir(Environment.DIRECTORY_DOWNLOADS)
            ?: File(context.filesDir, "downloads")
        val dir = File(base, "DakhlKharj")
        if (!dir.exists() && !dir.mkdirs()) error("پوشه خروجی ساخته نشد.")
        val file = File(dir, displayName)
        FileOutputStream(file, false).use(writer)
        return file.absolutePath
    }

    fun readText(context: Context, uri: Uri): String {
        val input = context.contentResolver.openInputStream(uri)
            ?: error("فایل انتخاب‌شده قابل خواندن نیست.")
        return input.bufferedReader(Charsets.UTF_8).use { it.readText() }
    }

    fun saveSafetyBackup(context: Context, json: String): String {
        val dir = File(context.filesDir, "restore-safety")
        if (!dir.exists() && !dir.mkdirs()) error("پوشه بکاپ ایمنی ساخته نشد.")
        val file = File(dir, "before-restore-${System.currentTimeMillis()}.json")
        file.writeText(json, Charsets.UTF_8)
        return file.absolutePath
    }
}
