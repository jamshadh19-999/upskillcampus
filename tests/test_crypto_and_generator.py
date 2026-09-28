import string
import unittest

import config
from core import crypto
from core.crypto import Cipher, CryptoError
from core.generator import AMBIGUOUS, SYMBOLS, check_strength, generate_password


class CryptoTests(unittest.TestCase):
    def setUp(self):
        # Fewer PBKDF2 rounds keeps the test-suite fast.
        self._orig = config.KDF_ITERATIONS
        config.KDF_ITERATIONS = 1000

    def tearDown(self):
        config.KDF_ITERATIONS = self._orig

    def test_round_trip(self):
        salt = crypto.generate_salt()
        cipher = Cipher(crypto.derive_key("master-pass-123", salt))
        token = cipher.encrypt("my secret")
        self.assertNotIn("my secret", token)
        self.assertEqual(cipher.decrypt(token), "my secret")

    def test_same_input_gives_different_ciphertext(self):
        cipher = Cipher(crypto.derive_key("master-pass-123", crypto.generate_salt()))
        self.assertNotEqual(cipher.encrypt("x"), cipher.encrypt("x"))

    def test_wrong_key_fails(self):
        salt = crypto.generate_salt()
        token = Cipher(crypto.derive_key("right-password", salt)).encrypt("data")
        with self.assertRaises(CryptoError):
            Cipher(crypto.derive_key("wrong-password", salt)).decrypt(token)

    def test_different_salt_gives_different_key(self):
        self.assertNotEqual(
            crypto.derive_key("same", crypto.generate_salt()),
            crypto.derive_key("same", crypto.generate_salt()),
        )

    def test_tampered_data_is_rejected(self):
        cipher = Cipher(crypto.derive_key("pw-pw-pw-pw", crypto.generate_salt()))
        token = cipher.encrypt("data")
        tampered = token[:-4] + ("AAAA" if not token.endswith("AAAA") else "BBBB")
        with self.assertRaises(CryptoError):
            cipher.decrypt(tampered)


class GeneratorTests(unittest.TestCase):
    def test_length(self):
        for length in (8, 16, 32, 64):
            self.assertEqual(len(generate_password(length)), length)

    def test_contains_every_selected_type(self):
        for _ in range(200):
            pw = generate_password(8)
            self.assertTrue(any(c in string.ascii_uppercase for c in pw))
            self.assertTrue(any(c in string.ascii_lowercase for c in pw))
            self.assertTrue(any(c in string.digits for c in pw))
            self.assertTrue(any(c in SYMBOLS for c in pw))

    def test_only_digits(self):
        pw = generate_password(
            12, use_upper=False, use_lower=False, use_digits=True, use_symbols=False
        )
        self.assertTrue(pw.isdigit())

    def test_exclude_ambiguous(self):
        for _ in range(200):
            pw = generate_password(32, exclude_ambiguous=True)
            self.assertFalse(any(c in AMBIGUOUS for c in pw))

    def test_passwords_are_random(self):
        self.assertEqual(len({generate_password(20) for _ in range(50)}), 50)

    def test_invalid_options(self):
        with self.assertRaises(ValueError):
            generate_password(4)
        with self.assertRaises(ValueError):
            generate_password(config.MAX_PASSWORD_LENGTH + 1)
        with self.assertRaises(ValueError):
            generate_password(
                12, use_upper=False, use_lower=False, use_digits=False, use_symbols=False
            )

    def test_strength_ordering(self):
        self.assertEqual(check_strength("")[1], 0)
        self.assertLess(check_strength("abc")[1], check_strength("Tr0ub4dor&3xyz!")[1])
        self.assertLessEqual(check_strength("aaaaaaaaaaaaaaaa")[1], 1)
        self.assertEqual(check_strength(generate_password(20))[0], "Very strong")


if __name__ == "__main__":
    unittest.main()
