# class encapsulating a loader for pi loadcell data
# ross lazarus 7 june 2019

import pandas as pd

import matplotlib as mpl
mpl.use('Agg') # headless!
from matplotlib import rcParams
rcParams.update({'figure.autolayout': True})
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime
import time
import sys
import os
from dateutil import tz
from tzlocal import get_localzone
tzl = get_localzone().zone
mdates.rcParams['timezone'] = tzl
NSD = 2.0

class loadCellData():

    def __init__(self,nsd,infi):
        self.started = time.time()
        self.tzl = tzl
        self.nsd = nsd
        self.have_cache = False
        if infi:
            self.infile = infi
        else:
            self.infile = '/home/ross/rossgit/plotlydash-flask-tutorial/data/loadcellsample55k.xls'
        df = pd.read_csv(self.infile,sep='\t')
        try:
            df['date'] = pd.to_datetime(df.iloc[:,0],unit='s')
        except:
            try:
                df['date'] = pd.to_datetime(df.iloc[:,0],format='%Y%m%d_%H%M%S')
            except:
                print('~~~~ cannot figure out date format')
        df.set_index(df['date'],inplace=True)
        df = df.tz_localize(tz=self.tzl)
        self.df = df.sort_index()
        ms = 2
        nrow = self.df.shape[0]
        if nrow > 1000:
            ms = 1
        if nrow > 10000:
            ms = 0.5
        if nrow > 100000:
            ms = 0.2
        self.ms = ms
        self.nrow = nrow
        self.trimcl()
 
    def trimcl(self):
        """ trim +/-nsd SD and ignore first IGSEC data as load cell settles a bit
        """
        firstone = float(self.df.iloc[0,0])
        firsttime = time.strftime('%H:%M:%S %d/%m/%Y',time.localtime(firstone))
        lastone = float(self.df.iloc[-1,0]) # easier to use the original epoch rather than the internal datetimes!
        lasttime = time.strftime('%H:%M:%S %d/%m/%Y',time.localtime(lastone))
        self.fstamp = time.strftime('%Y%m%d_%H%M%S',time.localtime(lastone))
        self.firsttime = firsttime
        self.lasttime = lasttime  
        if self.nsd:
            mene = self.df.iloc[:,1].mean()
            ci = self.df.iloc[:,1].std()*self.nsd
            ucl = mene + ci
            lcl = mene - ci
            notbig = self.df.iloc[:,1] < ucl
            df2 = self.df[notbig]
            notsmall = df2.iloc[:,1] > lcl
            df2 = df2[notsmall]
            nhi = sum(notbig==False)
            nlo = sum(notsmall==False)
            s = 'Trim +/- %.1f SD removed %d above %.2f and %d below %.2f\n' % (self.nsd,nhi,ucl,nlo,lcl)
            s2 = '##Before trim:\n %s\nAfter trim:\n %s' % (self.df.describe(),df2.describe())
            self.df = df2.sort_index()
        else:
            s = 'Raw untrimmed data'
            s2 = '##Raw:\n%s' % (self.df.describe())
        self.note = s2
        self.subt = s
