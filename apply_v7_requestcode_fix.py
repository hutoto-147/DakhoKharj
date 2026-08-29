#!/usr/bin/env python3
from pathlib import Path
import re
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
gradle = root / "app/build.gradle.kts"

if not gradle.exists():
    raise SystemExit("missing app/build.gradle.kts")

text = gradle.read_text(encoding="utf-8")

if 'applicationId = "io.github.hutoto147.dakhlokharj"' not in text:
    raise SystemExit("unexpected applicationId")

if 'signingConfig = signingConfigs.getByName("stableDebug")' not in text:
    raise SystemExit("stableDebug signing config not found")

# This patch is intentionally for the currently installed V6 baseline.
if not re.search(r'versionCode\s*=\s*6\b', text):
    raise SystemExit("expected versionCode = 6 baseline")

# The requestCode crash is caused by old FragmentActivity behavior being
# pulled transitively. Add a modern Fragment explicitly.
fragment_line = '    implementation("androidx.fragment:fragment-ktx:1.9.0")'
if 'androidx.fragment:fragment' not in text:
    match = re.search(
        r'(?m)^(\s*implementation\("androidx\.activity:activity-compose:[^"]+"\)\s*)$',
        text
    )
    if not match:
        raise SystemExit("activity-compose dependency line not found")
    text = text[:match.end()] + "\n" + fragment_line + text[match.end():]

text = re.sub(r'versionCode\s*=\s*6\b', 'versionCode = 7', text, count=1)
text = text.replace('versionName = "1.0.6"', 'versionName = "1.0.7"', 1)

gradle.write_text(text, encoding="utf-8")

check = gradle.read_text(encoding="utf-8")
required = [
    'applicationId = "io.github.hutoto147.dakhlokharj"',
    'versionCode = 7',
    'versionName = "1.0.7"',
    'signingConfig = signingConfigs.getByName("stableDebug")',
    'implementation("androidx.fragment:fragment-ktx:1.9.0")',
]
missing = [item for item in required if item not in check]
if missing:
    raise SystemExit("post-patch verification failed: " + ", ".join(missing))

print("V7 minimal requestCode fix applied successfully.")
print("- only app/build.gradle.kts changed")
print("- Fragment 1.9.0 added")
print("- versionCode 7 / versionName 1.0.7")
print("- package and signing config preserved")
