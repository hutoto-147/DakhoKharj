#!/usr/bin/env python3
from pathlib import Path
import shutil
import sys

path = Path("app/src/main/java/com/example/kharjyar/LegacyScreens.kt")
if not path.exists():
    sys.exit("ERROR: run from /workspaces/DakhoKharj")

original = path.read_text(encoding="utf-8")
text = original

# ---------- ComparisonScreen ----------
cs = text.find("internal fun ComparisonScreen(")
ce = text.find("\n@Composable", cs + 10)
if cs < 0 or ce < 0:
    sys.exit("ERROR: ComparisonScreen not found. Nothing written.")

comparison = text[cs:ce]

if "UI_PACK_3_COMPARISON" not in comparison:
    lazy = '    LazyColumn(Modifier.fillMaxSize(), contentPadding = PaddingValues(16.dp), verticalArrangement = Arrangement.spacedBy(16.dp)) {\n'
    if lazy not in comparison:
        sys.exit("ERROR: Comparison LazyColumn anchor not found. Nothing written.")

    comparison = comparison.replace(
        lazy,
        lazy + '''        item {
            // UI_PACK_3_COMPARISON
            Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
                Text(
                    "تحلیل و مقایسه",
                    fontSize = 24.sp,
                    fontWeight = FontWeight.Bold
                )
                Text(
                    "روند درآمد، هزینه، بدهی و قرض را در یک نمای یکپارچه بررسی کنید.",
                    fontSize = 12.sp,
                    color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.60f)
                )
            }
        }
''',
        1
    )

    old_data = '''        item {
            SectionTitle("نوع داده")
            Text("مشخص کنید می‌خواهید کدام بخش را تحلیل کنید.", modifier = Modifier.fillMaxWidth(), textAlign = TextAlign.Start, fontSize = 12.sp)
            LazyRow(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                items(dataTypes) { item ->
                    FilterChip(
                        selected = metric == item,
                        onClick = {
                            metric = item
                            expandedGroup = null
                            compareMode = if (item == "بدهی" || item == "قرض") {
                                if (compareMode in obligationModes) compareMode else "روند ماهانه"
                            } else {
                                if (compareMode in entryModes) compareMode else "دسته‌ها"
                            }
                        },
                        label = { Text(item) }
                    )
                }
            }
        }
'''
    new_data = '''        item {
            Card(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(20.dp),
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant)
            ) {
                Column(
                    modifier = Modifier.padding(16.dp),
                    verticalArrangement = Arrangement.spacedBy(10.dp)
                ) {
                    Text("نوع داده", fontSize = 16.sp, fontWeight = FontWeight.Bold)
                    Text(
                        "مشخص کنید می‌خواهید کدام بخش را تحلیل کنید.",
                        fontSize = 12.sp,
                        color = MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.66f)
                    )
                    LazyRow(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                        items(dataTypes) { item ->
                            FilterChip(
                                selected = metric == item,
                                onClick = {
                                    metric = item
                                    expandedGroup = null
                                    compareMode = if (item == "بدهی" || item == "قرض") {
                                        if (compareMode in obligationModes) compareMode else "روند ماهانه"
                                    } else {
                                        if (compareMode in entryModes) compareMode else "دسته‌ها"
                                    }
                                },
                                label = { Text(item) }
                            )
                        }
                    }
                }
            }
        }
'''
    if old_data not in comparison:
        sys.exit("ERROR: Comparison data selector anchor not found. Nothing written.")
    comparison = comparison.replace(old_data, new_data, 1)

    old_mode = '''        item {
            SectionTitle("نوع نمایش")
            LazyRow(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                items(if (isObligation) obligationModes else entryModes) { m ->
                    FilterChip(selected = compareMode == m, onClick = { compareMode = m; expandedGroup = null }, label = { Text(m) })
                }
            }
        }
'''
    new_mode = '''        item {
            Card(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(20.dp),
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant)
            ) {
                Column(
                    modifier = Modifier.padding(16.dp),
                    verticalArrangement = Arrangement.spacedBy(10.dp)
                ) {
                    Text("نوع نمایش", fontSize = 16.sp, fontWeight = FontWeight.Bold)
                    LazyRow(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                        items(if (isObligation) obligationModes else entryModes) { m ->
                            FilterChip(
                                selected = compareMode == m,
                                onClick = { compareMode = m; expandedGroup = null },
                                label = { Text(m) }
                            )
                        }
                    }
                }
            }
        }
'''
    if old_mode not in comparison:
        sys.exit("ERROR: Comparison display selector anchor not found. Nothing written.")
    comparison = comparison.replace(old_mode, new_mode, 1)

    # Make smaller result cards consistent with the 20dp system.
    comparison = comparison.replace("RoundedCornerShape(16.dp)", "RoundedCornerShape(20.dp)")

    text = text[:cs] + comparison + text[ce:]

# ---------- SettingsScreen ----------
ss = text.find("internal fun SettingsScreen(")
se = text.find("\n@Composable", ss + 10)
if ss < 0:
    sys.exit("ERROR: SettingsScreen not found. Nothing written.")
# Settings is followed by helper functions; use SettingsAccordionSection as boundary.
if se < 0 or "SettingsAccordionSection" not in text[se:]:
    helper = text.find("@Composable\nprivate fun SettingsAccordionSection", ss)
    if helper < 0:
        sys.exit("ERROR: SettingsScreen end not found. Nothing written.")
    se = helper

settings = text[ss:se]

if "UI_PACK_3_SETTINGS" not in settings:
    old_column = '''    Column(
        Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(10.dp), horizontalAlignment = Alignment.End
    ) {
        Text("برای تغییر هر بخش روی عنوان آن بزنید.", modifier = Modifier.fillMaxWidth(), textAlign = TextAlign.Start, fontSize = 12.sp)
'''
    new_column = '''    Column(
        Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(14.dp),
        horizontalAlignment = Alignment.End
    ) {
        // UI_PACK_3_SETTINGS
        Column(
            modifier = Modifier.fillMaxWidth(),
            verticalArrangement = Arrangement.spacedBy(4.dp)
        ) {
            Text("تنظیمات", fontSize = 24.sp, fontWeight = FontWeight.Bold)
            Text(
                "ظاهر، امنیت، بودجه، بکاپ و داده‌های برنامه",
                fontSize = 12.sp,
                color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.60f)
            )
        }

        Card(
            modifier = Modifier.fillMaxWidth(),
            shape = RoundedCornerShape(20.dp),
            colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant)
        ) {
            Text(
                "برای تغییر هر بخش روی عنوان آن بزنید.",
                modifier = Modifier.fillMaxWidth().padding(14.dp),
                textAlign = TextAlign.Start,
                fontSize = 12.sp,
                color = MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.72f)
            )
        }
'''
    if old_column not in settings:
        sys.exit("ERROR: Settings column anchor not found. Nothing written.")
    settings = settings.replace(old_column, new_column, 1)
    text = text[:ss] + settings + text[se:]

# ---------- Settings accordion visual polish ----------
old_acc = '''    Card(Modifier.fillMaxWidth(), shape = RoundedCornerShape(18.dp)) {
        Column(Modifier.fillMaxWidth()) {
            Row(
                Modifier.fillMaxWidth().clickable(onClick = onToggle).padding(horizontal = 16.dp, vertical = 14.dp),
'''
new_acc = '''    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(20.dp),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant)
    ) {
        Column(Modifier.fillMaxWidth()) {
            Row(
                Modifier.fillMaxWidth().clickable(onClick = onToggle).padding(horizontal = 16.dp, vertical = 16.dp),
'''
if old_acc in text:
    text = text.replace(old_acc, new_acc, 1)
elif "shape = RoundedCornerShape(20.dp)" not in text[text.find("private fun SettingsAccordionSection"):text.find("private fun saveBackupToDownloads")]:
    sys.exit("ERROR: Settings accordion anchor not found. Nothing written.")

# Animated accordion expansion, preserving content.
old_expand = '''            if (expanded) {
                HorizontalDivider()
                Column(Modifier.fillMaxWidth().padding(14.dp), verticalArrangement = Arrangement.spacedBy(10.dp), content = content)
            }
'''
new_expand = '''            AnimatedVisibility(
                visible = expanded,
                enter = fadeIn() + expandVertically(),
                exit = fadeOut() + shrinkVertically()
            ) {
                Column {
                    HorizontalDivider()
                    Column(
                        Modifier.fillMaxWidth().padding(16.dp),
                        verticalArrangement = Arrangement.spacedBy(12.dp),
                        content = content
                    )
                }
            }
'''
if old_expand in text:
    text = text.replace(old_expand, new_expand, 1)

# Global tiny UI polish only; no repository/data behavior touched.
old_empty = 'Surface(Modifier.fillMaxWidth(), color = MaterialTheme.colorScheme.surfaceVariant, shape = RoundedCornerShape(14.dp))'
if old_empty in text:
    text = text.replace(
        old_empty,
        'Surface(Modifier.fillMaxWidth(), color = MaterialTheme.colorScheme.surfaceVariant, shape = RoundedCornerShape(18.dp))',
        1
    )

# Atomic write: source is changed only after all required anchors pass.
backup = path.with_name("LegacyScreens.kt.before_ui_pack3")
if not backup.exists():
    shutil.copy2(path, backup)

tmp = path.with_suffix(".kt.pack3tmp")
tmp.write_text(text, encoding="utf-8")
tmp.replace(path)

print("DONE: UI Pack 3 applied.")
print("Comparison + Settings + final visual polish")
print("Changed:", path)
print("Backup:", backup)
