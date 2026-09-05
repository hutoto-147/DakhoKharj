#!/usr/bin/env python3
from pathlib import Path
import shutil, sys

root = Path(".")
legacy = root / "app/src/main/java/com/example/kharjyar/LegacyScreens.kt"
if not legacy.exists():
    sys.exit("ERROR: run from /workspaces/DakhoKharj")

text = legacy.read_text(encoding="utf-8")
backup = legacy.with_name("LegacyScreens.kt.before_core_screens_pack2")
if not backup.exists():
    shutil.copy2(legacy, backup)

changed = 0

def replace_once(old, new, label):
    global text, changed
    if old not in text:
        sys.exit(f"ERROR: anchor not found for {label}; no further changes applied.")
    text = text.replace(old, new, 1)
    changed += 1

# ---------- Add Entry: state for expandable details ----------
replace_once(
'''    var tagsExpanded by rememberSaveable { mutableStateOf(false) }
''',
'''    var tagsExpanded by rememberSaveable { mutableStateOf(false) }
    var detailsExpanded by rememberSaveable(editingEntry?.id, editingDebt?.id) {
        mutableStateOf(editingEntry != null || editingDebt != null)
    }
''',
"details state"
)

# ---------- Add Entry: screen title / quick mode ----------
replace_once(
'''        SectionTitle("نوع ثبت")
        LazyRow(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            items(listOf("هزینه", "درآمد", "بدهی", "قرض", "یادآور/قسط")) { item ->
                FilterChip(selected = mode == item, onClick = { if (editingEntry == null && editingDebt == null) mode = item }, label = { Text(item) })
            }
        }
''',
'''        Column(
            modifier = Modifier.fillMaxWidth(),
            verticalArrangement = Arrangement.spacedBy(4.dp)
        ) {
            Text(
                if (editingEntry != null || editingDebt != null) "ویرایش ثبت" else "ثبت سریع",
                fontSize = 24.sp,
                fontWeight = FontWeight.Bold
            )
            Text(
                "نوع ثبت را انتخاب کنید و اطلاعات اصلی را وارد کنید.",
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
''',
"quick mode header"
)

# ---------- Income/expense: account stays quick, rest moves under details ----------
replace_once(
'''            DropdownSelector("دسته", category, categories.keys.toList()) { category = it; subcategory = categories[it]?.firstOrNull().orEmpty() }
            val subs = categories[category].orEmpty()
''',
'''            DropdownSelector("دسته", category, categories.keys.toList()) {
                category = it
                subcategory = categories[it]?.firstOrNull().orEmpty()
            }
            DropdownSelector(
                "حساب",
                accountName,
                accounts.map { "${it.icon} ${it.name}" }
            ) { selected -> accountName = selected.substringAfter(" ") }

            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .clickable { detailsExpanded = !detailsExpanded },
                shape = RoundedCornerShape(18.dp),
                colors = CardDefaults.cardColors(
                    containerColor = MaterialTheme.colorScheme.surfaceVariant
                )
            ) {
                Row(
                    modifier = Modifier.fillMaxWidth().padding(14.dp),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Column(verticalArrangement = Arrangement.spacedBy(2.dp)) {
                        Text("جزئیات بیشتر", fontWeight = FontWeight.SemiBold)
                        Text(
                            "زیرمجموعه، عضو، تاریخ، تگ، توضیح و یادآوری",
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
                    val subs = categories[category].orEmpty()
''',
"income detail opening"
)

# Remove the old account selector inside the details.
replace_once(
'''            DropdownSelector("حساب", accountName, accounts.map { "${it.icon} ${it.name}" }) { selected -> accountName = selected.substringAfter(" ") }
            DropdownSelector("عضو / هزینه مشترک", memberName, members.map { it.name }) { memberName = it }
''',
'''                    DropdownSelector("عضو / هزینه مشترک", memberName, members.map { it.name }) { memberName = it }
''',
"duplicate account removal"
)

# Indentation is cosmetic; close AnimatedVisibility before save button.
replace_once(
'''            ReminderEditor(addReminder, { addReminder = it }, reminderOffset, { reminderOffset = it }, customReminderDate, { customReminderDate = it }, reminderHour, { reminderHour = it }, reminderMinute, { reminderMinute = it })
            Button(modifier = Modifier.fillMaxWidth(), onClick = {
''',
'''                    ReminderEditor(addReminder, { addReminder = it }, reminderOffset, { reminderOffset = it }, customReminderDate, { customReminderDate = it }, reminderHour, { reminderHour = it }, reminderMinute, { reminderMinute = it })
                }
            }

            Button(
                modifier = Modifier.fillMaxWidth().height(54.dp),
                shape = RoundedCornerShape(18.dp),
                onClick = {
''',
"income detail closing"
)

# ---------- Debt/loan: quick fields + expandable details ----------
replace_once(
'''            OutlinedTextField(amountText, { amountText = it.formatAmountInput() }, Modifier.fillMaxWidth(), label = { Text("مانده فعلی به تومان") }, keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number), singleLine = true, textStyle = LocalTextStyle.current.copy(textAlign = TextAlign.Start))
            SectionTitle("تاریخ شروع / ثبت")
''',
'''            OutlinedTextField(amountText, { amountText = it.formatAmountInput() }, Modifier.fillMaxWidth(), label = { Text("مانده فعلی به تومان") }, keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number), singleLine = true, textStyle = LocalTextStyle.current.copy(textAlign = TextAlign.Start))

            Card(
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
                    SectionTitle("تاریخ شروع / ثبت")
''',
"debt detail opening"
)

replace_once(
'''            ReminderEditor(addReminder, { addReminder = it }, reminderOffset, { reminderOffset = it }, customReminderDate, { customReminderDate = it }, reminderHour, { reminderHour = it }, reminderMinute, { reminderMinute = it }, title = "یادآوری سررسید")
            Button(modifier = Modifier.fillMaxWidth(), onClick = {
''',
'''                    ReminderEditor(addReminder, { addReminder = it }, reminderOffset, { reminderOffset = it }, customReminderDate, { customReminderDate = it }, reminderHour, { reminderHour = it }, reminderMinute, { reminderMinute = it }, title = "یادآوری سررسید")
                }
            }

            Button(
                modifier = Modifier.fillMaxWidth().height(54.dp),
                shape = RoundedCornerShape(18.dp),
                onClick = {
''',
"debt detail closing"
)

# ---------- Transactions: modern header/search ----------
replace_once(
'''        item {
            OutlinedTextField(
                value = query, onValueChange = { query = it }, modifier = Modifier.fillMaxWidth(),
                label = { Text("جستجو در هزینه، درآمد، حساب، عضو یا توضیح") }, singleLine = true,
                textStyle = LocalTextStyle.current.copy(textAlign = TextAlign.Start)
            )
        }
''',
'''        item {
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
''',
"transactions header"
)

# Modernize existing transaction cards.
text = text.replace(
    "shape = RoundedCornerShape(16.dp)) {\n                Column(Modifier.padding(12.dp)",
    "shape = RoundedCornerShape(20.dp)) {\n                Column(Modifier.padding(14.dp)",
    1
)
text = text.replace(
    "shape = RoundedCornerShape(18.dp)) {\n        Column(Modifier.padding(16.dp)",
    "shape = RoundedCornerShape(20.dp)) {\n        Column(Modifier.padding(16.dp)",
    2
)

# Make destructive action visually distinct while preserving explicit delete.
text = text.replace(
'''            Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) { TextButton(onClick = onEdit) { Text("ویرایش") }; TextButton(onClick = onDelete) { Text("حذف") } }
''',
'''            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                TextButton(onClick = onEdit) { Text("ویرایش") }
                TextButton(onClick = onDelete) {
                    Text("حذف", color = MaterialTheme.colorScheme.error)
                }
            }
''',
2
)

legacy.write_text(text, encoding="utf-8")

print("DONE: Core Screens Pack 2 applied.")
print("Changed:", legacy)
print("Backup:", backup)
print("Operations:", changed)
