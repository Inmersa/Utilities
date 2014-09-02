# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

__author__="tite"
__date__ ="$Jul 19, 2014 11:33:46 AM$"

import traceback, logging, os, MySQLdb
import subprocess
import urllib2
import urllib
from lxml import html

class DataExtractor(object):
    _aRequiredFields = None
    @property
    def requiredFields(self):
        """ I am the list of required fields """
        return self._aRequiredFields    
    @requiredFields.setter
    def requiredFields(self,value):
        if self.logger: self.logger.debug("aRequiredFields.__set__ con %s " % (str(value)))
#        else: print "aRequiredFields.__set__ con %s " % (str(value))
        if not self._aRequiredFields: self._aRequiredFields = value
        else: self._aRequiredFields += value
    
    _aRequiredPaths = None
    @property
    def requiredPaths(self):
        """ I am the list of required fields """
        return self._aRequiredPaths    
    @requiredPaths.setter
    def requiredPaths(self,value):
        if self.logger: self.logger.debug("aRequiredPaths.__set__ con %s " % (str(value)))
#        else: print "%s aRequiredPaths.__set__ con %s " % (self,str(value))
        if not self._aRequiredPaths: self._aRequiredPaths = value
        else: self._aRequiredPaths += value
        
    _aLocalGroups = None
    @property
    def localGroups(self):
        """ I am the list of required fields """
        return self._aLocalGroups
    @localGroups.setter
    def localGroups(self,value):
        if self.logger: self.logger.debug("localGroups.__set__ con %s " % (str(value)))
#        else: print "localGroups.__set__ con %s " % (str(value))
        if not self._aLocalGroups: self._aLocalGroups = value
        else: self._aLocalGroups += value


    logger = None
    rawData = None
    
    def __init__(self,config):
        self.logger = logging.getLogger(str(self.__class__))
        try:
            self.logger.debug("BEFORE RequiredFields : %s " % (str(self.requiredFields)))
            if isinstance(self.requiredFields,str): self.requiredFields = self.requiredFields,'extractor','formatter'
            else:
                self.requiredFields += ('extractor','formatter')
            self.logger.debug("AFTER RequiredFields : %s " % (str(self.requiredFields)))
            self.logger.debug("AFTER RequiredPaths : %s " % (str(self.requiredPaths)))
            
            if config:
                self.logger.debug("%s: Asignando el atributo params .. %s" %(config.seccion(),config.dCfg))
                self.params = config
                self.logger.debug("%s: hecho. ahora vamos a cargar los parametros: %s " % (self.params.seccion(),self.params.dCfg) )
                self._load()
                self.logger.debug("%s: despues del Job::_load() tenemos esta configuracion : %s " % (self.params.seccion(),self.params.dCfg) )
        except Exception,e:
            self.logger.exception("Errors on constructor!! for %s " % (self.params.seccion()))
            raise e
    
    
    def _load(self):
        self.logger.debug("%s: cargando los campos obligatorios .. %s " % (self.params.seccion(),str(self.requiredFields)))
        if self.requiredFields and len(self.requiredFields):
            #self.logger.debug("%s: with these required fields: %s " % (self.params.seccion(),str(self.requiredFields)) )
            for i in range(len(self.requiredFields)):
                fld = self.requiredFields[i]
                if not fld: continue
                if self.params.has_option(self.params.seccion(),fld):
                    sval = self.params.get(self.params.seccion(),fld)
                else: sval=None
                #self.logger.debug("%s: fld %s => %s" % (self.params.seccion(),fld,sval))

                if fld.find('_') != -1:
                    aTmp = fld.split('_')
                    if len(aTmp) > 1:
                        if sval: self.params.setCfgVarFromGroup(aTmp[0],aTmp[1],sval)
                        val = self.params.getCfgVarFromGroup(aTmp[0],aTmp[1])
                        if not val:
                            self.logger.error("Campo obligatorio %s no cumplimentado " % (fld))
                            raise Exception("Campo obligatorio %s no cumplimentado " % (fld))
                else:
                    if sval: 
                        #NOTE: looks like I didnt want to use the has_option method, so I use other container for the config
                        #   it might have to do with collection the values and then assigning them to the source structure
                        #   for the rest of the code to pickup
                        #self.logger.debug("%s: assigning fld %s => %s" % (self.params.seccion(),fld,sval))
                        self.params.setCfgVar(fld,sval)
                    val = self.params.getCfgVar(fld)
                    #self.logger.debug("%s: second try for fld %s => %s" % (self.params.seccion(),fld,val))
                    if not val:
                        self.logger.error("Campo obligatorio %s no cumplimentado " % (fld))
                        raise Exception("Campo obligatorio %s no cumplimentado " % (fld))
        self.logger.debug("%s: cargando los directorios obligatorios .. %s " % (self.params.seccion(),str(self.requiredPaths)))
        if self.requiredPaths and len(self.requiredPaths):
            for i in range(len(self.requiredPaths)):
                tmppath = self.requiredPaths[i]
                if not tmppath: continue
                if self.params.has_option(self.params.seccion(),tmppath): sval = self.params.get(self.params.seccion(),tmppath)
                else: sval=None
                self.logger.debug("%s: path actual es %s " % (self.params.seccion(),tmppath))
                if tmppath.find('_') != -1:
                    self.logger.debug("Que putada! tener circuito distinto pa esto")
                    aTmp = tmppath.split('_')
                    if len(aTmp) > 1:
                        if sval: self.params.setCfgVarFromGroup(aTmp[0],aTmp[1],sval)
                        val = self.params.getCfgVarFromGroup(aTmp[0],aTmp[1])
                        if not val:
                            self.logger.error("Campo obligatorio %s no cumplimentado " % (tmppath))
                            raise Exception("Campo obligatorio %s no cumplimentado " % (tmppath))
                        if not os.path.isdir(val):
                            self.params.setCfgVarFromGroup(aTmp[0],aTmp[1],None)
                            self.logger.error("Campo obligatorio %s no cumplimentado " % (val))
                            raise Exception("Campo obligatorio %s no cumplimentado " % (val))
                            continue
                else:
                    if sval: self.params.setCfgVar(tmppath,sval)
                    val = self.params.getCfgVar(tmppath)
                    if not val:
                        val = self.params.param(tmppath)
                    if not val:
                        self.logger.error("Campo obligatorio %s no cumplimentado " % (tmppath))
                        raise Exception("Campo obligatorio %s no cumplimentado " % (tmppath))
                    if not os.path.isdir(val):
                        self.params.setCfgVarFromGroup(aTmp[0],aTmp[1],None)
                        self.logger.error("Campo obligatorio %s no cumplimentado " % (val))
                        raise Exception("Campo obligatorio %s no cumplimentado " % (val))
                        continue
        self.logger.debug("%s: cargando los grupos locales obligatorios .. " % (self.params.seccion()))
        if self.localGroups and len(self.localGroups):
            self.params.mainConfigOptions = self.params.options(self.params.seccion())
            for i in range(len(self.params.mainConfigOptions)):
                #self.logger.debug("%s tenemos este grupete? %s " % (self.params.seccion(),self.params.mainConfigOptions))
                if self.params.mainConfigOptions[i].find('_') == -1:
                    self.params.dCfg[self.params.mainConfigOptions[i]] = self.params.get(self.params.seccion(),self.params.mainConfigOptions[i])
                else:
                    aTmp = self.params.mainConfigOptions[i].split('_')
                    if len(aTmp) > 1:
                        if aTmp[0] in self.localGroups:
                            if not self.params.dCfg.has_key(aTmp[0]) or isinstance(self.params.dCfg[aTmp[0]],dict) : self.params.dCfg[aTmp[0]] = {}
                            self.params.dCfg[aTmp[0]][aTmp[1]] = self.params.get(self.params.seccion(),self.params.mainConfigOptions[i])
                        else: self.params.dCfg[self.params.mainConfigOptions[i]] = self.params.get(self.params.seccion(),self.params.mainConfigOptions[i])
        self.logger.debug("%s: FIN de _load .. " % (self.params.seccion()))
    
    
    
    
    def getvalue(self):
        return self.rawData



class TabbedData(DataExtractor):
    pass

class SQLFileQuery (TabbedData):
    resultSet = None
    resultOrder = None

    def __init__ (self,oCfg,seccion=None):
        self.requiredFields = ('mysql_server','mysql_user','mysql_pass','mysql_dbase','fuente')
        self.requiredPaths = ('sql_path','base-path')
        self.localGroups = ('mysql',)
        DataExtractor.__init__ (self,oCfg)
        dMysql = self.params.getCfgGroup('mysql')
        self.logger.debug("Conex: %s " % dMysql)
    
    
    def extract(self):
        fuente = self.params.getVar('fuente')
        self.logger.debug("con param %s "%(fuente))
        path = self.params.getCfgVarFromGroup('sql','path')
        if not path or not fuente or not os.path.isfile(path + '/' + fuente):
            #TODO: convert this into a raised exception
            txt = "%s : No se ha posido localizar el fichero (%s/%s) " % (self.params.seccion(),path,fuente)
            self.logger.error(txt)
            raise Exception(txt)
        dMysql = self.params.getCfgGroup('mysql')
        file = path + '/' + fuente
        
        self.logger.debug("%s : Abriendo file %s " % (self.params.seccion(),file))
        f = open(file,'r')
        consulta = f.read()
        f.close()
        self.logger.debug("%s : Query obtenida. Conectando .." % (self.params.seccion()))
        oDb = MySQLdb.connect(host=dMysql['server'],user=dMysql['user'],passwd=dMysql['pass'],db=dMysql['dbase'],port=int(dMysql['port']))
        c = oDb.cursor(MySQLdb.cursors.DictCursor)
        
        self.logger.debug("%s : Conectado." % (self.params.seccion()))
        aTmp = consulta.split(";\n")
        for cons in aTmp:
            tmpcons = cons.replace(" ","")
            if not tmpcons or not len(tmpcons): continue
            tmpcons = cons.replace("\n","")
            if not tmpcons or not len(tmpcons): continue
            self.resultOrder = []
            try:
                self.logger.debug("%s : Running query:\n%s" % (self.params.seccion(),cons))
                c.execute(cons)
                self.logger.debug("%s : query ran with count %s" % (self.params.seccion(),c.rowcount))
                aVal = c.fetchall()
                if c.description and len(c.description):
                    for d in c.description: 
                     self.resultOrder.append(d[0])
            except Exception,e:
                aVal = [{'Error':str(e),'Consulta':cons,'file':file,'path':path}]
                raise e
                
            self.resultSet = list()
            if aVal and len(aVal):
                for val in aVal: 
                    if val and len(val): 
                        self.resultSet.append(val)
            if self.resultOrder and len(self.resultOrder): self.resultOrder = self.resultOrder
    
    
    def getvalue(self):
        return (self.resultSet,self.resultOrder)


class HTMLFetch (DataExtractor):
    #FIXME: same as TODO
    #TODO: This class needs to be able to iterate over the downloaded HTML and 
    #   rewrite all href attributes on the IMG and CSS entities into cid: entries
    #   for the multypart mime to take them from within the message, instead of an
    #   url which in most cases will be unreachable. 
    """
    FIXME: same as TODO
    TODO: this class needs to retrieve all the img and css objects from the 
        downloaded html file in order to add them to the ifnal multipart via cids
    """
    
    def __init__(self,params):
        self.requiredFields = ('servidor',)
        self.localGroups = ('form','get')
        DataExtractor.__init__(self,params)

    
    
    def url(self):
        servername = self.params.getCfgVar('servidor')
        relurl = self.params.getVar('url-relativa')
        if not relurl: url = servername
        else: url = servername + '/' + relurl
        return url
        
    def extract (self):
        #servername = self.params.getCfgVar('servidor')
        #relurl = self.params.getVar('url-relativa')
        #if not relurl: url = servername
        #else: url = servername + '/' + relurl
        url = self.url()

        #Obtenemos Variables POST
        vars = self.params.getVar('form','vars')
        self.logger.debug("%s : POST variables on the html form: %s " % (self.params.seccion(),vars))
#        vars = self.params.getVar('form_vars')
#        self.logger.debug("%s : POST variables on the html form: %s " % (self.params.seccion(),vars))
        dTmp = {}
        if vars and len(vars):
            aTmp = vars.split(' ')
            for vname in aTmp: 
                dTmp[vname] = self.params.getVar(vname)
                sec = self.params.seccion()
                if not dTmp[vname] and sec and self.oConfig.has_option(sec,vname): dTmp[vname] = self.oConfig.get(sec,vname)
            encodedform = urllib.urlencode(dTmp)
        else: encodedform = ''
        self.logger.debug("%s : the encoded form is %s " % (self.params.seccion(),encodedform))
        
        #Obtenemos Variables GET
        vars = self.params.getVar('get','vars')
        self.logger.debug("%s : GET variables on the html form: %s " % (self.params.seccion(),vars))
        dTmp = {}
        if vars and len(vars):
            aTmp = vars.split(' ')
            for vname in aTmp: 
                dTmp[vname] = self.params.getVar(vname)
                sec = self.params.seccion()
                if not dTmp[vname] and sec and self.oConfig.has_option(sec,vname): dTmp[vname] = self.oConfig.get(sec,vname)
            encodedget = '?'+urllib.urlencode(dTmp)
        else: encodedget = ''

        try:
            self.logger.debug("%s : Grabbing from %s " % (self.params.seccion(),'http://'+url+encodedget))
            full_url = 'http://'+url+encodedget
            file = urllib2.urlopen(full_url,encodedform)
            self.rawData = (html.fromstring(file.read(),base_url="http://%s"%(url)),) 
#            file = urllib2.urlopen('http://'+url+encodedget,encodedform)
#            self.rawData = file.read()
            
#            self.htmlData = html.fromstring(file.read(),base_url="http://%s"%(url)) 
            file.close()
        except Exception,e:
            htmltxt = "No se pudo abrir la url %s :=> %s " % ('http://'+url+encodedget,str(e))
            self.logger.exception(htmltxt)
            raise e
        #self.logger.debug("%s: yielded result :\n%s" % (self.params.seccion(),self.rawData))

class SQLValuesToWebFetch (SQLFileQuery):
    #TODO: This should not be a straight assignment, but a call to a class 
    #   method that will check if the entries exist already, and not a 
    #   reassignment, since when inheriting you could loose values
    
    def __init__(self,params):
        self.requiredFields = ('servidor',)
        self.localGroups = ('form','get')
        SQLFileQuery.__init__(self,params)
        
    def getvalue(self):
        return self.rawData
    
    def extract(self):
        self.logger.debug("%s: Since the HTML is based on a query, let's run the parent first. " % (self.params.seccion()))
        SQLFileQuery.extract(self)
        
        servername = self.params.getCfgVar('servidor')
        relurl = self.params.getVar('url-relativa')
        nombre_out = self.params.getVar('nombre-adjunto')
        sec = self.params.getVar('__seccion__')
        if not nombre_out: nombre_out = servername
        if not relurl: url = servername
        else: url = servername + '/' + relurl

        bSQLGet = False
        transport = self.params.getVar('sqldata-transport')
        if not transport or transport not in ('post','get'):
            self.logger.warn("unknown transport %s , using post " % (transport))
            transport = 'post'
        prefix = self.params.getVar('fuentesql-prefijo')
        emailfld = self.params.getVar('sqldata-email')
        data = SQLFileQuery.getvalue(self)[0]
        self.rawData = []
        
        self.logger.debug("data contiene %s " % (data))
        for n in range(len(data)):
            aV = data[n]
#            if prefix: nombre_file = prefix + ' ' +  str(n)
#            else: nombre_file = nombre_out + str(n)
            #Obtenemos Variables POST
            vars = self.params.getVar('form','vars')
            self.logger.debug("iterating over POST variables .. %s " % (vars))
            dTmp = {}
            if transport == 'post':
                aTmp = aV.keys()
                for k in aTmp:
                    if (not emailfld or emailfld != k):
                        self.logger.debug("Sumando campo %s al post: %s " % (k,aV[k]))
                        dTmp[k] = aV[k]
                if vars and len(vars):
                    aTmp = vars.split(' ')
                    for vname in aTmp: 
                        dTmp[vname] = self.params.getVar(vname)
                        sec = self.params.seccion()
                        if not dTmp[vname] and sec and self.params.has_option(sec,vname): dTmp[vname] = self.params.get(sec,vname)
                if len(dTmp)>0: encodedform = urllib.urlencode(dTmp)
            else: encodedform = ''
            #Obtenemos Variables GET
            self.logger.debug("iterating over GET variables .. %s " % (vars))
            vars = self.params.getVar('get','vars')
            dTmp = {}
            if transport == 'get':
                aTmp = aV.keys()
                for k in aTmp:
                    if (not emailfld or emailfld != k):
                        dTmp[k] = aV[k]
            if vars and len(vars):
                aTmp = vars.split(' ')
                for vname in aTmp: 
                    dTmp[vname] = self.params.getVar(vname)
                    sec = self.params.seccion()
                    if not dTmp[vname] and sec and self.params.has_option(sec,vname): dTmp[vname] = self.params.get(sec,vname)
                encodedget = '?'+urllib.urlencode(dTmp)
            else: encodedget = ''

            try:
                self.logger.debug("%s : Grabbing url %s with form: %s " % (self.params.seccion(),'http://'+url+encodedget,encodedform))
                full_url = 'http://'+url+encodedget
                file = urllib2.urlopen(full_url,encodedform)
                tmpval = (html.fromstring(file.read(),base_url="http://%s"%(url)),) 
                if emailfld:
                    if aV.has_key(emailfld): 
                        tmpval += (aV[emailfld],)
#                self.logger.debug("%s : ideally this would be for %s <%s>" % (self.params.seccion(),tmpval[1],tmpval[2]))
                self.rawData.append( tmpval )
#                self.logger.debug(self.rawData[-1])
                file.close()
            except Exception,e:
                html_txt = "No se pudo abrir la url %s :=> %s " % ('http://'+url+encodedget,str(e))
                self.logger.exception(html_txt)
                raise e


class SysExec (DataExtractor):
    
    def __init__(self,params):
        self.requiredFields = ('fuente',)
        self.requiredPaths = ('scripts-path',)
        self.localGroups = ('form','get')
        DataExtractor.__init__(self,params)
        
    def extract(self):        
        fuente = self.params.getVar('fuente')
        path = self.params.getCfgVar('scripts-path')
        self.logger.debug("%s: script will be %s at %s " % (self.params.seccion(),fuente,path))
        if os.path.isfile(path + '/' + fuente):
            try:
                self.logger.debug("%s Running .. " % (self.params.seccion()))
                cmd = path + '/' + fuente
                #p = os.popen(cmd,stdout=PIPE,stderr=PIPE)
                #p = subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
                p = subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
                #txt = p.read()
                self.rawData, errout = p.communicate()
                if p.returncode != 0:
                    tmpstr = "%s: %r failed, status code %s stdout %r stderr %r" % (self.params.seccion(), cmd, p.returncode, self.rawData, errout)
                    self.logger.error(tmpstr)
                    raise Exception(tmpstr)
                if errout:
                    if not self.rawData: self.rawData = ''
                    self.rawData += errout
                #p.close()
                self.logger.debug("%s output: %s o %s con %s " % (self.params.seccion(),self.rawData,p.returncode,errout))
                # self.logger.debug("output 2 : %s " % (txt.splitlines()))
                #oCuerpo = MIMEText(txt)
            except Exception,e :
                self.logger.exception("%s: Error ejecutando %s/%s" % (self.params.seccion(),path,fuente))
                raise e
        else: return None

    

