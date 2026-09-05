#!/usr/bin/env python3
from pathlib import Path
import shutil
import sys

root = Path(".")
legacy = root / "app/src/main/java/com/example/kharjyar/LegacyScreens.kt"
if not legacy.exists():
    sys.exit("ERROR: run from /workspaces/DakhoKharj")

text = legacy.read_text(encoding="utf-8")
backup = legacy.with_name("LegacyScreens.kt.before_ui_foundation_pack1")
if not backup.exists():
    shutil.copy2(legacy, backup)

# 1) Splash refresh: replace only SplashScreen block.
splash_start = text.find("@Composable\ninternal fun SplashScreen(")
splash_end = text.find("@Composable\ninternal fun LockScreen(", splash_start)

if splash_start == -1 or splash_end == -1:
    sys.exit("ERROR: SplashScreen anchors not found; no changes made.")

new_splash = r'''@Composable
internal fun SplashScreen(theme: VisualTheme) {
    val infinite = rememberInfiniteTransition(label = "splash")
    val pulse by infinite.animateFloat(
        initialValue = 0.92f,
        targetValue = 1.06f,
        animationSpec = infiniteRepeatable(
            animation = tween(durationMillis = 1300),
            repeatMode = RepeatMode.Reverse
        ),
        label = "pulse"
    )
    val glow by infinite.animateFloat(
        initialValue = 0.18f,
        targetValue = 0.34f,
        animationSpec = infiniteRepeatable(
            animation = tween(durationMillis = 1600),
            repeatMode = RepeatMode.Reverse
        ),
        label = "glow"
    )

    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(theme.background),
        contentAlignment = Alignment.Center
    ) {
        Box(
            modifier = Modifier
                .size((118 * pulse).dp)
                .clip(CircleShape)
                .background(theme.primary.copy(alpha = glow))
        )

        Column(
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.spacedBy(14.dp)
        ) {
            Surface(
                shape = CircleShape,
                color = theme.primary,
                shadowElevation = 12.dp,
                modifier = Modifier.size(82.dp)
            ) {
                Box(contentAlignment = Alignment.Center) {
                    Text(
                        text = "دخ",
                        color = Color.White,
                        fontSize = 24.sp,
                        fontWeight = FontWeight.Black
                    )
                }
            }

            Text(
                text = "دخل و خرج",
                fontSize = 30.sp,
                fontWeight = FontWeight.Black,
                color = MaterialTheme.colorScheme.onBackground
            )

            Text(
                text = "مدیریت هوشمند پول روزانه",
                fontSize = 14.sp,
                color = MaterialTheme.colorScheme.onBackground.copy(alpha = 0.66f)
            )

            Spacer(Modifier.height(4.dp))

            LinearProgressIndicator(
                modifier = Modifier.width(128.dp),
                color = theme.primary,
                trackColor = theme.primary.copy(alpha = 0.14f)
            )
        }
    }
}

'''
text = text[:splash_start] + new_splash + text[splash_end:]

# 2) Add shared section/card helpers just before MoneyText anchor if absent.
anchor = "@Composable\nprivate fun MoneyText("
insert_at = text.find(anchor)
if insert_at == -1:
    sys.exit("ERROR: MoneyText anchor not found.")

helpers = r'''
@Composable
private fun FinanceSectionHeader(
    title: String,
    subtitle: String? = null
) {
    Column(verticalArrangement = Arrangement.spacedBy(2.dp)) {
        Text(
            text = title,
            fontSize = 18.sp,
            fontWeight = FontWeight.Bold
        )
        if (!subtitle.isNullOrBlank()) {
            Text(
                text = subtitle,
                fontSize = 12.sp,
                color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.58f)
            )
        }
    }
}

@Composable
private fun FinanceInfoCard(
    title: String,
    value: String,
    modifier: Modifier = Modifier,
    accent: Color = MaterialTheme.colorScheme.primary,
    supporting: String? = null,
    onClick: (() -> Unit)? = null
) {
    val clickableModifier = if (onClick != null) {
        modifier.clickable(onClick = onClick)
    } else {
        modifier
    }

    Card(
        modifier = clickableModifier,
        shape = RoundedCornerShape(20.dp),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surfaceVariant
        )
    ) {
        Column(
            modifier = Modifier.padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(6.dp)
        ) {
            Text(
                text = title,
                fontSize = 12.sp,
                color = MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.68f)
            )
            Text(
                text = value,
                fontSize = 20.sp,
                fontWeight = FontWeight.Bold,
                color = accent
            )
            if (!supporting.isNullOrBlank()) {
                Text(
                    text = supporting,
                    fontSize = 11.sp,
                    color = MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.62f)
                )
            }
        }
    }
}

'''
if "private fun FinanceSectionHeader(" not in text:
    text = text[:insert_at] + helpers + text[insert_at:]

legacy.write_text(text, encoding="utf-8")

# 3) Add shared motion/spacing tokens to AppDesign if file exists.
design = root / "app/src/main/java/com/example/kharjyar/ui/design/AppDesign.kt"
if design.exists():
    dtext = design.read_text(encoding="utf-8")
    if "val sectionGapLarge" not in dtext:
        dtext = dtext.replace(
            "    val sectionGap = 16.dp\n",
            "    val sectionGap = 16.dp\n    val sectionGapLarge = 24.dp\n"
        )
    if "val heroElevation" not in dtext:
        dtext = dtext.replace(
            "    val controlRadius = 16.dp\n",
            "    val controlRadius = 16.dp\n    val heroElevation = 10.dp\n"
        )
    design.write_text(dtext, encoding="utf-8")

# 4) Create reusable section primitives file.
components = root / "app/src/main/java/com/example/kharjyar/ui/components"
components.mkdir(parents=True, exist_ok=True)
finance_file = components / "FinancePrimitives.kt"
finance_file.write_text(r'''package com.example.kharjyar.ui.components

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.kharjyar.ui.design.AppDesign

@Composable
internal fun FinanceSectionTitle(
    title: String,
    subtitle: String? = null
) {
    Column(verticalArrangement = Arrangement.spacedBy(3.dp)) {
        Text(
            text = title,
            fontSize = 18.sp,
            fontWeight = FontWeight.Bold
        )
        if (!subtitle.isNullOrBlank()) {
            Text(
                text = subtitle,
                fontSize = 12.sp,
                color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.58f)
            )
        }
    }
}

@Composable
internal fun FinanceProgressCard(
    title: String,
    value: String,
    progress: Float,
    accent: Color,
    supporting: String? = null,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier.fillMaxWidth(),
        shape = AppDesign.cardShape,
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surfaceVariant
        )
    ) {
        Column(
            modifier = Modifier.padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(10.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Text(title, fontWeight = FontWeight.SemiBold)
                Text(value, fontWeight = FontWeight.Bold, color = accent)
            }

            LinearProgressIndicator(
                progress = { progress.coerceIn(0f, 1f) },
                modifier = Modifier.fillMaxWidth(),
                color = accent
            )

            if (!supporting.isNullOrBlank()) {
                Text(
                    text = supporting,
                    fontSize = 11.sp,
                    color = MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.64f)
                )
            }
        }
    }
}
''', encoding="utf-8")

print("DONE: UI Foundation Pack 1 applied.")
print("Changed:", legacy)
print("Changed:", design if design.exists() else "AppDesign.kt not present")
print("Created:", finance_file)
print("Backup:", backup)
