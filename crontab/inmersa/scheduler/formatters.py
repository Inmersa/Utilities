# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

__author__="tite"
__date__ ="$Jul 25, 2014 7:50:52 AM$"

import StringIO
import xlwt
import email
import logging
import urllib

from email.MIMEText import MIMEText
from extractors import TabbedData
from lxml import html

class DataItem(StringIO.StringIO,object):
    _mimeType = None
    _to = None
    Type = None
    SubType = None
    charset = None
    
#    @property
    def get_to(self):
        self.logger.debug("HEREE get_to")
        return self._to
#    @to.setter
    def set_to(self,email,name=None):
        tmpval = email
        if name: tmpval = "%s <%s>" % (name,tmpval)
        self._to = tmpval
    to = property(get_to,set_to)
    
    @property
    def mimeType(self):
        return self._mimeType    
    @mimeType.setter
    def mimeType(self,type):
        self._mimeType = type
        tmp = type.split('/')
        self.Type = tmp[0]
        self.SubType = tmp[1]
    
    def __init__(self,value,type='text/plain'):
        self.logger = logging.getLogger(str(self.__class__))
        StringIO.StringIO.__init__(self,value)
        self.mimeType = type
        
    def suggestedExtension(self):
        self.logger.debug("Suggesting extension for %s subtype %s " % (self.Type,self.SubType))
        if self.Type in ('text'):
            if self.SubType in ('csv'):
                self.logger.debug("Identified csv format %s " % (self.mimeType))
                ext = '.csv'
            elif self.SubType in ('html'):
                self.logger.debug("Identified html format %s " % (self.mimeType))
                ext = '.html'
            else:
                ext = '.txt'
        elif self.Type in ('application'):
            if self.SubType in ('xls'):
                self.logger.debug("Identified xls format %s " % (self.mimeType))
                ext = '.xls'
            else:
                self.logger.debug("Unrecognized application %s " % (self.SubType))
        else:
            self.logger.debug("We dont have an extension!!! ")
            ext = ''
        return ext
        
    
    
    def factoryMIME(self,opts=None):
        rval = None
        self.logger.debug("%s - construyendo mime tipo %s chr %s" % (self,self.mimeType,self.charset))
        if self.Type == 'text':
            if self.SubType == 'html':
                rval = email.MIMEMultipart.MIMEMultipart(None,self.SubType,self.charset)
                tree = html.fromstring(self.getvalue())
                self.logger.debug("tree %s " % (tree))
                attachments = {}
                payload = []
                css = tree.xpath('//link[@rel="stylesheet"]')
                for link in css:
                    self.logger.debug("entities link for css %s from %s " % (link.get('href'),link.base))
                    base = 'http://iempresa.biomundo/escritorio/'
                    if attachments.has_key(link.get('href')): 
                        self.logger.debug("style %s already known" % (link.get('href')))
                        link.set('href',"cid:%s"%attachments[link.get('href')][1])
                        continue
                    tmpfile = urllib.urlopen(base+link.get('href'))
                    tmpid = email.utils.make_msgid()
                    self.logger.debug("Got CSS file : %s " % (tmpid))
                    tmpval = MIMEText(tmpfile.read(),'css',self.charset)
                    tmpval.add_header('Content-ID',tmpid)
                    attachments[link.get('href')] = (tmpval,tmpid)
                    payload.append(tmpval)
#                    rval.attach(tmpval)
                    link.set('href',"cid:%s" %(tmpid[1:-1]))
                css = tree.xpath('//img')
                for link in css:
                    self.logger.debug("img link for css %s from %s " % (link.get('src'),link.base))
                    base = 'http://iempresa.biomundo/escritorio/'
                    if attachments.has_key(link.get('src')):
                        self.logger.debug("image %s already known" % (link.get('src')))
                        link.set('src',"cid:%s"%attachments[link.get('src')][1])
                        continue
                    tmpfile = urllib.urlopen(base+link.get('src'))
                    tmpid = email.utils.make_msgid()
                    self.logger.debug("Got Img file : %s " % (tmpid))
                    tmpval = email.mime.image.MIMEImage(tmpfile.read())
                    tmpval.add_header('Content-ID',tmpid)
                    attachments[link.get('src')] = (tmpval,tmpid)
                    payload.append(tmpval)
#                    rval.attach(tmpval)
                    link.set('src',"cid:%s" %(tmpid[1:-1]))
                rval.set_payload( [MIMEText(html.tostring(tree))]+payload )
#                rval.set_payload(MIMEText(html.tostring(tree)))
#                rval.attach(html.tostring(tree))
#                for k,v in attachments.items():
#                    self.logger.debug("Attaching item %s " % (k))
#                    rval.attach(v[0])
            else:
                rval = MIMEText(self.getvalue(),self.SubType,self.charset)        
            if self.charset: rval.set_charset(self.charset)
            rval.set_type(self.mimeType)            
        else:
            #TODO: this value, as default for everything is not text, is not right!!
            self.logger.debug("be carefull, we are assigning vnd.ms-excel to whatever is not text!")
            rval = email.mime.base.MIMEBase('application','vnd.ms-excel')
            rval.set_payload(self.getvalue())
            email.encoders.encode_base64(rval)
        if opts and len(opts)>0:
            self.logger.debug("We have the following options: %s " % (opts))
            if 'disposition' in opts:
                if 'filename' in opts:
                    tmpstr = opts['disposition']+'; filename="'+opts['filename']+'"'
                else:
                    tmpstr = opts['disposition']
                rval.add_header('Content-Disposition',tmpstr)
        return rval


class DataFormatter(object):
    logger = None
    data = None
    params = None
    items = {}
    
    def __init__(self,Extract,params):
        self.logger = logging.getLogger(str(self.__class__))
        self.params = params
        self._load(Extract)
        
    
    
    def close(self):
        if self.items:
#            self.logger.debug("Items: %s " % (self.items))
            for k in self.items.keys():
                for i in self.items[k]:
                    self.logger.debug("%s: %s Closing data item  => %s " % (self.params.seccion(),k,i))
                    i.close()
                self.logger.debug("%s: deleting key %s " % (self.params.seccion(),k))
                del self.items[k]
            self.logger.debug("%s : resetting all items to {}" % (self.params.seccion()))
            self.items = {}
        else:
            self.logger.debug("%s : odd! we dont have items to close()" % (self.params.seccion()))

    
    
    def add(self,data,mimeType=None,email=None):
        #TODO: need to refactor this to take multiple addresses on the email field
        if not isinstance(data,DataItem): item = DataItem(data,mimeType)
        else: 
            self.logger.debug("%s: recieved an existing instance %s => %s " % (self.params.seccion(),email,data))
            item = data
        if not email: key = 'default'
        else: key = email
        if not self.items.has_key(key) or not self.items[key]: 
            self.logger.debug("%s: key %s does not exist, resetting value " % (self.params.seccion(),key) )
            self.items[key] = []
        else:
            self.logger.debug("%s: luck you! key %s does exist with value %s " % (self.params.seccion(),key,self.items[key]) )
        self.logger.debug("%s: adding item %s => %s " % (self.params.seccion(),key,item) )
        self.items[key].append(item)
        return item
            
    
    
    def getMimeResult (self):
        nombre_out = self.params.getVar('nombre-adjunto')
        fuente = self.params.getVar('fuente')
        sec = self.params.seccion()
        if not nombre_out and fuente:
            if fuente.find('.') != -1:
                aTmp = fuente.split('.')
                nombre_out = aTmp[0] 
            else: nombre_out = fuente 
            
        try:            
            rval = {}
            oCuerpo = None
            for k in self.items.keys():
                if len(self.items[k]) > 1 and not rval.has_key(k):
                    self.logger.debug("%s: Dado que tenemos multiple items, construimos un multipart ya" % (self.params.seccion()))
                    rval[k] = email.MIMEMultipart.MIMEMultipart()
                    
                for mime in self.items[k]:
                    opts = {}
                    #mime = self.items[k]
                    self.logger.debug("%s: iterating over data for destination. now on %s with key %s " % (self.params.seccion(),mime,k))
                    # para construir un mime, basicamente hace falta el tipo, la codificacion, y la disposicion
                    if not mime: continue

                    disp = self.params.param('disposition') or 'none'
                    self.logger.debug("%s: turns out disposition is %s " % (self.params.seccion(),disp))

                    #tipo_mime = self.mimeType
                    #if not tipo_mime or not len(tipo_mime): tipo_mime = 'application/vnd.ms-excel'
                    opts['disposition'] = disp 
                    if disp in ('attachment') and not nombre_out:
                        nombre_out = self.params.seccion()
                    if nombre_out:
                        ext = mime.suggestedExtension() 
                        opts['filename'] = nombre_out+ext 
                        self.logger.debug("%s: We got mime type %s with ext %s " % (self.params.seccion(),mime.mimeType,ext))
                        #TODO: the filename needs to be built/concatenated from parameters
                    tmpval = mime.factoryMIME(opts)

                    if rval.has_key(k): oCuerpo = rval[k]
                    if oCuerpo:
                        self.logger.debug("%s: Since this is a multipart we addup this msg to the multipart" % (self.params.seccion()))
                        oCuerpo.attach( tmpval )
                    else:
                        rval[k] = tmpval

            self.logger.debug("%s) Content-Transfer-Encoding es: %s " % (self.params.seccion(),rval[k].get('Content-Transfer-Encoding')))
            self.logger.debug("%s - Coming back with : %s " % (self.params.seccion(),rval))
            if len(rval.keys())==1 and (rval.keys()[0]=='default' or rval.keys()[0]=='default'=='all'): 
                self.logger.debug("%s - Since there is only one email destination, we return instance instead of list" % (self.params.seccion()))
                rval = rval[rval.keys()[0]]
        except Exception, e:
            # ERROR:
            self.logger.exception("%s - Error running the query" % (self.params.seccion()))
            raise e
        return rval

class ExcelFormat(DataFormatter):
    
    def __init__(self,Extract,params):
        if not Extract or not isinstance(Extract,TabbedData):
            raise Exception("%s the extractor provided (%s) is not TabbedData, hence incompatible with Excel format." % (Extract))
        DataFormatter.__init__(self,Extract,params)
    
    def _load(self,Extract):
        wb = xlwt.Workbook('ISO-8859-15')
        ws = wb.add_sheet(self.params.seccion())
        tmp = Extract.getvalue()
        aVal = tmp[0]
        if tmp[1]: aOrden = tmp[1]
        else: aOrden = None

        bFirst = True
        if len(aVal):
            i = 0
            for dRow in aVal:
                if bFirst:
                    if aOrden and len(aOrden): aKeys = aOrden
                    else: aKeys = dRow.keys()
                    for j in range(len(aKeys)): 
                        ws.write(i,j,aKeys[j])
                    bFirst = False
                i += 1
                j = 0
                for k in aKeys:
                    v = dRow[k]
                    #self.logger.debug("row(%s) col(%s) value(%s) " % (i,k,str(v)))
                    ws.write(i,j,v)
                    j += 1
        item = DataItem(None,'application/xls')
        wb.save(item)
        self.add(item)
        
        


class CSVFormat(DataFormatter):
    logger = None
    charset = 'ISO-8859-15'
    
    def __init__(self,Extract,params):
        if not Extract or not isinstance(Extract,TabbedData):
            raise Exception("%s the extractor provided (%s) is not TabbedData, hence incompatible with CSV format." % (params.seccion(),Extract))
        DataFormatter.__init__(self,Extract,params)

   
    def _load(self,Extract):
        tmp = Extract.getvalue()
        aVal = tmp[0]
        if tmp[1]: aOrden = tmp[1]
        else: aOrden = None

        formattedData = ''
        if len(aVal):
            for dRow in aVal:
                if not len(formattedData):
                    if aOrden and len(aOrden): aKeys = aOrden
                    else: aKeys = dRow.keys()
                    for j in range(len(aKeys)): 
                        if len(formattedData) : formattedData += "\t"
                        formattedData += aKeys[j]
                    formattedData += "\n"
                bTab = False
                for k in aKeys:
                    v = dRow[k]
                    if bTab : formattedData += "\t"
                    formattedData += str(v)
                    bTab = True
                formattedData += "\n"
        self.add(formattedData,'text/csv')
#        self.write(formattedData)
#        self.mimeType = 'text/csv'




class TextFormat(DataFormatter):
    logger = None
    charset = 'ISO-8859-15'
        
    def _load(self,Extract):
        itm = DataItem("",'text/plain')
        itm.write("Execution text-output of job: %s\n" % (self.params.seccion()))
        self.logger.debug("%s: %s chr es: %s " % (self.params.seccion(),itm,self.charset))
#        itm.charset(self.charset)
        itm.write(Extract.getvalue())
        itm.write("------\n")
        self.logger.debug("%s: with value %s " % (self.params.seccion(),itm.getvalue()))
        self.add(itm)


class HTMLFormat(DataFormatter):
    logger = None
    charset = 'ISO-8859-15'
    
    def _load(self,Extract):
        data = Extract.getvalue()
#        if not hasattr(data, '__iter__'): data = [data]
        if isinstance(data, (tuple,str)): data = [data]
        else:
            self.logger.debug("%s data is not a tuple is %s " % (self.params.seccion(),data.__class__))
        for d in data:
            if isinstance(d,tuple):
                item = DataItem(d[0],'text/html')
                if len(d)>1:
                    self.logger.debug("Its a tuple!! %s " % (d[1:]) )
#                    item.set_to(d[1],d[2] or None)
                    key = d[1]
                else:
                    self.logger.debug("Got a tuple, which is a singleton")
                    key = 'default'
#                self.logger.debug("got instance at %s . %s " % (item,item.to))
#                item.para(d[1],d[2])
#                item.to(d[1],d[2])
            else:
                key = 'default'
                item = DataItem(d,'text/html')
            if not self.items.has_key(key) or not self.items[key]: self.items[key] = []
            self.add(item,email=key,mimeType='text/html')
#            self.items[key].append(item)
#            self.logger.debug("formateando : %s " % (d))
#            self.write(d)
#        self.mimeType = 'text/html'


"""
if __name__ == "__main__":
    print "Hello World"
"""