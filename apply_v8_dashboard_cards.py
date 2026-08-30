#!/usr/bin/env python3
from pathlib import Path
import re
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
gradle = root / "app/build.gradle.kts"
main = root / "app/src/main/java/com/example/kharjyar/MainActivity.kt"

for p in (gradle, main):
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

# ------------------------------------------------------------
# Gradle: preserve package/signing, preserve the V7 Fragment fix,
# and move the installed debug build to V8.
# ------------------------------------------------------------
g = gradle.read_text(encoding="utf-8")

if 'applicationId = "io.github.hutoto147.dakhlokharj"' not in g:
    raise SystemExit("unexpected applicationId")
if 'signingConfig = signingConfigs.getByName("stableDebug")' not in g:
    raise SystemExit("stableDebug signing config not found")

fragment_line = '    implementation("androidx.fragment:fragment-ktx:1.9.0")'
if 'androidx.fragment:fragment' not in g:
    activity_match = re.search(
        r'(?m)^(\s*implementation\("androidx\.activity:activity-compose:[^"]+"\)\s*)$',
        g
    )
    if not activity_match:
        raise SystemExit("activity-compose dependency line not found")
    g = g[:activity_match.end()] + "\n" + fragment_line + g[activity_match.end():]

# Accept repository source being V5/V6/V7, but always produce V8.
g, count_code = re.subn(
    r'versionCode\s*=\s*(?:5|6|7)\b',
    'versionCode = 8',
    g,
    count=1
)
if count_code == 0 and not re.search(r'versionCode\s*=\s*8\b', g):
    raise SystemExit("versionCode is not 5, 6, 7 or 8")

for old_name in ('1.0.5', '1.0.6', '1.0.7'):
    old = f'versionName = "{old_name}"'
    if old in g:
        g = g.replace(old, 'versionName = "1.0.8"', 1)
        break
else:
    if 'versionName = "1.0.8"' not in g:
        raise SystemExit("versionName is not 1.0.5, 1.0.6, 1.0.7 or 1.0.8")

gradle.write_text(g, encoding="utf-8")

# ------------------------------------------------------------
# MainActivity: ONLY dashboard card presentation.
# Navigation/click behavior is preserved exactly as-is.
# ------------------------------------------------------------
m = main.read_text(encoding="utf-8")

metric_start = '''@Composable
private fun MetricCard('''
obligation_start = '''@Composable
private fun ObligationMetricCard('''
money_start = '''@Composable
private fun MoneyText('''

new_metric = r'''@Composable
private fun MetricCard(modifier: Modifier, title: String, value: String, background: Color, onClick: () -> Unit) {
    Card(
        modifier = modifier.height(116.dp).clickable(onClick = onClick),
        colors = CardDefaults.cardColors(containerColor = background),
        shape = RoundedCornerShape(20.dp)
    ) {
        Column(
            Modifier.fillMaxSize().padding(horizontal = 10.dp, vertical = 12.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center
        ) {
            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.Center
            ) {
                Text(title, textAlign = TextAlign.Center, fontWeight = FontWeight.SemiBold)
                Spacer(Modifier.width(4.dp))
                Text("‹", fontSize = 18.sp, fontWeight = FontWeight.Bold)
            }
            Spacer(Modifier.height(8.dp))
            Text(
                value,
                textAlign = TextAlign.Center,
                fontWeight = FontWeight.Bold,
                fontSize = 16.sp,
                lineHeight = 20.sp
            )
        }
    }
}
'''

new_obligation = r'''@Composable
private fun ObligationMetricCard(
    modifier: Modifier,
    title: String,
    value: String,
    count: Int,
    background: Color,
    onClick: () -> Unit
) {
    Card(
        modifier = modifier.height(112.dp).clickable(onClick = onClick),
        colors = CardDefaults.cardColors(containerColor = background),
        shape = RoundedCornerShape(18.dp)
    ) {
        Column(
            Modifier.fillMaxSize().padding(12.dp),
            verticalArrangement = Arrangement.Center,
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.Center
            ) {
                Text(title, fontWeight = FontWeight.Bold, textAlign = TextAlign.Center)
                Spacer(Modifier.width(4.dp))
                Text("‹", fontSize = 18.sp, fontWeight = FontWeight.Bold)
            }
            Spacer(Modifier.height(6.dp))
            Text(value, fontWeight = FontWeight.SemiBold, textAlign = TextAlign.Center)
            Text("${count.toString().toPersianDigits()} مورد", fontSize = 10.sp, textAlign = TextAlign.Center)
        }
    }
}
'''

m = replace_between(m, metric_start, obligation_start, new_metric, "MetricCard")
m = replace_between(m, obligation_start, money_start, new_obligation, "ObligationMetricCard")

# Update only the visible app version label if present.
for old_label in (
    'نسخه آزمایشی ۱.۰.۵',
    'نسخه آزمایشی ۱.۰.۶',
    'نسخه آزمایشی ۱.۰.۷',
):
    if old_label in m:
        m = m.replace(old_label, 'نسخه آزمایشی ۱.۰.۸', 1)
        break

main.write_text(m, encoding="utf-8")

# ------------------------------------------------------------
# Self-checks
# ------------------------------------------------------------
g2 = gradle.read_text(encoding="utf-8")
m2 = main.read_text(encoding="utf-8")

checks = {
    "versionCode 8": bool(re.search(r'versionCode\s*=\s*8\b', g2)),
    "versionName 1.0.8": 'versionName = "1.0.8"' in g2,
    "package preserved": 'applicationId = "io.github.hutoto147.dakhlokharj"' in g2,
    "debug signing preserved": 'signingConfig = signingConfigs.getByName("stableDebug")' in g2,
    "requestCode fix preserved": 'implementation("androidx.fragment:fragment-ktx:1.9.0")' in g2,
    "details text removed": 'نمایش جزئیات ←' not in m2,
    "obligation details text removed": 'مورد • جزئیات ←' not in m2,
    "dashboard arrow present": 'Text("‹", fontSize = 18.sp' in m2,
    "income click preserved": 'onOpenComparison("درآمد", "دسته‌ها")' in m2,
    "expense click preserved": 'onOpenComparison("هزینه", "دسته‌ها")' in m2,
    "balance click preserved": 'onOpenComparison("درآمد و هزینه", "ماه انتخابی")' in m2,
}
failed = [name for name, ok in checks.items() if not ok]
if failed:
    raise SystemExit("post-patch checks failed: " + ", ".join(failed))

print("V8 dashboard card cleanup applied successfully.")
print("- backup/restore code untouched by this patch")
print("- Fragment 1.9.0 preserved")
print("- versionCode 8 / versionName 1.0.8")
print("- «جزئیات» removed from dashboard cards")
print("- small chevron added; whole cards remain clickable")
