package com.example.kharjyar.ui.app

import androidx.compose.material3.LocalTextStyle
import androidx.compose.runtime.Composable
import androidx.compose.runtime.CompositionLocalProvider
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalLayoutDirection
import androidx.compose.ui.text.style.TextDirection
import androidx.compose.ui.unit.LayoutDirection
import com.example.kharjyar.KharjYarTheme
import com.example.kharjyar.LedgerRepository
import com.example.kharjyar.LockScreen
import com.example.kharjyar.ReminderScheduler
import com.example.kharjyar.SplashScreen
import com.example.kharjyar.visualTheme
import kotlinx.coroutines.delay

/**
 * Root Compose application.
 *
 * Existing behavior is intentionally preserved:
 * - Repository creation
 * - recurring transaction materialization
 * - reminder scheduling
 * - splash timing
 * - PIN / biometric lock
 * - theme / font settings
 * - RTL direction
 */
@Composable
fun LedgerApp(
    biometricAuthenticated: Boolean,
    requestBiometric: () -> Unit
) {
    val context = LocalContext.current
    val repo = remember { LedgerRepository(context) }

    var refreshToken by remember { mutableIntStateOf(0) }
    var showSplash by rememberSaveable { mutableStateOf(true) }
    var unlocked by rememberSaveable { mutableStateOf(false) }

    val lockEnabled = remember(refreshToken) {
        repo.setting("pin_enabled", "0") == "1" ||
            repo.setting("biometric_enabled", "0") == "1"
    }

    val biometricEnabled = remember(refreshToken) {
        repo.setting("biometric_enabled", "0") == "1"
    }

    LaunchedEffect(Unit) {
        repo.materializeRecurring()
        ReminderScheduler.scheduleAll(context)
        delay(3000)
        showSplash = false
    }

    LaunchedEffect(biometricAuthenticated) {
        if (biometricAuthenticated) {
            unlocked = true
        }
    }

    val theme = visualTheme(
        repo.setting("theme_base", "bank"),
        repo.setting("theme_dark", "0") == "1"
    )

    val fontName = repo.setting("font_name", "Arial")
    val fontScale = repo.setting("font_scale", "1.0").toFloatOrNull() ?: 1f

    KharjYarTheme(
        theme = theme,
        fontName = fontName,
        fontScale = fontScale
    ) {
        CompositionLocalProvider(
            LocalLayoutDirection provides LayoutDirection.Rtl,
            LocalTextStyle provides LocalTextStyle.current.copy(
                textDirection = TextDirection.Rtl
            )
        ) {
            when {
                showSplash -> {
                    SplashScreen(theme)
                }

                lockEnabled && !unlocked -> {
                    LockScreen(
                        repo = repo,
                        biometricEnabled = biometricEnabled,
                        requestBiometric = requestBiometric,
                        onUnlocked = { unlocked = true }
                    )
                }

                else -> {
                    MainScaffold(
                        repo = repo,
                        refreshToken = refreshToken,
                        theme = theme,
                        onRefresh = { refreshToken++ }
                    )
                }
            }
        }
    }
}
