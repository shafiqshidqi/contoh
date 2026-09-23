"""Vigenère Cipher (klasik): C = (P + K) mod 26, P = (C - K) mod 26.

Key diulang mengikuti panjang teks; indeks key hanya maju pada huruf,
karakter non-huruf dibiarkan.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Step:
    no: int
    char: str
    is_letter: bool
    value: int | None
    key_char: str | None
    key_value: int | None
    formula: str
    out: str


@dataclass(frozen=True)
class Result:
    mode: str  # "enc" | "dec"
    key: str
    input: str
    output: str
    key_stream: str
    steps: list[Step] = field(default_factory=list)


def validate_key(raw) -> str:
    key = (raw or "").strip()
    if not key:
        raise ValueError("Key Vigenère tidak boleh kosong.")
    if not (key.isascii() and key.isalpha()):
        raise ValueError("Key Vigenère hanya boleh berisi huruf A–Z (tanpa spasi, angka, atau simbol).")
    return key.upper()


def _base(ch: str) -> int | None:
    if "A" <= ch <= "Z":
        return 65
    if "a" <= ch <= "z":
        return 97
    return None


def process(text: str, key, decrypt: bool = False) -> Result:
    key = validate_key(key)
    steps: list[Step] = []
    out: list[str] = []
    stream: list[str] = []
    j = 0
    for i, ch in enumerate(text, 1):
        base = _base(ch)
        if base is None:
            steps.append(Step(i, ch, False, None, None, None, "Bukan huruf → tidak diubah", ch))
            out.append(ch)
            stream.append(ch)
            continue
        kc = key[j % len(key)]
        j += 1
        p, k = ord(ch) - base, ord(kc) - 65
        if decrypt:
            v = (p - k) % 26
            formula = f"({p} − {k}) mod 26 = {v}"
        else:
            v = (p + k) % 26
            formula = f"({p} + {k}) mod 26 = {v}"
        r = chr(v + base)
        steps.append(Step(i, ch, True, p, kc, k, formula, r))
        out.append(r)
        stream.append(kc)
    return Result("dec" if decrypt else "enc", key, text, "".join(out), "".join(stream), steps)


def encrypt(text: str, key) -> str:
    return process(text, key, False).output


def decrypt(text: str, key) -> str:
    return process(text, key, True).output
