from ipywidgets import interact, interactive, Box, HBox, VBox
import ipywidgets as widgets
from IPython.display import clear_output, display, HTML
import numpy as np
from scipy import integrate
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.colors import cnames
from matplotlib import animation
import platform

class Globs:

    def __init__(self, VAT1, VAT2, DOCHODOWY,ADJ,POW,cena_bez_podzialu,cena_adjacencka_bez_podzialu,wzrost_wartosci,n_dzialek,n_dzialek_pow):
        self.VAT1  = VAT1
        self.VAT2  = VAT2
        self.DOCHODOWY = DOCHODOWY
        self.ADJ = ADJ
        self.POW = POW
        self.cena_bez_podzialu = cena_bez_podzialu
        self.cena_adjacencka_bez_podzialu = cena_adjacencka_bez_podzialu
        self.wzrost_wartosci = wzrost_wartosci
        self.n_dzialek = n_dzialek
        self.n_dzialek_pow = n_dzialek_pow
        
        self.dochodowy = 0.0
        self.oplata_adjacencka = 0.0
        self.n_dzialek_pow_cal = 0
        if self.n_dzialek != len(self.n_dzialek_pow):
            print ('ilosc dzialek oraz ilosc podanych powierzchni nie pasuje')
            return
        
        for d in self.n_dzialek_pow:
            self.n_dzialek_pow_cal +=d
         
        self.size = 66         
        self.cena_sprzedazy = [0.0 for i in range(self.size)]
        self.x = np.zeros(self.size)
        self.y = np.zeros(self.size)
        self.y1 = np.zeros(self.size)
        self.ymax = np.zeros(self.size)
        
        self.zysk = 0.0
        

    def init_inwestycje(self,podatek_od_kapitalu_wejsciowego, inne_koszty, ilosc_lat, koszty_miesieczne, geodezja, droga, linia_energetyczna, koszty_nieruchomosci, spadek_kosztow, pelny_spadek_kosztow_po, sprzedaz_nieruchomosci, optymalizacja_podatkowa):
        
        self.pelny_spadek_kosztow = spadek_kosztow
        self.pelny_spadek_kosztow_po = pelny_spadek_kosztow_po
        self.koszty_nieruchomosci = koszty_nieruchomosci
        self.sprzedaz_nieruchomosci = sprzedaz_nieruchomosci
        self.optymalizacja_podatkowa = optymalizacja_podatkowa
        self.podatek_od_kapitalu_wejsciowego = podatek_od_kapitalu_wejsciowego
                
        self.koszty_globalne = geodezja + droga + linia_energetyczna + inne_koszty
        for rok in range(ilosc_lat):
            for month in range(0,12):
                self.koszty_globalne +=koszty_miesieczne
                
        self.spadek_kosztow = np.zeros(self.n_dzialek)
        for d in range(self.n_dzialek):
            self.spadek_kosztow[d] = self.pelny_spadek_kosztow
            
        factor = self.pelny_spadek_kosztow/self.pelny_spadek_kosztow_po
        
        for d in range(int(self.pelny_spadek_kosztow_po)):
            self.spadek_kosztow[d] = (float(d))*factor
        
    def sprzedaz_calosci(self, cena_bez_podzialu):
    
        self.cena_sprzedazy[0] = cena_bez_podzialu
        for i in range(1,self.size):
            self.cena_sprzedazy[i] = self.cena_sprzedazy[i-1] + 1.0

        index = 0
        for price in (self.cena_sprzedazy):
            self.x[index] = price
            self.y[index] = self.POW * cena_bez_podzialu
            self.ymax[index] = self.y[index]
            index +=1
        
            
    def oblicz_oplate_adjacencka(self, przed_adjacencka_cena_za_metr, wzrost_wartosci):
        self.oplata_adjacencka = self.POW * przed_adjacencka_cena_za_metr * wzrost_wartosci * self.ADJ
        
    def sprzedaz_dzialek(self):
        index = 0
        for price in (self.cena_sprzedazy):
            self.x[index] = price
            self.y[index] = self.n_dzialek_pow_cal*price - self.oplata_adjacencka
            if(self.y[index] > self.ymax[index]):
                self.ymax[index] = self.y[index]
            index +=1
                    
    def sprzedaz_domow_rel(self,koszty_nieruchomosci,sprzedaz_nieruchomosci,optymalizacja_podatkowa, podatek_wejsciowy):

        index = 0
        for price in (self.cena_sprzedazy):
            self.x[index] = price
            self.y[index] = 0.0
            self.y1[index] = 0.0
            zysk = 0.0
            for d in range(self.n_dzialek):
                zysk +=(sprzedaz_nieruchomosci - (koszty_nieruchomosci*(1 - self.spadek_kosztow[d])))
            
            zysk -= self.koszty_globalne
            zysk -= self.oplata_adjacencka
            
            self.y[index] += zysk
            self.y1[index] += zysk
            
            dochodowy = zysk * self.DOCHODOWY
            self.dochodowy = dochodowy
            dochodowy *=(1-optymalizacja_podatkowa) 
            self.y[index] -= dochodowy
            #nominalny
            self.zysk = self.y[index] - podatek_wejsciowy
            #relatywny do max z dzialki
            self.y[index] -= self.ymax[index] + podatek_wejsciowy
            self.y1[index] -= self.ymax[index] + podatek_wejsciowy
            
            
            index +=1
            
    def plot(self,cena_bez_podzialu, przed_adjacencka_cena_za_metr,wzrost_wartosci,koszty_nieruchomosci,sprzedaz_nieruchomosci, optymalizacja_podatkowa):
    
        self.oblicz_oplate_adjacencka(przed_adjacencka_cena_za_metr, wzrost_wartosci)
        podatek_wejsciowy = self.POW * przed_adjacencka_cena_za_metr *self.podatek_od_kapitalu_wejsciowego

        fig = plt.figure(figsize=(10,4))
        ax = fig.add_axes([0, 0, 1, 1])
        plt.ylabel('zysk')

        self.sprzedaz_calosci(cena_bez_podzialu)
        plt.xticks(np.arange(self.cena_sprzedazy[0],self.cena_sprzedazy[self.size-1]+5,5))
        plt.plot(self.x,self.y, linewidth=2,label="sprzedaz bez podzialu")

        self.sprzedaz_dzialek()
        plt.plot(self.x,self.y, linewidth=2,label="sprzedaz z podzialem")
        
        self.sprzedaz_domow_rel(koszty_nieruchomosci, sprzedaz_nieruchomosci, optymalizacja_podatkowa, podatek_wejsciowy)
        plt.plot(self.x,self.y1, linewidth=2,label="sprzedaz domow")
        plt.plot(self.x,self.y, linewidth=2,label="sprzedaz domow PO PODATKU")

        plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
        plt.grid()
        plt.show()
        
        print ('oplata adjacencka',self.oplata_adjacencka)
        print ('powierzchnia dzialek podzielonych',self.n_dzialek_pow_cal)
        print ('podatek dochodowy',self.dochodowy)
        print ('nominalnie zysku',self.zysk)
            

    def on_value_change(self,change):
        return change['new']
        
    def start(self):
        
        _cena_bez_podzialu = widgets.FloatSlider(min=self.cena_bez_podzialu[0], max=self.cena_bez_podzialu[1], step=self.cena_bez_podzialu[2])
        _przed_adjacencka_cena_za_metr = widgets.FloatSlider(min=self.cena_adjacencka_bez_podzialu[0], max=self.cena_adjacencka_bez_podzialu[1], step=self.cena_adjacencka_bez_podzialu[2])
        _wzrost_wartosci = widgets.FloatSlider(min=self.wzrost_wartosci[0], max=self.wzrost_wartosci[1], step=self.wzrost_wartosci[2])
        _koszty_nieruchomosci = widgets.FloatSlider(min=self.koszty_nieruchomosci[0], max=self.koszty_nieruchomosci[1], step=self.koszty_nieruchomosci[2])
        _sprzedaz_nieruchomosci = widgets.FloatSlider(min=self.sprzedaz_nieruchomosci[0], max=self.sprzedaz_nieruchomosci[1], step=self.sprzedaz_nieruchomosci[2])
        _optymalizacja_podatkowa = widgets.FloatSlider(min=self.optymalizacja_podatkowa[0], max=self.optymalizacja_podatkowa[1], step=self.optymalizacja_podatkowa[2])
        
        _cena_bez_podzialu.value = 100
        _przed_adjacencka_cena_za_metr.value = 90
        _wzrost_wartosci.value = .45
        _koszty_nieruchomosci.value = 300000
        _sprzedaz_nieruchomosci.value = 700000
        _optymalizacja_podatkowa.value = 0.0
        
        
        _cena_bez_podzialu.continuous_update = False
        _przed_adjacencka_cena_za_metr.continuous_update = False
        _wzrost_wartosci.continuous_update = False
        _koszty_nieruchomosci.continuous_update = False
        _sprzedaz_nieruchomosci.continuous_update = False
        _optymalizacja_podatkowa.continuous_update = False
        
        width = "100%"
            
        _cena_bez_podzialu.width = width
        _przed_adjacencka_cena_za_metr.width = width
        _wzrost_wartosci.width = width
        _koszty_nieruchomosci.width = width
        _sprzedaz_nieruchomosci.width = width
        _optymalizacja_podatkowa.width = width

        _cena_bez_podzialu.margin = "0px 0px 5px -70px"
        _przed_adjacencka_cena_za_metr.margin ="0px 0px 5px -70px"
        _wzrost_wartosci.margin = "0px 0px 5px -70px"
        _koszty_nieruchomosci.margin = "0px 0px 5px -70px"
        _sprzedaz_nieruchomosci.margin = "0px 0px 5px -70px"
        _optymalizacja_podatkowa.margin = "0px 0px 5px -70px"

        _cena_bez_podzialu.description = ' '
        _przed_adjacencka_cena_za_metr.description = ' '
        _wzrost_wartosci.description = ' '
        _koszty_nieruchomosci.description = ' '
        _sprzedaz_nieruchomosci.description = ' '
        _optymalizacja_podatkowa.description = ' '
        wid_params = []
        wid_names = []
        wid_extra_output = []
        boxes = []

        wid_params.append(_cena_bez_podzialu)
        wid_params.append(_przed_adjacencka_cena_za_metr)
        wid_params.append(_wzrost_wartosci)
        wid_params.append(_koszty_nieruchomosci)
        wid_params.append(_sprzedaz_nieruchomosci)
        wid_params.append(_optymalizacja_podatkowa)

       
        wid_names.append(widgets.ToggleButton(description='Cena sprzedazy', disabled=True, border='none'))
        wid_names.append(widgets.ToggleButton(description='Cena rzeczoznawcy', disabled=True, border='none'))
        wid_names.append(widgets.ToggleButton(description='Wzrost wartosci', disabled=True, border='none'))
        wid_names.append(widgets.ToggleButton(description='Koszt nieruchomosci (netto)', disabled=True, border='none'))
        wid_names.append(widgets.ToggleButton(description='Sprzedaz nieruchomosci (netto)', disabled=True, border='none'))
        wid_names.append(widgets.ToggleButton(description='Optymalizacja podatku', disabled=True, border='none'))
        
        width_ = "60%"
        wid_extra_output.append(widgets.Text(width = width_, disabled=True, value='-'))
        wid_extra_output.append(widgets.Text(width = width_, disabled=True, value='-'))
        wid_extra_output.append(widgets.Text(width = width_, disabled=True, value='Nominalnie za metr +'+str(wid_params[1].value * wid_params[2].value)))
        wid_extra_output.append(widgets.Text(width = width_, disabled=True, value='Brutto '+str(wid_params[3].value * (1+self.VAT1))))
        wid_extra_output.append(widgets.Text(width = width_, disabled=True, value='Brutto '+str(wid_params[4].value * (1+self.VAT2))))
        wid_extra_output.append(widgets.Text(width = width_, disabled=True, value='Mniej o '+str(self.dochodowy * wid_params[5].value)))
        
        def cena_rzeczoznawcy(change):
            a = widgets.Text(disabled=True, value = 'Nominalnie za metr +'+str(wid_params[2].value * change['new']))
            widgets.jsdlink((a, 'value'), (wid_extra_output[2], 'value'))
            
        def wzrost_wartosci(change):
            a = widgets.Text(disabled=True, value = 'Nominalnie za metr '+str(wid_params[1].value * change['new']))
            widgets.jsdlink((a, 'value'), (wid_extra_output[2], 'value'))
            
        def vat1(change):
            a = widgets.Text(disabled=True, value = 'Brutto '+str(change['new'] * (1+self.VAT1)))
            widgets.jsdlink((a, 'value'), (wid_extra_output[3], 'value'))
            
        def vat2(change):
            a = widgets.Text(disabled=True, value = 'Brutto '+str(change['new'] * (1+self.VAT2)))
            widgets.jsdlink((a, 'value'), (wid_extra_output[4], 'value'))
        
        def dochodowy_minus(change):
           a = widgets.Text(disabled=True, value = 'Mniej o '+str(self.dochodowy * change['new']))
           widgets.jsdlink((a, 'value'), (wid_extra_output[5], 'value'))

        wid_params[1].observe(cena_rzeczoznawcy, names='value')
        wid_params[2].observe(wzrost_wartosci, names='value')
        wid_params[3].observe(vat1, names='value')
        wid_params[4].observe(vat2, names='value')
        wid_params[5].observe(dochodowy_minus, names='value')
        
        for i in range(len(wid_params)):
            boxes.append(Box([wid_names[i],wid_params[i],wid_extra_output[i]],margin = "0px 0px 10px 20px",width = '28%')) 

        vbox1 = HBox([boxes[0], boxes[1], boxes[2]])
        vbox2 = HBox([boxes[3], boxes[4], boxes[5]])     
        display(vbox1)
        display(vbox2)
        
        self.plot(_cena_bez_podzialu.value, _przed_adjacencka_cena_za_metr.value, _wzrost_wartosci.value, _koszty_nieruchomosci.value,\
        _sprzedaz_nieruchomosci.value, _optymalizacja_podatkowa.value)
        interactive(self.plot,cena_bez_podzialu = _cena_bez_podzialu, przed_adjacencka_cena_za_metr = _przed_adjacencka_cena_za_metr, \
        wzrost_wartosci = _wzrost_wartosci, koszty_nieruchomosci = _koszty_nieruchomosci, sprzedaz_nieruchomosci = _sprzedaz_nieruchomosci, optymalizacja_podatkowa = _optymalizacja_podatkowa)
        