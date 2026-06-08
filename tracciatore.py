import numpy as np
import scipy as sp
import sys

'''
definisco una classe per simulare il tracciatore ed il passaggio attraverso
esso di un muone
'''

class trac:
    '''
    questa classe simula il tracciatore, ed il passaggio attraverso questo di
    un muone

    sp = spessore piani di silicio
    n = numero di piani
    d = distanza tra i piani
    s = simensione degli elementi discreti di rivelazione
    v = velocità del muone incidente
    chi = lunghezza di radiazione del materiale che costituisce il sensore
    pos = dizionario che contiene le coordinate xyz del muone quando esce da un
          piano e quando entra in quello successivo
    theta = dizionario che contiene i valori degli angoli del muone nel piano
            zy, zx e nello spazio
    errpos = dizionario che contiene le incertezze sulle coordinate x e y
             del muone
    '''
    def __init__(self):
        self.sp = 1
        self.n = 1
        self.d = 1
        self.s = 1
        self.chi = 1
        self.pos = {0 : 0}
        self.theta = {0 : 0}
        self.errpos = {0 : 0}
        
    def riv(self, sp, n, d, s, chi):
        self.sp = sp
        self.n = n
        self.d = d
        self.s = s
        self.chi = chi


    def cammino(self, v, xy, m):
        '''
        funzione che usa lo scattering coulombiano multiplo per calcolare
        il percorso di una particella carica attraverso il tracciatore

        le particelle da rivelare hanno velocità relativistiche

        p = m*gamma*v
        xy = coordinate x e y della particella quando raggiunge il tracciatore
             la coordinata z è inizialmente uguale a zero, per tutte
             le particelle
             xy = np.array([x, y])
        '''
        c = sp.constants.c
        b = v/c
        gamma = (1 - b**2)**(-0.5)
        p = m*gamma*v
        th0 = (13.6/(b*c*p))*((self.sp/self.chi)**0.5)*(1 + 0.038*np.log(self.sp/(self.chi*b**2)))
        '''
        calcolo il cammino del muone in blocchi (piano + spazio vuoto)
        calcolo l'angolo e la posizione y del muone una volta che
        questo ha attraversato il piano rivelatore.
        Poi calcolo la posizione y che il muone ha quando raggiungie
        il piano rivelatore successivo (l'angolo incidente è lo stesso
        che la particella aveva dopo aver attraversato il piano precedente)

        creo un dizionario che contiene le coordinate xyz del muone,
        insieme all'angolo della sua direzione nello spazio.
        creo anche un array per gli angoli nei piani zy e zx
        '''
        thx = np.array([0])
        thy = np.array([0])
        y = np.array([xy[1]])
        x = np.array([xy[0]])
        z = np.array([0])
        for i in range(0, self.n-1):
            z1 = np.random.normal(0, 1, 2)
            z2 = np.random.normal(0, 1, 2)
            #calcolo la posizione y e l'angolo nel piano zy e l'angolo di
            #uscita dal piano
            yy = y[-1] + z1[0]*self.sp*th0/(12)**0.5 + z2[0]*self.sp*th0/2
            th_y = thy[-1] + z2[0]*th0
            #calcolo la posizione x
            xx = x[-1] + z1[1]*self.sp*th0/(12)**0.5 + z2[1]*self.sp*th0/2
            th_x = thx[-1] + z2[1]*th0
            #coordinata z
            zz = z[-1] + self.sp
            #coordinate xyz del muone dopo aver appena attraversato un piano
            y = np.append(y, yy)
            x = np.append(x, xx)
            z = np.append(z, zz)
            thx = np.append(thx, th_x)
            thy = np.append(thy, th_y)
            #coordinate xyz del muone quando raggiunge il piano successivo
            xxx = np.tan(th_x)*self.d + xx
            yyy = np.tan(th_y)*self.d + yy
            zzz = zz + self.d
            x = np.append(x, xxx)
            y = np.append(y, yyy)
            z = np.append(z, zzz)

        #creo un dizionario contenente i valori degli angoli theta sul piano
        #zy, zx e nello spazio
        #faccio lo stesso per la posizione xyz del muone
        th = (thx**2 + thy**2)**0.5
        self.theta = {}
        self.pos = {}
        for i in range(len(y)):
            po = np.array([x[i], y[i], z[i]])
            self.pos.update({i : po})
        for i in range(len(thy)):
            the = np.array([thx[i], thy[i], th[i]])
            self.theta.update({i : the})
        '''
        aggiungo l'incertezza alle coordinate xy del muone
        non aggiungo un incertezza alla coordinate z perchè non vengono
        misurate dal rivelatore. Dal punto di vista matematico la coordinata
        z del muone viene trattata come un parametro.
        '''
        delta = self.s/12**0.5
        self.errpos = {}
        for i in range(len(self.pos)):
            err = np.array([delta, delta])
            self.errpos.update({i : err})
        return self.pos, self.theta, self.errpos

sys.path.append('/home/lunlun/MCF/esame-MCF')
