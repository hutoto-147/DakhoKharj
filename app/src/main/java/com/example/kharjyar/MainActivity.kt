package com.example.kharjyar

import android.Manifest
import android.app.Activity
import android.content.Intent
import android.net.Uri
import android.content.pm.PackageManager
import android.graphics.Typeface
import android.os.Build
import android.os.Bundle
import android.provider.Settings
import android.widget.Toast
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.compose.setContent
import androidx.activity.result.ActivityResultLauncher
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.animation.AnimatedContent
import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.animateContentSize
import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.animation.core.tween
import androidx.compose.animation.expandVertically
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.animation.shrinkVertically
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ColumnScope
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxHeight
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.layout.widthIn
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.CenterAlignedTopAppBar
import androidx.compose.material3.Checkbox
import androidx.compose.material3.DropdownMenu
import androidx.compose.material3.DropdownMenuItem
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.FilterChip
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.LocalTextStyle
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Surface
import androidx.compose.material3.Switch
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.material3.TopAppBarDefaults
import androidx.compose.material3.Typography
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.CompositionLocalProvider
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.luminance
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.platform.LocalLayoutDirection
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.text.style.TextDirection
import androidx.compose.ui.unit.Density
import androidx.compose.ui.unit.LayoutDirection
import androidx.compose.ui.unit.TextUnit
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.core.content.ContextCompat
import androidx.biometric.BiometricManager
import androidx.biometric.BiometricPrompt
import androidx.fragment.app.FragmentActivity
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import java.security.MessageDigest
import java.security.SecureRandom
import java.util.Base64
import javax.crypto.SecretKeyFactory
import javax.crypto.spec.PBEKeySpec
import kotlin.math.roundToInt

private val IncomeSoftLight = Color(0xFFE2F4E8)
private val ExpenseSoftLight = Color(0xFFFBE2E7)
private val BalanceSoftLight = Color(0xFFE1ECFA)
private val DebtSoftLight = Color(0xFFFFF0D6)
private val LoanSoftLight = Color(0xFFE9E5FA)
private val IncomeStrong = Color(0xFF4E9B6A)
private val ExpenseStrong = Color(0xFFD87584)
private val DebtStrong = Color(0xFFD49A38)
private val LoanStrong = Color(0xFF7866B0)

private data class ThemeBase(
    val id: String,
    val title: String,
    val lightTop: Color,
    val lightBottom: Color,
    val lightSurface: Color,
    val lightNav: Color,
    val darkTop: Color,
    val darkBottom: Color,
    val darkSurface: Color,
    val darkNav: Color,
    val primary: Color
)

private val themeBases = listOf(
    ThemeBase("lavender", "یاسی", Color(0xFFFFFAFF), Color(0xFFF4EFFA), Color(0xFFF5F0F7), Color(0xFFF0EAF7), Color(0xFF211C27), Color(0xFF17141C), Color(0xFF2A2430), Color(0xFF251F2C), Color(0xFF795CB9)),
    ThemeBase("mist", "آبی", Color(0xFFF2FAFF), Color(0xFFDCEFFA), Color(0xFFE5F3FA), Color(0xFFD9EBF6), Color(0xFF18232B), Color(0xFF10191F), Color(0xFF202E37), Color(0xFF1B2830), Color(0xFF397FAE)),
    ThemeBase("mint", "سبز", Color(0xFFF2FFF7), Color(0xFFDDF4E6), Color(0xFFE5F5EB), Color(0xFFD8EEDF), Color(0xFF17241C), Color(0xFF101A14), Color(0xFF203026), Color(0xFF1A291F), Color(0xFF3F8D60)),
    ThemeBase("peach", "هلویی", Color(0xFFFFFCFA), Color(0xFFFBF0E9), Color(0xFFFAF3EE), Color(0xFFF7ECE5), Color(0xFF291F1A), Color(0xFF1D1612), Color(0xFF332720), Color(0xFF2C211B), Color(0xFFB57355)),
    ThemeBase("sand", "کرم", Color(0xFFFFFEF9), Color(0xFFF7F3E5), Color(0xFFF8F5EA), Color(0xFFF1EDDE), Color(0xFF27251B), Color(0xFF1A1912), Color(0xFF302E22), Color(0xFF29271D), Color(0xFF8B7A47))
)

private data class VisualTheme(
    val id: String,
    val title: String,
    val top: Color,
    val bottom: Color,
    val surface: Color,
    val nav: Color,
    val primary: Color,
    val isDark: Boolean
)

private fun visualTheme(baseId: String, dark: Boolean): VisualTheme {
    val b = themeBases.firstOrNull { it.id == baseId } ?: themeBases.first()
    return VisualTheme(
        id = b.id,
        title = b.title,
        top = if (dark) b.darkTop else b.lightTop,
        bottom = if (dark) b.darkBottom else b.lightBottom,
        surface = if (dark) b.darkSurface else b.lightSurface,
        nav = if (dark) b.darkNav else b.lightNav,
        primary = b.primary,
        isDark = dark
    )
}

private data class ChartPalette(val id: String, val title: String, val income: Color, val expense: Color, val other: Color)
private val chartPalettes = listOf(
    ChartPalette("green_red", "سبز ـ قرمز", Color(0xFF65A97C), Color(0xFFD97C89), Color(0xFF7186B7)),
    ChartPalette("blue_yellow", "آبی ـ زرد", Color(0xFF5B8FBE), Color(0xFFD7AC54), Color(0xFF8A77B8)),
    ChartPalette("purple_teal", "بنفش ـ فیروزه‌ای", Color(0xFF8468B4), Color(0xFF58A3A0), Color(0xFFD08B67)),
    ChartPalette("navy_orange", "سرمه‌ای ـ نارنجی", Color(0xFF526D9E), Color(0xFFD79255), Color(0xFF6D9B75)),
    ChartPalette("teal_pink", "سبزآبی ـ صورتی", Color(0xFF4C9C95), Color(0xFFD879A2), Color(0xFF8B78BC))
)

private val fontOptions = listOf("Arial", "Times New Roman", "Vazir", "B Nazanin", "IRANSans")
private val fontSizeOptions = listOf("خیلی کوچک" to 0.85f, "کوچک" to 0.93f, "معمولی" to 1f, "بزرگ" to 1.12f, "خیلی بزرگ" to 1.25f)

private fun systemFontFamily(name: String): FontFamily = FontFamily(Typeface.create(name, Typeface.NORMAL))

private fun typographyFor(family: FontFamily): Typography {
    val base = Typography()
    return Typography(
        displayLarge = base.displayLarge.copy(fontFamily = family), displayMedium = base.displayMedium.copy(fontFamily = family), displaySmall = base.displaySmall.copy(fontFamily = family),
        headlineLarge = base.headlineLarge.copy(fontFamily = family), headlineMedium = base.headlineMedium.copy(fontFamily = family), headlineSmall = base.headlineSmall.copy(fontFamily = family),
        titleLarge = base.titleLarge.copy(fontFamily = family), titleMedium = base.titleMedium.copy(fontFamily = family), titleSmall = base.titleSmall.copy(fontFamily = family),
        bodyLarge = base.bodyLarge.copy(fontFamily = family), bodyMedium = base.bodyMedium.copy(fontFamily = family), bodySmall = base.bodySmall.copy(fontFamily = family),
        labelLarge = base.labelLarge.copy(fontFamily = family), labelMedium = base.labelMedium.copy(fontFamily = family), labelSmall = base.labelSmall.copy(fontFamily = family)
    )
}

class MainActivity : FragmentActivity() {
    private var biometricAuthenticated by mutableStateOf(false)

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            LedgerApp(
                biometricAuthenticated = biometricAuthenticated,
                requestBiometric = { requestBiometric() }
            )
        }
    }

    private fun requestBiometric() {
        val prompt = BiometricPrompt(this, ContextCompat.getMainExecutor(this), object : BiometricPrompt.AuthenticationCallback() {
            override fun onAuthenticationSucceeded(result: BiometricPrompt.AuthenticationResult) {
                biometricAuthenticated = true
            }
        })
        val info = BiometricPrompt.PromptInfo.Builder()
            .setTitle("ورود به دخل و خرج")
            .setSubtitle("با اثر انگشت یا قفل دستگاه وارد شوید")
            .setAllowedAuthenticators(BiometricManager.Authenticators.BIOMETRIC_STRONG or BiometricManager.Authenticators.DEVICE_CREDENTIAL)
            .build()
        runCatching { prompt.authenticate(info) }
    }
}

@Composable
private fun KharjYarTheme(theme: VisualTheme, fontName: String, fontScale: Float, content: @Composable () -> Unit) {
    val baseDensity = LocalDensity.current
    val family = remember(fontName) { systemFontFamily(fontName) }
    val colorScheme = if (theme.isDark) {
        darkColorScheme(primary = theme.primary, surface = theme.surface, background = theme.bottom, surfaceVariant = theme.surface)
    } else {
        lightColorScheme(primary = theme.primary, surface = theme.surface, background = theme.bottom, surfaceVariant = theme.surface)
    }
    CompositionLocalProvider(LocalDensity provides Density(baseDensity.density, fontScale)) {
        MaterialTheme(colorScheme = colorScheme, typography = typographyFor(family), content = content)
    }
}

private data class BottomTab(val title: String, val icon: String)

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun LedgerApp(biometricAuthenticated: Boolean, requestBiometric: () -> Unit) {
    val context = LocalContext.current
    val repo = remember { LedgerRepository(context) }
    var refreshToken by remember { mutableIntStateOf(0) }
    var showSplash by rememberSaveable { mutableStateOf(true) }
    var unlocked by rememberSaveable { mutableStateOf(false) }
    val lockEnabled = remember(refreshToken) { repo.setting("pin_enabled", "0") == "1" || repo.setting("biometric_enabled", "0") == "1" }
    val biometricEnabled = remember(refreshToken) { repo.setting("biometric_enabled", "0") == "1" }

    LaunchedEffect(Unit) {
        repo.materializeRecurring()
        ReminderScheduler.scheduleAll(context)
        delay(3000)
        showSplash = false
    }
    LaunchedEffect(biometricAuthenticated) { if (biometricAuthenticated) unlocked = true }

    val theme = visualTheme(
        repo.setting("theme_base", "lavender"),
        repo.setting("theme_dark", "0") == "1"
    )
    val fontName = repo.setting("font_name", "Arial")
    val fontScale = repo.setting("font_scale", "1.0").toFloatOrNull() ?: 1f

    KharjYarTheme(theme, fontName, fontScale) {
        CompositionLocalProvider(
            LocalLayoutDirection provides LayoutDirection.Rtl,
            LocalTextStyle provides LocalTextStyle.current.copy(textDirection = TextDirection.Rtl)
        ) {
            when {
                showSplash -> SplashScreen(theme)
                lockEnabled && !unlocked -> LockScreen(repo, biometricEnabled, requestBiometric) { unlocked = true }
                else -> MainScaffold(repo, refreshToken, theme, onRefresh = { refreshToken++ })
            }
        }
    }
}

@Composable
private fun SplashScreen(theme: VisualTheme) {
    var visible by remember { mutableStateOf(false) }
    LaunchedEffect(Unit) { visible = true }

    val alpha by animateFloatAsState(
        if (visible) 1f else 0f,
        animationSpec = tween(1000),
        label = "splashNameAlpha"
    )

    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(
                Brush.verticalGradient(
                    listOf(Color(0xFF0B4564), Color(0xFF052A42), Color(0xFF031C2E))
                )
            ),
        contentAlignment = Alignment.Center
    ) {
        Column(
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.spacedBy(8.dp),
            modifier = Modifier.graphicsLayer(alpha = alpha)
        ) {
            Text(
                "دخل و خرج",
                color = Color.White,
                fontSize = 42.sp,
                fontWeight = FontWeight.Bold
            )
            Text(
                "حساب ساده، تصمیم روشن",
                color = Color.White.copy(alpha = 0.84f),
                fontSize = 14.sp
            )
        }
    }
}

@Composable
private fun LockScreen(repo: LedgerRepository, biometricEnabled: Boolean, requestBiometric: () -> Unit, onUnlocked: () -> Unit) {
    var pin by remember { mutableStateOf("") }
    var error by remember { mutableStateOf(false) }
    Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
        Card(Modifier.fillMaxWidth().padding(28.dp), shape = RoundedCornerShape(24.dp)) {
            Column(Modifier.padding(22.dp), horizontalAlignment = Alignment.CenterHorizontally, verticalArrangement = Arrangement.spacedBy(14.dp)) {
                Text("🔐", fontSize = 38.sp)
                Text("ورود به دخل و خرج", fontSize = 24.sp, fontWeight = FontWeight.Bold)
                OutlinedTextField(
                    value = pin, onValueChange = { pin = it.filter(Char::isDigit).take(8); error = false },
                    label = { Text("PIN") }, keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.NumberPassword),
                    visualTransformation = PasswordVisualTransformation(), singleLine = true, modifier = Modifier.fillMaxWidth(),
                    isError = error, textStyle = LocalTextStyle.current.copy(textAlign = TextAlign.Center)
                )
                Button(modifier = Modifier.fillMaxWidth(), onClick = {
                    if (verifyPin(pin, repo)) onUnlocked() else error = true
                }) { Text("ورود") }
                if (biometricEnabled) OutlinedButton(modifier = Modifier.fillMaxWidth(), onClick = requestBiometric) { Text("ورود با اثر انگشت / قفل دستگاه") }
                if (error) Text("PIN صحیح نیست.", color = MaterialTheme.colorScheme.error)
            }
        }
    }
}

private fun sha256(text: String): String = MessageDigest.getInstance("SHA-256").digest(text.toByteArray()).joinToString("") { "%02x".format(it) }

private fun newPinSalt(): String {
    val bytes = ByteArray(16)
    SecureRandom().nextBytes(bytes)
    return Base64.getEncoder().encodeToString(bytes)
}

private fun securePinHash(pin: String, salt: String): String {
    val spec = PBEKeySpec(pin.toCharArray(), Base64.getDecoder().decode(salt), 120_000, 256)
    return try {
        Base64.getEncoder().encodeToString(SecretKeyFactory.getInstance("PBKDF2WithHmacSHA256").generateSecret(spec).encoded)
    } finally {
        spec.clearPassword()
    }
}

private fun verifyPin(pin: String, repo: LedgerRepository): Boolean {
    val stored = repo.setting("pin_hash", "")
    val salt = repo.setting("pin_salt", "")
    if (stored.isBlank()) return false
    return if (salt.isNotBlank()) securePinHash(pin, salt) == stored else sha256(pin) == stored
}

private data class AnalysisGroupV2(
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
@Composable
private fun TransactionsScreen(
    repo: LedgerRepository,
    refreshToken: Int,
    onEdit: (LedgerEntry) -> Unit,
    onEditDebt: (Debt) -> Unit,
    onDeleted: () -> Unit
) {
    val entries = remember(refreshToken) { repo.entries() }
    val obligations = remember(refreshToken) { repo.debts() }
    var query by rememberSaveable { mutableStateOf("") }
    var filter by rememberSaveable { mutableStateOf("همه") }
    var sortField by rememberSaveable { mutableStateOf("تاریخ") }
    var sortDirection by rememberSaveable { mutableStateOf("کاهشی") }
    var pendingDeleteEntry by remember { mutableStateOf<LedgerEntry?>(null) }
    var pendingDeleteDebt by remember { mutableStateOf<Debt?>(null) }
    val normalized = query.trim()

    val feed = buildList<LedgerFeedItem> {
        entries.filter { e ->
            val typeOk = when (filter) { "هزینه" -> e.type == EntryType.EXPENSE; "درآمد" -> e.type == EntryType.INCOME; "بدهی", "قرض" -> false; else -> true }
            val searchOk = normalized.isBlank() || listOf(e.category, e.subcategory, e.note, e.accountName, e.memberName, e.tags.joinToString(" ")).any { it.contains(normalized, true) }
            typeOk && searchOk
        }.forEach { add(LedgerFeedItem.EntryItem(it)) }
        obligations.filter { d ->
            val typeOk = when (filter) { "بدهی" -> d.kind == ObligationKind.DEBT; "قرض" -> d.kind == ObligationKind.LOAN; "همه" -> true; else -> false }
            val searchOk = normalized.isBlank() || d.name.contains(normalized, true) || d.note.contains(normalized, true)
            typeOk && searchOk
        }.forEach { add(LedgerFeedItem.DebtItem(it)) }
    }.let { items ->
        val comparator = if (sortField == "مبلغ") compareBy<LedgerFeedItem> { it.amount }.thenBy { it.date } else compareBy<LedgerFeedItem> { it.date }.thenBy { it.amount }
        if (sortDirection == "افزایشی") items.sortedWith(comparator) else items.sortedWith(comparator.reversed())
    }

    LazyColumn(Modifier.fillMaxSize(), contentPadding = PaddingValues(16.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
        item {
            OutlinedTextField(
                value = query, onValueChange = { query = it }, modifier = Modifier.fillMaxWidth(),
                label = { Text("جستجو در هزینه، درآمد، حساب، عضو یا توضیح") }, singleLine = true,
                textStyle = LocalTextStyle.current.copy(textAlign = TextAlign.Start)
            )
        }
        item {
            LazyRow(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                items(listOf("همه", "هزینه", "درآمد", "بدهی", "قرض")) { item ->
                    FilterChip(selected = filter == item, onClick = { filter = item }, label = { Text(item) })
                }
            }
        }
        item {
            Card(Modifier.fillMaxWidth(), shape = RoundedCornerShape(16.dp)) {
                Column(Modifier.padding(12.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                    Text("مرتب‌سازی", fontWeight = FontWeight.SemiBold)
                    Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                        Box(Modifier.weight(1f)) { DropdownSelector("بر اساس", sortField, listOf("تاریخ", "مبلغ")) { sortField = it } }
                        Box(Modifier.weight(1f)) { DropdownSelector("ترتیب", sortDirection, listOf("کاهشی", "افزایشی")) { sortDirection = it } }
                    }
                }
            }
        }
        if (feed.isEmpty()) item { EmptyState("موردی پیدا نشد.") }
        items(feed, key = { it.idKey }) { item ->
            when (item) {
                is LedgerFeedItem.EntryItem -> EntryCard(item.entry, onEdit = { onEdit(item.entry) }, onDelete = { pendingDeleteEntry = item.entry })
                is LedgerFeedItem.DebtItem -> DebtCard(item.debt, onEdit = { onEditDebt(item.debt) }, onDelete = { pendingDeleteDebt = item.debt })
            }
        }
    }

    pendingDeleteEntry?.let { e ->
        AlertDialog(onDismissRequest = { pendingDeleteEntry = null }, title = { Text("حذف تراکنش") }, text = { Text("این تراکنش حذف شود؟") },
            confirmButton = { TextButton(onClick = { repo.delete(e.id); pendingDeleteEntry = null; onDeleted() }) { Text("حذف") } },
            dismissButton = { TextButton(onClick = { pendingDeleteEntry = null }) { Text("انصراف") } })
    }
    pendingDeleteDebt?.let { d ->
        AlertDialog(onDismissRequest = { pendingDeleteDebt = null }, title = { Text("حذف ${d.kind.titleFa}") }, text = { Text("${d.name} حذف شود؟") },
            confirmButton = { TextButton(onClick = { repo.deleteDebt(d.id); pendingDeleteDebt = null; onDeleted() }) { Text("حذف") } },
            dismissButton = { TextButton(onClick = { pendingDeleteDebt = null }) { Text("انصراف") } })
    }
}

@Composable
private fun EntryCard(entry: LedgerEntry, onEdit: () -> Unit, onDelete: () -> Unit) {
    val dark = MaterialTheme.colorScheme.background.luminance() < 0.5f
    val bg = if (entry.type == EntryType.INCOME) { if (dark) Color(0xFF234130) else IncomeSoftLight } else { if (dark) Color(0xFF4A2830) else ExpenseSoftLight }
    val strong = if (entry.type == EntryType.INCOME) { if (dark) Color(0xFF8BD0A1) else IncomeStrong } else { if (dark) Color(0xFFF0A0AC) else ExpenseStrong }
    Card(Modifier.fillMaxWidth(), colors = CardDefaults.cardColors(containerColor = bg), shape = RoundedCornerShape(18.dp)) {
        Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(7.dp)) {
            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween, verticalAlignment = Alignment.CenterVertically) {
                Row(horizontalArrangement = Arrangement.spacedBy(9.dp), verticalAlignment = Alignment.CenterVertically) {
                    Box(Modifier.size(38.dp).clip(CircleShape).background(Color.White.copy(alpha = 0.55f)), contentAlignment = Alignment.Center) {
                        Text(Presets.categoryIcon(entry.category, entry.type), fontSize = 20.sp)
                    }
                    Column {
                        Text(entry.category, fontWeight = FontWeight.Bold, fontSize = 17.sp)
                        if (entry.subcategory.isNotBlank()) Text(entry.subcategory, fontSize = 12.sp)
                    }
                }
                MoneyText(
                    amount = entry.amount,
                    forcedSign = if (entry.type == EntryType.INCOME) "+" else "−",
                    color = strong,
                    fontWeight = FontWeight.Bold
                )
            }
            Text("${PersianDate.format(entry.occurredAt)}  •  ${entry.accountName}  •  ${entry.memberName}", modifier = Modifier.fillMaxWidth(), textAlign = TextAlign.Start, fontSize = 12.sp)
            if (entry.note.isNotBlank()) Text(entry.note, modifier = Modifier.fillMaxWidth(), textAlign = TextAlign.Start)
            if (entry.tags.isNotEmpty()) Text(entry.tags.joinToString("  ") { "#$it" }, modifier = Modifier.fillMaxWidth(), textAlign = TextAlign.Start, fontSize = 12.sp)
            Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) { TextButton(onClick = onEdit) { Text("ویرایش") }; TextButton(onClick = onDelete) { Text("حذف") } }
        }
    }
}

@Composable
private fun DebtCard(debt: Debt, onEdit: () -> Unit, onDelete: () -> Unit) {
    val isLoan = debt.kind == ObligationKind.LOAN
    val dark = MaterialTheme.colorScheme.background.luminance() < 0.5f
    val bg = if (isLoan) { if (dark) Color(0xFF332C4E) else LoanSoftLight } else { if (dark) Color(0xFF49371D) else DebtSoftLight }
    Card(Modifier.fillMaxWidth(), colors = CardDefaults.cardColors(containerColor = bg), shape = RoundedCornerShape(18.dp)) {
        Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(7.dp)) {
            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween, verticalAlignment = Alignment.CenterVertically) {
                Row(horizontalArrangement = Arrangement.spacedBy(8.dp), verticalAlignment = Alignment.CenterVertically) {
                    Text(if (isLoan) "🤝" else "📒", fontSize = 22.sp)
                    Column { Text(debt.name, fontWeight = FontWeight.Bold, fontSize = 17.sp); Text(debt.kind.titleFa, fontSize = 12.sp) }
                }
                MoneyText(debt.currentAmount, color = if (isLoan) LoanStrong else DebtStrong, fontWeight = FontWeight.Bold)
            }
            if (debt.dueAt > 0) Text("سررسید: ${PersianDate.format(debt.dueAt)}", modifier = Modifier.fillMaxWidth(), textAlign = TextAlign.Start)
            if (debt.note.isNotBlank()) Text(debt.note, modifier = Modifier.fillMaxWidth(), textAlign = TextAlign.Start)
            Row(horizontalArrangement = Arrangement.spacedBy(10.dp)) { TextButton(onClick = onEdit) { Text("ویرایش") }; TextButton(onClick = onDelete) { Text("حذف") } }
        }
    }
}

@Composable
private fun AddEntryScreen(
    repo: LedgerRepository,
    refreshToken: Int,
    editingEntry: LedgerEntry?,
    editingDebt: Debt?,
    onSaved: () -> Unit
) {
    val context = LocalContext.current
    val initialMode = when {
        editingDebt?.kind == ObligationKind.LOAN -> "قرض"
        editingDebt != null -> "بدهی"
        editingEntry?.type == EntryType.INCOME -> "درآمد"
        else -> "هزینه"
    }
    var mode by remember(editingEntry?.id, editingDebt?.id) { mutableStateOf(initialMode) }
    val entryType = if (mode == "درآمد") EntryType.INCOME else EntryType.EXPENSE
    val baseDate = editingEntry?.occurredAt ?: editingDebt?.occurredAt ?: System.currentTimeMillis()
    val baseParts = PersianDate.parts(baseDate)

    var amountText by remember(editingEntry?.id, editingDebt?.id) { mutableStateOf((editingEntry?.amount ?: editingDebt?.currentAmount)?.toString()?.formatAmountInput().orEmpty()) }
    var nameText by remember(editingDebt?.id) { mutableStateOf(editingDebt?.name.orEmpty()) }
    var note by remember(editingEntry?.id, editingDebt?.id) { mutableStateOf(editingEntry?.note ?: editingDebt?.note.orEmpty()) }
    var selectedYear by remember(editingEntry?.id, editingDebt?.id) { mutableIntStateOf(baseParts.year) }
    var selectedMonth by remember(editingEntry?.id, editingDebt?.id) { mutableIntStateOf(baseParts.month) }
    var selectedDay by remember(editingEntry?.id, editingDebt?.id) { mutableIntStateOf(baseParts.day) }
    var tagsExpanded by rememberSaveable { mutableStateOf(false) }
    var selectedTags by remember(editingEntry?.id) { mutableStateOf(editingEntry?.tags?.toSet() ?: emptySet()) }
    var customTag by remember { mutableStateOf("") }
    var addReminder by rememberSaveable { mutableStateOf(false) }
    var reminderOffset by rememberSaveable { mutableIntStateOf(3) }
    var customReminderDate by rememberSaveable { mutableStateOf("") }
    var reminderHour by rememberSaveable { mutableIntStateOf(9) }
    var reminderMinute by rememberSaveable { mutableIntStateOf(0) }
    var recurring by rememberSaveable { mutableStateOf(false) }
    var recurrence by rememberSaveable { mutableStateOf(RecurrenceFrequency.MONTHLY) }
    var status by remember { mutableStateOf<String?>(null) }

    val categories = remember(refreshToken, entryType) { Presets.mergedCategories(entryType, repo.customCategories(entryType)) }
    var category by remember(editingEntry?.id, entryType) {
        mutableStateOf(
            editingEntry?.category?.let { if (it == "رفت‌وآمد") "خودرو و تردد" else it }
                ?: categories.keys.firstOrNull().orEmpty()
        )
    }
    LaunchedEffect(entryType, categories.keys) { if (category !in categories.keys) category = categories.keys.firstOrNull().orEmpty() }
    var subcategory by remember(editingEntry?.id, category) { mutableStateOf(editingEntry?.subcategory?.takeIf { it in (categories[category] ?: emptyList()) } ?: categories[category]?.firstOrNull().orEmpty()) }
    val accounts = remember(refreshToken) { repo.accounts() }
    val members = remember(refreshToken) { repo.members() }
    var accountName by remember(editingEntry?.id) { mutableStateOf(editingEntry?.accountName ?: accounts.firstOrNull()?.name.orEmpty()) }
    var memberName by remember(editingEntry?.id) { mutableStateOf(editingEntry?.memberName ?: members.firstOrNull()?.name.orEmpty()) }
    val allTags = remember(refreshToken) { (Presets.defaultTags + repo.customTags()).distinct() }

    var installmentTitle by remember { mutableStateOf("") }
    var installmentCount by remember { mutableStateOf("") }
    var reminderKind by remember { mutableStateOf(ReminderKind.INSTALLMENT) }

    val years = PersianDate.selectableYears(2, 1)
    val days = (1..PersianDate.daysInMonth(selectedYear, selectedMonth)).toList()
    LaunchedEffect(selectedYear, selectedMonth) {
        if (selectedDay !in days) selectedDay = days.last()
    }

    val notificationPermissionLauncher = rememberLauncherForActivityResult(ActivityResultContracts.RequestPermission()) { }

    Column(
        modifier = Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(14.dp), horizontalAlignment = Alignment.End
    ) {
        SectionTitle("نوع ثبت")
        LazyRow(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            items(listOf("هزینه", "درآمد", "بدهی", "قرض", "یادآور/قسط")) { item ->
                FilterChip(selected = mode == item, onClick = { if (editingEntry == null && editingDebt == null) mode = item }, label = { Text(item) })
            }
        }

        if (mode == "هزینه" || mode == "درآمد") {
            OutlinedTextField(
                value = amountText, onValueChange = { amountText = it.formatAmountInput() }, modifier = Modifier.fillMaxWidth(),
                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number), singleLine = true,
                label = { Text("مبلغ به تومان") }, textStyle = LocalTextStyle.current.copy(textAlign = TextAlign.Start)
            )
            DropdownSelector("دسته", category, categories.keys.toList()) { category = it; subcategory = categories[it]?.firstOrNull().orEmpty() }
            val subs = categories[category].orEmpty()
            if (entryType == EntryType.INCOME && category in Presets.incomeNameableCategories) {
                OutlinedTextField(
                    value = if (subcategory == "نام دلخواه") "" else subcategory,
                    onValueChange = { subcategory = it },
                    modifier = Modifier.fillMaxWidth(),
                    label = { Text("نام منبع درآمد") },
                    placeholder = { Text("مثلاً پروژه طراحی، فروشگاه، قرض از علی") },
                    singleLine = true,
                    textStyle = LocalTextStyle.current.copy(textAlign = TextAlign.Start)
                )
            } else if (subs.isNotEmpty()) {
                DropdownSelector("زیرمجموعه", subcategory, subs) { subcategory = it }
            }
            DropdownSelector("حساب", accountName, accounts.map { "${it.icon} ${it.name}" }) { selected -> accountName = selected.substringAfter(" ") }
            DropdownSelector("عضو / هزینه مشترک", memberName, members.map { it.name }) { memberName = it }

            SectionTitle("تاریخ تراکنش")
            Text("برای وارد کردن تراکنش ماه‌های قبل، ماه و سال را جداگانه انتخاب کنید.", modifier = Modifier.fillMaxWidth(), textAlign = TextAlign.Start, fontSize = 12.sp)
            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                Box(Modifier.weight(1f)) { DropdownSelector("سال", selectedYear.toString().toPersianDigits(), years.map { it.toString().toPersianDigits() }) { selectedYear = it.toEnglishDigits().toInt() } }
                Box(Modifier.weight(1f)) { DropdownSelector("ماه", PersianDate.monthNames[selectedMonth - 1], PersianDate.monthNames) { selectedMonth = PersianDate.monthNames.indexOf(it) + 1 } }
                Box(Modifier.weight(0.75f)) { DropdownSelector("روز", selectedDay.toString().toPersianDigits(), days.map { it.toString().toPersianDigits() }) { selectedDay = it.toEnglishDigits().toInt() } }
            }

            Card(Modifier.fillMaxWidth().clickable { tagsExpanded = !tagsExpanded }, shape = RoundedCornerShape(14.dp)) {
                Row(Modifier.fillMaxWidth().padding(14.dp), horizontalArrangement = Arrangement.SpaceBetween) {
                    Text("تگ‌ها (اختیاری)", fontWeight = FontWeight.SemiBold)
                    Text(if (tagsExpanded) "▲" else "▼")
                }
            }
            if (tagsExpanded) {
                LazyRow(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    items(allTags) { tag -> FilterChip(selected = tag in selectedTags, onClick = { selectedTags = if (tag in selectedTags) selectedTags - tag else selectedTags + tag }, label = { Text("#$tag") }) }
                }
                Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp), verticalAlignment = Alignment.CenterVertically) {
                    OutlinedTextField(customTag, { customTag = it }, Modifier.weight(1f), label = { Text("تگ جدید") }, singleLine = true, textStyle = LocalTextStyle.current.copy(textAlign = TextAlign.Start))
                    OutlinedButton(onClick = { val t = customTag.trim().removePrefix("#"); if (t.isNotBlank()) { repo.addTag(t); selectedTags = selectedTags + t; customTag = "" } }) { Text("افزودن") }
                }
            }

            OutlinedTextField(note, { note = it }, Modifier.fillMaxWidth().height(110.dp), label = { Text("یادداشت / توضیح (اختیاری)") }, textStyle = LocalTextStyle.current.copy(textAlign = TextAlign.Start))

            Card(Modifier.fillMaxWidth(), shape = RoundedCornerShape(16.dp)) {
                Column(Modifier.padding(14.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                    Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween, verticalAlignment = Alignment.CenterVertically) {
                        Text("تراکنش تکرارشونده", fontWeight = FontWeight.SemiBold)
                        Switch(checked = recurring, onCheckedChange = { recurring = it })
                    }
                    if (recurring) LazyRow(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                        items(RecurrenceFrequency.entries) { f -> FilterChip(selected = recurrence == f, onClick = { recurrence = f }, label = { Text(f.titleFa) }) }
                    }
                }
            }

            ReminderEditor(addReminder, { addReminder = it }, reminderOffset, { reminderOffset = it }, customReminderDate, { customReminderDate = it }, reminderHour, { reminderHour = it }, reminderMinute, { reminderMinute = it })

            Button(modifier = Modifier.fillMaxWidth(), onClick = {
                val amount = amountText.toLongAmountOrNull()
                val date = PersianDate.dateForParts(selectedYear, selectedMonth, selectedDay)
                if (amount == null || amount <= 0) { status = "مبلغ معتبر وارد کنید."; return@Button }
                if (date == null) { status = "تاریخ انتخاب‌شده معتبر نیست."; return@Button }
                val saved = LedgerEntry(
                    id = editingEntry?.id ?: 0L, type = entryType, amount = amount, category = category, subcategory = subcategory,
                    tags = selectedTags.toList(), note = note.trim(), occurredAt = date, createdAt = editingEntry?.createdAt ?: System.currentTimeMillis(),
                    accountName = accountName, memberName = memberName, source = editingEntry?.source ?: "manual"
                )
                repo.save(saved)
                if (recurring && editingEntry == null) repo.saveRecurring(RecurringRule(type = entryType, amount = amount, category = category, subcategory = subcategory, note = note, accountName = accountName, memberName = memberName, frequency = recurrence, dayOfMonth = selectedDay, nextRunAt = when (recurrence) { RecurrenceFrequency.WEEKLY -> PersianDate.addDays(date, 7); RecurrenceFrequency.MONTHLY -> PersianDate.addMonths(date, 1); RecurrenceFrequency.YEARLY -> PersianDate.addMonths(date, 12) }))
                if (addReminder) {
                    val remindAt = reminderTime(date, reminderOffset, customReminderDate, reminderHour, reminderMinute)
                    val rid = repo.saveReminder(ReminderItem(title = "${entryType.titleFa}: $category", note = note, kind = ReminderKind.GENERAL, dueAt = date, remindAt = remindAt))
                    repo.reminders().firstOrNull { it.id == rid }?.let { ReminderScheduler.schedule(context, it) }
                    if (Build.VERSION.SDK_INT >= 33 && context.checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS) != PackageManager.PERMISSION_GRANTED) notificationPermissionLauncher.launchSafely(Manifest.permission.POST_NOTIFICATIONS) { status = it }
                }
                onSaved()
            }) { Text(if (editingEntry == null) "ثبت ${entryType.titleFa}" else "ذخیره تغییرات") }
        } else if (mode == "بدهی" || mode == "قرض") {
            val kind = if (mode == "قرض") ObligationKind.LOAN else ObligationKind.DEBT
            OutlinedTextField(nameText, { nameText = it }, Modifier.fillMaxWidth(), label = { Text(if (kind == ObligationKind.LOAN) "نام فرد / موضوع قرض" else "نام بدهی / طلبکار") }, singleLine = true, textStyle = LocalTextStyle.current.copy(textAlign = TextAlign.Start))
            OutlinedTextField(amountText, { amountText = it.formatAmountInput() }, Modifier.fillMaxWidth(), label = { Text("مانده فعلی به تومان") }, keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number), singleLine = true, textStyle = LocalTextStyle.current.copy(textAlign = TextAlign.Start))
            SectionTitle("تاریخ شروع / ثبت")
            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                Box(Modifier.weight(1f)) { DropdownSelector("سال", selectedYear.toString().toPersianDigits(), years.map { it.toString().toPersianDigits() }) { selectedYear = it.toEnglishDigits().toInt() } }
                Box(Modifier.weight(1f)) { DropdownSelector("ماه", PersianDate.monthNames[selectedMonth - 1], PersianDate.monthNames) { selectedMonth = PersianDate.monthNames.indexOf(it) + 1 } }
                Box(Modifier.weight(0.75f)) { DropdownSelector("روز", selectedDay.toString().toPersianDigits(), days.map { it.toString().toPersianDigits() }) { selectedDay = it.toEnglishDigits().toInt() } }
            }
            OutlinedTextField(note, { note = it }, Modifier.fillMaxWidth().height(105.dp), label = { Text("یادداشت") }, textStyle = LocalTextStyle.current.copy(textAlign = TextAlign.Start))
            ReminderEditor(addReminder, { addReminder = it }, reminderOffset, { reminderOffset = it }, customReminderDate, { customReminderDate = it }, reminderHour, { reminderHour = it }, reminderMinute, { reminderMinute = it }, title = "یادآوری سررسید")
            Button(modifier = Modifier.fillMaxWidth(), onClick = {
                val amount = amountText.toLongAmountOrNull()
                val date = PersianDate.dateForParts(selectedYear, selectedMonth, selectedDay)
                if (nameText.isBlank() || amount == null || amount <= 0 || date == null) { status = "نام، مبلغ و تاریخ را کامل کنید."; return@Button }
                val dueAt = if (addReminder) date else editingDebt?.dueAt ?: 0L
                val remindAt = if (addReminder) reminderTime(dueAt, reminderOffset, customReminderDate, reminderHour, reminderMinute) else 0L
                val id = repo.saveDebt(Debt(id = editingDebt?.id ?: 0L, name = nameText, originalAmount = editingDebt?.originalAmount ?: amount, currentAmount = amount, note = note, occurredAt = date, kind = kind, dueAt = dueAt, reminderAt = remindAt))
                if (addReminder) {
                    val rid = repo.saveReminder(ReminderItem(title = "${kind.titleFa}: $nameText", note = note, kind = if (kind == ObligationKind.LOAN) ReminderKind.LOAN else ReminderKind.DEBT, dueAt = dueAt, remindAt = remindAt, linkedId = id))
                    repo.reminders().firstOrNull { it.id == rid }?.let { ReminderScheduler.schedule(context, it) }
                    if (Build.VERSION.SDK_INT >= 33 && context.checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS) != PackageManager.PERMISSION_GRANTED) notificationPermissionLauncher.launchSafely(Manifest.permission.POST_NOTIFICATIONS) { status = it }
                }
                onSaved()
            }) { Text(if (editingDebt == null) "ثبت ${kind.titleFa}" else "ذخیره تغییرات") }
        } else {
            SectionTitle("قسط، چک یا یادآوری")
            LazyRow(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                items(listOf(ReminderKind.INSTALLMENT, ReminderKind.CHECK, ReminderKind.GENERAL)) { k -> FilterChip(selected = reminderKind == k, onClick = { reminderKind = k }, label = { Text(k.titleFa) }) }
            }
            OutlinedTextField(installmentTitle, { installmentTitle = it }, Modifier.fillMaxWidth(), label = { Text("عنوان") }, singleLine = true, textStyle = LocalTextStyle.current.copy(textAlign = TextAlign.Start))
            OutlinedTextField(amountText, { amountText = it.formatAmountInput() }, Modifier.fillMaxWidth(), label = { Text(if (reminderKind == ReminderKind.INSTALLMENT) "مبلغ هر قسط" else "مبلغ (اختیاری)") }, keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number), singleLine = true, textStyle = LocalTextStyle.current.copy(textAlign = TextAlign.Start))
            if (reminderKind == ReminderKind.INSTALLMENT) OutlinedTextField(installmentCount, { installmentCount = it }, Modifier.fillMaxWidth(), label = { Text("تعداد اقساط باقی‌مانده") }, keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number), singleLine = true, textStyle = LocalTextStyle.current.copy(textAlign = TextAlign.Start))
            SectionTitle("سررسید")
            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                Box(Modifier.weight(1f)) { DropdownSelector("سال", selectedYear.toString().toPersianDigits(), years.map { it.toString().toPersianDigits() }) { selectedYear = it.toEnglishDigits().toInt() } }
                Box(Modifier.weight(1f)) { DropdownSelector("ماه", PersianDate.monthNames[selectedMonth - 1], PersianDate.monthNames) { selectedMonth = PersianDate.monthNames.indexOf(it) + 1 } }
                Box(Modifier.weight(0.75f)) { DropdownSelector("روز", selectedDay.toString().toPersianDigits(), days.map { it.toString().toPersianDigits() }) { selectedDay = it.toEnglishDigits().toInt() } }
            }
            OutlinedTextField(note, { note = it }, Modifier.fillMaxWidth().height(100.dp), label = { Text("یادداشت") }, textStyle = LocalTextStyle.current.copy(textAlign = TextAlign.Start))
            ReminderEditor(true, {}, reminderOffset, { reminderOffset = it }, customReminderDate, { customReminderDate = it }, reminderHour, { reminderHour = it }, reminderMinute, { reminderMinute = it }, title = "زمان هشدار", showSwitch = false)
            Button(modifier = Modifier.fillMaxWidth(), onClick = {
                val dueAt = PersianDate.dateForParts(selectedYear, selectedMonth, selectedDay)
                if (installmentTitle.isBlank() || dueAt == null) { status = "عنوان و تاریخ سررسید را کامل کنید."; return@Button }
                val remindAt = reminderTime(dueAt, reminderOffset, customReminderDate, reminderHour, reminderMinute)
                if (reminderKind == ReminderKind.INSTALLMENT) {
                    val amount = amountText.toLongAmountOrNull() ?: 0L
                    val count = installmentCount.toEnglishDigits().toIntOrNull() ?: 1
                    val id = repo.saveInstallment(InstallmentPlan(title = installmentTitle, installmentAmount = amount, remainingCount = count.coerceAtLeast(1), nextDueAt = dueAt, accountName = accountName.ifBlank { "حساب اصلی" }, note = note, reminderDaysBefore = reminderOffset.coerceAtLeast(0), reminderHour = reminderHour, reminderMinute = reminderMinute))
                    ReminderScheduler.schedule(context, ReminderItem(id = 1_000_000L + id, title = "قسط: $installmentTitle", note = note, kind = ReminderKind.INSTALLMENT, dueAt = dueAt, remindAt = remindAt, linkedId = id))
                } else {
                    val rid = repo.saveReminder(ReminderItem(title = installmentTitle, note = note, kind = reminderKind, dueAt = dueAt, remindAt = remindAt))
                    repo.reminders().firstOrNull { it.id == rid }?.let { ReminderScheduler.schedule(context, it) }
                }
                if (Build.VERSION.SDK_INT >= 33 && context.checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS) != PackageManager.PERMISSION_GRANTED) notificationPermissionLauncher.launchSafely(Manifest.permission.POST_NOTIFICATIONS) { status = it }
                onSaved()
            }) { Text("ثبت و تنظیم هشدار") }
        }

        status?.let { Text(it, color = MaterialTheme.colorScheme.error, modifier = Modifier.fillMaxWidth(), textAlign = TextAlign.Start) }
        Spacer(Modifier.height(30.dp))
    }
}

@Composable
private fun ReminderEditor(
    enabled: Boolean,
    onEnabled: (Boolean) -> Unit,
    offset: Int,
    onOffset: (Int) -> Unit,
    customDate: String,
    onCustomDate: (String) -> Unit,
    hour: Int,
    onHour: (Int) -> Unit,
    minute: Int,
    onMinute: (Int) -> Unit,
    title: String = "یادآوری",
    showSwitch: Boolean = true
) {
    Card(Modifier.fillMaxWidth().animateContentSize(), shape = RoundedCornerShape(16.dp)) {
        Column(Modifier.padding(14.dp), verticalArrangement = Arrangement.spacedBy(9.dp)) {
            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween, verticalAlignment = Alignment.CenterVertically) {
                Text(title, fontWeight = FontWeight.SemiBold)
                if (showSwitch) Switch(checked = enabled, onCheckedChange = onEnabled)
            }
            AnimatedVisibility(visible = enabled, enter = fadeIn() + expandVertically(), exit = fadeOut() + shrinkVertically()) {
                Column(verticalArrangement = Arrangement.spacedBy(9.dp)) {
                    LazyRow(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                        items(listOf(7 to "یک هفته قبل", 3 to "۳ روز قبل", 0 to "همان روز", -1 to "تاریخ دلخواه")) { pair ->
                            FilterChip(selected = offset == pair.first, onClick = { onOffset(pair.first) }, label = { Text(pair.second) })
                        }
                    }
                    if (offset == -1) OutlinedTextField(customDate, onCustomDate, Modifier.fillMaxWidth(), label = { Text("تاریخ هشدار: مثال ۱۴۰۵/۰۶/۱۰") }, singleLine = true, textStyle = LocalTextStyle.current.copy(textAlign = TextAlign.Start))
                    Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                        Box(Modifier.weight(1f)) { DropdownSelector("ساعت", hour.toString().padStart(2, '0').toPersianDigits(), (0..23).map { it.toString().padStart(2, '0').toPersianDigits() }) { onHour(it.toEnglishDigits().toInt()) } }
                        Box(Modifier.weight(1f)) { DropdownSelector("دقیقه", minute.toString().padStart(2, '0').toPersianDigits(), (0..59 step 5).map { it.toString().padStart(2, '0').toPersianDigits() }) { onMinute(it.toEnglishDigits().toInt()) } }
                    }
                    Text("هشدار در ساعت ${hour.toString().padStart(2, '0').toPersianDigits()}:${minute.toString().padStart(2, '0').toPersianDigits()} با صدای پیش‌فرض اعلان/پیام دستگاه نمایش داده می‌شود.", modifier = Modifier.fillMaxWidth(), textAlign = TextAlign.Start, fontSize = 11.sp)
                }
            }
        }
    }
}

private fun reminderTime(dueAt: Long, offset: Int, custom: String, hour: Int, minute: Int): Long {
    val base = if (offset == -1) PersianDate.parse(custom) ?: dueAt else PersianDate.addDays(dueAt, -offset)
    return PersianDate.withTime(base, hour, minute)
}

@Composable
private fun DropdownSelector(label: String, value: String, options: List<String>, onSelect: (String) -> Unit) {
    var expanded by remember { mutableStateOf(false) }
    Box(Modifier.fillMaxWidth()) {
        OutlinedButton(onClick = { expanded = true }, modifier = Modifier.fillMaxWidth()) {
            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) { Text(label); Text(value.ifBlank { "انتخاب کنید" }, fontWeight = FontWeight.SemiBold) }
        }
        DropdownMenu(expanded = expanded, onDismissRequest = { expanded = false }, modifier = Modifier.fillMaxWidth(0.78f)) {
            options.distinct().forEach { option -> DropdownMenuItem(text = { Text(option, modifier = Modifier.fillMaxWidth(), textAlign = TextAlign.Start) }, onClick = { onSelect(option); expanded = false }) }
        }
    }
}

private fun monthSums(entries: List<LedgerEntry>, monthKey: String): Pair<Long, Long> {
    val list = entries.filter { PersianDate.parts(it.occurredAt).key == monthKey }
    return list.filter { it.type == EntryType.INCOME }.sumOf { it.amount } to list.filter { it.type == EntryType.EXPENSE }.sumOf { it.amount }
}

@Composable
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
@Composable
private fun ColumnBarChart(groups: List<ChartGroup>, paletteId: String, chartHeight: Int) {
    val maxValue = groups.flatMap { it.bars }.maxOfOrNull { it.value }?.coerceAtLeast(1L) ?: 1L
    val scroll = rememberScrollState()
    Row(Modifier.fillMaxWidth().horizontalScroll(scroll).height(chartHeight.dp).padding(top = 12.dp), horizontalArrangement = Arrangement.spacedBy(18.dp), verticalAlignment = Alignment.Bottom) {
        groups.forEach { group ->
            Column(Modifier.widthIn(min = 88.dp), horizontalAlignment = Alignment.CenterHorizontally, verticalArrangement = Arrangement.Bottom) {
                Row(Modifier.height((chartHeight - 62).dp), horizontalArrangement = Arrangement.spacedBy(6.dp), verticalAlignment = Alignment.Bottom) {
                    group.bars.forEachIndexed { index, bar ->
                        val ratio = bar.value.toFloat() / maxValue.toFloat()
                        val maxBar = (chartHeight - 108).coerceAtLeast(100)
                        val barHeight = if (bar.value == 0L) 4.dp else (maxBar * ratio).coerceAtLeast(12f).dp
                        Column(horizontalAlignment = Alignment.CenterHorizontally, verticalArrangement = Arrangement.Bottom, modifier = Modifier.fillMaxHeight()) {
                            Text(bar.value.asCompactToman(), fontSize = 10.sp, textAlign = TextAlign.Center, modifier = Modifier.width(72.dp))
                            Spacer(Modifier.height(4.dp))
                            Box(Modifier.width(if (group.bars.size > 1) 34.dp else 46.dp).height(barHeight).clip(RoundedCornerShape(topStart = 8.dp, topEnd = 8.dp)).background(seriesColor(bar.label, index, paletteId)))
                        }
                    }
                }
                Text(group.label, textAlign = TextAlign.Center, fontSize = 11.sp, lineHeight = 14.sp, modifier = Modifier.widthIn(min = 78.dp, max = 135.dp))
            }
        }
    }
}

private fun seriesColor(label: String, index: Int, paletteId: String): Color {
    val p = chartPalettes.firstOrNull { it.id == paletteId } ?: chartPalettes.first()
    return when {
        label.contains("درآمد") -> p.income
        label.contains("هزینه") -> p.expense
        label.contains("بدهی") -> DebtStrong
        label.contains("قرض") -> LoanStrong
        index % 3 == 0 -> p.income
        index % 3 == 1 -> p.expense
        else -> p.other
    }
}

@Composable
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
private fun <I> ActivityResultLauncher<I>.launchSafely(input: I, onFailure: (String) -> Unit) {
    runCatching { launch(input) }.onFailure { onFailure("این قابلیت روی دستگاه باز نشد: ${it.message ?: "خطای نامشخص"}") }
}

private fun openUrlSafely(context: android.content.Context, url: String, onFailure: (String) -> Unit) {
    runCatching { context.startActivity(Intent(Intent.ACTION_VIEW, Uri.parse(url))) }
        .onFailure { onFailure("باز کردن لینک ممکن نشد: ${it.message ?: "خطای نامشخص"}") }
}

@Composable
private fun SectionTitle(text: String) {
    Text(text, modifier = Modifier.fillMaxWidth(), textAlign = TextAlign.Start, fontSize = 20.sp, fontWeight = FontWeight.Bold)
}

@Composable
private fun EmptyState(message: String) {
    Surface(Modifier.fillMaxWidth(), color = MaterialTheme.colorScheme.surfaceVariant, shape = RoundedCornerShape(14.dp)) {
        Text(message, Modifier.padding(16.dp).fillMaxWidth(), textAlign = TextAlign.Center)
    }
}
