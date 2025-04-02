import unittest
from logika_hry import LogikaHry

class TestLogikaHry(unittest.TestCase):
    def setUp(self):
        self.hra = LogikaHry()

    def test_vyhra_vodorovne(self):
        # Nastavenie hracej plochy pre vodorovnú výhru
        self.hra.zoznam_policok = [
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 1, 1, 1, 1, 0],
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0],  # Výherná línia pre červeného hráča
        ]

        self.hra.VyhodnotHru()
        self.assertEqual(self.hra.VYHRA_CERVENA, 0)
        self.assertEqual(self.hra.VYHRA_MODRA, 1)

    def test_vyhra_vertikalne(self):
        self.hra.ObnovHru()

        self.hra.zoznam_policok = [
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 2, 0],
            [0, 0, 0, 0, 0, 2, 0],
            [0, 0, 0, 0, 0, 2, 0],
            [0, 0, 0, 0, 0, 2, 0],
            [0, 0, 0, 0, 0, 0, 0],
        ]

        self.hra.VyhodnotHru()
        self.assertEqual(self.hra.VYHRA_CERVENA, 1)
        self.assertEqual(self.hra.VYHRA_MODRA, 0)

    def test_vyhra_diagonalne(self):
        self.hra.ObnovHru()

        self.hra.zoznam_policok = [
            [1, 0, 0, 0, 0, 0, 0],
            [0, 1, 0, 0, 0, 0, 0],
            [0, 0, 1, 0, 0, 0, 0],
            [0, 0, 0, 1, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0],
        ]

        self.hra.VyhodnotHru()
        self.assertEqual(self.hra.VYHRA_CERVENA, 0)
        self.assertEqual(self.hra.VYHRA_MODRA, 1)

        self.hra.zoznam_policok = [
            [0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 2, 0],
            [0, 0, 0, 0, 2, 0, 0],
            [0, 0, 0, 2, 0, 0, 0],
            [0, 0, 2, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0],
        ]
        self.hra.VyhodnotHru()
        self.assertEqual(self.hra.VYHRA_CERVENA, 1)
        self.assertEqual(self.hra.VYHRA_MODRA, 1)

if __name__ == '__main__':
    unittest.main()