#!/usr/bin/env python3
from pathlib import Path
import sys

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path.cwd()
MAIN = ROOT / 'app/src/main/java/com/example/kharjyar/MainActivity.kt'
REMINDER = ROOT / 'app/src/main/java/com/example/kharjyar/ReminderSupport.kt'
GRADLE = ROOT / 'app/build.gradle.kts'


def fail(msg: str):
    raise SystemExit(f'ERROR: {msg}')


def replace_between(text: str, start_marker: str, end_marker: str, replacement: str) -> str:
    start = text.find(start_marker)
    if start < 0:
        fail(f'start marker not found: {start_marker[:80]!r}')
    end = text.find(end_marker, start)
    if end < 0:
        fail(f'end marker not found: {end_marker[:80]!r}')
    return text[:start] + replacement.rstrip() + '\n' + text[end:]


if not MAIN.exists():
    fail(f'MainActivity.kt not found under {ROOT}')

text = MAIN.read_text(encoding='utf-8')

# V5: release/1.0.0 base + dashboard analysis + accordion settings.
main_block = r'''private data class AnalysisGroupV2(
    val label: String,
    val income: Long,
    val expense: Long,
    val latestAt: Long,
    val entries: List<LedgerEntry>
) {
    fun valueFor(metric: String): Long = when (metric) {
        "درآمد" -> income
        "هزینه" -> expense
        else -> income + expense
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun MainScaffold(repo: LedgerRepository, refreshToken: Int, theme: VisualTheme, onRefresh: () -> Unit) {
    var selectedTab by rememberSaveable { mutableIntStateOf(0) }
    var editingEntry by remember { mutableStateOf<LedgerEntry?>(null) }
    var editingDebt by remember { mutableStateOf<Debt?>(null) }
    var comparisonMetric by rememberSaveable { mutableStateOf("درآمد و هزینه") }
    var comparisonMode by rememberSaveable { mutableStateOf("ماه انتخابی") }
    var comparisonLaunchKey by rememberSaveable { mutableIntStateOf(0) }

    fun openComparison(metric: String, mode: String) {
        comparisonMetric = metric
        comparisonMode = mode
        comparisonLaunchKey++
        editingEntry = null
        editingDebt = null
        selectedTab = 3
    }

    val tabs = listOf(
        BottomTab("خانه", "⌂"), BottomTab("تراکنش‌ها", "≡"), BottomTab("ثبت", "＋"), BottomTab("مقایسه", "▥"), BottomTab("تنظیمات", "⚙")
    )
    val title = when {
        selectedTab == 2 && editingDebt != null -> if (editingDebt?.kind == ObligationKind.LOAN) "ویرایش قرض" else "ویرایش بدهی"
        selectedTab == 2 && editingEntry != null -> "ویرایش تراکنش"
        selectedTab == 0 -> "دخل و خرج"
        selectedTab == 1 -> "تراکنش‌ها"
        selectedTab == 2 -> "ثبت"
        selectedTab == 3 -> "مقایسه و تحلیل"
        else -> "تنظیمات"
    }
    Box(Modifier.fillMaxSize().background(Brush.verticalGradient(listOf(theme.top, theme.bottom)))) {
        Scaffold(
            containerColor = Color.Transparent,
            topBar = { CenterAlignedTopAppBar(title = { Text(title) }, colors = TopAppBarDefaults.centerAlignedTopAppBarColors(containerColor = Color.Transparent)) },
            bottomBar = {
                NavigationBar(containerColor = theme.nav) {
                    tabs.forEachIndexed { index, tab ->
                        NavigationBarItem(
                            selected = selectedTab == index,
                            onClick = {
                                if (index != 2) { editingEntry = null; editingDebt = null }
                                selectedTab = index
                            },
                            icon = { Text(tab.icon, fontSize = 20.sp) }, label = { Text(tab.title, fontSize = 11.sp) }
                        )
                    }
                }
            }
        ) { padding ->
            Box(Modifier.fillMaxSize().padding(padding)) {
                when (selectedTab) {
                    0 -> DashboardScreen(repo, refreshToken, theme.isDark, onOpenComparison = ::openComparison)
                    1 -> TransactionsScreen(repo, refreshToken,
                        onEdit = { editingEntry = it; editingDebt = null; selectedTab = 2 },
                        onEditDebt = { editingDebt = it; editingEntry = null; selectedTab = 2 },
                        onDeleted = onRefresh)
                    2 -> AddEntryScreen(repo, refreshToken, editingEntry, editingDebt, onSaved = { editingEntry = null; editingDebt = null; onRefresh(); selectedTab = 1 })
                    3 -> ComparisonScreen(repo, refreshToken, comparisonMetric, comparisonMode, comparisonLaunchKey)
                    else -> SettingsScreen(repo, refreshToken, onRefresh)
                }
            }
        }
    }
}

@Composable
private fun DashboardScreen(
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
    val top = monthEntries.filter { it.type == EntryType.EXPENSE }.groupBy { it.category }
        .mapValues { (_, list) -> list.sumOf { it.amount } }.toList().sortedByDescending { it.second }.take(5)
    val incomeBg = if (dark) Color(0xFF234130) else IncomeSoftLight
    val expenseBg = if (dark) Color(0xFF4A2830) else ExpenseSoftLight
    val balanceBg = if (dark) Color(0xFF23394F) else BalanceSoftLight
    val debtBg = if (dark) Color(0xFF49371D) else DebtSoftLight
    val loanBg = if (dark) Color(0xFF302A49) else LoanSoftLight
    LazyColumn(
        modifier = Modifier.fillMaxSize(), contentPadding = PaddingValues(16.dp), verticalArrangement = Arrangement.spacedBy(14.dp)
    ) {
        item {
            Text(PersianDate.formatMonth(System.currentTimeMillis()), fontWeight = FontWeight.SemiBold, modifier = Modifier.fillMaxWidth(), textAlign = TextAlign.Start)
        }
        item {
            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                MetricCard(Modifier.weight(1f), "درآمد", income.asCompactToman(), incomeBg) { onOpenComparison("درآمد", "دسته‌ها") }
                MetricCard(Modifier.weight(1f), "هزینه", expense.asCompactToman(), expenseBg) { onOpenComparison("هزینه", "دسته‌ها") }
                MetricCard(Modifier.weight(1f), "مانده", balance.asCompactToman(), balanceBg) { onOpenComparison("درآمد و هزینه", "ماه انتخابی") }
            }
        }
        item {
            Card(Modifier.fillMaxWidth(), colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant), shape = RoundedCornerShape(20.dp)) {
                Column(Modifier.padding(18.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
                    Text("خلاصه ماه", fontSize = 20.sp, fontWeight = FontWeight.Bold, modifier = Modifier.fillMaxWidth(), textAlign = TextAlign.Start)
                    val comparison = when {
                        prevEntries.isEmpty() -> "برای ماه قبل داده کافی نداریم."
                        prevExpense == 0L -> "ماه قبل هزینه ثبت‌شده صفر بوده است."
                        else -> {
                            val pct = ((expense - prevExpense).toDouble() / prevExpense.toDouble() * 100).roundToInt()
                            if (pct >= 0) "هزینه نسبت به ماه قبل ${pct.toString().toPersianDigits()}٪ بیشتر شده." else "هزینه نسبت به ماه قبل ${(-pct).toString().toPersianDigits()}٪ کمتر شده."
                        }
                    }
                    Text(comparison, modifier = Modifier.fillMaxWidth(), textAlign = TextAlign.Start)
                    Text("مانده خالص: ${balance.asToman()}", modifier = Modifier.fillMaxWidth(), textAlign = TextAlign.Start)
                    Text("بدهی فعال: ${debts.sumOf { it.currentAmount }.asToman()}  •  قرض داده‌شده: ${loans.sumOf { it.currentAmount }.asToman()}", modifier = Modifier.fillMaxWidth(), textAlign = TextAlign.Start)
                    if (budget > 0L) {
                        val progress = (expense.toFloat() / budget.toFloat()).coerceIn(0f, 1f)
                        Text("بودجه: ${budget.asToman()}", modifier = Modifier.fillMaxWidth(), textAlign = TextAlign.Start)
                        LinearProgressIndicator(progress = { progress }, modifier = Modifier.fillMaxWidth())
                        Text("باقی‌مانده بودجه: ${(budget - expense).asToman()}", modifier = Modifier.fillMaxWidth(), textAlign = TextAlign.Start)
                    }
                }
            }
        }
        item {
            SectionTitle("بیشترین هزینه‌ها")
            if (top.isEmpty()) EmptyState("هنوز برای این ماه هزینه‌ای ثبت نشده است.") else Card(Modifier.fillMaxWidth(), shape = RoundedCornerShape(18.dp)) {
                Column(Modifier.padding(horizontal = 16.dp, vertical = 8.dp)) {
                    top.forEachIndexed { index, pair ->
                        Row(
                            Modifier.fillMaxWidth().clickable { onOpenComparison("هزینه", "دسته‌ها") }.padding(vertical = 12.dp),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                                Text(Presets.categoryIcon(pair.first, EntryType.EXPENSE), fontSize = 20.sp)
                                Text(pair.first, fontWeight = FontWeight.SemiBold)
                            }
                            Text(pair.second.asToman())
                        }
                        if (index != top.lastIndex) HorizontalDivider()
                    }
                }
            }
        }
        item {
            SectionTitle("بدهی و قرض")
            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                ObligationMetricCard(
                    modifier = Modifier.weight(1f),
                    title = "بدهی",
                    value = debts.sumOf { it.currentAmount }.asCompactToman(),
                    count = debts.size,
                    background = debtBg
                ) { onOpenComparison("بدهی", "روند ماهانه") }
                ObligationMetricCard(
                    modifier = Modifier.weight(1f),
                    title = "قرض داده‌شده",
                    value = loans.sumOf { it.currentAmount }.asCompactToman(),
                    count = loans.size,
                    background = loanBg
                ) { onOpenComparison("قرض", "روند ماهانه") }
            }
        }
        item { Spacer(Modifier.height(12.dp)) }
    }
}

@Composable
private fun MetricCard(modifier: Modifier, title: String, value: String, background: Color, onClick: () -> Unit) {
    Card(modifier = modifier.height(116.dp).clickable(onClick = onClick), colors = CardDefaults.cardColors(containerColor = background), shape = RoundedCornerShape(20.dp)) {
        Column(Modifier.fillMaxSize().padding(10.dp), horizontalAlignment = Alignment.CenterHorizontally, verticalArrangement = Arrangement.Center) {
            Text(title, textAlign = TextAlign.Center, fontWeight = FontWeight.SemiBold)
            Spacer(Modifier.height(8.dp))
            Text(value, textAlign = TextAlign.Center, fontWeight = FontWeight.Bold, fontSize = 16.sp, lineHeight = 20.sp)
            Spacer(Modifier.height(4.dp))
            Text("نمایش جزئیات ←", fontSize = 10.sp)
        }
    }
}

@Composable
private fun ObligationMetricCard(
    modifier: Modifier,
    title: String,
    value: String,
    count: Int,
    background: Color,
    onClick: () -> Unit
) {
    Card(modifier = modifier.height(112.dp).clickable(onClick = onClick), colors = CardDefaults.cardColors(containerColor = background), shape = RoundedCornerShape(18.dp)) {
        Column(Modifier.fillMaxSize().padding(12.dp), verticalArrangement = Arrangement.Center, horizontalAlignment = Alignment.CenterHorizontally) {
            Text(title, fontWeight = FontWeight.Bold, textAlign = TextAlign.Center)
            Spacer(Modifier.height(6.dp))
            Text(value, fontWeight = FontWeight.SemiBold, textAlign = TextAlign.Center)
            Text("${count.toString().toPersianDigits()} مورد • جزئیات ←", fontSize = 10.sp, textAlign = TextAlign.Center)
        }
    }
}
@Composable
private fun MoneyText(
    amount: Long,
    modifier: Modifier = Modifier,
    compact: Boolean = false,
    forcedSign: String? = null,
    color: Color = Color.Unspecified,
    fontWeight: FontWeight? = null,
    fontSize: TextUnit = TextUnit.Unspecified
) {
    val raw = amount.toGroupedPersianDigits()
    val sign = when {
        forcedSign == "+" -> "+"
        forcedSign == "−" -> "−"
        amount < 0L -> "−"
        else -> ""
    }
    Text(
        text = "$raw$sign تومان",
        modifier = modifier,
        color = color,
        fontWeight = fontWeight,
        fontSize = fontSize
    )
}

@Composable
private fun LabeledMoneyLine(
    label: String,
    amount: Long,
    centered: Boolean = false,
    fontWeight: FontWeight? = null,
    fontSize: TextUnit = TextUnit.Unspecified
) {
    Text(
        text = "$label ${amount.asToman()}",
        modifier = Modifier.fillMaxWidth(),
        textAlign = if (centered) TextAlign.Center else TextAlign.Start,
        fontWeight = fontWeight,
        fontSize = fontSize
    )
}

private sealed interface LedgerFeedItem {
    val idKey: String
    val date: Long
    val amount: Long
    data class EntryItem(val entry: LedgerEntry) : LedgerFeedItem {
        override val idKey = "e${entry.id}"
        override val date = entry.occurredAt
        override val amount = entry.amount
    }
    data class DebtItem(val debt: Debt) : LedgerFeedItem {
        override val idKey = "d${debt.id}"
        override val date = debt.occurredAt
        override val amount = debt.currentAmount
    }
}
'''
text = replace_between(
    text,
    '@OptIn(ExperimentalMaterial3Api::class)\n@Composable\nprivate fun MainScaffold',
    '@Composable\nprivate fun TransactionsScreen',
    main_block
)

# 2) Installment lifecycle is hardened in ReminderSupport below.

# 3) Comparison/analysis screen.
comparison_block = r'''@Composable
private fun ComparisonScreen(
    repo: LedgerRepository,
    refreshToken: Int,
    initialMetric: String = "درآمد و هزینه",
    initialMode: String = "ماه انتخابی",
    launchKey: Int = 0
) {
    val entries = remember(refreshToken) { repo.entries() }
    val paletteId = remember(refreshToken) { repo.setting("chart_palette", "green_red") }
    val now = PersianDate.nowParts()
    val currentRef = MonthRef(now.year, now.month, "")
    val currentSums = monthSums(entries, currentRef.key)
    val months24 = remember { PersianDate.lastMonths(24) }.reversed()
    var compareMode by rememberSaveable { mutableStateOf(initialMode) }
    var targetKey by rememberSaveable { mutableStateOf(months24.drop(1).firstOrNull()?.key ?: currentRef.key) }
    var analysisKey by rememberSaveable { mutableStateOf(currentRef.key) }
    var metric by rememberSaveable { mutableStateOf(if (initialMetric == "هر دو") "درآمد و هزینه" else initialMetric) }
    var averageMode by rememberSaveable { mutableStateOf("۳ ماهه") }
    var debtMonths by rememberSaveable { mutableIntStateOf(6) }
    var sortBy by rememberSaveable { mutableStateOf("مبلغ") }
    var descending by rememberSaveable { mutableStateOf(true) }
    var expandedGroup by rememberSaveable { mutableStateOf<String?>(null) }

    LaunchedEffect(launchKey) {
        metric = if (initialMetric == "هر دو") "درآمد و هزینه" else initialMetric
        compareMode = initialMode
        expandedGroup = null
    }

    val isObligation = metric == "بدهی" || metric == "قرض"
    val dataTypes = listOf("درآمد و هزینه", "درآمد", "هزینه", "بدهی", "قرض")
    val entryModes = listOf("ماه انتخابی", "میانگین‌ها", "دسته‌ها", "زیرمجموعه‌ها", "تگ‌ها")
    val obligationModes = listOf("روند ماهانه", "جزئیات")

    LazyColumn(Modifier.fillMaxSize(), contentPadding = PaddingValues(16.dp), verticalArrangement = Arrangement.spacedBy(16.dp)) {
        item {
            val title = when (metric) {
                "درآمد" -> "درآمد این ماه"
                "هزینه" -> "هزینه این ماه"
                "بدهی" -> "بدهی فعال"
                "قرض" -> "قرض داده‌شده"
                else -> "درآمد و هزینه این ماه"
            }
            SectionTitle(title)
            Card(Modifier.fillMaxWidth(), shape = RoundedCornerShape(20.dp)) {
                Column(Modifier.padding(14.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                    when (metric) {
                        "بدهی", "قرض" -> {
                            val kind = if (metric == "بدهی") ObligationKind.DEBT else ObligationKind.LOAN
                            val list = repo.debts(kind)
                            Text(list.sumOf { it.currentAmount }.asToman(), modifier = Modifier.fillMaxWidth(), textAlign = TextAlign.Center, fontSize = 22.sp, fontWeight = FontWeight.Bold)
                            Text("${list.size.toString().toPersianDigits()} مورد فعال", modifier = Modifier.fillMaxWidth(), textAlign = TextAlign.Center)
                        }
                        else -> {
                            val bars = metricBarsV2(currentSums, metric)
                            ColumnBarChart(listOf(ChartGroup("ماه جاری", bars)), paletteId, 230)
                            if (metric == "درآمد و هزینه") {
                                Text("مانده: ${(currentSums.first - currentSums.second).asToman()}", modifier = Modifier.fillMaxWidth(), textAlign = TextAlign.Center, fontWeight = FontWeight.Bold)
                            }
                        }
                    }
                }
            }
        }

        item {
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

        item {
            SectionTitle("نوع نمایش")
            LazyRow(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                items(if (isObligation) obligationModes else entryModes) { m ->
                    FilterChip(selected = compareMode == m, onClick = { compareMode = m; expandedGroup = null }, label = { Text(m) })
                }
            }
        }

        if (isObligation) {
            val kind = if (metric == "بدهی") ObligationKind.DEBT else ObligationKind.LOAN
            val label = if (metric == "بدهی") "بدهی" else "قرض"
            if (compareMode == "روند ماهانه") {
                item {
                    Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween, verticalAlignment = Alignment.CenterVertically) {
                        Text("بازه", fontWeight = FontWeight.SemiBold)
                        LazyRow(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                            items(listOf(3, 6, 12)) { count ->
                                FilterChip(selected = debtMonths == count, onClick = { debtMonths = count }, label = { Text("${count.toString().toPersianDigits()} ماه") })
                            }
                        }
                    }
                }
                item {
                    val refs = PersianDate.lastMonths(debtMonths)
                    val groups = refs.map { ref -> ChartGroup(PersianDate.monthLabel(ref), listOf(ChartBar(label, repo.debtTotalAt(PersianDate.endOfMonth(ref), kind)))) }
                    Card(Modifier.fillMaxWidth(), shape = RoundedCornerShape(20.dp)) {
                        Column(Modifier.padding(12.dp)) {
                            Text("روند ${label} در ${debtMonths.toString().toPersianDigits()} ماه اخیر", modifier = Modifier.fillMaxWidth(), textAlign = TextAlign.Start)
                            ColumnBarChart(groups, paletteId, 330)
                        }
                    }
                }
            } else {
                item { SortControlsV2(sortBy, { sortBy = it }, descending, { descending = it }) }
                val obligations = repo.debts(kind).let { list ->
                    val sorted = if (sortBy == "تاریخ") list.sortedBy { it.occurredAt } else list.sortedBy { it.currentAmount }
                    if (descending) sorted.reversed() else sorted
                }
                if (obligations.isEmpty()) {
                    item { EmptyState("مورد فعالی برای نمایش وجود ندارد.") }
                } else {
                    items(obligations, key = { "ob-${it.id}" }) { d ->
                        Card(Modifier.fillMaxWidth(), shape = RoundedCornerShape(16.dp)) {
                            Column(Modifier.padding(14.dp), verticalArrangement = Arrangement.spacedBy(5.dp)) {
                                Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                                    Text(d.name, fontWeight = FontWeight.Bold)
                                    Text(d.currentAmount.asToman(), fontWeight = FontWeight.Bold)
                                }
                                Text("ثبت: ${PersianDate.format(d.occurredAt)}", fontSize = 12.sp)
                                if (d.dueAt > 0) Text("سررسید: ${PersianDate.format(d.dueAt)}", fontSize = 12.sp)
                                if (d.note.isNotBlank()) Text(d.note, modifier = Modifier.fillMaxWidth(), textAlign = TextAlign.Start, fontSize = 12.sp)
                            }
                        }
                    }
                }
            }
        } else {
            when (compareMode) {
                "ماه انتخابی" -> {
                    item {
                        val targetRef = months24.firstOrNull { it.key == targetKey } ?: currentRef
                        DropdownSelector("ماه مقایسه", PersianDate.monthLabel(targetRef), months24.map { PersianDate.monthLabel(it) }) { chosen ->
                            months24.firstOrNull { PersianDate.monthLabel(it) == chosen }?.let { targetKey = it.key }
                        }
                    }
                    item {
                        val targetRef = months24.firstOrNull { it.key == targetKey } ?: currentRef
                        val target = monthSums(entries, targetRef.key)
                        Card(Modifier.fillMaxWidth(), shape = RoundedCornerShape(20.dp)) {
                            Column(Modifier.padding(12.dp)) {
                                ColumnBarChart(
                                    listOf(
                                        ChartGroup("ماه جاری", metricBarsV2(currentSums, metric)),
                                        ChartGroup(PersianDate.monthLabel(targetRef), metricBarsV2(target, metric))
                                    ), paletteId, 300
                                )
                            }
                        }
                    }
                }
                "میانگین‌ها" -> {
                    item {
                        LazyRow(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                            items(listOf("۳ ماهه", "۶ ماهه", "سال گذشته")) { item -> FilterChip(selected = averageMode == item, onClick = { averageMode = item }, label = { Text(item) }) }
                        }
                    }
                    item {
                        val target: Pair<Long, Long>
                        val label: String
                        if (averageMode == "سال گذشته") {
                            val lastYear = MonthRef(now.year - 1, now.month, "")
                            target = monthSums(entries, lastYear.key)
                            label = "ماه مشابه سال قبل"
                        } else {
                            val count = if (averageMode == "۳ ماهه") 3 else 6
                            val refs = (1..count).map { PersianDate.shiftMonth(currentRef, -it) }
                            val sums = refs.map { monthSums(entries, it.key) }
                            target = (sums.sumOf { it.first } / count) to (sums.sumOf { it.second } / count)
                            label = "میانگین $averageMode"
                        }
                        Card(Modifier.fillMaxWidth(), shape = RoundedCornerShape(20.dp)) {
                            Column(Modifier.padding(12.dp)) {
                                ColumnBarChart(
                                    listOf(
                                        ChartGroup("ماه جاری", metricBarsV2(currentSums, metric)),
                                        ChartGroup(label, metricBarsV2(target, metric))
                                    ), paletteId, 300
                                )
                            }
                        }
                    }
                }
                "دسته‌ها", "زیرمجموعه‌ها", "تگ‌ها" -> {
                    item {
                        val analysisRef = months24.firstOrNull { it.key == analysisKey } ?: currentRef
                        DropdownSelector("ماه تحلیل", PersianDate.monthLabel(analysisRef), months24.map { PersianDate.monthLabel(it) }) { chosen ->
                            months24.firstOrNull { PersianDate.monthLabel(it) == chosen }?.let { analysisKey = it.key }
                        }
                        Spacer(Modifier.height(10.dp))
                        SortControlsV2(sortBy, { sortBy = it }, descending, { descending = it })
                    }
                    val monthList = entries.filter { PersianDate.parts(it.occurredAt).key == analysisKey }
                    val typed = when (metric) {
                        "درآمد" -> monthList.filter { it.type == EntryType.INCOME }
                        "هزینه" -> monthList.filter { it.type == EntryType.EXPENSE }
                        else -> monthList
                    }
                    val groups = analysisGroupsV2(typed, compareMode).map { (label, list) ->
                        AnalysisGroupV2(
                            label = label,
                            income = list.filter { it.type == EntryType.INCOME }.sumOf { it.amount },
                            expense = list.filter { it.type == EntryType.EXPENSE }.sumOf { it.amount },
                            latestAt = list.maxOfOrNull { it.occurredAt } ?: 0L,
                            entries = list
                        )
                    }.let { rows ->
                        val sorted = if (sortBy == "تاریخ") rows.sortedBy { it.latestAt } else rows.sortedBy { it.valueFor(metric) }
                        if (descending) sorted.reversed() else sorted
                    }
                    if (groups.isEmpty()) {
                        item { EmptyState("برای این نوع نمایش داده‌ای در ماه انتخاب‌شده نیست.") }
                    } else {
                        item {
                            Card(Modifier.fillMaxWidth(), shape = RoundedCornerShape(20.dp)) {
                                Column(Modifier.padding(12.dp)) {
                                    ColumnBarChart(
                                        groups.take(8).map { g ->
                                            val bars = when (metric) {
                                                "درآمد" -> listOf(ChartBar("درآمد", g.income))
                                                "هزینه" -> listOf(ChartBar("هزینه", g.expense))
                                                else -> listOf(ChartBar("درآمد", g.income), ChartBar("هزینه", g.expense))
                                            }
                                            ChartGroup(g.label, bars)
                                        }, paletteId, 330
                                    )
                                }
                            }
                        }
                        item { Text("جزئیات", fontWeight = FontWeight.Bold, fontSize = 18.sp, modifier = Modifier.fillMaxWidth(), textAlign = TextAlign.Start) }
                        items(groups, key = { "grp-${it.label}" }) { g ->
                            Card(Modifier.fillMaxWidth().clickable { expandedGroup = if (expandedGroup == g.label) null else g.label }, shape = RoundedCornerShape(16.dp)) {
                                Column(Modifier.padding(14.dp), verticalArrangement = Arrangement.spacedBy(7.dp)) {
                                    Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween, verticalAlignment = Alignment.CenterVertically) {
                                        Column {
                                            Text(g.label, fontWeight = FontWeight.Bold)
                                            Text("${g.entries.size.toString().toPersianDigits()} تراکنش • آخرین: ${PersianDate.format(g.latestAt)}", fontSize = 11.sp)
                                        }
                                        Text(g.valueFor(metric).asToman(), fontWeight = FontWeight.Bold)
                                    }
                                    if (metric == "درآمد و هزینه") {
                                        Text("درآمد: ${g.income.asToman()}  •  هزینه: ${g.expense.asToman()}", fontSize = 12.sp)
                                    }
                                    Text(if (expandedGroup == g.label) "بستن جزئیات ▲" else "نمایش تراکنش‌ها ▼", fontSize = 11.sp)
                                    if (expandedGroup == g.label) {
                                        HorizontalDivider()
                                        g.entries.sortedByDescending { it.occurredAt }.forEachIndexed { index, e ->
                                            Row(Modifier.fillMaxWidth().padding(vertical = 5.dp), horizontalArrangement = Arrangement.SpaceBetween) {
                                                Column(Modifier.weight(1f)) {
                                                    Text("${e.type.titleFa} • ${PersianDate.format(e.occurredAt)}", fontSize = 12.sp, fontWeight = FontWeight.SemiBold)
                                                    val detail = listOf(e.category, e.subcategory, e.tags.joinToString(" #", prefix = if (e.tags.isEmpty()) "" else "#"), e.note).filter { it.isNotBlank() }.joinToString(" • ")
                                                    if (detail.isNotBlank()) Text(detail, fontSize = 11.sp, modifier = Modifier.fillMaxWidth(), textAlign = TextAlign.Start)
                                                }
                                                Text(e.amount.asToman(), fontSize = 12.sp, fontWeight = FontWeight.Bold)
                                            }
                                            if (index != g.entries.lastIndex) HorizontalDivider()
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        item { Spacer(Modifier.height(18.dp)) }
    }
}

private fun metricBarsV2(pair: Pair<Long, Long>, metric: String): List<ChartBar> = when (metric) {
    "درآمد" -> listOf(ChartBar("درآمد", pair.first))
    "هزینه" -> listOf(ChartBar("هزینه", pair.second))
    else -> listOf(ChartBar("درآمد", pair.first), ChartBar("هزینه", pair.second))
}

private fun analysisGroupsV2(entries: List<LedgerEntry>, mode: String): Map<String, List<LedgerEntry>> {
    return when (mode) {
        "دسته‌ها" -> entries.groupBy { it.category.ifBlank { "بدون دسته" } }
        "زیرمجموعه‌ها" -> entries.groupBy { it.subcategory.ifBlank { "بدون زیرمجموعه" } }
        else -> {
            val out = linkedMapOf<String, MutableList<LedgerEntry>>()
            entries.forEach { entry ->
                val tags = entry.tags.ifEmpty { listOf("بدون تگ") }
                tags.forEach { tag -> out.getOrPut(tag) { mutableListOf() }.add(entry) }
            }
            out
        }
    }
}

@Composable
private fun SortControlsV2(
    sortBy: String,
    onSortBy: (String) -> Unit,
    descending: Boolean,
    onDescending: (Boolean) -> Unit
) {
    Column(Modifier.fillMaxWidth(), verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Text("مرتب‌سازی", fontWeight = FontWeight.SemiBold, modifier = Modifier.fillMaxWidth(), textAlign = TextAlign.Start)
        LazyRow(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            items(listOf("مبلغ", "تاریخ")) { item -> FilterChip(selected = sortBy == item, onClick = { onSortBy(item) }, label = { Text(item) }) }
            item { FilterChip(selected = descending, onClick = { onDescending(true) }, label = { Text("کاهشی") }) }
            item { FilterChip(selected = !descending, onClick = { onDescending(false) }, label = { Text("افزایشی") }) }
        }
    }
}
'''
text = replace_between(
    text,
    '@Composable\nprivate fun ComparisonScreen',
    '@Composable\nprivate fun ColumnBarChart',
    comparison_block
)

# 4) Settings: accordion sections instead of one long always-open form.
settings_block = r'''@Composable
private fun SettingsScreen(repo: LedgerRepository, refreshToken: Int, onChanged: () -> Unit) {
    val context = LocalContext.current
    val entries = remember(refreshToken) { repo.entries() }
    val selectedTheme = remember(refreshToken) { repo.setting("theme_base", "lavender") }
    val isDark = remember(refreshToken) { repo.setting("theme_dark", "0") == "1" }
    val selectedPalette = remember(refreshToken) { repo.setting("chart_palette", "green_red") }
    val selectedFont = remember(refreshToken) { repo.setting("font_name", "Arial") }
    val selectedScale = remember(refreshToken) { repo.setting("font_scale", "1.0").toFloatOrNull() ?: 1f }
    val accounts = remember(refreshToken) { repo.accounts() }
    val members = remember(refreshToken) { repo.members() }
    val recurring = remember(refreshToken) { repo.recurringRules() }
    val installments = remember(refreshToken) { repo.installments() }
    val reminders = remember(refreshToken) { repo.reminders() }
    val bankImports = remember(refreshToken) { repo.bankImports("pending") }
    val customCategories = remember(refreshToken) { repo.customCategories() }
    val customTags = remember(refreshToken) { repo.customTags() }
    var openSection by rememberSaveable { mutableStateOf<String?>(null) }
    var status by remember { mutableStateOf<String?>(null) }
    var budgetText by remember(refreshToken) { mutableStateOf(repo.budget().takeIf { it > 0 }?.toString()?.toPersianDigits().orEmpty()) }
    var accountName by remember { mutableStateOf("") }
    var memberName by remember { mutableStateOf("") }
    var categoryType by remember { mutableStateOf(EntryType.EXPENSE) }
    var categoryName by remember { mutableStateOf("") }
    var subcategoryName by remember { mutableStateOf("") }
    var tagName by remember { mutableStateOf("") }
    var pinText by remember { mutableStateOf("") }

    val backupLauncher = rememberLauncherForActivityResult(ActivityResultContracts.CreateDocument("application/json")) { uri ->
        uri ?: return@rememberLauncherForActivityResult
        runCatching { context.contentResolver.openOutputStream(uri)?.use { it.write(repo.exportJson().toByteArray(Charsets.UTF_8)) } }
            .onSuccess { status = "بکاپ ذخیره شد. اگر Google Drive را انتخاب کرده باشید، فایل در فضای ابری شماست." }
            .onFailure { status = "خطا در ذخیره بکاپ: ${it.message}" }
    }
    val restoreLauncher = rememberLauncherForActivityResult(ActivityResultContracts.OpenDocument()) { uri ->
        uri ?: return@rememberLauncherForActivityResult
        runCatching {
            val json = context.contentResolver.openInputStream(uri)?.bufferedReader()?.use { it.readText() } ?: error("فایل خوانده نشد")
            repo.importJson(json)
            ReminderScheduler.scheduleAll(context)
        }.onSuccess { status = "بکاپ بازیابی شد."; onChanged() }.onFailure { status = "بازیابی ناموفق: ${it.message}" }
    }
    val xlsxLauncher = rememberLauncherForActivityResult(ActivityResultContracts.CreateDocument("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")) { uri ->
        uri ?: return@rememberLauncherForActivityResult
        runCatching { context.contentResolver.openOutputStream(uri)?.use { Exporters.writeExcel(entries, it) } }
            .onSuccess { status = "فایل Excel ذخیره شد." }.onFailure { status = "خطا در Excel: ${it.message}" }
    }
    val pdfLauncher = rememberLauncherForActivityResult(ActivityResultContracts.CreateDocument("application/pdf")) { uri ->
        uri ?: return@rememberLauncherForActivityResult
        runCatching { context.contentResolver.openOutputStream(uri)?.use { Exporters.writePdf(entries, it) } }
            .onSuccess { status = "فایل PDF ذخیره شد." }.onFailure { status = "خطا در PDF: ${it.message}" }
    }
    val notificationPermissionLauncher = rememberLauncherForActivityResult(ActivityResultContracts.RequestPermission()) { granted -> status = if (granted) "اجازه اعلان فعال شد." else "اجازه اعلان داده نشد." }

    val fontSizeLabel = fontSizeOptions.minByOrNull { kotlin.math.abs(selectedScale - it.second) }?.first ?: "معمولی"
    val themeLabel = themeBases.firstOrNull { it.id == selectedTheme }?.title ?: "یاسی"
    val paletteLabel = chartPalettes.firstOrNull { it.id == selectedPalette }?.title ?: "پیش‌فرض"

    Column(
        Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(10.dp), horizontalAlignment = Alignment.End
    ) {
        Text("برای تغییر هر بخش روی عنوان آن بزنید.", modifier = Modifier.fillMaxWidth(), textAlign = TextAlign.Start, fontSize = 12.sp)

        SettingsAccordionSection("ظاهر برنامه", "$themeLabel • ${if (isDark) "تیره" else "روشن"} • نمودار $paletteLabel", openSection == "appearance", { openSection = if (openSection == "appearance") null else "appearance" }) {
            Text("رنگ و پس‌زمینه", modifier = Modifier.fillMaxWidth(), textAlign = TextAlign.Start, fontWeight = FontWeight.SemiBold)
            LazyRow(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                items(themeBases) { t -> FilterChip(selected = selectedTheme == t.id, onClick = { repo.setSetting("theme_base", t.id); onChanged() }, label = { Text(t.title) }) }
            }
            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween, verticalAlignment = Alignment.CenterVertically) {
                Text("حالت تیره", fontWeight = FontWeight.SemiBold)
                Switch(checked = isDark, onCheckedChange = { repo.setSetting("theme_dark", if (it) "1" else "0"); onChanged() })
            }
            Text("رنگ نمودارها", modifier = Modifier.fillMaxWidth(), textAlign = TextAlign.Start, fontWeight = FontWeight.SemiBold)
            LazyRow(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                items(chartPalettes) { p -> FilterChip(selected = selectedPalette == p.id, onClick = { repo.setSetting("chart_palette", p.id); onChanged() }, label = { Text(p.title) }) }
            }
        }

        SettingsAccordionSection("فونت و اندازه نوشته", "$selectedFont • $fontSizeLabel", openSection == "font", { openSection = if (openSection == "font") null else "font" }) {
            DropdownSelector("فونت", selectedFont, fontOptions) { repo.setSetting("font_name", it); onChanged() }
            Text("فونت از فونت‌های نصب‌شده دستگاه استفاده می‌شود؛ اگر فونت موجود نباشد Android نزدیک‌ترین جایگزین را نمایش می‌دهد.", modifier = Modifier.fillMaxWidth(), textAlign = TextAlign.Start, fontSize = 11.sp)
            LazyRow(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                items(fontSizeOptions) { pair -> FilterChip(selected = kotlin.math.abs(selectedScale - pair.second) < 0.01f, onClick = { repo.setSetting("font_scale", pair.second.toString()); onChanged() }, label = { Text(pair.first) }) }
            }
        }

        SettingsAccordionSection("بودجه ماهانه", repo.budget().takeIf { it > 0 }?.asToman() ?: "تعیین نشده", openSection == "budget", { openSection = if (openSection == "budget") null else "budget" }) {
            OutlinedTextField(budgetText, { budgetText = it }, Modifier.fillMaxWidth(), label = { Text("بودجه به تومان") }, keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number), singleLine = true, textStyle = LocalTextStyle.current.copy(textAlign = TextAlign.Start))
            Button(onClick = { repo.setBudget(budgetText.toLongAmountOrNull() ?: 0L); status = "بودجه ذخیره شد."; onChanged() }) { Text("ذخیره بودجه") }
        }

        SettingsAccordionSection("بکاپ و انتقال اطلاعات", "بکاپ، بازیابی، Excel و PDF", openSection == "backup", { openSection = if (openSection == "backup") null else "backup" }) {
            Text("بکاپ شامل تراکنش‌ها، بدهی و قرض، حساب‌ها، دسته‌ها، تگ‌ها، تنظیمات، اقساط و یادآورهاست.", modifier = Modifier.fillMaxWidth(), textAlign = TextAlign.Start, fontSize = 12.sp)
            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                Button(modifier = Modifier.weight(1f), onClick = { backupLauncher.launch("KharjYar-Backup-${PersianDate.format(System.currentTimeMillis()).replace("/", "-")}.json") }) { Text("تهیه بکاپ") }
                OutlinedButton(modifier = Modifier.weight(1f), onClick = { restoreLauncher.launch(arrayOf("application/json", "text/plain", "*/*")) }) { Text("بازیابی") }
            }
            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                OutlinedButton(modifier = Modifier.weight(1f), onClick = { xlsxLauncher.launch("KharjYar-Transactions.xlsx") }) { Text("خروجی Excel") }
                OutlinedButton(modifier = Modifier.weight(1f), onClick = { pdfLauncher.launch("KharjYar-Report.pdf") }) { Text("خروجی PDF") }
            }
        }

        SettingsAccordionSection("اعلان بانکی و حساب‌ها", "${accounts.size.toString().toPersianDigits()} حساب • ${bankImports.size.toString().toPersianDigits()} پیام در انتظار", openSection == "bank", { openSection = if (openSection == "bank") null else "bank" }) {
            Text("با فعال‌کردن دسترسی اعلان‌ها، دخل و خرج اعلان‌های بانکی را فقط روی همین دستگاه بررسی می‌کند؛ داده‌ای به سرور ارسال نمی‌شود.", modifier = Modifier.fillMaxWidth(), textAlign = TextAlign.Start, fontSize = 12.sp)
            OutlinedButton(modifier = Modifier.fillMaxWidth(), onClick = {
                runCatching { context.startActivity(Intent(Settings.ACTION_NOTIFICATION_LISTENER_SETTINGS)) }
                    .onFailure { status = "باز کردن دسترسی اعلان‌ها ممکن نشد: ${it.message}" }
            }) { Text("دسترسی اعلان‌های بانکی") }
            if (bankImports.isNotEmpty()) {
                Text("صندوق بررسی بانکی (${bankImports.size.toString().toPersianDigits()})", modifier = Modifier.fillMaxWidth(), textAlign = TextAlign.Start, fontWeight = FontWeight.Bold)
                bankImports.take(12).forEach { item ->
                    Card(Modifier.fillMaxWidth(), shape = RoundedCornerShape(14.dp)) {
                        Column(Modifier.padding(12.dp), verticalArrangement = Arrangement.spacedBy(6.dp)) {
                            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) { Text(item.sender, fontWeight = FontWeight.Bold); Text(item.amount.asToman()) }
                            Text(item.body.take(220), modifier = Modifier.fillMaxWidth(), textAlign = TextAlign.Start, fontSize = 11.sp)
                            Row(horizontalArrangement = Arrangement.spacedBy(4.dp)) {
                                TextButton(onClick = { repo.save(LedgerEntry(type = EntryType.EXPENSE, amount = item.amount, category = "بانکی - بررسی نشده", subcategory = item.sender, tags = listOf("نیازمند دسته‌بندی"), note = item.body, occurredAt = item.occurredAt, accountName = accounts.firstOrNull()?.name ?: "حساب اصلی", source = "bank_import")); repo.updateBankImportStatus(item.id, "imported"); onChanged() }) { Text("هزینه") }
                                TextButton(onClick = { repo.save(LedgerEntry(type = EntryType.INCOME, amount = item.amount, category = "بانکی - بررسی نشده", subcategory = item.sender, tags = listOf("نیازمند دسته‌بندی"), note = item.body, occurredAt = item.occurredAt, accountName = accounts.firstOrNull()?.name ?: "حساب اصلی", source = "bank_import")); repo.updateBankImportStatus(item.id, "imported"); onChanged() }) { Text("درآمد") }
                                TextButton(onClick = { repo.updateBankImportStatus(item.id, "ignored"); onChanged() }) { Text("نادیده") }
                            }
                        }
                    }
                }
            }
            HorizontalDivider()
            accounts.forEach { a ->
                val accountEntries = entries.filter { it.accountName == a.name }
                val balance = a.openingBalance + accountEntries.filter { it.type == EntryType.INCOME }.sumOf { it.amount } - accountEntries.filter { it.type == EntryType.EXPENSE }.sumOf { it.amount }
                Row(Modifier.fillMaxWidth().padding(vertical = 4.dp), horizontalArrangement = Arrangement.SpaceBetween) {
                    Text("${a.icon} ${a.name} • ${a.type}")
                    Text(balance.asToman(), fontWeight = FontWeight.SemiBold)
                }
            }
            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp), verticalAlignment = Alignment.CenterVertically) {
                OutlinedTextField(accountName, { accountName = it }, Modifier.weight(1f), label = { Text("نام حساب جدید") }, singleLine = true, textStyle = LocalTextStyle.current.copy(textAlign = TextAlign.Start))
                OutlinedButton(onClick = { if (accountName.isNotBlank()) { repo.saveAccount(Account(name = accountName, icon = "🏦")); accountName = ""; onChanged() } }) { Text("افزودن") }
            }
        }

        SettingsAccordionSection("اعضای خانواده", "${members.size.toString().toPersianDigits()} عضو", openSection == "members", { openSection = if (openSection == "members") null else "members" }) {
            Text("در ثبت تراکنش می‌توانید مشخص کنید تراکنش مربوط به چه کسی است.", modifier = Modifier.fillMaxWidth(), textAlign = TextAlign.Start)
            Text(members.joinToString("  •  ") { it.name }, modifier = Modifier.fillMaxWidth(), textAlign = TextAlign.Start)
            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp), verticalAlignment = Alignment.CenterVertically) {
                OutlinedTextField(memberName, { memberName = it }, Modifier.weight(1f), label = { Text("نام عضو") }, singleLine = true, textStyle = LocalTextStyle.current.copy(textAlign = TextAlign.Start))
                OutlinedButton(onClick = { if (memberName.isNotBlank()) { repo.addMember(memberName); memberName = ""; onChanged() } }) { Text("افزودن") }
            }
        }

        SettingsAccordionSection("تراکنش‌های تکرارشونده", "${recurring.size.toString().toPersianDigits()} مورد", openSection == "recurring", { openSection = if (openSection == "recurring") null else "recurring" }) {
            if (recurring.isEmpty()) EmptyState("تراکنش تکرارشونده‌ای ثبت نشده است.") else recurring.forEach { rule ->
                Card(Modifier.fillMaxWidth(), shape = RoundedCornerShape(14.dp)) {
                    Row(Modifier.fillMaxWidth().padding(12.dp), horizontalArrangement = Arrangement.SpaceBetween, verticalAlignment = Alignment.CenterVertically) {
                        Column { Text("${rule.type.titleFa}: ${rule.category}", fontWeight = FontWeight.Bold); Text("${rule.frequency.titleFa} • بعدی ${PersianDate.format(rule.nextRunAt)}", fontSize = 11.sp) }
                        TextButton(onClick = { repo.deleteRecurring(rule.id); onChanged() }) { Text("حذف") }
                    }
                }
            }
        }

        SettingsAccordionSection("اقساط و یادآورها", "${installments.size.toString().toPersianDigits()} قسط • ${reminders.count { it.enabled && it.kind != ReminderKind.INSTALLMENT }.toString().toPersianDigits()} یادآور", openSection == "reminders", { openSection = if (openSection == "reminders") null else "reminders" }) {
            if (installments.isEmpty() && reminders.none { it.enabled && it.kind != ReminderKind.INSTALLMENT }) EmptyState("قسط یا یادآوری ثبت‌شده‌ای ندارید.")
            installments.forEach { plan ->
                Card(Modifier.fillMaxWidth(), colors = CardDefaults.cardColors(containerColor = if (isDark) Color(0xFF49371D) else DebtSoftLight), shape = RoundedCornerShape(14.dp)) {
                    Column(Modifier.padding(12.dp), verticalArrangement = Arrangement.spacedBy(6.dp)) {
                        Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) { Text("قسط: ${plan.title}", fontWeight = FontWeight.Bold); Text(plan.installmentAmount.asToman()) }
                        Text("${plan.remainingCount.toString().toPersianDigits()} قسط باقی‌مانده • سررسید بعدی ${PersianDate.format(plan.nextDueAt)}", fontSize = 12.sp)
                        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                            TextButton(onClick = { ReminderScheduler.cancelInstallment(context, plan.id); repo.advanceInstallment(plan); ReminderScheduler.scheduleAll(context); onChanged() }) { Text("این قسط پرداخت شد") }
                            TextButton(onClick = { ReminderScheduler.cancelInstallment(context, plan.id); repo.deleteInstallment(plan.id); onChanged() }) { Text("حذف") }
                        }
                    }
                }
            }
            reminders.filter { it.enabled && it.kind != ReminderKind.INSTALLMENT }.take(10).forEach { r ->
                Row(Modifier.fillMaxWidth().padding(vertical = 5.dp), horizontalArrangement = Arrangement.SpaceBetween, verticalAlignment = Alignment.CenterVertically) {
                    Column(Modifier.weight(1f)) { Text("🔔 ${r.title}", fontWeight = FontWeight.SemiBold); Text("هشدار ${PersianDate.formatDateTime(r.remindAt)}", fontSize = 11.sp) }
                    TextButton(onClick = { ReminderScheduler.cancel(context, r.id); repo.deleteReminder(r.id); onChanged() }) { Text("حذف") }
                }
            }
            OutlinedButton(modifier = Modifier.fillMaxWidth(), onClick = {
                if (Build.VERSION.SDK_INT >= 33) notificationPermissionLauncher.launch(Manifest.permission.POST_NOTIFICATIONS) else status = "در این نسخه Android نیازی به مجوز جداگانه اعلان نیست."
            }) { Text("بررسی / فعال‌سازی اجازه نوتیفیکیشن") }
            OutlinedButton(modifier = Modifier.fillMaxWidth(), onClick = {
                runCatching {
                    context.startActivity(Intent(Settings.ACTION_CHANNEL_NOTIFICATION_SETTINGS).apply {
                        putExtra(Settings.EXTRA_APP_PACKAGE, context.packageName)
                        putExtra(Settings.EXTRA_CHANNEL_ID, ReminderScheduler.CHANNEL_ID)
                    })
                }.onFailure { status = "تنظیمات صدای یادآور باز نشد: ${it.message}" }
            }) { Text("تنظیم صدای یادآورها") }
        }

        SettingsAccordionSection("قفل و امنیت", if (repo.setting("pin_enabled", "0") == "1" || repo.setting("biometric_enabled", "0") == "1") "فعال" else "غیرفعال", openSection == "security", { openSection = if (openSection == "security") null else "security" }) {
            OutlinedTextField(pinText, { pinText = it.filter(Char::isDigit).take(8) }, Modifier.fillMaxWidth(), label = { Text("PIN چهار تا هشت رقمی") }, visualTransformation = PasswordVisualTransformation(), keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.NumberPassword), singleLine = true, textStyle = LocalTextStyle.current.copy(textAlign = TextAlign.Center))
            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                Button(modifier = Modifier.weight(1f), onClick = { if (pinText.length < 4) status = "PIN باید حداقل ۴ رقم باشد." else { val salt = newPinSalt(); repo.setSetting("pin_salt", salt); repo.setSetting("pin_hash", securePinHash(pinText, salt)); repo.setSetting("pin_enabled", "1"); pinText = ""; status = "قفل PIN فعال شد."; onChanged() } }) { Text("فعال‌سازی PIN") }
                OutlinedButton(modifier = Modifier.weight(1f), onClick = { repo.setSetting("pin_enabled", "0"); repo.setSetting("pin_hash", ""); repo.setSetting("pin_salt", ""); repo.setSetting("biometric_enabled", "0"); status = "قفل غیرفعال شد."; onChanged() }) { Text("خاموش کردن") }
            }
            val biometricAvailable = remember { BiometricManager.from(context).canAuthenticate(BiometricManager.Authenticators.BIOMETRIC_STRONG or BiometricManager.Authenticators.DEVICE_CREDENTIAL) == BiometricManager.BIOMETRIC_SUCCESS }
            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween, verticalAlignment = Alignment.CenterVertically) {
                Column(Modifier.weight(1f)) { Text("اثر انگشت / قفل دستگاه", fontWeight = FontWeight.SemiBold); Text(if (biometricAvailable) "روی این دستگاه قابل استفاده است." else "در دسترس نیست.", fontSize = 11.sp) }
                Switch(checked = repo.setting("biometric_enabled", "0") == "1", enabled = biometricAvailable, onCheckedChange = { repo.setSetting("biometric_enabled", if (it) "1" else "0"); onChanged() })
            }
        }

        SettingsAccordionSection("دسته‌ها و تگ‌ها", "${customCategories.size.toString().toPersianDigits()} دسته سفارشی • ${customTags.size.toString().toPersianDigits()} تگ", openSection == "taxonomy", { openSection = if (openSection == "taxonomy") null else "taxonomy" }) {
            Text("دسته و زیرمجموعه سفارشی", fontWeight = FontWeight.Bold, modifier = Modifier.fillMaxWidth(), textAlign = TextAlign.Start)
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                FilterChip(selected = categoryType == EntryType.EXPENSE, onClick = { categoryType = EntryType.EXPENSE }, label = { Text("هزینه") })
                FilterChip(selected = categoryType == EntryType.INCOME, onClick = { categoryType = EntryType.INCOME }, label = { Text("درآمد") })
            }
            OutlinedTextField(categoryName, { categoryName = it }, Modifier.fillMaxWidth(), label = { Text("نام دسته") }, singleLine = true, textStyle = LocalTextStyle.current.copy(textAlign = TextAlign.Start))
            OutlinedTextField(subcategoryName, { subcategoryName = it }, Modifier.fillMaxWidth(), label = { Text("زیرمجموعه (اختیاری)") }, singleLine = true, textStyle = LocalTextStyle.current.copy(textAlign = TextAlign.Start))
            Button(onClick = { if (categoryName.isNotBlank()) { repo.addCategory(categoryType, categoryName, subcategoryName); categoryName = ""; subcategoryName = ""; onChanged() } }) { Text("افزودن دسته") }
            if (customCategories.isNotEmpty()) Text(customCategories.joinToString("\n") { "• ${it.type.titleFa}: ${it.name}${if (it.subcategory.isBlank()) "" else " ← ${it.subcategory}"}" }, modifier = Modifier.fillMaxWidth(), textAlign = TextAlign.Start)
            HorizontalDivider()
            Text("تگ سفارشی", fontWeight = FontWeight.Bold, modifier = Modifier.fillMaxWidth(), textAlign = TextAlign.Start)
            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp), verticalAlignment = Alignment.CenterVertically) {
                OutlinedTextField(tagName, { tagName = it }, Modifier.weight(1f), label = { Text("نام تگ") }, singleLine = true, textStyle = LocalTextStyle.current.copy(textAlign = TextAlign.Start))
                OutlinedButton(onClick = { if (tagName.isNotBlank()) { repo.addTag(tagName); tagName = ""; onChanged() } }) { Text("افزودن") }
            }
            if (customTags.isNotEmpty()) Text(customTags.joinToString("  ") { "#$it" }, modifier = Modifier.fillMaxWidth(), textAlign = TextAlign.Start)
        }

        SettingsAccordionSection("درباره برنامه", "نسخه آزمایشی ۱.۰.۵", openSection == "about", { openSection = if (openSection == "about") null else "about" }) {
            Text("دخل و خرج برای مدیریت آفلاین درآمد، هزینه و تعهدات مالی ساخته شده است.", modifier = Modifier.fillMaxWidth(), textAlign = TextAlign.Start)
            Text("توسعه‌دهنده: hutoto-147", fontWeight = FontWeight.SemiBold, modifier = Modifier.fillMaxWidth(), textAlign = TextAlign.Start)
            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                OutlinedButton(onClick = { openUrlSafely(context, "https://github.com/hutoto-147/KharjYar") { status = it } }, modifier = Modifier.weight(1f)) { Text("GitHub") }
                OutlinedButton(onClick = { openUrlSafely(context, "https://github.com/hutoto-147/KharjYar/issues") { status = it } }, modifier = Modifier.weight(1f)) { Text("گزارش مشکل") }
            }
            OutlinedButton(modifier = Modifier.fillMaxWidth(), onClick = { openUrlSafely(context, "https://hutoto-147.github.io/KharjYar/privacy.html") { status = it } }) { Text("سیاست حریم خصوصی") }
        }

        status?.let { Card(Modifier.fillMaxWidth(), colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant)) { Text(it, Modifier.padding(12.dp), textAlign = TextAlign.Start) } }
        Spacer(Modifier.height(28.dp))
    }
}

@Composable
private fun SettingsAccordionSection(
    title: String,
    summary: String,
    expanded: Boolean,
    onToggle: () -> Unit,
    content: @Composable ColumnScope.() -> Unit
) {
    Card(Modifier.fillMaxWidth(), shape = RoundedCornerShape(18.dp)) {
        Column(Modifier.fillMaxWidth()) {
            Row(
                Modifier.fillMaxWidth().clickable(onClick = onToggle).padding(horizontal = 16.dp, vertical = 14.dp),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Column(Modifier.weight(1f)) {
                    Text(title, fontWeight = FontWeight.Bold, fontSize = 17.sp)
                    if (summary.isNotBlank()) Text(summary, fontSize = 11.sp, color = MaterialTheme.colorScheme.onSurfaceVariant)
                }
                Text(if (expanded) "▲" else "▼", fontSize = 13.sp)
            }
            if (expanded) {
                HorizontalDivider()
                Column(Modifier.fillMaxWidth().padding(14.dp), verticalArrangement = Arrangement.spacedBy(10.dp), content = content)
            }
        }
    }
}
'''
text = replace_between(
    text,
    '@Composable\nprivate fun SettingsScreen',
    'private fun <I> ActivityResultLauncher<I>.launchSafely',
    settings_block
)

# ColumnScope is required by the accordion content receiver.
if 'import androidx.compose.foundation.layout.ColumnScope\n' not in text:
    anchor = 'import androidx.compose.foundation.layout.Column\n'
    if anchor not in text:
        fail('Column import anchor not found')
    text = text.replace(anchor, anchor + 'import androidx.compose.foundation.layout.ColumnScope\n', 1)

MAIN.write_text(text, encoding='utf-8')

# 5) Reminder scheduler: one alarm per installment and migration of legacy duplicate reminder rows.
reminder_text = r'''package com.example.kharjyar
import android.Manifest
import android.app.AlarmManager
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.media.AudioAttributes
import android.media.RingtoneManager
import android.os.Build
import androidx.core.app.NotificationCompat
import androidx.core.app.NotificationManagerCompat
import kotlin.math.absoluteValue

object ReminderScheduler {
    const val CHANNEL_ID = "dakhl_kharj_reminders_v2"
    private const val EXTRA_TITLE = "title"
    private const val EXTRA_NOTE = "note"
    private const val EXTRA_ID = "notification_id"
    private const val INSTALLMENT_ID_BASE = 1_000_000L

    fun schedule(context: Context, item: ReminderItem) {
        if (!item.enabled || item.remindAt <= 0L) return
        val alarm = context.getSystemService(Context.ALARM_SERVICE) as AlarmManager
        val notificationId = (item.id.takeIf { it != 0L } ?: item.title.hashCode().toLong()).toInt().absoluteValue
        val intent = Intent(context, ReminderReceiver::class.java).apply {
            putExtra(EXTRA_TITLE, item.title)
            putExtra(EXTRA_NOTE, item.note.ifBlank { "سررسید: ${PersianDate.formatDateTime(item.dueAt)}" })
            putExtra(EXTRA_ID, notificationId)
        }
        val pending = PendingIntent.getBroadcast(
            context,
            notificationId,
            intent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )
        if (Build.VERSION.SDK_INT >= 31 && alarm.canScheduleExactAlarms()) {
            alarm.setExactAndAllowWhileIdle(AlarmManager.RTC_WAKEUP, item.remindAt, pending)
        } else if (Build.VERSION.SDK_INT < 31) {
            alarm.setExactAndAllowWhileIdle(AlarmManager.RTC_WAKEUP, item.remindAt, pending)
        } else {
            alarm.setAndAllowWhileIdle(AlarmManager.RTC_WAKEUP, item.remindAt, pending)
        }
    }

    fun cancel(context: Context, id: Long) {
        val alarm = context.getSystemService(Context.ALARM_SERVICE) as AlarmManager
        val requestCode = id.toInt().absoluteValue
        val pending = PendingIntent.getBroadcast(
            context,
            requestCode,
            Intent(context, ReminderReceiver::class.java),
            PendingIntent.FLAG_NO_CREATE or PendingIntent.FLAG_IMMUTABLE
        ) ?: return
        alarm.cancel(pending)
        pending.cancel()
    }

    fun cancelInstallment(context: Context, planId: Long) = cancel(context, INSTALLMENT_ID_BASE + planId)

    private fun scheduleInstallment(context: Context, plan: InstallmentPlan) {
        if (!plan.enabled || plan.remainingCount <= 0) {
            cancelInstallment(context, plan.id)
            return
        }
        val remindAt = PersianDate.withTime(
            PersianDate.addDays(plan.nextDueAt, -plan.reminderDaysBefore),
            plan.reminderHour,
            plan.reminderMinute
        )
        schedule(
            context,
            ReminderItem(
                id = INSTALLMENT_ID_BASE + plan.id,
                title = "قسط: ${plan.title}",
                note = "${plan.installmentAmount.asToman()} • سررسید ${PersianDate.formatDateTime(plan.nextDueAt)}",
                kind = ReminderKind.INSTALLMENT,
                dueAt = plan.nextDueAt,
                remindAt = remindAt,
                linkedId = plan.id
            )
        )
    }

    fun scheduleAll(context: Context) {
        val repo = LedgerRepository(context)
        repo.reminders()
            .filter { it.enabled && it.kind != ReminderKind.INSTALLMENT && it.remindAt > System.currentTimeMillis() }
            .forEach { schedule(context, it) }
        // Iterating all plans also cancels any alarm left by a just-completed final installment.
        repo.installments().forEach { scheduleInstallment(context, it) }
    }
}

class ReminderReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        createChannel(context)
        val title = intent.getStringExtra("title") ?: "یادآوری دخل و خرج"
        val note = intent.getStringExtra("note") ?: "یک سررسید ثبت‌شده دارید."
        val id = intent.getIntExtra("notification_id", title.hashCode().absoluteValue)
        if (Build.VERSION.SDK_INT >= 33 && context.checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS) != PackageManager.PERMISSION_GRANTED) return
        val openIntent = Intent(context, MainActivity::class.java)
        val contentPending = PendingIntent.getActivity(context, id, openIntent, PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE)
        val sound = RingtoneManager.getDefaultUri(RingtoneManager.TYPE_NOTIFICATION)
        val notification = NotificationCompat.Builder(context, ReminderScheduler.CHANNEL_ID)
            .setSmallIcon(R.drawable.ic_dakhl_kharj_notification_v2)
            .setContentTitle(title)
            .setContentText(note)
            .setStyle(NotificationCompat.BigTextStyle().bigText(note))
            .setAutoCancel(true)
            .setSound(sound)
            .setVibrate(longArrayOf(0, 250, 120, 250))
            .setPriority(NotificationCompat.PRIORITY_HIGH)
            .setCategory(NotificationCompat.CATEGORY_REMINDER)
            .setContentIntent(contentPending)
            .build()
        NotificationManagerCompat.from(context).notify(id, notification)
    }

    private fun createChannel(context: Context) {
        if (Build.VERSION.SDK_INT >= 26) {
            val manager = context.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
            val sound = RingtoneManager.getDefaultUri(RingtoneManager.TYPE_NOTIFICATION)
            val audioAttributes = AudioAttributes.Builder()
                .setUsage(AudioAttributes.USAGE_NOTIFICATION_COMMUNICATION_INSTANT)
                .setContentType(AudioAttributes.CONTENT_TYPE_SONIFICATION)
                .build()
            val channel = NotificationChannel(ReminderScheduler.CHANNEL_ID, "یادآوری‌های دخل و خرج", NotificationManager.IMPORTANCE_HIGH).apply {
                description = "اقساط، بدهی‌ها، قرض‌ها، چک‌ها و یادداشت‌های سررسیددار"
                setSound(sound, audioAttributes)
                enableVibration(true)
                vibrationPattern = longArrayOf(0, 250, 120, 250)
            }
            manager.createNotificationChannel(channel)
        }
    }
}

class BootReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        if (intent.action == Intent.ACTION_BOOT_COMPLETED || intent.action == Intent.ACTION_MY_PACKAGE_REPLACED) {
            ReminderScheduler.scheduleAll(context)
        }
    }
}
'''
REMINDER.write_text(reminder_text, encoding='utf-8')

# 6) V5 identity/version + stable DEBUG signing. Release remains secret-based.
if not GRADLE.exists():
    fail('app/build.gradle.kts not found')
gradle = GRADLE.read_text(encoding='utf-8')
if 'applicationId = "io.github.hutoto147.dakhlokharj"' not in gradle:
    fail('Expected release/1.0.0 applicationId was not found. Sync release/1.0.0 first.')
gradle = gradle.replace('versionCode = 1', 'versionCode = 5', 1)
gradle = gradle.replace('versionName = "1.0.0"', 'versionName = "1.0.5"', 1)

sign_anchor = '    signingConfigs {\n        if (\n'
if sign_anchor not in gradle:
    fail('release/1.0.0 signingConfigs anchor not found')
stable_signing = '''    signingConfigs {
        // Public development key for io.github.hutoto147.dakhlokharj.debug only.
        // V5+ debug APKs can update each other; never use this key for Play release.
        create("stableDebug") {
            storeFile = file("kharjyar-v5-debug.keystore")
            storePassword = "kharjyar-v5-debug"
            keyAlias = "kharjyar-debug"
            keyPassword = "kharjyar-v5-debug"
        }
        if (
'''
gradle = gradle.replace(sign_anchor, stable_signing, 1)

debug_anchor = '''        getByName("debug") {
            // Debug builds can coexist with the public app and cannot overwrite it.
            applicationIdSuffix = ".debug"
            versionNameSuffix = "-debug"
'''
if debug_anchor not in gradle:
    fail('debug buildType anchor not found')
gradle = gradle.replace(debug_anchor, debug_anchor + '            signingConfig = signingConfigs.getByName("stableDebug")\n', 1)
GRADLE.write_text(gradle, encoding='utf-8')
print('DakhlKharj V5 update applied successfully.')
print(f'Updated: {MAIN.relative_to(ROOT)}')
print(f'Updated: {REMINDER.relative_to(ROOT)}')
print(f'Updated: {GRADLE.relative_to(ROOT)}')
