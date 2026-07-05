import secrets
import string


AMBIGUOUS = set("0Oo1lI")


def generate_password(length: int = 12, avoid_ambiguous_chars: bool = True) -> str:
    length = max(length, 8)
    alphabet = string.ascii_letters + string.digits
    if avoid_ambiguous_chars:
        alphabet = "".join(ch for ch in alphabet if ch not in AMBIGUOUS)

    while True:
        password = "".join(secrets.choice(alphabet) for _ in range(length))
        if (
            any(ch.islower() for ch in password)
            and any(ch.isupper() for ch in password)
            and any(ch.isdigit() for ch in password)
        ):
            return password

