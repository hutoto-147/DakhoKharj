#!/usr/bin/env python3
from pathlib import Path
import shutil
import sys

root = Path(".")
legacy = root / "app/src/main/java/com/example/kharjyar/LegacyScreens.kt"
ledger = root / "app/src/main/java/com/example/kharjyar/ui/app/LedgerApp.kt"
bottom = root / "app/src/main/java/com/example/kharjyar/ui/components/KharjBottomBar.kt"
design = root / "app/src/main/java/com/example/kharjyar/ui/design/AppDesign.kt"

for p in (legacy, ledger, bottom, design):
    if not p.exists():
        sys.exit(f"ERROR: missing {p}; run from /workspaces/DakhoKharj")

lt = legacy.read_text(encoding="utf-8")
app = ledger.read_text(encoding="utf-8")
ds = design.read_text(encoding="utf-8")

# Idempotency.
if "FINAL_BANKING_VISUAL_PACK" in lt:
    print("DONE: Final Banking Visual Pack already applied.")
    sys.exit(0)

# 1) Add a dedicated banking theme while preserving all existing themes.
theme_anchor = 'private val themeBases = listOf(\n'
if theme_anchor not in lt:
    sys.exit("ERROR: theme list anchor not found. Nothing written.")

bank_theme = '''private val themeBases = listOf(
    // FINAL_BANKING_VISUAL_PACK
    ThemeBase(
        "bank",
        "بانکی",
        Color(0xFFF4F8FB),
        Color(0xFFE8F0F5),
        Color(0xFFF9FBFC),
        Color(0xFFF0F5F8),
        Color(0xFF071923),
        Color(0xFF041118),
        Color(0xFF0D222D),
        Color(0xFF0A1C26),
        Color(0xFF0B6B78)
    ),
'''
lt = lt.replace(theme_anchor, bank_theme, 1)

# 2) Banking hero card: Beam-inspired subtle border, implemented natively in Compose.
old_hero = '''        item {
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .clickable { onOpenComparison("درآمد و هزینه", "ماه انتخابی") },
                colors = CardDefaults.cardColors(
                    containerColor = if (balance < 0L) {
                        MaterialTheme.colorScheme.errorContainer
                    } else {
                        MaterialTheme.colorScheme.primary
                    }
                ),
                shape = RoundedCornerShape(24.dp)
            ) {
                Column(
                    modifier = Modifier.padding(horizontal = 22.dp, vertical = 24.dp),
                    verticalArrangement = Arrangement.spacedBy(9.dp)
                ) {
                    Text(
                        "موجودی فعلی",
                        color = if (balance < 0L) {
                            MaterialTheme.colorScheme.onErrorContainer.copy(alpha = 0.74f)
                        } else {
                            MaterialTheme.colorScheme.onPrimary.copy(alpha = 0.76f)
                        },
                        fontSize = 14.sp
                    )
                    Text(
                        balance.asToman(),
                        color = if (balance < 0L) {
                            MaterialTheme.colorScheme.error
                        } else {
                            MaterialTheme.colorScheme.onPrimary
                        },
                        fontSize = 30.sp,
                        fontWeight = FontWeight.Bold
                    )
                    Text(
                        "مشاهده جزئیات مالی ‹",
                        color = if (balance < 0L) {
                            MaterialTheme.colorScheme.onErrorContainer.copy(alpha = 0.72f)
                        } else {
                            MaterialTheme.colorScheme.onPrimary.copy(alpha = 0.72f)
                        },
                        fontSize = 12.sp
                    )
                }
            }
        }
'''
new_hero = '''        item {
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .clip(RoundedCornerShape(26.dp))
                    .background(
                        brush = Brush.horizontalGradient(
                            listOf(
                                MaterialTheme.colorScheme.primary.copy(alpha = 0.42f),
                                Color.White.copy(alpha = if (dark) 0.16f else 0.72f),
                                MaterialTheme.colorScheme.primary.copy(alpha = 0.42f)
                            )
                        )
                    )
                    .padding(1.dp)
            ) {
                Card(
                    modifier = Modifier
                        .fillMaxWidth()
                        .clickable { onOpenComparison("درآمد و هزینه", "ماه انتخابی") },
                    colors = CardDefaults.cardColors(
                        containerColor = if (balance < 0L) {
                            MaterialTheme.colorScheme.errorContainer
                        } else {
                            MaterialTheme.colorScheme.primary
                        }
                    ),
                    shape = RoundedCornerShape(25.dp),
                    elevation = CardDefaults.cardElevation(defaultElevation = 8.dp)
                ) {
                    Column(
                        modifier = Modifier.padding(horizontal = 22.dp, vertical = 24.dp),
                        verticalArrangement = Arrangement.spacedBy(9.dp)
                    ) {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Text(
                                "موجودی فعلی",
                                color = if (balance < 0L) {
                                    MaterialTheme.colorScheme.onErrorContainer.copy(alpha = 0.74f)
                                } else {
                                    MaterialTheme.colorScheme.onPrimary.copy(alpha = 0.76f)
                                },
                                fontSize = 14.sp
                            )
                            Text(
                                "● امن",
                                color = if (balance < 0L) {
                                    MaterialTheme.colorScheme.onErrorContainer.copy(alpha = 0.62f)
                                } else {
                                    MaterialTheme.colorScheme.onPrimary.copy(alpha = 0.62f)
                                },
                                fontSize = 10.sp
                            )
                        }
                        Text(
                            balance.asToman(),
                            color = if (balance < 0L) {
                                MaterialTheme.colorScheme.error
                            } else {
                                MaterialTheme.colorScheme.onPrimary
                            },
                            fontSize = 30.sp,
                            fontWeight = FontWeight.Bold
                        )
                        Text(
                            "مشاهده تحلیل و جزئیات مالی ‹",
                            color = if (balance < 0L) {
                                MaterialTheme.colorScheme.onErrorContainer.copy(alpha = 0.72f)
                            } else {
                                MaterialTheme.colorScheme.onPrimary.copy(alpha = 0.72f)
                            },
                            fontSize = 12.sp
                        )
                    }
                }
            }
        }
'''
if old_hero not in lt:
    sys.exit("ERROR: dashboard hero anchor not found. Nothing written.")
lt = lt.replace(old_hero, new_hero, 1)

# 3) Final splash polish - keep behavior, add a premium banking caption.
old_caption = '''            Text(
                text = "مدیریت هوشمند پول روزانه",
                fontSize = 14.sp,
                color = MaterialTheme.colorScheme.onBackground.copy(alpha = 0.66f)
            )
'''
new_caption = '''            Text(
                text = "مدیریت هوشمند پول روزانه",
                fontSize = 14.sp,
                fontWeight = FontWeight.Medium,
                color = MaterialTheme.colorScheme.onBackground.copy(alpha = 0.72f)
            )
            Text(
                text = "ساده • امن • روشن",
                fontSize = 11.sp,
                color = theme.primary.copy(alpha = 0.86f)
            )
'''
if old_caption not in lt:
    sys.exit("ERROR: splash caption anchor not found. Nothing written.")
lt = lt.replace(old_caption, new_caption, 1)

# 4) New installs default to banking theme; existing saved choice remains untouched.
if 'repo.setting("theme_base", "lavender")' not in app:
    sys.exit("ERROR: LedgerApp default theme anchor not found. Nothing written.")
app = app.replace('repo.setting("theme_base", "lavender")', 'repo.setting("theme_base", "bank")', 1)

# Settings default label must match LedgerApp default.
if 'repo.setting("theme_base", "lavender")' in lt:
    lt = lt.replace('repo.setting("theme_base", "lavender")', 'repo.setting("theme_base", "bank")', 1)

# 5) Extend design tokens, safely.
if "val hairline" not in ds:
    ds = ds.replace(
        "    val heroElevation = 10.dp\n",
        "    val heroElevation = 10.dp\n    val hairline = 1.dp\n    val navItemRadius = 14.dp\n"
    )

# 6) Replace bottom navigation with a premium banking-style version.
new_bottom = '''package com.example.kharjyar.ui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.offset
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.kharjyar.ui.design.AppDesign

private data class NavItem(
    val title: String,
    val icon: String
)

private val navItems = listOf(
    NavItem("خانه", "⌂"),
    NavItem("تراکنش‌ها", "⇄"),
    NavItem("ثبت", "＋"),
    NavItem("مقایسه", "▥"),
    NavItem("تنظیمات", "⚙")
)

@Composable
internal fun KharjBottomBar(
    selectedIndex: Int,
    containerColor: Color,
    primaryColor: Color,
    onSelect: (Int) -> Unit
) {
    Surface(
        color = containerColor,
        tonalElevation = 8.dp,
        shadowElevation = 12.dp,
        shape = AppDesign.navShape,
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 10.dp, vertical = 8.dp)
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .height(70.dp)
                .padding(horizontal = 4.dp),
            horizontalArrangement = Arrangement.SpaceEvenly,
            verticalAlignment = Alignment.CenterVertically
        ) {
            navItems.forEachIndexed { index, item ->
                if (index == 2) {
                    RegisterNavItem(
                        selected = selectedIndex == index,
                        title = item.title,
                        primaryColor = primaryColor,
                        onClick = { onSelect(index) }
                    )
                } else {
                    StandardNavItem(
                        selected = selectedIndex == index,
                        title = item.title,
                        icon = item.icon,
                        primaryColor = primaryColor,
                        onClick = { onSelect(index) }
                    )
                }
            }
        }
    }
}

@Composable
private fun StandardNavItem(
    selected: Boolean,
    title: String,
    icon: String,
    primaryColor: Color,
    onClick: () -> Unit
) {
    val contentColor = if (selected) {
        primaryColor
    } else {
        MaterialTheme.colorScheme.onSurface.copy(alpha = 0.54f)
    }

    Column(
        modifier = Modifier
            .clip(AppDesign.controlShape)
            .clickable(onClick = onClick)
            .padding(horizontal = 7.dp, vertical = 6.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.spacedBy(3.dp)
    ) {
        Surface(
            shape = AppDesign.controlShape,
            color = if (selected) primaryColor.copy(alpha = 0.12f) else Color.Transparent
        ) {
            Text(
                text = icon,
                color = contentColor,
                fontSize = 19.sp,
                fontWeight = if (selected) FontWeight.Bold else FontWeight.Medium,
                modifier = Modifier.padding(horizontal = 11.dp, vertical = 3.dp)
            )
        }
        Text(
            text = title,
            color = contentColor,
            fontSize = 10.sp,
            fontWeight = if (selected) FontWeight.Bold else FontWeight.Medium
        )
    }
}

@Composable
private fun RegisterNavItem(
    selected: Boolean,
    title: String,
    primaryColor: Color,
    onClick: () -> Unit
) {
    Column(
        modifier = Modifier
            .clickable(onClick = onClick)
            .padding(horizontal = 5.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.spacedBy(1.dp)
    ) {
        Box(
            modifier = Modifier
                .size(56.dp)
                .offset(y = (-8).dp)
                .clip(CircleShape)
                .background(
                    brush = Brush.linearGradient(
                        listOf(
                            primaryColor.copy(alpha = 0.52f),
                            Color.White.copy(alpha = 0.80f),
                            primaryColor.copy(alpha = 0.52f)
                        )
                    )
                )
                .padding(2.dp),
            contentAlignment = Alignment.Center
        ) {
            Surface(
                modifier = Modifier.size(50.dp),
                shape = CircleShape,
                color = primaryColor,
                shadowElevation = if (selected) 14.dp else 10.dp
            ) {
                Box(contentAlignment = Alignment.Center) {
                    Text(
                        text = "＋",
                        color = Color.White,
                        fontSize = 27.sp,
                        fontWeight = FontWeight.Bold
                    )
                }
            }
        }

        Text(
            text = title,
            color = if (selected) primaryColor
            else MaterialTheme.colorScheme.onSurface.copy(alpha = 0.62f),
            fontSize = 10.sp,
            fontWeight = FontWeight.Bold
        )
    }
}
'''

# Backups first, then atomic-ish writes.
for p in (legacy, ledger, bottom, design):
    backup = p.with_name(p.name + ".before_final_banking_pack")
    if not backup.exists():
        shutil.copy2(p, backup)

def atomic_write(path, content):
    tmp = path.with_name(path.name + ".finaltmp")
    tmp.write_text(content, encoding="utf-8")
    tmp.replace(path)

atomic_write(legacy, lt)
atomic_write(ledger, app)
atomic_write(design, ds)
atomic_write(bottom, new_bottom)

print("DONE: Final Banking Visual Pack applied.")
print("Changed:")
print(" -", legacy)
print(" -", ledger)
print(" -", design)
print(" -", bottom)
print("No Repository or database changes.")
