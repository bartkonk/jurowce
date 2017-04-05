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

    def __init__(self,VAT,DOCHODOWY,ADJ,POW,cena_bez_podzialu,cena_adjacencka_bez_podzialu,wzrost_wartosci,n_dzialek,n_dzialek_pow,cena_sprzedazy):
        self.VAT  = VAT
        self.DOCHODOWY = DOCHODOWY
        self.ADJ = ADJ
        self.POW = POW
        self.cena_bez_podzialu = cena_bez_podzialu
        self.cena_adjacencka_bez_podzialu = cena_adjacencka_bez_podzialu
        self.wzrost_wartosci = wzrost_wartosci
        self.n_dzialek = n_dzialek
        self.n_dzialek_pow = n_dzialek_pow
        
        self.cena_sprzedazy = (cena_sprzedazy[0],cena_sprzedazy[1] + 1)
        
        self.dochodowy = 0.0
        self.oplata_adjacencka = 0.0
        self.n_dzialek_pow_cal = 0
        if self.n_dzialek != len(self.n_dzialek_pow):
            print 'ilosc dzialek oraz ilosc podanych powierzchni nie pasuje'
            return
        
        for d in self.n_dzialek_pow:
            self.n_dzialek_pow_cal +=d
                
        self.size = self.cena_sprzedazy[1] - self.cena_sprzedazy[0]
        self.x = np.zeros(self.size)
        self.y = np.zeros(self.size)
        self.y1 = np.zeros(self.size)
        self.ymax = np.zeros(self.size)
        
    def init_inwestycje(self, geodezja, droga, linia_energetyczna, koszty_nieruchomosci, pelny_spadek_kosztow, pelny_spadek_kosztow_po, sprzedaz_nieruchomosci, optymalizacja_podatkowa):
        self.geodezja = geodezja
        self.droga = droga
        self.linia_energetyczna = linia_energetyczna
        self.pelny_spadek_kosztow = pelny_spadek_kosztow
        self.pelny_spadek_kosztow_po = pelny_spadek_kosztow_po
        self.koszty_nieruchomosci = koszty_nieruchomosci
        self.sprzedaz_nieruchomosci = sprzedaz_nieruchomosci
        self.optymalizacja_podatkowa = optymalizacja_podatkowa
        
        self.koszty_globalne = self.geodezja + self.droga + self.linia_energetyczna

        self.spadek_kosztow = np.zeros(self.n_dzialek)
        for d in range(self.n_dzialek):
            self.spadek_kosztow[d] = self.pelny_spadek_kosztow
            
        factor = self.pelny_spadek_kosztow/self.pelny_spadek_kosztow_po
        
        for d in range(int(self.pelny_spadek_kosztow_po)):
            self.spadek_kosztow[d] = (float(d))*factor
        
    def sprzedaz_calosci(self, cena_bez_podzialu):
        index = 0
        for i in range(self.cena_sprzedazy[0], self.cena_sprzedazy[1]):
            self.x[index] = i
            self.y[index] = self.POW * cena_bez_podzialu
            self.ymax[index] = self.y[index]
            index +=1
            
    def oblicz_oplate_adjacencka(self, przed_adjacencka_cena_za_metr, wzrost_wartosci):
        self.oplata_adjacencka = self.POW * przed_adjacencka_cena_za_metr * wzrost_wartosci * self.ADJ
        
    def sprzedaz_dzialek(self):
        index = 0
        for i in range(self.cena_sprzedazy[0], self.cena_sprzedazy[1]):
            self.x[index] = i
            self.y[index] = self.n_dzialek_pow_cal*i - self.oplata_adjacencka
            if(self.y[index] > self.ymax[index]):
                self.ymax[index] = self.y[index]
            index +=1
                    
    def sprzedaz_domow_rel(self,koszty_nieruchomosci,sprzedaz_nieruchomosci,optymalizacja_podatkowa):

        index = 0
        for i in range(self.cena_sprzedazy[0], self.cena_sprzedazy[1]):
            self.x[index] = i
            self.y[index] = 0.0
            self.y1[index] = 0.0
            koszty_nieruchomosci_netto = koszty_nieruchomosci/(1 + self.VAT)
            sprzedaz_nieruchomosci_netto = sprzedaz_nieruchomosci/(1 + self.VAT)
            zysk = 0.0
            for d in range(self.n_dzialek):
                zysk +=(sprzedaz_nieruchomosci_netto - (koszty_nieruchomosci_netto*(1 - self.spadek_kosztow[d])))
            
            zysk -= self.koszty_globalne
            zysk -= self.oplata_adjacencka
            
            self.y[index] += zysk
            self.y1[index] += zysk
            
            self.dochodowy = zysk * self.DOCHODOWY
            self.dochodowy *=(1-optymalizacja_podatkowa)
            self.y[index] -= self.dochodowy
            #minus max z dzialki
            self.y[index] -= self.ymax[index]
            self.y1[index] -= self.ymax[index]
            
            index +=1
            
    def plot(self,cena_bez_podzialu, przed_adjacencka_cena_za_metr,wzrost_wartosci,koszty_nieruchomosci,sprzedaz_nieruchomosci, optymalizacja_podatkowa):
    
        self.oblicz_oplate_adjacencka(przed_adjacencka_cena_za_metr, wzrost_wartosci)
        
        print 'oplata adjacencka',
        print self.oplata_adjacencka
        
        print 'powierzchnia dzialek podzielonych',
        print self.n_dzialek_pow_cal
        
        fig = plt.figure(figsize=(10,7))
        ax = fig.add_axes([0, 0, 1, 1])
        plt.ylabel('zysk')
        plt.xticks(np.arange(self.cena_sprzedazy[0],self.cena_sprzedazy[1],5))
        
        self.sprzedaz_calosci(cena_bez_podzialu)
        plt.plot(self.x,self.y, linewidth=2,label="sprzedaz bez podzialu")
        
        self.sprzedaz_dzialek()
        plt.plot(self.x,self.y, linewidth=2,label="sprzedaz z podzialem")
        
        self.sprzedaz_domow_rel(koszty_nieruchomosci, sprzedaz_nieruchomosci, optymalizacja_podatkowa)
        plt.plot(self.x,self.y1, linewidth=2,label="sprzedaz domow")
        plt.plot(self.x,self.y, linewidth=2,label="sprzedaz domow PO PODATKU")
        
        print 'podatek dochodowy',
        print self.dochodowy
        
        
        plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
        plt.grid()
        plt.show()
            

    def start(self):
        interact(self.plot, \
        cena_bez_podzialu = widgets.FloatSlider(min=self.cena_bez_podzialu[0], max=self.cena_bez_podzialu[1], step=self.cena_bez_podzialu[2], continuous_update=False),\
        przed_adjacencka_cena_za_metr = widgets.FloatSlider(min=self.cena_adjacencka_bez_podzialu[0], max=self.cena_adjacencka_bez_podzialu[1], step=self.cena_adjacencka_bez_podzialu[2], continuous_update=False),\
        wzrost_wartosci = widgets.FloatSlider(min=self.wzrost_wartosci[0], max=self.wzrost_wartosci[1], step=self.wzrost_wartosci[2], continuous_update=False),\
        koszty_nieruchomosci = widgets.FloatSlider(min=self.koszty_nieruchomosci[0], max=self.koszty_nieruchomosci[1], step=self.koszty_nieruchomosci[2], continuous_update=False),\
        sprzedaz_nieruchomosci = widgets.FloatSlider(min=self.sprzedaz_nieruchomosci[0], max=self.sprzedaz_nieruchomosci[1], step=self.sprzedaz_nieruchomosci[2], continuous_update=False),\
        optymalizacja_podatkowa = widgets.FloatSlider(min=self.optymalizacja_podatkowa[0], max=self.optymalizacja_podatkowa[1], step=self.optymalizacja_podatkowa[2], continuous_update=False))
        

    

    
    
    


