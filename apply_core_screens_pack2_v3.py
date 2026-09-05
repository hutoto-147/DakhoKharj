#!/usr/bin/env python3
from pathlib import Path
import shutil
import sys

path = Path("app/src/main/java/com/example/kharjyar/LegacyScreens.kt")
if not path.exists():
    sys.exit("ERROR: run from /workspaces/DakhoKharj")

original = path.read_text(encoding="utf-8")
text = original

fn_start = text.find("internal fun AddEntryScreen(")
fn_end = text.find("\n@Composable", fn_start + 10)
if fn_start < 0 or fn_end < 0:
    sys.exit("ERROR: AddEntryScreen block not found. Nothing written.")

before = text[:fn_start]
add = text[fn_start:fn_end]
after = text[fn_end:]

if "CORE_PACK_2_V3" in add:
    print("DONE: Core Screens Pack 2 v3 already applied.")
    sys.exit(0)

needle = '    var tagsExpanded by rememberSaveable { mutableStateOf(false) }\n'
if needle not in add:
    sys.exit("ERROR: tags state anchor not found. Nothing written.")
add = add.replace(
    needle,
    needle + '''    var detailsExpanded by rememberSaveable(editingEntry?.id, editingDebt?.id) {
        mutableStateOf(editingEntry != null || editingDebt != null)
    }
    // CORE_PACK_2_V3
''',
    1
)

old_header_start = add.find('        SectionTitle("نوع ثبت")')
old_header_end = add.find('        if (mode == "هزینه" || mode == "درآمد") {', old_header_start)
if old_header_start < 0 or old_header_end < 0:
    sys.exit("ERROR: quick-entry header anchors not found. Nothing written.")

new_header = '''        Column(
            modifier = Modifier.fillMaxWidth(),
            verticalArrangement = Arrangement.spacedBy(4.dp)
        ) {
            Text(
                if (editingEntry != null || editingDebt != null) "ویرایش ثبت" else "ثبت سریع",
                fontSize = 24.sp,
                fontWeight = FontWeight.Bold
            )
            Text(
                "اطلاعات اصلی را سریع وارد کنید؛ گزینه‌های تکمیلی در جزئیات بیشتر هستند.",
                fontSize = 12.sp,
                color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.60f)
            )
        }

        Card(
            modifier = Modifier.fillMaxWidth(),
            shape = RoundedCornerShape(20.dp),
            colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant)
        ) {
            LazyRow(
                modifier = Modifier.padding(horizontal = 10.dp, vertical = 8.dp),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                items(listOf("هزینه", "درآمد", "بدهی", "قرض", "یادآور/قسط")) { item ->
                    FilterChip(
                        selected = mode == item,
                        onClick = {
                            if (editingEntry == null && editingDebt == null) {
                                mode = item
                                detailsExpanded = false
                            }
                        },
                        label = { Text(item) }
                    )
                }
            }
        }
'''
add = add[:old_header_start] + new_header + add[old_header_end:]

income_if = add.find('        if (mode == "هزینه" || mode == "درآمد") {')
details_start = add.find('            val subs = categories[category].orEmpty()', income_if)
save_button = add.find('            Button(modifier = Modifier.fillMaxWidth(), onClick = {', details_start)
if details_start < 0 or save_button < 0:
    sys.exit("ERROR: income form boundaries not found. Nothing written.")

income_optional = add[details_start:save_button]
income_wrapper = '''            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .clickable { detailsExpanded = !detailsExpanded },
                shape = RoundedCornerShape(18.dp),
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant)
            ) {
                Row(
                    modifier = Modifier.fillMaxWidth().padding(14.dp),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Column(verticalArrangement = Arrangement.spacedBy(2.dp)) {
                        Text("جزئیات بیشتر", fontWeight = FontWeight.SemiBold)
                        Text(
                            "زیرمجموعه، حساب، عضو، تاریخ، تگ، توضیح و یادآوری",
                            fontSize = 11.sp,
                            color = MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.62f)
                        )
                    }
                    Text(if (detailsExpanded) "▲" else "▼")
                }
            }

            AnimatedVisibility(
                visible = detailsExpanded,
                enter = fadeIn() + expandVertically(),
                exit = fadeOut() + shrinkVertically()
            ) {
                Column(verticalArrangement = Arrangement.spacedBy(14.dp)) {
''' + income_optional + '''                }
            }

'''
add = add[:details_start] + income_wrapper + add[save_button:]

first_button = '            Button(modifier = Modifier.fillMaxWidth(), onClick = {'
styled_button = '''            Button(
                modifier = Modifier.fillMaxWidth().height(54.dp),
                shape = RoundedCornerShape(18.dp),
                onClick = {'''
if first_button not in add:
    sys.exit("ERROR: income save button not found after wrapping. Nothing written.")
add = add.replace(first_button, styled_button, 1)

debt_if = add.find('        } else if (mode == "بدهی" || mode == "قرض") {')
debt_details_start = add.find('            SectionTitle("تاریخ شروع / ثبت")', debt_if)
debt_button = add.find('            Button(modifier = Modifier.fillMaxWidth(), onClick = {', debt_details_start)
if debt_if < 0 or debt_details_start < 0 or debt_button < 0:
    sys.exit("ERROR: debt form boundaries not found. Nothing written.")

debt_optional = add[debt_details_start:debt_button]
debt_wrapper = '''            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .clickable { detailsExpanded = !detailsExpanded },
                shape = RoundedCornerShape(18.dp),
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant)
            ) {
                Row(
                    modifier = Modifier.fillMaxWidth().padding(14.dp),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Column(verticalArrangement = Arrangement.spacedBy(2.dp)) {
                        Text("جزئیات بیشتر", fontWeight = FontWeight.SemiBold)
                        Text(
                            "تاریخ، توضیح و یادآوری سررسید",
                            fontSize = 11.sp,
                            color = MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.62f)
                        )
                    }
                    Text(if (detailsExpanded) "▲" else "▼")
                }
            }

            AnimatedVisibility(
                visible = detailsExpanded,
                enter = fadeIn() + expandVertically(),
                exit = fadeOut() + shrinkVertically()
            ) {
                Column(verticalArrangement = Arrangement.spacedBy(14.dp)) {
''' + debt_optional + '''                }
            }

'''
add = add[:debt_details_start] + debt_wrapper + add[debt_button:]

if first_button not in add:
    sys.exit("ERROR: debt save button not found after wrapping. Nothing written.")
add = add.replace(first_button, styled_button, 1)

text = before + add + after

tx_start = text.find("internal fun TransactionsScreen(")
tx_end = text.find("\n@Composable", tx_start + 10)
if tx_start < 0 or tx_end < 0:
    sys.exit("ERROR: TransactionsScreen block not found. Nothing written.")

tx = text[tx_start:tx_end]
if "CORE_TX_PACK_2_V3" not in tx:
    search_start = tx.find('        item {\n            OutlinedTextField(\n                value = query')
    next_item = tx.find('        item {', search_start + 20)
    if search_start < 0 or next_item < 0:
        sys.exit("ERROR: transaction search block not found. Nothing written.")

    new_search = '''        item {
            // CORE_TX_PACK_2_V3
            Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
                Text("تراکنش‌ها", fontSize = 24.sp, fontWeight = FontWeight.Bold)
                Text(
                    "${feed.size.toString().toPersianDigits()} مورد",
                    fontSize = 12.sp,
                    color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.58f)
                )
            }
        }
        item {
            Card(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(20.dp),
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant)
            ) {
                OutlinedTextField(
                    value = query,
                    onValueChange = { query = it },
                    modifier = Modifier.fillMaxWidth().padding(8.dp),
                    label = { Text("جستجو") },
                    placeholder = { Text("دسته، حساب، عضو یا توضیح") },
                    singleLine = true,
                    textStyle = LocalTextStyle.current.copy(textAlign = TextAlign.Start)
                )
            }
        }
'''
    tx = tx[:search_start] + new_search + tx[next_item:]
    tx = tx.replace("shape = RoundedCornerShape(16.dp)", "shape = RoundedCornerShape(20.dp)", 1)
    text = text[:tx_start] + tx + text[tx_end:]

text = text.replace(
    'Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) { TextButton(onClick = onEdit) { Text("ویرایش") }; TextButton(onClick = onDelete) { Text("حذف") } }',
    '''Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                TextButton(onClick = onEdit) { Text("ویرایش") }
                TextButton(onClick = onDelete) { Text("حذف", color = MaterialTheme.colorScheme.error) }
            }''',
    2
)
text = text.replace("shape = RoundedCornerShape(18.dp)) {", "shape = RoundedCornerShape(20.dp)) {", 2)

backup = path.with_name("LegacyScreens.kt.before_core_screens_pack2_v3")
if not backup.exists():
    shutil.copy2(path, backup)

tmp = path.with_suffix(".kt.pack2tmp")
tmp.write_text(text, encoding="utf-8")
tmp.replace(path)

print("DONE: Core Screens Pack 2 v3 applied.")
print("Changed:", path)
print("Backup:", backup)
