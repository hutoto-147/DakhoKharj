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
import androidx.compose.ui.graphics.Brush
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
    NavItem("تراکنش‌ها", "⇄"),
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
        tonalElevation = 8.dp,
        shadowElevation = 12.dp,
        shape = AppDesign.navShape,
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 10.dp, vertical = 8.dp)
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .height(70.dp)
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
        MaterialTheme.colorScheme.onSurface.copy(alpha = 0.54f)
    }

    Column(
        modifier = Modifier
            .clip(AppDesign.controlShape)
            .clickable(onClick = onClick)
            .padding(horizontal = 7.dp, vertical = 6.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.spacedBy(3.dp)
    ) {
        Surface(
            shape = AppDesign.controlShape,
            color = if (selected) primaryColor.copy(alpha = 0.12f) else Color.Transparent
        ) {
            Text(
                text = icon,
                color = contentColor,
                fontSize = 19.sp,
                fontWeight = if (selected) FontWeight.Bold else FontWeight.Medium,
                modifier = Modifier.padding(horizontal = 11.dp, vertical = 3.dp)
            )
        }
        Text(
            text = title,
            color = contentColor,
            fontSize = 10.sp,
            fontWeight = if (selected) FontWeight.Bold else FontWeight.Medium
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
            .padding(horizontal = 5.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.spacedBy(1.dp)
    ) {
        Box(
            modifier = Modifier
                .size(56.dp)
                .offset(y = (-8).dp)
                .clip(CircleShape)
                .background(
                    brush = Brush.linearGradient(
                        listOf(
                            primaryColor.copy(alpha = 0.52f),
                            Color.White.copy(alpha = 0.80f),
                            primaryColor.copy(alpha = 0.52f)
                        )
                    )
                )
                .padding(2.dp),
            contentAlignment = Alignment.Center
        ) {
            Surface(
                modifier = Modifier.size(50.dp),
                shape = CircleShape,
                color = primaryColor,
                shadowElevation = if (selected) 14.dp else 10.dp
            ) {
                Box(contentAlignment = Alignment.Center) {
                    Text(
                        text = "＋",
                        color = Color.White,
                        fontSize = 27.sp,
                        fontWeight = FontWeight.Bold
                    )
                }
            }
        }

        Text(
            text = title,
            color = if (selected) primaryColor
            else MaterialTheme.colorScheme.onSurface.copy(alpha = 0.62f),
            fontSize = 10.sp,
            fontWeight = FontWeight.Bold
        )
    }
}
