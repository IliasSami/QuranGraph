import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from translit import transliterate, transliterate_word


class TestTranslit(unittest.TestCase):
    def test_basmala(self):
        # 1:1
        ar = "بِسْمِ ٱللَّهِ ٱلرَّحْمَٰنِ ٱلرَّحِيمِ"
        lat = transliterate(ar)
        self.assertEqual(lat, "bismi Allāhi ar-raḥmāni ar-raḥīmi")

    def test_fatiha_ayah_2(self):
        # 1:2
        ar = "ٱلْحَمْدُ لِلَّهِ رَبِّ ٱلْعَٰلَمِينَ"
        lat = transliterate(ar)
        self.assertEqual(lat, "al-ḥamdu lillāhi rabbi al-‘ālamīna")

    def test_surah_ikhlas(self):
        # 112:1
        ar = "قُلْ هُوَ ٱللَّهُ أَحَدٌ"
        lat = transliterate(ar)
        self.assertEqual(lat, "qul huwa Allāhu 'aḥadun")

    def test_sun_letter_assimilation(self):
        # ash-shams
        ar = "ٱلشَّمْسُ"
        lat = transliterate(ar)
        self.assertEqual(lat, "ash-shamsu")


if __name__ == "__main__":
    unittest.main()
