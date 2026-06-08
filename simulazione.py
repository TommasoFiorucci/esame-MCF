import numpy as np
import scipy as sp
import matplotlib.pyplot as plt
import argparse
import tracciatore as tr
import pandas as pd

'''
Ho deciso di usare il modulo argparse, per permettere di esaminare
il funzionamento delle varie funzionalità del codice in maniera indipendente
tra di loro
'''
c = sp.constants.c
m_eV = (105.7*10**6)/c**2 #massa del muone in eV/c^2
m = m_eV * 1.602176634 * 10**(-19) #massa del muone in J/c^2 = kg

#defniamo una funzione per calcolare la velocità dei muoni a partire dalla
#loro energia cinetica
#trattiamo i muoni in maniera relativistica, in quanto hanno velocità
#relativistiche
def vel(T_eV, m):
    '''
    funzione che calcola la velocità di una particella relativistica di massa m
    ed energia conetica T
    m = massa della particella in eV/c^2
    T = energia cinetica della particella in eV
    '''
    T = T_eV * 1.602176634 * 10**(-19) #energia cinetica in joule

    v = c*((T**2 + 2*m*T*c**2)/(T + m*c**2)**2)**0.5
    return v

#definisco la funzione gaussiana da fittare agli istogrammi

def gauss(x, A, x0, sig):
    '''
    è la funzione gaussiana
    f(x) = A*exp[-(x - x0)^2/(2*sig^2)]
    '''
    return A*np.exp((-(x - x0)**2)/(2*sig**2))

'''
scipy non riusciva a fare il fit perchè avevo scritto la funzione male
NON USARE PARENTESI QUADRE [] E TONDE () IN MODO INTERSCAMBIABILE
'''

#definisco gli argomenti di argparse

def parse_arguments():
    parser = argparse.ArgumentParser(description = 'Simulazione di un fascio di muoni che incide ed entra nel tracciatore.', usage = 'python3 simulatore.py --opzione')
    parser.add_argument('-i', '--istogrammi', action = 'store_true', help = 'Mostra 3 istogrammi: \n- un istogramma della coordinata x dei muoni; \n- un instogramma della coordinata y dei muoni; \n- un istogramma delle coordinate (x,y) dei muoni. \nTutti gli istogrammi fanno riferimento ad un fascio di muoni gaussiano che incide ortogonalmente sul tracciatore. Ogni muone ha energia cinetica pari a 50 MeV')
    parser.add_argument('-fit', '--istogrammi_fittati', action = 'store_true', help = 'Mostra gli istogrammi delle posizioni x e y dei muoni del fascio sovrapposti alle curve gaussiane che sono state fittate loro. \nDi fianco a questi istogrammi sono presenti i grafici delle deviazioni standard delle curve fittate in funzione dell\' energia dei muoni incidenti.\nIl comando produce anche 2 tabelle, una per ogni tipo di istogramma, nelle quali sono raccolti i valori ottimizzati per il fit dei parametri della curva gaussiana. La curva usata per il fit ha questa forma: \nf(x) = A*exp(-(x - x0)^2/(2*σ^2))')
    return parser.parse_args()

#definiamo la funzione main() del codice

def main():

    args = parse_arguments()
    
    #simulo un fascio di muoni che attraversa il tracciatore
    
    #definiamo i parametri del tracciatore 
    s_p = 400*10**(-6)
    n = 3
    d = 10**(-2)
    s = 30*10**(-6)
    chi_gcm = 21.82 #radiation length in g/cm^2
    chi = chi_gcm * 10 #radiation length in kg/m^2
    
    #definiamo la larghezza ed il waist del fascio, e anche la sua varianza
    
    w = 1.5*s
    sig = w/2

    #creaiamo il fascio
    
    ''' creiamo un dizionario contenente le coordinate x e y iniziali di ogni
    muone che costituisce il fascio'''
    fa = {}
    #numero totale di muoni appartenenti al fascio ed incidenti sul riv.
    N = 10000 
    i = 0

    
    while i < N:
        r = np.random.normal(0, sig, 2)
        if r[0] <= w and r[1] <= w:
            fa.update({i : [r[0], r[1]]})
            i = i + 1

    #definiamo una variabile tracciatore ed usiamo i suoi moduli per simulare
    #il passaggio del fascio attraverso il rivelatore
    sim = tr.trac()
    simu = sim.riv(s_p, n, d, s, chi)

    #simuliamo il cammino dei muoni con diverse energie, ad intervalli di 50 MeV

    #ampieza dell'intervallo di energia alla quale l'energia cinetica dei muoni
    #può appartenere
    deltaT_eV = 50*999*10**6
    dT_eV = 999*10**6
    NT_eV = int(deltaT_eV/dT_eV)
    #array con i valori che sono stati selezionati
    TT = np.array([50*10**6])
    for i in range(1, NT_eV):
        tt = TT[-1] + dT_eV
        TT = np.append(TT, tt)
    '''
    creiamo dei dizionari per immagazzinare gli array delle coordinate
    finali dei fasci ad ogni valore energetico
    '''
    xx = {}
    yy = {}

    nbinx = 100
    nbiny = 100
    for i in range(NT_eV):
        v = vel(TT[i], m)
        #simuliamo il passaggio di ogni muone singolarmente
        #e creiamo due array, uno per le coordinate x e uno per le
        #coordinate y dei muoni
        x = np.empty(0)
        y = np.empty(0)
        for j in range(len(fa)):
            cam = sim.cammino(v, fa[j], m)
            '''
            creiamo una lista delle chiavi del dizionario cam[0],
            e poi la usiamo
            per usare l'ultimo elemento del dizionario
            dict.keys() crea una lista con le chiavi del dizionario
            list(dict.keys()) la rende un array, e quindi manipolabile
            con gli indici
            '''
            a = list(cam[0].keys())
            A = a[-1]
            x = np.append(x, cam[0][A][0])
            y = np.append(y, cam[0][A][1])
        xx.update({i : x})
        yy.update({i : y})

    if args.istogrammi == True:
        
        '''
        disegnamo 2 istogrammi, uno per le posizioni x e uno per le
        posizioni y dei muoni
        '''
        fig, ax = plt.subplots(1, 3, figsize = (18, 6))

        
        ax[0].hist(xx[0], bins = nbinx, range = (xx[0].min(), xx[0].max()))
        ax[0].set_title('ISTOGRAMMA COORDINATA X (T = 50 MeV)')
        ax[0].set_xlabel('X')
        ax[0].set_ylabel('NUMERO MUONI')
        
        ax[1].hist(yy[0], bins = nbiny, range = (yy[0].min(), yy[0].max()))
        ax[1].set_title('ISTOGRAMMA COORDINATA Y (T = 50 MeV)')
        ax[1].set_xlabel('Y')
        ax[1].set_ylabel('NUMERO MUONI')
        
        #istogramma in 2d delle coordinate x,y dei muoni
        
        bins = ax[2].hist2d(xx[0], yy[0], bins = 100, range = ([xx[0].min(), xx[0].max()], [yy[0].min(), yy[0].max()]))
        ax[2].set_title('ISTOGRAMMA COORDINATE (X,Y) (T = 50 MeV)')
        ax[2].set_xlabel('X')
        ax[2].set_ylabel('Y')
        
        plt.show()

    elif args.istogrammi_fittati == True:
        #creiamo due array per i valori delle sigma e per i loro errori
        sig_x = np.empty(0)
        sig_y = np.empty(0)
        errs_x = np.empty(0)
        errs_y = np.empty(0)
        '''
        creiamo anche dei dizionari per
        immagazzianre i valori dei parametri fittati

        creiamo dei dizionari anche per immagazzinare le coordinate
        dei centri dei bin per ogni simulazione del cammino del fascio
        '''
        px = {}
        py = {}
        llx = {}
        lly = {}
        ''' creiamo un dizionario per gli array pstart di ogni fit.
        i valori di A et x0 vanno bene, è il valore di sigma che va
        diminuito man mano che si susseguono i fit
        '''
        ps = {}
        sig_s = np.logspace(6, 14, NT_eV, base = np.e)
        sig_start = np.flip(sig_s)

        '''
        creiamo anche una tabella per organizzare i valori dei coefficienti
        del fit gaussiano in funzione dell'energia
        '''
        amp_x = np.empty(0)
        amp_y = np.empty(0)
        centro_x = np.empty(0)
        centro_y = np.empty(0)
        
        erramp_x = np.empty(0)
        erramp_y = np.empty(0)
        errcentro_x = np.empty(0)
        errcentro_y = np.empty(0)
        
        for i in range(0, NT_eV):
            '''            
            facciamo il fit della funzione gaussiana sui due istogrammi
            monodimensionali
            prova con le coordinate x
            
            la larghezza dei bin è la larghezza dei sensori del tracciatore
            cioè s
            
            nbinx = int((xx[i].max() - xx[i].min())/s)
            nbiny = int((yy[i].max() - yy[i].min())/s)

            è necessario sostituire nbinx et nbiny con un
            valore molto più piccolo e meno accurato, in quanto il mio computer
            non è in grado di disegnare un istogramma con numero di bin pari a
            nbinx o nbiny
            '''
            
            binx = np.histogram(xx[i], bins = nbinx, range = (xx[i].min(), xx[i].max()))
            bx = np.array(binx[0])

            biny = np.histogram(yy[i], bins = nbiny, range = (yy[i].min(), yy[i].max()))
            by = np.array(biny[0])
            
            #troviamo il centro dei bin
            #binx[1] contiene le coordinate dei confini dei bin
            
            lx = np.empty(0)
            ly = np.empty(0)
            for j in range(1, len(binx[1])):
                xxx = (binx[1][j] - binx[1][j - 1])/2
                dx = np.absolute(xxx)
                yyy = (biny[1][j] - biny[1][j - 1])/2
                dy = np.absolute(yyy)

                
                Lx = binx[1][j] - dx
                lx = np.append(lx, Lx)
                Ly = biny[1][j] - dy
                ly = np.append(ly, Ly)
            '''
            #il fit non tornava perchè il valore iniziale
            #pstart di sigma era troppo basso
            pstart = np.array([300, 0, 1e6])
            '''
            ps.update({i : [300, 0, sig_start[i]]})
            params_x, pcov_x = sp.optimize.curve_fit(gauss, lx, bx, p0 = ps[i], maxfev = 5000)
            params_y, pcov_y = sp.optimize.curve_fit(gauss, ly, by, p0 = ps[i], maxfev = 5000)

            amp_x = np.append(amp_x, params_x[0])
            amp_y = np.append(amp_y, params_y[0])
            centro_x = np.append(centro_x, params_x[1])
            centro_y = np.append(centro_y, params_y[1])
            sig_x = np.append(sig_x, params_x[2])
            sig_y = np.append(sig_y, params_y[2])
            erramp_x = np.append(erramp_x, (np.absolute(pcov_x.diagonal()[0]))**(0.5))
            erramp_y = np.append(erramp_y, (np.absolute(pcov_y.diagonal()[0]))**(0.5))
            errcentro_x = np.append(errcentro_x, (np.absolute(pcov_x.diagonal()[1]))**(0.5))
            errcentro_y = np.append(errcentro_y, (np.absolute(pcov_y.diagonal()[1]))**(0.5))
            errs_x = np.append(errs_x, (np.absolute(pcov_x.diagonal()[2]))**(0.5))
            errs_y = np.append(errs_y, (np.absolute(pcov_y.diagonal()[2]))**(0.5))
            px.update({i : params_x})
            py.update({i : params_y})
            llx.update({i : lx})
            lly.update({i : ly})

        '''
        creiamo una maschera per filtrare i valori delle sigma errati, dovuti
        all'incapacità del mio pc di calcolare i parametri ottimizzati per
        fittare i dati. l'errore è probabilmente dovuto al fatto che i valori
        iniziali, pstart, dei parametri in alcuni casi sono troppo lontani
        dai valori reali
        '''
        mask_x = (amp_x < 700) & (amp_x > 200)
        mask_y = (amp_y < 700) & (amp_y > 200)
        
        #disegnamo il grafico delle sigma in funzione dell'energia
        
        fig, ax = plt.subplots(2, 2, figsize = (12, 12))

        ax[0][0].hist(xx[0], bins = nbinx , range = (xx[0].min(), xx[0].max()), color = 'blue')
        ax[0][0].plot(llx[0], gauss(llx[0], px[0][0], px[0][1], px[0][2]), color = 'orange')
        ax[0][0].set_title('FIT GAUSSIANO COORDINATA X (T = 50 MeV)')
        ax[0][0].set_xlabel('X')
        ax[0][0].set_ylabel('NUMERO MUONI')

        ax[1][0].hist(yy[0], bins = nbiny, range = (yy[0].min(), yy[0].max()), color = 'blue')
        ax[1][0].plot(lly[0], gauss(lly[0], py[0][0], py[0][1], py[0][2]), color = 'orange')
        ax[1][0].set_title('FIT GAUSSIANO COORDINATA Y (T = 50 MeV)')
        ax[1][0].set_xlabel('Y')
        ax[1][0].set_ylabel('NUMERO MUONI')

        ax[0][1].plot(TT[mask_x], sig_x[mask_x], 'o')
        ax[0][1].set_title('σ_x IN FUNZIONE DELL\' ENERGIA DEL FASCIO')
        ax[0][1].set_xlabel('T [eV]')
        ax[0][1].set_ylabel('σ_x (scala logaritmica)')
        ax[0][1].set_yscale('log')

        ax[1][1].plot(TT[mask_y], sig_y[mask_y], 'o')
        ax[1][1].set_title('σ_y IN FUNZIONE DELL\' ENERGIA DEL FASCIO')
        ax[1][1].set_xlabel('T [eV]')
        ax[1][1].set_ylabel('σ_y (scala logaritmica)')
        ax[1][1].set_yscale('log')
        
        plt.show()

        #scriviamo la tabella

        tab_x = pd.DataFrame( columns = ['energia cinetica T[eV]', 'A_x', 'ΔA_x', 'x0', 'Δx0', 'σ_x', 'Δσ_x'])
        tab_x['energia cinetica T[eV]'] = TT[mask_x]
        tab_x['A_x'] = amp_x[mask_x]
        tab_x['ΔA_x'] = erramp_x[mask_x]
        tab_x['x0'] = centro_x[mask_x]
        tab_x['Δx0'] = errcentro_x[mask_x]
        tab_x['σ_x'] = sig_x[mask_x]
        tab_x['Δσ_x'] = errs_x[mask_x]

        print(tab_x)

        tab_y = pd.DataFrame( columns = ['energia cinetica T[eV]', 'A_y', 'ΔA_y', 'y0', 'Δy0', 'σ_y', 'Δσ_y'])
        tab_y['energia cinetica T[eV]'] = TT[mask_y]
        tab_y['A_y'] = amp_y[mask_y]
        tab_y['ΔA_y'] = erramp_y[mask_y]
        tab_y['y0'] = centro_y[mask_y]
        tab_y['Δy0'] = errcentro_y[mask_y]
        tab_y['σ_y'] = sig_y[mask_y]
        tab_y['Δσ_y'] = errs_y[mask_y]

        print(tab_y)

        #convertiamo le tabelle in file .csv

        tab_x.to_csv()
        tab_y.to_csv()
        
if __name__ == "__main__":
    main()
