#!/usr/bin/env python
'''
basic modules to make, print tgraphs
20150921 

'''
import time
import datetime
import sys
import os
import math
import ROOT 
from ROOT import TH1D, TFile, gROOT, TCanvas, TLegend, TGraph, TDatime, TMultiGraph, gStyle, TGraphErrors, TLine
from array import array

class graphUtils():
    def __init__(self):
    # use in color()
        self.goodColors = [x for x in range(1,10)]
        self.goodColors.extend( [11, 12, 18] )
        self.goodColors.extend( [x for x in range(28,50)] )
        self.goodMarkers = [x for x in range(20,31) ]
        return
    
    def t2dt(self,t):
        '''
        convert struct_time to datetime object
        '''
        return datetime.datetime.fromtimestamp(time.mktime(t))
    def dt2t(self,dt):
        '''
        convert datetime object to struct_time (time object)
        '''
        fmt = "%Y %M %d %H %m %S"
        return time.strptime(dt.strftime(fmt),fmt)
    def addSeconds(self,t,seconds=0):
        '''
        add seconds to struct_time t by converting to datetime object,
        using timedelta and converting back
        '''
        dt = self.t2dt(t)
        dt += datetime.timedelta(seconds=seconds)
        return self.dt2t(dt)
    def convertTime(self,day,fmt,text):
        c = text.count(":")
        if c==1: return time.strptime(day+text,fmt+"%H:%M")
        if c==2: return time.strptime(day+text,fmt+"%H:%M:%S")
        sys.exit("graphUtils.convertTime ERROR Unknown input " + str(text))
        return
    def fixTimeDisplay(self,g,showDate=False):
        '''
        set time axis to display nicely
        '''
        if g:
            g.GetXaxis().SetTimeDisplay(1)
            g.GetXaxis().SetTimeFormat("%H:%M")
            if showDate: g.GetXaxis().SetTimeFormat("#splitline{%H:%M}{%y/%m/%d}")
            g.GetXaxis().SetNdivisions(-409)
            g.GetXaxis().SetLabelSize(0.025) #0.5*lx)
#            g.GetXaxis().SetTimeOffset(0,"gmt") # using gmt option gives times that are only off by 1 hour on tgraph
        else:
            print 'graphUtils.fixTimeDisplay: WARNING Null pointer passed to fixTimeDisplay?????'
        return

    def makeTH1D(self,v,title,name,nx=100,xmi=1,xma=-1):
        if xmi>xma:
            xmi = min(v)
            xma = max(v)
        dx = (xma-xmi)/float(nx)
        xmi -= dx/2.
        xma += dx/2.
        h = TH1D(name,title,nx,xmi,xma)
        for y in v: h.Fill(y)
        return h

    def drawGraph(self,g,figDir=""):
        '''
        output graph to file
        '''
        title = g.GetTitle()
        name  = g.GetName()
        pdf   = figDir + name + '.pdf'
    
        xsize,ysize = 1100,850 # landscape style
        noPopUp = True
        if noPopUp : gROOT.ProcessLine("gROOT->SetBatch()")
        canvas = TCanvas(pdf,title,xsize,ysize)
    
        g.Draw()
    
        canvas.Draw()
        canvas.SetGrid(1)
        canvas.SetTicks(1)
        canvas.cd()
        canvas.Modified()
        canvas.Update()
        canvas.Print(pdf,'pdf')
        return
    def drawMultiGraph(self,TMG,figdir='',SetLogy=False, abscissaIsTime = True, drawLines=True):
        '''
        draw TMultiGraph with legend and output as pdf
        Default is that abscissa is calendar time.
        
        '''
        debugMG = False
        if not TMG.GetListOfGraphs(): return  # empty
        title = TMG.GetTitle()
        name  = TMG.GetName()
        if SetLogy: name += '_logy'
        if debugMG: print 'graphUtils.multiGraph',title,name,'TMG.GetListOfGraphs()',TMG.GetListOfGraphs(),'TMG.GetListOfGraphs().GetSize()',TMG.GetListOfGraphs().GetSize()
        nGraphs = TMG.GetListOfGraphs().GetSize()

        



        pdf = figdir + name  + '.pdf'
        ps  = figdir + name  + '.ps'
        xsize,ysize = 1100,850 # landscape style
        noPopUp = True
        if noPopUp : gROOT.ProcessLine("gROOT->SetBatch()")
        canvas = TCanvas(pdf,title,xsize,ysize)
        canvas.SetLogy(SetLogy)


        # move title to left in order to put legend above plot
        gStyle.SetTitleX(0.3)
        x1 = 0.5
        x2 = x1 + .5
        y1 = 0.9
        y2 = y1 + .1
        lg = TLegend(x1,y1,x2,y2) 
        for g in TMG.GetListOfGraphs():
            t = g.GetTitle()
            lg.AddEntry(g, t, "lp" )
            if abscissaIsTime : self.fixTimeDisplay(g)

        dOption = "AP"
        if drawLines: dOption += "L"

        # complicated monkey business because of idiotic way that logY is set
        if SetLogy:
            ymi,yma = 1.e20,1.e-20
            for g in TMG.GetListOfGraphs():
                ymi = min(ymi,g.GetYaxis().GetXmin())
                yma = max(yma,g.GetYaxis().GetXmax())
            if ymi<=0: ymi = 0.1
            TMG.SetMinimum(ymi)
            TMG.SetMaximum(yma)
            for g in TMG.GetListOfGraphs():
                g.SetMinimum(ymi)
                g.SetMaximum(yma)
                g.Draw(dOption)
                dOption = dOption.replace("A","")
            

        else:
            TMG.Draw(dOption)
            if abscissaIsTime : self.fixTimeDisplay(TMG)


        self.labelTMultiGraph(TMG)
        lg.Draw()
        canvas.Draw()
        canvas.SetGrid(1)
        canvas.SetTicks(1)
        canvas.cd()
        canvas.Modified()
        canvas.Update()
        if 0:
            canvas.Print(pdf,'pdf')
        else:
            canvas.Print(ps,'Landscape')
            os.system('ps2pdf ' + ps + ' ' + pdf)
            if os.path.exists(pdf): os.system('rm ' + ps)

        return
    def makeTMultiGraph(self,name,tit=None):
        title = tit
        if tit is None:title = name.replace('_',' ')
        tmg = TMultiGraph()
        tmg.SetName(name)
        tmg.SetTitle(title)
        return tmg
    def labelTMultiGraph(self,tmg):
        name = tmg.GetName()
        if 'vs' in name:
            s = name.split('_')
            xt = s[2]
            yt = s[0]
            xt = xt.replace('by','/')
            xt = xt.replace('BY','/')
            yt = yt.replace('by','/')
            yt = yt.replace('BY','/')
            tmg.GetXaxis().SetTitle(xt)
            tmg.GetYaxis().SetTitle(yt)
        return
    def makeTGraph(self,u,v,title,name,ex=None,ey=None):
        if ex is None:
            g = TGraph(len(u),array('d',u), array('d',v))
        else:
            dy = ey
            if ey is None: dy = [0. for x in range(len(ex))]
            g = TGraphErrors(len(u),array('d',u),array('d',v),array('d',ex),array('d',dy))
        g.SetTitle(title)
        g.SetName(name)
        return g
    def color(self,obj,n,M,setMarkerColor=False):
        '''
        set line color and marker type for obj based on indices n and M
        if M=n then use M to set marker type, otherwise determine marker type from n
        '''
        debug = False
        LC = len(self.goodColors)
        LM = len(self.goodMarkers)
        c = n%LC
        obj.SetLineColor( self.goodColors[c] )
        if debug: print 'color: obj',obj,'n',n,'obj.IsA().GetName()',obj.IsA().GetName()
        if obj.IsA().GetName()=='TGraph':
            if M==n:
                m = M%LM
            else:
                m = int(float(n)/float(LC))%LM
            obj.SetMarkerStyle( self.goodMarkers[m] )
            if setMarkerColor: obj.SetMarkerColor( self.goodColors[c] )
            if debug: print 'color: m',m,'self.goodMarkers[m]',self.goodMarkers[m]
        return