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
        self.D1 = DOCHODOWY
        self.D2 = DOCHODOWY+DOCHODOWY - DOCHODOWY*DOCHODOWY
        self.ADJ = ADJ
        self.POW = POW
        self.cena_bez_podzialu = cena_bez_podzialu
        self.cena_adjacencka_bez_podzialu = cena_adjacencka_bez_podzialu
        self.wzrost_wartosci = wzrost_wartosci
        self.n_dzialek = n_dzialek
        self.n_dzialek_pow = n_dzialek_pow
        self.optymalizacja_podatkowa = 0.0
        
        self.D = 0.0
        self.dochodowy = 0.0
        self.dochodowy_opt = 0.0
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
        
        self.y_all = np.zeros(self.size)
        self.y_split = np.zeros(self.size)
        self.y_estate = np.zeros(self.size)
        self.y_estate_tax = np.zeros(self.size)
        
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
            
    def set_inwestycje(d, optymalizacja_podatkowa):
        self.D = d
        self.optymalizacja_podatkowa = optymalizacja_podatkowa
        
        
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
                    
    def sprzedaz_domow_rel(self,koszty_nieruchomosci,sprzedaz_nieruchomosci, optymalizacja_podatkowa, podatek_wejsciowy, tax):
    
        if(tax == 'pojedynczy'):
            self.D = self.D1
        else:
            self.D = self.D2
            
        index = 0
        for price in (self.cena_sprzedazy):
            self.x[index] = price
            self.y[index] = 0.0
            self.y1[index] = 0.0
            zysk_netto = 0.0
            for d in range(self.n_dzialek):
                zysk_netto +=(sprzedaz_nieruchomosci - (koszty_nieruchomosci*(1 - self.spadek_kosztow[d])))
            
            zysk_netto -= self.koszty_globalne
            zysk_netto -= self.oplata_adjacencka
            
            self.y[index] += zysk_netto
            self.y1[index] += zysk_netto
            
            dochodowy = zysk_netto * self.D
            self.dochodowy = dochodowy
            self.dochodowy_opt = dochodowy
            self.dochodowy_opt *=(1-optymalizacja_podatkowa) 
            self.y[index] -= self.dochodowy_opt
            
            self.y[index] -= podatek_wejsciowy
            self.y1[index] -= podatek_wejsciowy
            
            self.zysk = self.y[index]
                        
            index +=1
            
    def plot(self):

        fig = plt.figure(figsize=(10,4))
        ax = fig.add_axes([0, 0, 1, 1])
        plt.ylabel('zysk')
        plt.xticks(np.arange(self.cena_sprzedazy[0],self.cena_sprzedazy[self.size-1]+5,5))
        plt.plot(self.x,self.y_all, linewidth=2,label="sprzedaz bez podzialu")
        plt.plot(self.x,self.y_split, linewidth=2,label="sprzedaz z podzialem")
        plt.plot(self.x,self.y_estate, linewidth=2,label="sprzedaz domow")
        plt.plot(self.x,self.y_estate_tax,linewidth=2,label="sprzedaz domow PO PODATKU")

        plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
        plt.grid()
        plt.show()
        
        ##end of plot 1
        display(HTML('<h4>Zysk relatywny do maximum(sprzedaz dzialek lub calosci))</h4>'))
        fig = plt.figure(figsize=(10,4))
        ax = fig.add_axes([0, 0, 1, 1])
        plt.ylabel('zysk relatywny')
        plt.plot(self.x,self.y/self.ymax, linewidth=2,label="oplacalnosc inwestycji")
        plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
        plt.grid()
        plt.show()
        
        print ('oplata adjacencka',self.oplata_adjacencka)
        print ('powierzchnia dzialek podzielonych',self.n_dzialek_pow_cal)
        print ('podatek dochodowy',self.dochodowy)
        print ('nominalnie zysku',self.zysk)
        
    def compute(self,cena_bez_podzialu, przed_adjacencka_cena_za_metr,wzrost_wartosci,koszty_nieruchomosci,sprzedaz_nieruchomosci, optymalizacja_podatkowa, tax):
        
        self.oblicz_oplate_adjacencka(przed_adjacencka_cena_za_metr, wzrost_wartosci)
        podatek_wejsciowy = self.POW * przed_adjacencka_cena_za_metr *self.podatek_od_kapitalu_wejsciowego
        self.sprzedaz_calosci(cena_bez_podzialu)
        self.y_all = np.copy(self.y)
        self.sprzedaz_dzialek()
        self.y_split = np.copy(self.y)
        self.sprzedaz_domow_rel(koszty_nieruchomosci, sprzedaz_nieruchomosci, optymalizacja_podatkowa, podatek_wejsciowy, tax)
        self.y_estate = np.copy(self.y1)
        self.y_estate_tax = np.copy(self.y)
        
        self.plot()
        
    
            

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
        _sprzedaz_nieruchomosci.value = 600000
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
        
        _tax = widgets.RadioButtons(options = ['pojedynczy', 'podwojny'], description='Tax:',disabled=False)
        
        def cut_string(string):
            index = 0
            cut_index = 0
            for i in string:
                if(i == '.'):
                   cut_index = index
                index+=1
            return string[0:cut_index]
        
        def cena_rzeczoznawcy(change):
            a = widgets.Text(disabled=True, value = 'Nominalnie za metr +'+str(wid_params[2].value * change['new']))
            widgets.jsdlink((a, 'value'), (wid_extra_output[2], 'value'))
            
        def wzrost_wartosci(change):
            a = widgets.Text(disabled=True, value = 'Nominalnie za metr '+str(wid_params[1].value * change['new']))
            widgets.jsdlink((a, 'value'), (wid_extra_output[2], 'value'))
            
        def vat1(change):
            a = widgets.Text(disabled=True, value = 'Brutto '+str(change['new'] * (1+self.VAT1)))
            widgets.jsdlink((a, 'value'), (wid_extra_output[3], 'value'))
            string = cut_string(str(self.dochodowy * wid_params[5].value))
            b = widgets.Text(disabled=True, value = 'Mniej o '+string)
            widgets.jsdlink((b, 'value'), (wid_extra_output[5], 'value'))
            
        def vat2(change):
            a = widgets.Text(disabled=True, value = 'Brutto '+str(change['new'] * (1+self.VAT2)))
            widgets.jsdlink((a, 'value'), (wid_extra_output[4], 'value'))
            string = cut_string(str(self.dochodowy * wid_params[5].value))
            b = widgets.Text(disabled=True, value = 'Mniej o '+string)
            widgets.jsdlink((b, 'value'), (wid_extra_output[5], 'value'))

        def dochodowy_minus(change):
            string = cut_string(str(self.dochodowy * change['new']))
            a = widgets.Text(disabled=True, value = 'Mniej o '+string)
            widgets.jsdlink((a, 'value'), (wid_extra_output[5], 'value'))
            
        def tax_output(change):
            string = cut_string(str(self.dochodowy * wid_params[5].value))
            a = widgets.Text(disabled=True, value = 'Mniej o '+string)
            widgets.jsdlink((a, 'value'), (wid_extra_output[5], 'value'))

        for i in range(len(wid_params)):
            boxes.append(Box([wid_names[i],wid_params[i],wid_extra_output[i]],margin = "0px 0px 10px 20px",width = '28%')) 

        vbox1 = HBox([boxes[0], boxes[1], boxes[2]])
        vbox2 = HBox([boxes[3], boxes[4], boxes[5]])
        display(vbox1)
        display(vbox2)
        display(_tax)
        
        self.compute(_cena_bez_podzialu.value, _przed_adjacencka_cena_za_metr.value, _wzrost_wartosci.value, _koszty_nieruchomosci.value,\
        _sprzedaz_nieruchomosci.value, _optymalizacja_podatkowa.value, _tax.value)
        
        interactive(self.compute,cena_bez_podzialu = _cena_bez_podzialu, przed_adjacencka_cena_za_metr = _przed_adjacencka_cena_za_metr, \
        wzrost_wartosci = _wzrost_wartosci, koszty_nieruchomosci = _koszty_nieruchomosci, sprzedaz_nieruchomosci = _sprzedaz_nieruchomosci,\
        optymalizacja_podatkowa = _optymalizacja_podatkowa, tax = _tax)
        
        wid_params[1].observe(cena_rzeczoznawcy, names='value')
        wid_params[2].observe(wzrost_wartosci, names='value')
        wid_params[3].observe(vat1, names='value')
        wid_params[4].observe(vat2, names='value')
        wid_params[5].observe(dochodowy_minus, names='value')
        _tax.observe(tax_output,names='value')
        
       
        