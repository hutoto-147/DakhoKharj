#!/usr/bin/env python3
"""
Safe first-stage refactor for DakhlKharj MainActivity.kt.

Run from repository root:
    python3 tools/apply_main_refactor.py

What it does:
1. Verifies the current monolithic MainActivity.kt has the expected anchors.
2. Creates a text backup under refactor_backup/.
3. Creates LegacyScreens.kt from the current source.
4. Removes MainActivity, LedgerApp and MainScaffold from LegacyScreens.
5. Changes ONLY the top-level UI declarations needed by ui/app from private -> internal.
6. Writes the new MainActivity.kt, ui/app/LedgerApp.kt and ui/app/MainScaffold.kt.

It does NOT touch LedgerDb.kt, repository logic, models, database schema, import/export,
reminders, recurring transaction behavior or existing screen implementation bodies.
"""

from pathlib import Path
import shutil
import sys
import re

ROOT = Path(__file__).resolve().parents[1]

SOURCE = ROOT / "app/src/main/java/com/example/kharjyar/MainActivity.kt"
LEGACY = ROOT / "app/src/main/java/com/example/kharjyar/LegacyScreens.kt"
NEW_MAIN_TEMPLATE = ROOT / "refactor_templates/MainActivity.kt"
NEW_LEDGER_TEMPLATE = ROOT / "refactor_templates/LedgerApp.kt"
NEW_SCAFFOLD_TEMPLATE = ROOT / "refactor_templates/MainScaffold.kt"

TARGET_MAIN = SOURCE
TARGET_LEDGER = ROOT / "app/src/main/java/com/example/kharjyar/ui/app/LedgerApp.kt"
TARGET_SCAFFOLD = ROOT / "app/src/main/java/com/example/kharjyar/ui/app/MainScaffold.kt"
BACKUP_DIR = ROOT / "refactor_backup"


def fail(message: str) -> None:
    print(f"[ERROR] {message}")
    sys.exit(1)


def find_function_block(text: str, function_name: str):
    """
    Returns (start, end) covering annotations directly above a top-level Kotlin function
    through its matching closing brace.
    """
    match = re.search(
        rf"(?m)^[ \t]*(?:private|internal|public)?[ \t]*fun[ \t]+{re.escape(function_name)}[ \t]*\(",
        text,
    )
    if not match:
        fail(f"Could not find function: {function_name}")

    start = match.start()

    # Include contiguous @Composable / @OptIn annotation lines immediately above.
    line_start = text.rfind("\n", 0, start) + 1
    probe = line_start
    while probe > 0:
        prev_end = probe - 1
        prev_start = text.rfind("\n", 0, prev_end) + 1
        prev_line = text[prev_start:prev_end].strip()
        if prev_line.startswith("@"):
            start = prev_start
            probe = prev_start
        else:
            break

    brace = text.find("{", match.end())
    if brace == -1:
        fail(f"Opening brace not found for {function_name}")

    depth = 0
    in_string = False
    escaped = False
    i = brace
    while i < len(text):
        ch = text[i]

        if in_string:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == '"':
                in_string = False
        else:
            if ch == '"':
                in_string = True
            elif ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    end = i + 1
                    if end < len(text) and text[end] == "\n":
                        end += 1
                    return start, end
        i += 1

    fail(f"Matching closing brace not found for {function_name}")


def find_class_block(text: str, class_name: str):
    match = re.search(
        rf"(?m)^[ \t]*(?:private|internal|public)?[ \t]*class[ \t]+{re.escape(class_name)}\b",
        text,
    )
    if not match:
        fail(f"Could not find class: {class_name}")

    start = match.start()
    brace = text.find("{", match.end())
    if brace == -1:
        fail(f"Opening brace not found for class {class_name}")

    depth = 0
    in_string = False
    escaped = False
    i = brace

    while i < len(text):
        ch = text[i]

        if in_string:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == '"':
                in_string = False
        else:
            if ch == '"':
                in_string = True
            elif ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    end = i + 1
                    if end < len(text) and text[end] == "\n":
                        end += 1
                    return start, end
        i += 1

    fail(f"Matching closing brace not found for class {class_name}")


def remove_ranges(text: str, ranges):
    for start, end in sorted(ranges, reverse=True):
        text = text[:start] + text[end:]
    return text


def main():
    if not SOURCE.exists():
        fail(f"Source file not found: {SOURCE}")

    for template in (NEW_MAIN_TEMPLATE, NEW_LEDGER_TEMPLATE, NEW_SCAFFOLD_TEMPLATE):
        if not template.exists():
            fail(f"Template not found: {template}")

    original = SOURCE.read_text(encoding="utf-8")

    anchors = [
        "class MainActivity : FragmentActivity()",
        "fun LedgerApp(",
        "fun MainScaffold(",
        "private fun DashboardScreen(",
        "private fun TransactionsScreen(",
        "private fun AddEntryScreen(",
        "private fun ComparisonScreen(",
        "private fun SettingsScreen(",
    ]
    missing = [a for a in anchors if a not in original]
    if missing:
        fail(
            "The repository MainActivity.kt does not match the expected source. "
            "Missing anchors: " + ", ".join(missing)
        )

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    backup = BACKUP_DIR / "MainActivity.before_ui_refactor.kt.txt"
    backup.write_text(original, encoding="utf-8")

    ranges = [
        find_class_block(original, "MainActivity"),
        find_function_block(original, "LedgerApp"),
        find_function_block(original, "MainScaffold"),
    ]

    legacy = remove_ranges(original, ranges)

    # BottomTab belongs to the new MainScaffold.
    legacy = re.sub(
        r"(?m)^private data class BottomTab\(val title: String, val icon: String\)\s*\n?",
        "",
        legacy,
        count=1,
    )

    visibility_changes = {
        "private data class VisualTheme(": "internal data class VisualTheme(",
        "private fun visualTheme(": "internal fun visualTheme(",
        "private fun KharjYarTheme(": "internal fun KharjYarTheme(",
        "private fun SplashScreen(": "internal fun SplashScreen(",
        "private fun LockScreen(": "internal fun LockScreen(",
        "private fun DashboardScreen(": "internal fun DashboardScreen(",
        "private fun TransactionsScreen(": "internal fun TransactionsScreen(",
        "private fun AddEntryScreen(": "internal fun AddEntryScreen(",
        "private fun ComparisonScreen(": "internal fun ComparisonScreen(",
        "private fun SettingsScreen(": "internal fun SettingsScreen(",
    }

    for old, new in visibility_changes.items():
        if old not in legacy:
            fail(f"Expected declaration not found while preparing LegacyScreens: {old}")
        legacy = legacy.replace(old, new, 1)

    LEGACY.write_text(legacy, encoding="utf-8")

    TARGET_LEDGER.parent.mkdir(parents=True, exist_ok=True)
    TARGET_SCAFFOLD.parent.mkdir(parents=True, exist_ok=True)

    TARGET_MAIN.write_text(
        NEW_MAIN_TEMPLATE.read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    TARGET_LEDGER.write_text(
        NEW_LEDGER_TEMPLATE.read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    TARGET_SCAFFOLD.write_text(
        NEW_SCAFFOLD_TEMPLATE.read_text(encoding="utf-8"),
        encoding="utf-8",
    )

    print("[OK] Refactor files created.")
    print(f"[OK] Backup: {backup.relative_to(ROOT)}")
    print(f"[OK] Legacy UI: {LEGACY.relative_to(ROOT)}")
    print(f"[OK] Main: {TARGET_MAIN.relative_to(ROOT)}")
    print(f"[OK] LedgerApp: {TARGET_LEDGER.relative_to(ROOT)}")
    print(f"[OK] MainScaffold: {TARGET_SCAFFOLD.relative_to(ROOT)}")
    print()
    print("Next:")
    print("  ./gradlew testDebugUnitTest")
    print("  ./gradlew assembleDebug")
    print()
    print("Do not merge the branch until both commands pass.")


if __name__ == "__main__":
    main()
