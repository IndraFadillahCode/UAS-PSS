from django.contrib.auth.hashers import check_password
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
import jwt  

# Validasi password biasa vs hashed
def validate_password(plain_password, hashed_password):
    return check_password(plain_password, hashed_password)

# Fungsi untuk membuat JWT token (login)
def create_jwt_token(user):
    payload = {
        'user_id': user.id,
        'username': user.username,
        'exp': timezone.now() + timedelta(days=1),  # expire 1 hari
        'iat': timezone.now()
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    return token

# Fungsi waktu saat ini dengan awareness timezone
def get_current_timestamp():
    return timezone.now()

# Tambahan placeholder OTP 
def generate_otp():
    # Kode OTP bisa 6-digit acak
    import random
    return str(random.randint(100000, 999999))

def send_email_otp(email, otp):
    # untuk pengiriman email OTP
    print(f"OTP untuk {email} adalah: {otp}")