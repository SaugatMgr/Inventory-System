import pyotp


def generate_otp():
    secret_key = pyotp.random_base32()
    otp = pyotp.TOTP(secret_key)

    return otp.now()
