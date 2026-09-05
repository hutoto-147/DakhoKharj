#!/usr/bin/env python3
from pathlib import Path
import shutil, sys

target = Path("app/src/main/java/com/example/kharjyar/LegacyScreens.kt")
if not target.exists():
    sys.exit("ERROR: run from /workspaces/DakhoKharj")

original = target.read_text(encoding="utf-8")
text = original

def must_replace(old, new, label, count=1):
    global text
    if old not in text:
        sys.exit(f"ERROR: {label} not found. No changes were written.")
    text = text.replace(old, new, count)

# Add expandable-details state.
must_replace(
    '    var tagsExpanded by rememberSaveable { mutableStateOf(false) }\n',
    '''    var tagsExpanded by rememberSaveable { mutableStateOf(false) }
    var detailsExpanded by rememberSaveable(editingEntry?.id, editingDebt?.id) {
        mutableStateOf(editingEntry != null || editingDebt != null)
    }
''',
    "details state"
)

# Modern quick-entry header.
must_replace(
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
                "اطلاعات اصلی را سریع وارد کنید؛ گزینه‌های تکمیلی پایین‌تر هستند.",
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
    "quick header"
)

# Income/expense: keep account in quick area and wrap optional fields.
must_replace(
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
    "income details opening"
)

must_replace(
'''            DropdownSelector("حساب", accountName, accounts.map { "${it.icon} ${it.name}" }) { selected -> accountName = selected.substringAfter(" ") }
            DropdownSelector("عضو / هزینه مشترک", memberName, members.map { it.name }) { memberName = it }
''',
'''                    DropdownSelector("عضو / هزینه مشترک", memberName, members.map { it.name }) { memberName = it }
''',
    "old account selector"
)

must_replace(
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
    "income details closing"
)

# Debt/loan details.
must_replace(
'''            OutlinedTextField(amountText, { amountText = it.formatAmountInput() }, Modifier.fillMaxWidth(), label = { Text("مانده فعلی به تومان") }, keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number), singleLine = true, textStyle = LocalTextStyle.current.copy(textAlign = TextAlign.Start))
            SectionTitle("تاریخ شروع / ثبت")
''',
'''            OutlinedTextField(amountText, { amountText = it.formatAmountInput() }, Modifier.fillMaxWidth(), label = { Text("مانده فعلی به تومان") }, keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number), singleLine = true, textStyle = LocalTextStyle.current.copy(textAlign = TextAlign.Start))

            Card(
                modifier = Modifier.fillMaxWidth().clickable { detailsExpanded = !detailsExpanded },
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
    "debt details opening"
)

must_replace(
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
    "debt details closing"
)

# Transactions header and search.
must_replace(
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
    "transactions search"
)

# Cosmetic card radius upgrades; these don't affect data behavior.
text = text.replace(
    'Card(Modifier.fillMaxWidth(), shape = RoundedCornerShape(16.dp)) {\n                Column(Modifier.padding(12.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {',
    'Card(Modifier.fillMaxWidth(), shape = RoundedCornerShape(20.dp)) {\n                Column(Modifier.padding(14.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {',
    1
)

# Only now write to disk, so failures above leave source untouched.
backup = target.with_name("LegacyScreens.kt.before_core_screens_pack2_v2")
if not backup.exists():
    shutil.copy2(target, backup)

target.write_text(text, encoding="utf-8")
print("DONE: Core Screens Pack 2 v2 applied.")
print("Changed:", target)
print("Backup:", backup)
