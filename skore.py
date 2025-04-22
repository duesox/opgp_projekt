class Score:
    POCET_RIADKOV = 6
    POCET_STLPCOV = 7
    def __init__(self):
        self.skore=self.POCET_RIADKOV*self.POCET_STLPCOV*50
        self.celkove_skore=self.skore

    def get_skore(self,pocet_kol):
        return self.skore-50*pocet_kol

    def set_celkove_skore(self,pocet_kol):
        self.celkove_skore+=self.get_skore(pocet_kol)

