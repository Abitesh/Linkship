# links/utils.py

BASE62_ALPHABET = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'


def encode_base62(number: int) -> str:
    # Convert a positive integer into a Base62 string.
    if number < 0:
        raise ValueError('Number must be non-negative')

    if number == 0:
        return BASE62_ALPHABET[0]

    base = len(BASE62_ALPHABET)
    digits = []

    while number > 0:
        number, rem = divmod(number, base)
        digits.append(BASE62_ALPHABET[rem])

    # digits are in reverse order, so i did reverse at the end
    return ''.join(reversed(digits))


def decode_base62(code: str) -> int:
    #Convert a Base62 string back into an integer.
    base = len(BASE62_ALPHABET)
    value = 0

    for char in code:
        index = BASE62_ALPHABET.index(char)
        value = value * base + index

    return value