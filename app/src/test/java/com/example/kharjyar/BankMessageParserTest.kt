package com.example.kharjyar

import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Test

class BankMessageParserTest {
    @Test
    fun transactionAmountWinsOverBalance() {
        val parsed = BankMessageParser.parse(
            "بانک نمونه",
            "خرید به مبلغ ۲۰۰,۰۰۰ تومان انجام شد. موجودی ۱۵,۰۰۰,۰۰۰ تومان",
            1_700_000_000_000
        )
        assertEquals(200_000L, parsed?.amount)
        assertEquals(BankImportDirection.DEBIT, parsed?.direction)
    }

    @Test
    fun rialIsConvertedToToman() {
        val parsed = BankMessageParser.parse(
            "بانک نمونه",
            "برداشت مبلغ 2,500,000 ریال از حساب شما",
            1_700_000_000_000
        )
        assertEquals(250_000L, parsed?.amount)
    }

    @Test
    fun otpMessageIsIgnored() {
        val parsed = BankMessageParser.parse(
            "بانک نمونه",
            "رمز پویا 123456 برای خرید 2,000,000 ریال",
            1_700_000_000_000
        )
        assertNull(parsed)
    }
}
