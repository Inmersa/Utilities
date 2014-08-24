#!/usr/bin/python

import sys
import os
import string
import datetime
from types import *

import MySQLdb
import urllib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEImage import MIMEImage

class CrontabParams :
    mainsection = 'General'
    __dCfgGroups = {}
    __dCfgVars = {}
    aRequiredFields = None
    aRequiredPaths = None
    dCfg = {}
    aLocalGroups = None
    bStatusOK = True
    oConfig = None

    def __init__ (self,oCfg,seccion):
        tmpOpts = oCfg.options(self.mainsection)
        if not len(tmpOpts): 
            self.bStatusOK = False
            return None
        self.dCfg = {}
        self.__dCfgGroups = {}
        self.__dCfgVars = {}

        self.dCfg['__seccion__'] = seccion
        self.oConfig = oCfg

        for i in range(len(tmpOpts)):
            if tmpOpts[i].find('_') != -1:
                aTmp = tmpOpts[i].split('_')
                if len(aTmp) > 1:
                    if not self.__dCfgGroups.has_key(aTmp[0]): self.__dCfgGroups[aTmp[0]] = {}
                    if oCfg.has_option(seccion,tmpOpts[i]):
                        self.__dCfgGroups[aTmp[0]][aTmp[1]] = oCfg.get(seccion,tmpOpts[i])
                    else:
                        self.__dCfgGroups[aTmp[0]][aTmp[1]] = oCfg.get(self.mainsection,tmpOpts[i])
            else:
                if oCfg.has_option(seccion,tmpOpts[i]):
                    self.__dCfgVars[tmpOpts[i]] = oCfg.get(seccion,tmpOpts[i])
                else:
                    self.__dCfgVars[tmpOpts[i]] = oCfg.get(self.mainsection,tmpOpts[i])

        if self.aRequiredFields and len(self.aRequiredFields):
            for i in range(len(self.aRequiredFields)):
                fld = self.aRequiredFields[i]
                if not fld: continue
                if oCfg.has_option(seccion,fld):
                    sval = oCfg.get(seccion,fld)
                else: sval=None

                if fld.find('_') != -1:
                    aTmp = fld.split('_')
                    if len(aTmp) > 1:
                        if sval: self.setCfgVarFromGroup(aTmp[0],aTmp[1],sval)
                        val = self.getCfgVarFromGroup(aTmp[0],aTmp[1])
                        if not val:
                            print "Campo obligatorio ",fld," no cumplimentado "
                            self.bStatusOK = False
                            return None
                else:
                    if sval: self.setCfgVar(fld,sval)
                    val = self.getCfgVar(fld)
                    if not val:
                        print "Campo obligatorio ",fld," no cumplimentado "
                        self.bStatusOK = False
                        return None

        if self.aRequiredPaths and len(self.aRequiredPaths):
            for i in range(len(self.aRequiredPaths)):
                tmppath = self.aRequiredPaths[i]
                if not tmppath: continue
                if oCfg.has_option(seccion,tmppath): sval = oCfg.get(seccion,tmppath)
                else: sval=None

                if tmppath.find('_') != -1:
                    aTmp = tmppath.split('_')
                    if len(aTmp) > 1:
                        if sval: self.setCfgVarFromGroup(aTmp[0],aTmp[1],sval)
                        val = self.getCfgVarFromGroup(aTmp[0],aTmp[1])
                        if not val:
                            print "Campo obligatorio ",tmppath," no cumplimentado "
                            self.bStatusOK = False
                            return None
                        if not os.path.isdir(val):
                            self.setCfgVarFromGroup(aTmp[0],aTmp[1],None)
                            print "Path inexistente ",val
                            continue
                else:
                    if sval: self.setCfgVar(tmppath,sval)
                    val = self.getCfgVar(tmppath)
                    if not val:
                        print "Campo obligatorio ",tmppath," no cumplimentado ", val
                        self.bStatusOK = False
                        return None
                    if not os.path.isdir(val):
                        self.setCfgVarFromGroup(aTmp[0],aTmp[1],None)
                        print "Path inexistente ",val
                        self.bStatusOK = False
                        continue

        if self.aLocalGroups and len(self.aLocalGroups):
            tmpOpts = oCfg.options(seccion)
            for i in range(len(tmpOpts)):
                if tmpOpts[i].find('_') == -1:
                    self.dCfg[tmpOpts[i]] = oCfg.get(seccion,tmpOpts[i])
                else:
                    aTmp = tmpOpts[i].split('_')
                    if len(aTmp) > 1:
                        if aTmp[0] in self.aLocalGroups:
                            if not self.dCfg.has_key(aTmp[0]) or type(self.dCfg[aTmp[0]]) is not DictType: self.dCfg[aTmp[0]] = {}
                            self.dCfg[aTmp[0]][aTmp[1]] = oCfg.get(seccion,tmpOpts[i])
                        else: self.dCfg[tmpOpts[i]] = oCfg.get(seccion,tmpOpts[i])
   
    def getCfgGroup (self,gname):
        if not gname: return None
        if not self.__dCfgGroups.has_key(gname): return None
        return self.__dCfgGroups[gname]

    def getCfgVar (self,vname):
        if not vname: return None
        if not self.__dCfgVars.has_key(vname): return None
        return self.__dCfgVars[vname]
   
    def setCfgVar (self,vname,val):
        if not vname or not val: return False
        self.__dCfgVars[vname] = val
        return True
   
    def getCfgVarFromGroup (self,gname,vname):
        if not gname: return None
        if not self.__dCfgGroups.has_key(gname): return None
        if type(self.__dCfgGroups[gname]) is not DictType: return None
        if not self.__dCfgGroups[gname].has_key(vname): return None
        return self.__dCfgGroups[gname][vname]

    def setCfgVarFromGroup (self,gname,vname,val):
        if not gname or not vname or not self.__dCfgGroups.has_key(gname) or \
            type(self.__dCfgGroups[gname]) is not DictType : return False
        self.__dCfgGroups[gname][vname] = val
        return True

    def getVar(self,gname,vname = None):
        if not vname and gname: 
            vname = gname
            gname = None
        if not vname: return None
        if gname and vname :
            if not self.dCfg.has_key(gname) or \
                type(self.dCfg[gname]) is not DictType or \
                not self.dCfg[gname].has_key(vname): return None
            return self.dCfg[gname][vname]
        else:
            if not self.dCfg.has_key(vname): return None
            return self.dCfg[vname]
  
    def resultsFromSQLFile(self,fuente):
       path = self.getCfgVarFromGroup('sql','path')
       if not os.path.isfile(path + '/' + fuente):
          print "No se ha posido localizar el fichero (",path+'/'+fuente,") "
          return None
       dMysql = self.getCfgGroup('mysql')
       file = path + '/' + fuente

       f = open(file,'r')
       consulta = f.read()
       f.close()
       oDb = MySQLdb.connect(host=dMysql['server'],user=dMysql['user'],passwd=dMysql['pass'],db=dMysql['dbase'],port=int(dMysql['port']))
       c = oDb.cursor(MySQLdb.cursors.DictCursor)

       aRetVal = {}
       aTmp = consulta.split(";\n")
       for cons in aTmp:
          tmpcons = cons.replace(" ","")
          if not tmpcons or not len(tmpcons): continue
          tmpcons = cons.replace("\n","")
          if not tmpcons or not len(tmpcons): continue
          aFieldOrder = []
          try:
             c.execute(cons)
             aVal = c.fetchall()
             if c.description and len(c.description):
                for d in c.description: 
                   aFieldOrder.append(d[0])
          except Exception,e:
             aVal = [{'Error':str(e),'Consulta':cons,'file':file,'path':path}]

          aRetVal['ResultSet'] = list()
          if aVal and len(aVal):
             for val in aVal: 
                if val and len(val): 
                   aRetVal['ResultSet'].append(val)
          if aFieldOrder and len(aFieldOrder): aRetVal['SQLOrder'] = aFieldOrder
       return aRetVal



# Crear una clase padre para los distitnos metodos de dTipo. Con acceso a este 'CrontabParams'
#    dTipos =  'sql':SQLFileQuery 'html':HTMLFetch, 'system':SysExec
# Cada clase de estas, tiene que tener un metodo run, que equivale al metodo padre "resultsFromSQLFile" 

class SQLFileQuery (CrontabParams):
   aRequiredFields = ('mysql_server','mysql_user','mysql_pass','mysql_dbase')
   aRequiredPaths = ('sql_path','base-path')

   def __init__ (self,oCfg,seccion):
      # TODO: Esto deberia ser un rais (en todos los sitios)
      if not seccion: return None

      self.aLocalGroups = ('mysql')
      CrontabParams.__init__ (self,oCfg,seccion)
      dMysql = self.getCfgGroup('mysql')
      if not len(dMysql): return None

   
   
   def getMimeResult (self):
      if not self.bStatusOK: return None

      fuente = self.getVar('fuente')
      if not fuente:
         print "No se ha indicado el fichero con la consulta. "
         return None


      nombre_out = self.getVar('nombre-adjunto')
      sec = self.getVar('__seccion__')
      if not nombre_out:
         if fuente.find('.') != -1:
            aTmp = fuente.split('.')
            nombre_out = aTmp[0] 
         else: nombre_out = fuente 

      aRS = self.resultsFromSQLFile(fuente)
      aVal = aRS['ResultSet']
      if aRS.has_key('SQLOrder'): aOrden = aRS['SQLOrder']
      else: aOrden = None

      rawfile = ''
      if len(aVal):
         for dRow in aVal:
            if not dRow.has_key('Error'):
               if not len(rawfile):
                  if aOrden and len(aOrden): aKeys = aOrden
                  else: aKeys = dRow.keys()
                  for j in range(len(aKeys)): 
                     if len(rawfile) : rawfile += "\t"
                     rawfile += aKeys[j]
                  rawfile += "\n"
               bTab = False
               for k in aKeys:
                  v = dRow[k]
                  if bTab : rawfile += "\t"
                  rawfile += str(v)
                  bTab = True
               rawfile += "\n"
            else:
               # ERROR:
               tmptxt = ''
               for (k,v) in dRow.items(): tmptxt += k + ' : ' + str(v) + "\n"
               oCuerpo = MIMEText(tmptxt,'plain','ISO-8859-15')
               oCuerpo.set_type('text/plain')
               oCuerpo.set_charset('ISO-8859-15')
               oCuerpo.add_header('Content-Disposition','inline; filename="SQLError.txt"')
               return oCuerpo

      if not rawfile: return None
      tipo_mime = self.getVar('tipo-mime')
      if not tipo_mime or not len(tipo_mime): tipo_mime = 'application/vnd.ms-excel'
      disp = self.getCfgVar('disposicion')
      if disp in (None,'adjunto'): disp = 'attachment'
      elif disp in ('interno','in','dentro'): disp = 'inline'
      else: disp = 'attachment'

      oCuerpo = MIMEText(rawfile,'csv','ISO-8859-15')
      #oCuerpo.set_type('text/csv')
      #oCuerpo.set_type('binary/octect-stream')
      oCuerpo.set_charset('ISO-8859-15')
      oCuerpo.set_type(tipo_mime)
      oCuerpo.add_header('Content-Disposition',disp+'; filename="'+nombre_out+'.csv"')

      return oCuerpo



class HTMLFetch (CrontabParams):
   aRequiredFields = ('servidor',None)

   def __init__ (self,oCfg,seccion):
      # TODO: Esto deberia ser un rais (en todos los sitios)
      if not seccion: return None
      self.aLocalGroups = ('form','get')
      CrontabParams.__init__ (self,oCfg,seccion)

   
   
   def getMimeResult (self):
      if not self.bStatusOK: return None

      servername = self.getCfgVar('servidor')
      relurl = self.getVar('url-relativa')
      nombre_out = self.getVar('nombre-adjunto')
      sec = self.getVar('__seccion__')
      if not nombre_out: nombre_out = servername
      if not relurl: url = servername
      else: url = servername + '/' + relurl

      bSQLGet = False
      fuentesql = self.getVar('form','fuentesql')
      prefix = self.getVar('fuentesql-prefijo')
      namefld = None
      if not fuentesql: 
         fuentesql = self.getVar('get','fuentesql')
         if fuentesql: 
            bSQLGet = True
            emailfld = self.getVar('get','fuentesql-campoemail')
            namefld = self.getVar('get','fuentesql-camponombre')
      else:
         emailfld = self.getVar('form','fuentesql-campoemail')
         namefld = self.getVar('form','fuentesql-camponombre')

      if not fuentesql: ntimes = 1
      else:
         aRS = self.resultsFromSQLFile(fuentesql)
         aVal = aRS['ResultSet']
         ntimes = len(aVal)

      defaultemail = self.getVar('email')
      if not defaultemail: defaultemail = self.getCfgVar('email')
      tipo_mime = self.getVar('tipo-mime')
      if not tipo_mime: tipo_mime = 'text/html'
      disp = self.getCfgVar('disposicion')
      if disp in (None,'adjunto'): disp = 'attachment'
      elif disp in ('interno','in','dentro','en el mail'): disp = 'inline'
      else: disp = 'attachment'

      dMsgList = {}
      for n in range(ntimes):
         if fuentesql: 
            aV = aVal[n]
            if aV.has_key('Error'):
               tmptxt = ''
               for (k,v) in aV.items(): tmptxt += k + ' : ' + str(v) + "\n"
               oMsg = MIMEText(tmptxt,'plain','ISO-8859-15')
               oMsg.set_type('text/plain')
               oMsg.set_charset('ISO-8859-15')
               oMsg.add_header('Content-Disposition','inline; filename="SQLError.txt"')
               fuentesql = None
               break
         if not fuentesql or not len(fuentesql): nombre_file = nombre_out
         else: 
            if prefix: nombre_file = prefix + ' ' +  str(n)
            else: nombre_file = nombre_out + str(n)
         #Obtenemos Variables POST
         vars = self.getVar('form','vars')
         dTmp = {}
         if fuentesql and not bSQLGet:
            aTmp = aV.keys()
            for k in aTmp:
               if (not emailfld or emailfld != k) and (not namefld or namefld != k):
                  #print "Sumando campo ",k," al post: ",aV[k]
                  dTmp[k] = aV[k]
         if vars and len(vars):
            aTmp = vars.split(' ')
            for vname in aTmp: 
               dTmp[vname] = self.getVar(vname)
               sec = self.getVar('__seccion__')
               if not dTmp[vname] and sec and self.oConfig.has_option(sec,vname): dTmp[vname] = self.oConfig.get(sec,vname)
            encodedform = urllib.urlencode(dTmp)
         else: encodedform = ''
         #Obtenemos Variables GET
         vars = self.getVar('get','vars')
         dTmp = {}
         if fuentesql and bSQLGet:
            aTmp = aV.keys()
            for k in aTmp:
               if (not emailfld or emailfld != k) and (not namefld or namefld != k):
                  dTmp[k] = aV[k]
         if vars and len(vars):
            aTmp = vars.split(' ')
            for vname in aTmp: 
               dTmp[vname] = self.getVar(vname)
               sec = self.getVar('__seccion__')
               if not dTmp[vname] and sec and self.oConfig.has_option(sec,vname): dTmp[vname] = self.oConfig.get(sec,vname)
            encodedget = '?'+urllib.urlencode(dTmp)
         else: encodedget = ''

         try:
            file = urllib.urlopen('http://'+url+encodedget,encodedform)
            html = file.read()
            file.close()
         except Exception,e:
            html = "No se pudo abrir la url %s :=> %s " % ('http://'+url+encodedget,str(e))

         oMsg = MIMEText(html,'html','iso-8859-15')
         oMsg.set_type(tipo_mime)
         #oElCuerpo.set_charset(None)
         oMsg.set_charset('ISO-8859-15')
         if namefld and len(namefld) and aV.has_key(namefld): 
            if prefix: nombre_file = prefix + ' ' + aV[namefld]
            else: nombre_file = aV[namefld]
         oMsg.add_header('Content-Disposition',disp+'; filename="'+nombre_file+'.html"')
         if fuentesql and len(fuentesql): 
            if emailfld and aV.has_key(emailfld): email = aV[emailfld]
            else: email = defaultemail

            if email:
               if not dMsgList.has_key(email) : dMsgList[email] = MIMEMultipart()
               dMsgList[email].attach(oMsg)

      if not fuentesql or not len(fuentesql): oCuerpo = oMsg
      else: oCuerpo = dMsgList

      return oCuerpo



class SysExec (CrontabParams):
   aRequiredFields = ('fuente',None)
   aRequiredPaths = ('scripts-path',None)

   def __init__ (self,oCfg,seccion):
      # TODO: Esto deberia ser un RaiseError (en todos los sitios)
      if not seccion: return None
      self.aLocalGroups = ('form','get')
      CrontabParams.__init__ (self,oCfg,seccion)

   
   
   def getMimeResult (self):
      if not self.bStatusOK: return None
      # TODO: Permmitir enviar parametros al script

      fuente = self.getVar('fuente')
      path = self.getCfgVar('scripts-path')

      tipo_mime = self.getVar('tipo-mime')
      if not tipo_mime: tipo_mime = 'text/plain'
      disp = self.getCfgVar('disposicion')
      if disp in (None,'adjunto'): disp = 'attachment'
      elif disp in ('interno','in','dentro','en el mail'): disp = 'inline'
      else: disp = 'attachment'

      if os.path.isfile(path + '/' + fuente):
         try:
            p = os.popen(path + '/' + fuente)
            txt = p.read()
            p.close()
            oCuerpo = MIMEText(txt)
         except Exception,e :
            txt = 'Error Ejecutando ' + fuente + ': ' + str(e)
            oCuerpo = MIMEText(txt)
      else: return None

      oCuerpo.set_type(tipo_mime)
      oCuerpo.add_header('Content-Disposition',disp+'; filename="'+fuente+'"')
      return oCuerpo

