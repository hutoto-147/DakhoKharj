package com.example.kharjyar

import android.graphics.Paint
import android.graphics.pdf.PdfDocument
import java.io.OutputStream
import java.util.zip.ZipEntry
import java.util.zip.ZipOutputStream

object Exporters {
    fun writeExcel(entries: List<LedgerEntry>, output: OutputStream) {
        val zip = ZipOutputStream(output)
        fun put(path: String, content: String) {
            zip.putNextEntry(ZipEntry(path))
            zip.write(content.toByteArray(Charsets.UTF_8))
            zip.closeEntry()
        }

        put("[Content_Types].xml", """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
<Default Extension="xml" ContentType="application/xml"/>
<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>
<Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>
</Types>""")
        put("_rels/.rels", """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>
</Relationships>""")
        put("xl/workbook.xml", """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
<sheets><sheet name="تراکنش‌ها" sheetId="1" r:id="rId1"/></sheets></workbook>""")
        put("xl/_rels/workbook.xml.rels", """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>
</Relationships>""")

        val headers = listOf("نوع", "مبلغ (تومان)", "دسته", "زیرمجموعه", "تاریخ", "حساب", "عضو", "تگ‌ها", "توضیح")
        val sheet = buildString {
            append("<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>")
            append("<worksheet xmlns=\"http://schemas.openxmlformats.org/spreadsheetml/2006/main\"><sheetViews><sheetView rightToLeft=\"1\" workbookViewId=\"0\"/></sheetViews><sheetData>")
            append("<row r=\"1\">")
            headers.forEachIndexed { i, h -> append(textCell(columnName(i) + "1", h)) }
            append("</row>")
            entries.forEachIndexed { index, e ->
                val row = index + 2
                append("<row r=\"$row\">")
                append(textCell("A$row", e.type.titleFa))
                append(numberCell("B$row", e.amount))
                append(textCell("C$row", e.category))
                append(textCell("D$row", e.subcategory))
                append(textCell("E$row", PersianDate.format(e.occurredAt)))
                append(textCell("F$row", e.accountName))
                append(textCell("G$row", e.memberName))
                append(textCell("H$row", e.tags.joinToString("، ")))
                append(textCell("I$row", e.note))
                append("</row>")
            }
            append("</sheetData></worksheet>")
        }
        put("xl/worksheets/sheet1.xml", sheet)
        zip.finish()
        zip.flush()
    }

    fun writePdf(entries: List<LedgerEntry>, output: OutputStream) {
        val document = PdfDocument()
        val titlePaint = Paint(Paint.ANTI_ALIAS_FLAG).apply { textSize = 20f; textAlign = Paint.Align.RIGHT; isFakeBoldText = true }
        val textPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply { textSize = 11f; textAlign = Paint.Align.RIGHT }
        val smallPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply { textSize = 9f; textAlign = Paint.Align.RIGHT }
        var pageNumber = 1
        var page = document.startPage(PdfDocument.PageInfo.Builder(595, 842, pageNumber).create())
        var canvas = page.canvas
        var y = 50f

        fun header() {
            canvas.drawText("گزارش تراکنش‌های خرج‌یار", 555f, y, titlePaint)
            y += 28f
            canvas.drawText("تعداد تراکنش‌ها: ${entries.size.toString().toPersianDigits()}", 555f, y, smallPaint)
            y += 24f
        }
        fun nextPage() {
            document.finishPage(page)
            pageNumber++
            page = document.startPage(PdfDocument.PageInfo.Builder(595, 842, pageNumber).create())
            canvas = page.canvas
            y = 45f
            header()
        }
        header()
        entries.forEach { e ->
            if (y > 795f) nextPage()
            val sign = if (e.type == EntryType.INCOME) "+" else "−"
            val first = "${Presets.categoryIcon(e.category, e.type)}  ${e.category}${if (e.subcategory.isBlank()) "" else " / ${e.subcategory}"}    $sign ${e.amount.asToman()}"
            canvas.drawText(first, 555f, y, textPaint)
            y += 16f
            canvas.drawText("${PersianDate.format(e.occurredAt)}   •   ${e.accountName}   •   ${e.memberName}", 555f, y, smallPaint)
            y += 15f
            if (e.note.isNotBlank()) { canvas.drawText(e.note.take(90), 555f, y, smallPaint); y += 14f }
            y += 7f
        }
        document.finishPage(page)
        document.writeTo(output)
        document.close()
    }

    private fun textCell(ref: String, value: String): String = "<c r=\"$ref\" t=\"inlineStr\"><is><t>${xml(value)}</t></is></c>"
    private fun numberCell(ref: String, value: Long): String = "<c r=\"$ref\"><v>$value</v></c>"
    private fun xml(s: String): String = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\"", "&quot;").replace("'", "&apos;")
    private fun columnName(index: Int): String { var n = index + 1; val out = StringBuilder(); while (n > 0) { val r = (n - 1) % 26; out.insert(0, ('A'.code + r).toChar()); n = (n - 1) / 26 }; return out.toString() }
}
