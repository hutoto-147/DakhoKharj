package com.example.kharjyar

import android.os.Bundle
import androidx.activity.compose.setContent
import androidx.biometric.BiometricManager
import androidx.biometric.BiometricPrompt
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.core.content.ContextCompat
import androidx.fragment.app.FragmentActivity
import com.example.kharjyar.ui.app.LedgerApp

/**
 * Android entry point for DakhlKharj.
 *
 * Responsibilities intentionally kept here:
 * - Host Jetpack Compose.
 * - Own BiometricPrompt because it requires FragmentActivity.
 *
 * App-level Compose state, startup flow and navigation live in ui/app.
 */
class MainActivity : FragmentActivity() {

    private var biometricAuthenticated by mutableStateOf(false)

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        setContent {
            LedgerApp(
                biometricAuthenticated = biometricAuthenticated,
                requestBiometric = ::requestBiometric
            )
        }
    }

    private fun requestBiometric() {
        val prompt = BiometricPrompt(
            this,
            ContextCompat.getMainExecutor(this),
            object : BiometricPrompt.AuthenticationCallback() {
                override fun onAuthenticationSucceeded(
                    result: BiometricPrompt.AuthenticationResult
                ) {
                    super.onAuthenticationSucceeded(result)
                    biometricAuthenticated = true
                }
            }
        )

        val info = BiometricPrompt.PromptInfo.Builder()
            .setTitle("ورود به دخل و خرج")
            .setSubtitle("با اثر انگشت یا قفل دستگاه وارد شوید")
            .setAllowedAuthenticators(
                BiometricManager.Authenticators.BIOMETRIC_STRONG or
                    BiometricManager.Authenticators.DEVICE_CREDENTIAL
            )
            .build()

        runCatching {
            prompt.authenticate(info)
        }
    }
}
