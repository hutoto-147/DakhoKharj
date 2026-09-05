#!/usr/bin/env python3
from pathlib import Path
import shutil
import sys

target = Path("app/src/main/java/com/example/kharjyar/LegacyScreens.kt")

if not target.exists():
    sys.exit("ERROR: Run this script from the repository root: /workspaces/DakhoKharj")

text = target.read_text(encoding="utf-8")

start_marker = "@Composable\ninternal fun DashboardScreen("
end_marker = "@Composable\nprivate fun MoneyText("

start = text.find(start_marker)
end = text.find(end_marker, start)

if start == -1 or end == -1:
    sys.exit("ERROR: Dashboard block was not found. No file was changed.")

backup = target.with_name("LegacyScreens.kt.before_dashboard_v1")
if not backup.exists():
    shutil.copy2(target, backup)

replacement = r'''@Composable
internal fun DashboardScreen(
    repo: LedgerRepository,
    refreshToken: Int,
    dark: Boolean,
    onOpenComparison: (String, String) -> Unit
) {
    val entries = remember(refreshToken) { repo.entries() }
    val debts = remember(refreshToken) { repo.debts(ObligationKind.DEBT) }
    val loans = remember(refreshToken) { repo.debts(ObligationKind.LOAN) }

    val now = PersianDate.nowParts()
    val monthEntries = entries.filter { PersianDate.parts(it.occurredAt).key == now.key }
    val income = monthEntries.filter { it.type == EntryType.INCOME }.sumOf { it.amount }
    val expense = monthEntries.filter { it.type == EntryType.EXPENSE }.sumOf { it.amount }
    val balance = income - expense

    val budget = remember(refreshToken) { repo.budget() }
    val previousRef = PersianDate.shiftMonth(MonthRef(now.year, now.month, ""), -1)
    val prevEntries = entries.filter { PersianDate.parts(it.occurredAt).key == previousRef.key }
    val prevExpense = prevEntries.filter { it.type == EntryType.EXPENSE }.sumOf { it.amount }

    val top = monthEntries
        .filter { it.type == EntryType.EXPENSE }
        .groupBy { it.category }
        .mapValues { (_, list) -> list.sumOf { it.amount } }
        .toList()
        .sortedByDescending { it.second }
        .take(5)

    val incomeBg = if (dark) Color(0xFF183B2A) else Color(0xFFE7F6EC)
    val expenseBg = if (dark) Color(0xFF48252C) else Color(0xFFFFE9EC)
    val debtBg = if (dark) Color(0xFF49371D) else Color(0xFFFFF2D9)
    val loanBg = if (dark) Color(0xFF302A49) else Color(0xFFEDE9FA)

    LazyColumn(
        modifier = Modifier.fillMaxSize(),
        contentPadding = PaddingValues(horizontal = 16.dp, vertical = 18.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        item {
            Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
                Text(
                    "نمای کلی مالی",
                    fontSize = 13.sp,
                    color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.58f)
                )
                Text(
                    PersianDate.formatMonth(System.currentTimeMillis()),
                    fontSize = 22.sp,
                    fontWeight = FontWeight.Bold
                )
            }
        }

        item {
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

        item {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                DashboardMoneyCard(
                    modifier = Modifier.weight(1f),
                    icon = "↗",
                    title = "درآمد این ماه",
                    value = income.asCompactToman(),
                    background = incomeBg,
                    valueColor = IncomeStrong
                ) { onOpenComparison("درآمد", "دسته‌ها") }

                DashboardMoneyCard(
                    modifier = Modifier.weight(1f),
                    icon = "↙",
                    title = "هزینه این ماه",
                    value = expense.asCompactToman(),
                    background = expenseBg,
                    valueColor = ExpenseStrong
                ) { onOpenComparison("هزینه", "دسته‌ها") }
            }
        }

        item {
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(
                    containerColor = MaterialTheme.colorScheme.surfaceVariant
                ),
                shape = RoundedCornerShape(20.dp)
            ) {
                Column(
                    modifier = Modifier.padding(18.dp),
                    verticalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    Text(
                        "خلاصه این ماه",
                        fontSize = 19.sp,
                        fontWeight = FontWeight.Bold
                    )

                    val comparison = when {
                        prevEntries.isEmpty() -> "برای ماه قبل داده کافی نداریم."
                        prevExpense == 0L -> "ماه قبل هزینه ثبت‌شده صفر بوده است."
                        else -> {
                            val pct = (
                                (expense - prevExpense).toDouble() /
                                    prevExpense.toDouble() * 100
                                ).roundToInt()
                            if (pct >= 0) {
                                "هزینه نسبت به ماه قبل ${pct.toString().toPersianDigits()}٪ بیشتر شده."
                            } else {
                                "هزینه نسبت به ماه قبل ${(-pct).toString().toPersianDigits()}٪ کمتر شده."
                            }
                        }
                    }

                    Text(
                        comparison,
                        color = MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.78f)
                    )

                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        Text("مانده خالص", fontWeight = FontWeight.SemiBold)
                        Text(balance.asToman(), fontWeight = FontWeight.Bold)
                    }

                    if (budget > 0L) {
                        val progress = (expense.toFloat() / budget.toFloat()).coerceIn(0f, 1f)

                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween
                        ) {
                            Text("بودجه ماه", fontWeight = FontWeight.SemiBold)
                            Text(budget.asToman(), fontWeight = FontWeight.SemiBold)
                        }

                        LinearProgressIndicator(
                            progress = { progress },
                            modifier = Modifier.fillMaxWidth()
                        )

                        Text(
                            "باقی‌مانده بودجه: ${(budget - expense).asToman()}",
                            fontSize = 12.sp,
                            color = MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.70f)
                        )
                    }
                }
            }
        }

        item {
            SectionTitle("هزینه‌ها بر اساس دسته‌بندی")
            Spacer(Modifier.height(8.dp))

            if (top.isEmpty()) {
                EmptyState("هنوز برای این ماه هزینه‌ای ثبت نشده است.")
            } else {
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(20.dp)
                ) {
                    Column(
                        modifier = Modifier.padding(16.dp),
                        verticalArrangement = Arrangement.spacedBy(16.dp)
                    ) {
                        top.forEach { pair ->
                            val progress = if (expense > 0L) {
                                (pair.second.toFloat() / expense.toFloat()).coerceIn(0f, 1f)
                            } else {
                                0f
                            }

                            Column(
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .clickable { onOpenComparison("هزینه", "دسته‌ها") },
                                verticalArrangement = Arrangement.spacedBy(7.dp)
                            ) {
                                Row(
                                    modifier = Modifier.fillMaxWidth(),
                                    horizontalArrangement = Arrangement.SpaceBetween,
                                    verticalAlignment = Alignment.CenterVertically
                                ) {
                                    Row(
                                        verticalAlignment = Alignment.CenterVertically,
                                        horizontalArrangement = Arrangement.spacedBy(8.dp)
                                    ) {
                                        Text(
                                            Presets.categoryIcon(pair.first, EntryType.EXPENSE),
                                            fontSize = 20.sp
                                        )
                                        Text(
                                            pair.first,
                                            fontWeight = FontWeight.SemiBold
                                        )
                                    }

                                    Text(
                                        pair.second.asCompactToman(),
                                        fontSize = 12.sp,
                                        fontWeight = FontWeight.SemiBold
                                    )
                                }

                                LinearProgressIndicator(
                                    progress = { progress },
                                    modifier = Modifier.fillMaxWidth()
                                )
                            }
                        }
                    }
                }
            }
        }

        item {
            SectionTitle("بدهی و قرض")
            Spacer(Modifier.height(8.dp))

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                DashboardObligationCard(
                    modifier = Modifier.weight(1f),
                    icon = "↓",
                    title = "بدهی",
                    value = debts.sumOf { it.currentAmount }.asCompactToman(),
                    count = debts.size,
                    background = debtBg,
                    accent = DebtStrong
                ) { onOpenComparison("بدهی", "روند ماهانه") }

                DashboardObligationCard(
                    modifier = Modifier.weight(1f),
                    icon = "↑",
                    title = "قرض داده‌شده",
                    value = loans.sumOf { it.currentAmount }.asCompactToman(),
                    count = loans.size,
                    background = loanBg,
                    accent = LoanStrong
                ) { onOpenComparison("قرض", "روند ماهانه") }
            }
        }

        item {
            Spacer(Modifier.height(18.dp))
        }
    }
}

@Composable
private fun DashboardMoneyCard(
    modifier: Modifier,
    icon: String,
    title: String,
    value: String,
    background: Color,
    valueColor: Color,
    onClick: () -> Unit
) {
    Card(
        modifier = modifier
            .height(124.dp)
            .clickable(onClick = onClick),
        colors = CardDefaults.cardColors(containerColor = background),
        shape = RoundedCornerShape(20.dp)
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(14.dp),
            verticalArrangement = Arrangement.SpaceBetween
        ) {
            Text(
                icon,
                color = valueColor,
                fontSize = 22.sp,
                fontWeight = FontWeight.Bold
            )

            Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
                Text(
                    title,
                    fontSize = 12.sp,
                    color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.68f)
                )
                Text(
                    value,
                    fontSize = 17.sp,
                    fontWeight = FontWeight.Bold,
                    color = valueColor
                )
            }
        }
    }
}

@Composable
private fun DashboardObligationCard(
    modifier: Modifier,
    icon: String,
    title: String,
    value: String,
    count: Int,
    background: Color,
    accent: Color,
    onClick: () -> Unit
) {
    Card(
        modifier = modifier
            .height(128.dp)
            .clickable(onClick = onClick),
        colors = CardDefaults.cardColors(containerColor = background),
        shape = RoundedCornerShape(20.dp)
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(14.dp),
            verticalArrangement = Arrangement.SpaceBetween
        ) {
            Text(
                icon,
                color = accent,
                fontSize = 22.sp,
                fontWeight = FontWeight.Bold
            )

            Column(verticalArrangement = Arrangement.spacedBy(3.dp)) {
                Text(
                    title,
                    fontWeight = FontWeight.SemiBold,
                    fontSize = 13.sp
                )
                Text(
                    value,
                    color = accent,
                    fontWeight = FontWeight.Bold
                )
                Text(
                    "${count.toString().toPersianDigits()} مورد",
                    fontSize = 10.sp,
                    color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.58f)
                )
            }
        }
    }
}

'''

target.write_text(text[:start] + replacement + text[end:], encoding="utf-8")

print("Dashboard Redesign v1 applied successfully.")
print(f"Changed: {target}")
print(f"Backup:  {backup}")
