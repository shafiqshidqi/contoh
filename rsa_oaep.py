"""RSA-2048 + OAEP(SHA-256) memakai library `cryptography`.

Enkripsi/dekripsi dilakukan library. Bagian `generate_keypair` hanya mengambil p dan q dari
library, lalu menghitung n, φ(n), d = e⁻¹ mod φ(n) agar setiap langkah bisa ditampilkan
secara edukatif; key dibangun ulang & divalidasi oleh library.
"""
from __future__ import annotations

import math
import secrets
from dataclasses import dataclass

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa

from .utils import b64d, b64e

KEY_BITS = 2048
E = 65537
BLOCK = KEY_BITS // 8            # 256 byte per blok ciphertext
MAX_BLOCK = BLOCK - 2 * 32 - 2   # 190 byte plaintext per blok (OAEP-SHA256)


def _oaep() -> padding.OAEP:
    return padding.OAEP(mgf=padding.MGF1(hashes.SHA256()), algorithm=hashes.SHA256(), label=None)


def is_probable_prime(n: int, rounds: int = 20) -> bool:
    """Uji Miller–Rabin (untuk verifikasi edukatif p dan q)."""
    if n < 2:
        return False
    for sp in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29):
        if n % sp == 0:
            return n == sp
    d, r = n - 1, 0
    while d % 2 == 0:
        d //= 2
        r += 1
    for _ in range(rounds):
        a = secrets.randbelow(n - 3) + 2
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True


@dataclass
class KeyPair:
    private_key: rsa.RSAPrivateKey
    p: int
    q: int
    n: int
    e: int
    phi: int
    d: int
    p_prime: bool
    q_prime: bool
    public_pem: str
    private_pem: str

    @property
    def public_key(self) -> rsa.RSAPublicKey:
        return self.private_key.public_key()


def generate_keypair() -> KeyPair:
    gen = rsa.generate_private_key(public_exponent=E, key_size=KEY_BITS)
    nums = gen.private_numbers()
    p, q = nums.p, nums.q
    n, phi = p * q, (p - 1) * (q - 1)
    d = pow(E, -1, phi)
    priv = rsa.RSAPrivateNumbers(
        p=p, q=q, d=d,
        dmp1=rsa.rsa_crt_dmp1(d, p), dmq1=rsa.rsa_crt_dmq1(d, q), iqmp=rsa.rsa_crt_iqmp(p, q),
        public_numbers=rsa.RSAPublicNumbers(E, n),
    ).private_key()
    public_pem = priv.public_key().public_bytes(
        serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo).decode()
    private_pem = priv.private_bytes(
        serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()).decode()
    return KeyPair(priv, p, q, n, E, phi, d, is_probable_prime(p), is_probable_prime(q), public_pem, private_pem)


def _require(key, what: str):
    if key is None:
        raise ValueError(f"RSA membutuhkan {what}. Generate key pair terlebih dahulu.")


def encrypt_block(public_key, data: bytes) -> bytes:
    _require(public_key, "public key")
    if not data:
        raise ValueError("Plaintext tidak boleh kosong.")
    if len(data) > MAX_BLOCK:
        raise ValueError(
            f"Plaintext terlalu panjang untuk RSA-2048 OAEP: {len(data)} byte (maksimum {MAX_BLOCK} byte). "
            "Pada sistem nyata RSA dipakai untuk mengenkripsi key/session key, bukan teks panjang."
        )
    return public_key.encrypt(data, _oaep())


def decrypt_block(private_key, blob: bytes) -> bytes:
    _require(private_key, "private key")
    if len(blob) != BLOCK:
        raise ValueError(f"Ciphertext RSA-2048 harus tepat {BLOCK} byte (terbaca {len(blob)} byte).")
    try:
        return private_key.decrypt(blob, _oaep())
    except ValueError:
        raise ValueError("Dekripsi RSA gagal: ciphertext rusak atau bukan pasangan private key ini.") from None


def encrypt_text(public_key, text: str) -> bytes:
    return encrypt_block(public_key, text.encode("utf-8"))


def decrypt_text(private_key, b64: str) -> tuple[bytes, str]:
    raw = decrypt_block(private_key, b64d(b64, "Ciphertext RSA"))
    try:
        return raw, raw.decode("utf-8")
    except UnicodeDecodeError:
        raise ValueError("Hasil dekripsi bukan teks UTF-8 yang valid.") from None


def encrypt_chunked(public_key, data: bytes) -> bytes:
    """Dipakai Super Encryption: data dipecah per 190 byte, tiap blok dienkripsi OAEP (acak)."""
    _require(public_key, "public key")
    if not data:
        raise ValueError("Data tidak boleh kosong.")
    return b"".join(encrypt_block(public_key, data[i:i + MAX_BLOCK]) for i in range(0, len(data), MAX_BLOCK))


def decrypt_chunked(private_key, blob: bytes) -> bytes:
    _require(private_key, "private key")
    if not blob or len(blob) % BLOCK:
        raise ValueError(f"Ciphertext RSA harus kelipatan {BLOCK} byte (terbaca {len(blob)} byte).")
    return b"".join(decrypt_block(private_key, blob[i:i + BLOCK]) for i in range(0, len(blob), BLOCK))


def gcd_ok(kp: KeyPair) -> bool:
    return math.gcd(kp.e, kp.phi) == 1
