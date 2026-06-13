import base64
import hmac
import hashlib
import json
import time
import os

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError(
        "JWT_SECRET_KEY chưa được set — bắt buộc, không có fallback. "
        "Đặt biến môi trường JWT_SECRET_KEY (vd: openssl rand -hex 32) trước khi chạy. "
        "Xem mục 'Deploy / Environment' trong README.md và .env.example."
    )

def base64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode('utf-8')

def base64url_decode(data: str) -> bytes:
    padding = '=' * (4 - (len(data) % 4))
    return base64.urlsafe_b64decode(data + padding)

def create_jwt(payload: dict, secret: str = SECRET_KEY, expires_in: int = 3600) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    payload_copy = payload.copy()
    payload_copy["exp"] = int(time.time()) + expires_in
    payload_copy["iat"] = int(time.time())
    
    header_b64 = base64url_encode(json.dumps(header).encode('utf-8'))
    payload_b64 = base64url_encode(json.dumps(payload_copy).encode('utf-8'))
    
    signing_input = f"{header_b64}.{payload_b64}".encode('utf-8')
    signature = hmac.new(secret.encode('utf-8'), signing_input, hashlib.sha256).digest()
    signature_b64 = base64url_encode(signature)
    
    return f"{header_b64}.{payload_b64}.{signature_b64}"

def decode_jwt(token: str, secret: str = SECRET_KEY) -> dict | None:
    try:
        parts = token.split('.')
        if len(parts) != 3:
            return None
        header_b64, payload_b64, signature_b64 = parts
        
        # Verify signature
        signing_input = f"{header_b64}.{payload_b64}".encode('utf-8')
        expected_signature = hmac.new(secret.encode('utf-8'), signing_input, hashlib.sha256).digest()
        expected_signature_b64 = base64url_encode(expected_signature)
        
        if not hmac.compare_digest(signature_b64, expected_signature_b64):
            return None
            
        payload = json.loads(base64url_decode(payload_b64).decode('utf-8'))
        
        # Check expiration
        if payload.get("exp", 0) < time.time():
            return None
            
        return payload
    except Exception:
        return None

def hash_password(password: str) -> str:
    salt = os.urandom(16)
    rounds = 100000
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, rounds)
    return f"pbkdf2_sha256${rounds}${salt.hex()}${key.hex()}"

def verify_password(password: str, hashed: str) -> bool:
    try:
        parts = hashed.split('$')
        if len(parts) != 4 or parts[0] != 'pbkdf2_sha256':
            return False
        rounds = int(parts[1])
        salt = bytes.fromhex(parts[2])
        key = bytes.fromhex(parts[3])
        new_key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, rounds)
        return hmac.compare_digest(key, new_key)
    except Exception:
        return False
