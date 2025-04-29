class Score:

    def __init__(self,Pocet_riadkov,Pocet_stlpcov):
        self.skore=Pocet_riadkov*Pocet_stlpcov*50
        self.celkove_skore=self.skore

    def get_skore(self,pocet_kol):
        return self.skore-50*pocet_kol

    def set_celkove_skore(self,pocet_kol):
        self.celkove_skore+=self.get_skore(pocet_kol)

