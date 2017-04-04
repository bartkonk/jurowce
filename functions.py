from ipywidgets import interact, interactive, fixed
import ipywidgets as widgets
from IPython.display import clear_output, display, HTML
import numpy as np
from scipy import integrate
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.colors import cnames
from matplotlib import animation

class Globs:

    def __init__(self,VAT,DOCHODOWY,ADJ,POW,cena_bez_podzialu,cena_adjacencka_bez_podzialu,wzrost_wartosci,n_dzialek,n_dzialek_pow,Cena_sprzedazy):
        self.VAT  = VAT
        self.DOCHODOWY = DOCHODOWY
        self.ADJ = ADJ
        self.POW = POW
        self.cena_bez_podzialu = cena_bez_podzialu
        self.cena_adjacencka_bez_podzialu = cena_adjacencka_bez_podzialu
        self.wzrost_wartosci = wzrost_wartosci
        self.n_dzialek = n_dzialek
        self.n_dzialek_pow = n_dzialek_pow
        self.cena_sprzedazy = Cena_sprzedazy
        
        self.n_dzialek_pow_cal = 0
        if self.n_dzialek != len(self.n_dzialek_pow):
            print 'ilosc dzialek oraz ilosc podanychwww powierzchni nie pasuje'
            return
        
        for d in self.n_dzialek_pow:
            self.n_dzialek_pow_cal +=d
            
        self.size = self.cena_sprzedazy[1] - self.cena_sprzedazy[0]
        self.x = np.zeros(self.size)
        self.y = np.zeros(self.size)
        
    def init_inwestycje(self, geodezja, droga, linia_energetyczna, koszty_nieruchomosci, spadek_kosztow, pelny_spadek_kosztow_po, sprzedaz_nieruchomosci):
        self.geodezja = geodezja
        self.droga = droga
        self.linia_energetyczna = linia_energetyczna
        self.spadek_kosztow = spadek_kosztow
        self.pelny_spadek_kosztow_po = pelny_spadek_kosztow_po
        self.koszty_nieruchomosci = koszty_nieruchomosci
        self.sprzedaz_nieruchomosci = sprzedaz_nieruchomosci
        
    def sprzedaz_calosci(self,cena_bez_podzialu):
        index = 0
        for i in range(self.cena_sprzedazy[0], self.cena_sprzedazy[1]):
            self.x[index] = i
            self.y[index] = self.POW * cena_bez_podzialu
            index +=1
    
    def sprzedaz_dzialek(self, przed_adjacencka_cena_za_metr, wzrost_wartosci):
        
        oplata_adjacencka = przed_adjacencka_cena_za_metr * wzrost_wartosci * self.ADJ * self.POW
        print'adjacencka = ',
        print oplata_adjacencka
        
        print 'calkowita powierzchnia podzielonych dzialek = ',
        print self.n_dzialek_pow_cal
        
        index = 0
        for i in range(self.cena_sprzedazy[0], self.cena_sprzedazy[1]):
            self.x[index] = i
            self.y[index] = self.n_dzialek_pow_cal*i - oplata_adjacencka
            index +=1
            
            
    def sprzedaz_domow(self, przed_adjacencka_cena_za_metr, wzrost_wartosci, sprzedaz_nieruchomosci, koszty_nieruchomosci):

        oplata_adjacencka = przed_adjacencka_cena_za_metr * wzrost_wartosci * self.ADJ * self.POW
        koszty_globalne = self.geodezja + self.droga + self.linia_energetyczna

        #self.spadek_kosztow = spadek_kosztow
        #self.pelny_spadek_kosztow_po = pelny_spadek_kosztow_po

        index = 0
        for i in range(self.cena_sprzedazy[0], self.cena_sprzedazy[1]):
            self.x[index] = i
            self.y[index] = 0.0
            self.y[index] -= oplata_adjacencka
            self.y[index] -= koszty_globalne
            koszty_nieruchomosci_netto = koszty_nieruchomosci/(1+self.VAT)
            sprzedaz_nieruchomosci_netto = sprzedaz_nieruchomosci/(1+self.VAT)
            zysk = 0.0
            for d in range(self.n_dzialek):
                zysk +=(sprzedaz_nieruchomosci_netto - koszty_nieruchomosci_netto)

            self.y[index] += zysk
            self.y[index] *=(1-self.DOCHODOWY)
            
            index +=1
            
    def sprzedaz_domow_rel(self, przed_adjacencka_cena_za_metr, wzrost_wartosci, sprzedaz_nieruchomosci, koszty_nieruchomosci):

        oplata_adjacencka = przed_adjacencka_cena_za_metr * wzrost_wartosci * self.ADJ * self.POW
        koszty_globalne = self.geodezja + self.droga + self.linia_energetyczna

        #self.spadek_kosztow = spadek_kosztow
        #self.pelny_spadek_kosztow_po = pelny_spadek_kosztow_po

        index = 0
        for i in range(self.cena_sprzedazy[0], self.cena_sprzedazy[1]):
            self.x[index] = i
            self.y[index] = 0.0
            self.y[index] -= oplata_adjacencka
            self.y[index] -= koszty_globalne
            self.y[index] -= self.n_dzialek_pow_cal*i
            koszty_nieruchomosci_netto = koszty_nieruchomosci/(1+self.VAT)
            sprzedaz_nieruchomosci_netto = sprzedaz_nieruchomosci/(1+self.VAT)
            zysk = 0.0
            for d in range(self.n_dzialek):
                zysk +=(sprzedaz_nieruchomosci_netto - koszty_nieruchomosci_netto)

            self.y[index] += zysk
            dochodowy = zysk*self.DOCHODOWY
            self.y[index] *=(1-self.DOCHODOWY)
            
            index +=1
        print 'dochodowy = ',
        print dochodowy


    def plot(self,cena_bez_podzialu, przed_adjacencka_cena_za_metr,wzrost_wartosci, sprzedaz_nieruchomosci, koszty_nieruchomosci):

        fig = plt.figure(figsize=(10,7))
        ax = fig.add_axes([0, 0, 1, 1])
        
        self.sprzedaz_calosci(cena_bez_podzialu)
        plt.plot(self.x,self.y, linewidth=2,label="sprzedaz bez podzialu")
    
        self.sprzedaz_dzialek(przed_adjacencka_cena_za_metr, wzrost_wartosci)
        plt.plot(self.x,self.y, linewidth=2,label="sprzedaz z podzialem")
        
        self.sprzedaz_domow(przed_adjacencka_cena_za_metr, wzrost_wartosci, sprzedaz_nieruchomosci, koszty_nieruchomosci)
        plt.plot(self.x,self.y, linewidth=2,label="sprzedaz domow + VAT i DOCHODOWY")
        
        self.sprzedaz_domow_rel(przed_adjacencka_cena_za_metr, wzrost_wartosci, sprzedaz_nieruchomosci, koszty_nieruchomosci)
        plt.plot(self.x,self.y, linewidth=2,label="sprzedaz domow + VAT i DOCHODOWY (minus sprzedaz dzialek)")
        
        plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
        plt.grid()
        plt.show()
            

    def start(self):
        interact(self.plot, \
        cena_bez_podzialu = widgets.FloatSlider(min=self.cena_bez_podzialu[0], max=self.cena_bez_podzialu[1], step=self.cena_bez_podzialu[2], continuous_update=False),\
        przed_adjacencka_cena_za_metr = widgets.FloatSlider(min=self.cena_adjacencka_bez_podzialu[0], max=self.cena_adjacencka_bez_podzialu[1], step=self.cena_adjacencka_bez_podzialu[2], continuous_update=False),\
        wzrost_wartosci = widgets.FloatSlider(min=self.wzrost_wartosci[0], max=self.wzrost_wartosci[1], step=self.wzrost_wartosci[2], continuous_update=False),\
        koszty_nieruchomosci = widgets.FloatSlider(min=self.koszty_nieruchomosci[0], max=self.koszty_nieruchomosci[1], step=self.koszty_nieruchomosci[2], continuous_update=False),\
        sprzedaz_nieruchomosci = widgets.FloatSlider(min=self.sprzedaz_nieruchomosci[0], max=self.sprzedaz_nieruchomosci[1], step=self.sprzedaz_nieruchomosci[2], continuous_update=False))
        
        
        


    

    

    
    
    


