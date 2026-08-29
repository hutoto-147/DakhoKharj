package com.example.kharjyar

object Presets {
    val expenseCategories: LinkedHashMap<String, List<String>> = linkedMapOf(
        "خوراکی" to listOf(
            "سوپرمارکت", "میوه و سبزیجات", "رستوران", "فست‌فود",
            "کافه", "سفارش آنلاین غذا", "نان", "نوشیدنی", "تنقلات", "سایر خوراکی‌ها"
        ),
        "خودرو و تردد" to listOf(
            "تاکسی", "تاکسی اینترنتی", "بنزین", "مترو", "اتوبوس",
            "پارکینگ", "عوارض", "تعمیر خودرو", "سرویس خودرو",
            "کارواش", "قطعات خودرو", "سایر"
        ),
        "خانه" to listOf(
            "اجاره خانه", "شارژ ساختمان", "برق", "آب", "گاز",
            "تعمیرات خانه", "تعویض لوازم خانه", "خرید وسایل خانه",
            "لوازم مصرفی خانه", "نظافت", "دکوراسیون", "سایر"
        ),
        "تلفن و اینترنت" to listOf(
            "شارژ موبایل", "قبض موبایل", "اینترنت موبایل", "اینترنت خانه",
            "خرید گوشی", "تعمیر گوشی", "لوازم جانبی", "اشتراک نرم‌افزار", "سایر"
        ),
        "خرید شخصی" to listOf(
            "لباس", "کفش", "کیف", "لوازم شخصی", "لوازم دیجیتال",
            "هدیه", "خرید اینترنتی", "سایر"
        ),
        "هزینه‌های روزمره" to listOf(
            "خرید کوچک روزانه", "خوراکی روزانه", "خدمات", "انعام",
            "هزینه کاری", "سایر"
        ),
        "تفریح" to listOf(
            "سینما", "رستوران", "کافه", "بازی", "سفر", "هتل",
            "تفریح خانوادگی", "کنسرت", "اشتراک فیلم و موسیقی", "سایر"
        ),
        "سلامت و درمان" to listOf(
            "دکتر", "دارو", "آزمایش", "دندانپزشکی", "عینک",
            "بیمارستان", "بیمه", "مکمل", "سایر"
        ),
        "آموزش" to listOf(
            "کلاس", "دانشگاه", "کتاب", "دوره آنلاین",
            "نرم‌افزار آموزشی", "لوازم آموزشی", "سایر"
        ),
        "مالی" to listOf(
            "قسط", "وام", "کارمزد بانکی", "بیمه", "مالیات", "بدهی", "سایر"
        ),
        "سایر" to listOf("سایر")
    )

    val incomeCategories: LinkedHashMap<String, List<String>> = linkedMapOf(
        "حقوق" to listOf("حقوق اصلی"),
        "حقوق هم‌خانه" to listOf("حقوق هم‌خانه"),
        "شغل دوم" to listOf("نام دلخواه"),
        "شغل سوم" to listOf("نام دلخواه"),
        "قرض" to listOf("دریافتی قرض"),
        "سایر منابع" to listOf("نام دلخواه")
    )

    val defaultTags = listOf(
        "شخصی", "کاری", "خانوادگی", "ضروری", "غیرضروری",
        "تفریح", "سفر", "ماشین", "خانه", "روزانه", "مهمانی", "درمان"
    )

    val incomeNameableCategories = setOf("شغل دوم", "شغل سوم", "قرض", "سایر منابع")

    fun categoryIcon(category: String, type: EntryType? = null): String = when {
        category == "خانه" -> "🏠"
        category == "خوراکی" -> "🍽️"
        category == "خودرو و تردد" || category == "رفت‌وآمد" -> "🚗"
        category == "تلفن و اینترنت" -> "📱"
        category == "خرید شخصی" -> "🛍️"
        category == "هزینه‌های روزمره" -> "🧾"
        category == "تفریح" -> "🎬"
        category == "سلامت و درمان" -> "💊"
        category == "آموزش" -> "📚"
        category == "مالی" -> "💳"
        category == "حقوق" -> "💰"
        category == "حقوق هم‌خانه" -> "👥"
        category == "شغل دوم" || category == "شغل سوم" -> "💼"
        category == "قرض" -> "🤝"
        category == "سایر منابع" -> "🪙"
        type == EntryType.INCOME -> "🟢"
        else -> "📌"
    }

    fun mergedCategories(
        type: EntryType,
        custom: List<CategoryRow>
    ): LinkedHashMap<String, List<String>> {
        val result = linkedMapOf<String, MutableList<String>>()
        val base = if (type == EntryType.EXPENSE) expenseCategories else incomeCategories
        base.forEach { (name, subs) -> result[name] = subs.toMutableList() }

        custom.filter { it.type == type }.forEach { row ->
            val normalizedName = if (row.name == "رفت‌وآمد") "خودرو و تردد" else row.name
            val list = result.getOrPut(normalizedName) { mutableListOf() }
            if (row.subcategory.isNotBlank() && row.subcategory !in list) list += row.subcategory
        }

        return LinkedHashMap<String, List<String>>().apply {
            result.forEach { (key, value) -> put(key, value) }
        }
    }
}
