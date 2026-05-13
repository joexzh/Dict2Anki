from ..addon.misc import dec_cookies, enc_cookies


def assert_enc_dec_cookies(cookies: str):
    s_enc = enc_cookies(cookies)
    assert s_enc != cookies

    s_dec = dec_cookies(s_enc)
    assert s_dec == cookies


def test_enc_dec_cookies_utf8():
    cookies = 'Hello,¡Hola!,你好,こんにちは,Здравствуйте,Olá,εια σου,👋🏽'
    assert_enc_dec_cookies(cookies)


def test_enc_dec_cookies_ascii():
    cookies = '{"__qc_wId": "25", "pgv_pvid": "34915688948", "EudicWebSession": "TFlOC1hMDU0LTAwMGMyOWU2ZmFkOSIsInVzZXJuYW1lIjoi5rWq5a6i44Ck5YqN5b%252bDIiwiY3JlYXRpb25fZGF0ZSI6IjIwMTgtMDktMTFUMjA6Mjc6MThaIiwicm9sZXMiOm51bGwsIm9wZW5pZF90eXBlIjpudWxsLCJvcGVuaWRfZGVzYyI6bnVsbCwicHJvZmlsZSI6eyJuaWNrbmFtZSI6InhpZXpoZW5oYW9AZ21haWwuY29tIiwiZW1haWwiOiJ4aWV6aGVuaGFvQGdtYWlsLmNvbSIsImdlbmRlciI6IueUtyIsInBhc3N3b3JkIjpudWxsLCJ2b2NhYnVsYXJpZXMiOnsiZW4iOjUwMzJ9fSwibGFzdF9wYXNzd29yZF9jaGFuZ2VkX2RhdGUiOiI5LzEyLzIwMTggNTo0MDoyMSBBTSIsInJlZGlyZWN0X3VWxzZSwidG9rZW4iOiI3cXd4TzllWGRCKytpUElJNDlrMVhkR3lFK289IiwiZXhwaXJlaW4iOjEzMTQwMDybCI6bnVsbH0%253dQYNeyJoYXNfb2xkX3Bhc3N3b3JkIjpmYAsInVzZXJpZCI6IjFlNTUzY2FmLWI2NDQtM", ".AspNetCore.Session": "vOqOPvxVzcpREhA6dAT%2FPHpoJSp4yYlBhZ%2F%2FCfDJ8Cb3qNcpe6tHpwPVvuzeKhPjdpvwArmJ7VArjp0kbUJ5c0El2FPz6t4VhAGL6ODXZsSLLCKMAJftASSbkD7q4g4UItpdosofKQGTmbVKXwIuURcPJQFEGAFQXTkg6Xj%2BtO7XO%2F0w", ".AspNetCore.Antiforgery.W85QSzz26FE": "pG9pZ8qGSbcK9avyleuCfDBRCktP5RPLRg6v5ZlIlleOHri38G2aKjNLZLJWFAT0VqhwJ8Cb3qNcpe6tHpPz6t4VhAGJocuozjuy5WOVtsc5h7ZWfoNA-8DRhTk9mlU2AY6-KuhCGb_BuxK7XTl3k3TMewq"}'
    assert_enc_dec_cookies(cookies)


def test_enc_desc_cookies_empty():
    s_enc = enc_cookies('')
    assert s_enc == ''

    s_dec = dec_cookies('')
    assert s_dec == ''
