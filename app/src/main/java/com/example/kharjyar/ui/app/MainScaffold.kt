package com.example.kharjyar.ui.app

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.CenterAlignedTopAppBar
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBarDefaults
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.sp
import com.example.kharjyar.AddEntryScreen
import com.example.kharjyar.ComparisonScreen
import com.example.kharjyar.DashboardScreen
import com.example.kharjyar.Debt
import com.example.kharjyar.LedgerEntry
import com.example.kharjyar.LedgerRepository
import com.example.kharjyar.ObligationKind
import com.example.kharjyar.SettingsScreen
import com.example.kharjyar.TransactionsScreen
import com.example.kharjyar.VisualTheme
import com.example.kharjyar.ui.components.KharjBottomBar

/**
 * Existing five-tab navigation and edit flow extracted from the old MainActivity.kt.
 * No business behavior is intentionally changed in this step.
 */
private data class BottomTab(
    val title: String,
    val icon: String
)

@OptIn(ExperimentalMaterial3Api::class)
@Composable
internal fun MainScaffold(
    repo: LedgerRepository,
    refreshToken: Int,
    theme: VisualTheme,
    onRefresh: () -> Unit
) {
    var selectedTab by rememberSaveable { mutableIntStateOf(0) }
    var editingEntry by remember { mutableStateOf<LedgerEntry?>(null) }
    var editingDebt by remember { mutableStateOf<Debt?>(null) }

    var comparisonMetric by rememberSaveable {
        mutableStateOf("درآمد و هزینه")
    }

    var comparisonMode by rememberSaveable {
        mutableStateOf("ماه انتخابی")
    }

    var comparisonLaunchKey by rememberSaveable {
        mutableIntStateOf(0)
    }

    fun openComparison(
        metric: String,
        mode: String
    ) {
        comparisonMetric = metric
        comparisonMode = mode
        comparisonLaunchKey++

        editingEntry = null
        editingDebt = null
        selectedTab = 3
    }

    val tabs = remember {
        listOf(
            BottomTab("خانه", "⌂"),
            BottomTab("تراکنش‌ها", "≡"),
            BottomTab("ثبت", "＋"),
            BottomTab("مقایسه", "▥"),
            BottomTab("تنظیمات", "⚙")
        )
    }

    val title = when {
        selectedTab == 2 && editingDebt != null -> {
            if (editingDebt?.kind == ObligationKind.LOAN) {
                "ویرایش قرض"
            } else {
                "ویرایش بدهی"
            }
        }

        selectedTab == 2 && editingEntry != null -> "ویرایش تراکنش"
        selectedTab == 0 -> "دخل و خرج"
        selectedTab == 1 -> "تراکنش‌ها"
        selectedTab == 2 -> "ثبت"
        selectedTab == 3 -> "مقایسه و تحلیل"
        else -> "تنظیمات"
    }

    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(
                Brush.verticalGradient(
                    listOf(theme.top, theme.bottom)
                )
            )
    ) {
        Scaffold(
            containerColor = Color.Transparent,
            topBar = {
                CenterAlignedTopAppBar(
                    title = { Text(title) },
                    colors = TopAppBarDefaults.centerAlignedTopAppBarColors(
                        containerColor = Color.Transparent
                    )
                )
            },
            bottomBar = {
                KharjBottomBar(
                    selectedIndex = selectedTab,
                    containerColor = theme.nav,
                    primaryColor = theme.primary,
                    onSelect = { index ->
                        if (index != 2) {
                            editingEntry = null
                            editingDebt = null
                        }
                        selectedTab = index
                    }
                )
            }
        ) { padding ->
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(padding)
            ) {
                when (selectedTab) {
                    0 -> {
                        DashboardScreen(
                            repo = repo,
                            refreshToken = refreshToken,
                            dark = theme.isDark,
                            onOpenComparison = ::openComparison
                        )
                    }

                    1 -> {
                        TransactionsScreen(
                            repo = repo,
                            refreshToken = refreshToken,
                            onEdit = {
                                editingEntry = it
                                editingDebt = null
                                selectedTab = 2
                            },
                            onEditDebt = {
                                editingDebt = it
                                editingEntry = null
                                selectedTab = 2
                            },
                            onDeleted = onRefresh
                        )
                    }

                    2 -> {
                        AddEntryScreen(
                            repo = repo,
                            refreshToken = refreshToken,
                            editingEntry = editingEntry,
                            editingDebt = editingDebt,
                            onSaved = {
                                editingEntry = null
                                editingDebt = null
                                onRefresh()
                                selectedTab = 1
                            }
                        )
                    }

                    3 -> {
                        ComparisonScreen(
                            repo = repo,
                            refreshToken = refreshToken,
                            initialMetric = comparisonMetric,
                            initialMode = comparisonMode,
                            launchKey = comparisonLaunchKey
                        )
                    }

                    else -> {
                        SettingsScreen(
                            repo = repo,
                            refreshToken = refreshToken,
                            onRefresh = onRefresh
                        )
                    }
                }
            }
        }
    }
}
