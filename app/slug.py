import secrets
import string

_ALPHABET = string.ascii_letters + string.digits  # 62 символа — база62, как у bit.ly


def generate_slug(length: int = 7) -> str:
    """Криптографически случайный код фиксированной длины.

    62**7 ≈ 3.5 * 10^12 комбинаций — вероятность коллизии ничтожна,
    но create_short_link всё равно перепроверяет уникальность перед записью:
    "почти невозможно" — не то же самое, что "невозможно".
    """
    return "".join(secrets.choice(_ALPHABET) for _ in range(length))
