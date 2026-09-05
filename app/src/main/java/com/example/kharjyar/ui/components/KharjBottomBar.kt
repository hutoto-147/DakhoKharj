package com.example.kharjyar.ui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.offset
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.kharjyar.ui.design.AppDesign

private data class NavItem(
    val title: String,
    val icon: String
)

private val navItems = listOf(
    NavItem("خانه", "⌂"),
    NavItem("تراکنش‌ها", "≡"),
    NavItem("ثبت", "＋"),
    NavItem("مقایسه", "▥"),
    NavItem("تنظیمات", "⚙")
)

@Composable
internal fun KharjBottomBar(
    selectedIndex: Int,
    containerColor: Color,
    primaryColor: Color,
    onSelect: (Int) -> Unit
) {
    Surface(
        color = containerColor,
        tonalElevation = 6.dp,
        shadowElevation = 10.dp,
        shape = AppDesign.navShape,
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 10.dp, vertical = 8.dp)
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .height(68.dp)
                .padding(horizontal = 4.dp),
            horizontalArrangement = Arrangement.SpaceEvenly,
            verticalAlignment = Alignment.CenterVertically
        ) {
            navItems.forEachIndexed { index, item ->
                if (index == 2) {
                    RegisterNavItem(
                        selected = selectedIndex == index,
                        title = item.title,
                        primaryColor = primaryColor,
                        onClick = { onSelect(index) }
                    )
                } else {
                    StandardNavItem(
                        selected = selectedIndex == index,
                        title = item.title,
                        icon = item.icon,
                        primaryColor = primaryColor,
                        onClick = { onSelect(index) }
                    )
                }
            }
        }
    }
}

@Composable
private fun StandardNavItem(
    selected: Boolean,
    title: String,
    icon: String,
    primaryColor: Color,
    onClick: () -> Unit
) {
    val contentColor = if (selected) {
        primaryColor
    } else {
        MaterialTheme.colorScheme.onSurface.copy(alpha = 0.56f)
    }

    Column(
        modifier = Modifier
            .clip(AppDesign.controlShape)
            .clickable(onClick = onClick)
            .padding(horizontal = 8.dp, vertical = 7.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.spacedBy(2.dp)
    ) {
        Box(
            modifier = if (selected) {
                Modifier
                    .clip(CircleShape)
                    .background(primaryColor.copy(alpha = 0.12f))
                    .padding(horizontal = 10.dp, vertical = 2.dp)
            } else {
                Modifier.padding(horizontal = 10.dp, vertical = 2.dp)
            },
            contentAlignment = Alignment.Center
        ) {
            Text(
                text = icon,
                color = contentColor,
                fontSize = 19.sp,
                fontWeight = if (selected) FontWeight.Bold else FontWeight.Normal
            )
        }

        Text(
            text = title,
            color = contentColor,
            fontSize = 10.sp,
            fontWeight = if (selected) FontWeight.SemiBold else FontWeight.Normal
        )
    }
}

@Composable
private fun RegisterNavItem(
    selected: Boolean,
    title: String,
    primaryColor: Color,
    onClick: () -> Unit
) {
    Column(
        modifier = Modifier
            .clickable(onClick = onClick)
            .padding(horizontal = 6.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.spacedBy(1.dp)
    ) {
        Surface(
            modifier = Modifier
                .size(50.dp)
                .offset(y = (-7).dp),
            shape = CircleShape,
            color = primaryColor,
            shadowElevation = if (selected) 12.dp else 8.dp
        ) {
            Box(contentAlignment = Alignment.Center) {
                Text(
                    text = "＋",
                    color = Color.White,
                    fontSize = 26.sp,
                    fontWeight = FontWeight.Bold
                )
            }
        }

        Text(
            text = title,
            color = if (selected) primaryColor else MaterialTheme.colorScheme.onSurface.copy(alpha = 0.62f),
            fontSize = 10.sp,
            fontWeight = FontWeight.SemiBold
        )
    }
}
