"""Strong password generation and a simple strength meter.

Uses the `secrets` module (cryptographically secure randomness), NOT `random`.
"""

import secrets
import string

import config

SYMBOLS = "!@#$%^&*()-_=+[]{};:,.?"
AMBIGUOUS = "Il1O0o"  # characters that are easy to confuse when read aloud/typed


def generate_password(
    length: int = config.DEFAULT_PASSWORD_LENGTH,
    use_upper: bool = True,
    use_lower: bool = True,
    use_digits: bool = True,
    use_symbols: bool = True,
    exclude_ambiguous: bool = False,
) -> str:
    """Generate a random password guaranteed to contain every selected type."""
    if not (config.MIN_PASSWORD_LENGTH <= length <= config.MAX_PASSWORD_LENGTH):
        raise ValueError(
            f"Length must be between {config.MIN_PASSWORD_LENGTH} "
            f"and {config.MAX_PASSWORD_LENGTH}."
        )

    pools = []
    if use_upper:
        pools.append(string.ascii_uppercase)
    if use_lower:
        pools.append(string.ascii_lowercase)
    if use_digits:
        pools.append(string.digits)
    if use_symbols:
        pools.append(SYMBOLS)

    if exclude_ambiguous:
        pools = ["".join(c for c in pool if c not in AMBIGUOUS) for pool in pools]

    if not pools:
        raise ValueError("Select at least one character type.")

    # Guarantee at least one character from each selected pool ...
    chars = [secrets.choice(pool) for pool in pools]
    # ... then fill the remaining length from all pools combined.
    combined = "".join(pools)
    chars += [secrets.choice(combined) for _ in range(length - len(chars))]

    # Shuffle so the guaranteed characters aren't always at the start.
    secrets.SystemRandom().shuffle(chars)
    return "".join(chars)


def check_strength(password: str) -> tuple:
    """Return (label, score) where score is 0-4 (Very weak ... Very strong)."""
    if not password:
        return "Empty", 0

    score = 0
    if len(password) >= 8:
        score += 1
    if len(password) >= 12:
        score += 1
    if len(password) >= 16:
        score += 1

    variety = sum(
        [
            any(c.islower() for c in password),
            any(c.isupper() for c in password),
            any(c.isdigit() for c in password),
            any(not c.isalnum() for c in password),
        ]
    )
    if variety >= 3:
        score += 1

    # Penalise very repetitive passwords such as "aaaaaaaaaaaa".
    if len(set(password)) <= max(3, len(password) // 4):
        score = max(0, score - 2)

    score = min(score, 4)
    labels = ["Very weak", "Weak", "Fair", "Strong", "Very strong"]
    return labels[score], score
