from ukladanie import Saving

class Score:

    def __init__(self,Pocet_riadkov,Pocet_stlpcov):
        self.save = Saving()
        self.skore=Pocet_riadkov*Pocet_stlpcov*50
        self.celkove_skore=0

    def get_skore(self,pocet_kol):
        return self.skore-50*pocet_kol

    def set_celkove_skore(self,pocet_kol):
        self.celkove_skore+=self.get_skore(pocet_kol)
        self.vyhodnot_max_skore()
    def get_celkove_skore(self):
        return self.celkove_skore


    def vyhodnot_max_skore(self):
        max_skore=self.max_skore()
        if self.celkove_skore>max_skore:
            zoznam = self.save.load_and_decrypt()
            zoznam[2] = self.celkove_skore
            self.save.encrypt_and_save(zoznam)

    def max_skore(self):
        return int(self.save.load_and_decrypt()[2])

    def vynulovat_skore(self):
        self.celkove_skore=0



