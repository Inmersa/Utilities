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

   def __init__ (this,oCfg,seccion):
      tmpOpts = oCfg.options(this.mainsection)
      if not len(tmpOpts): 
         this.bStatusOK = False
         return None
      this.dCfg = {}
      this.__dCfgGroups = {}
      this.__dCfgVars = {}

      this.dCfg['__seccion__'] = seccion
      this.oConfig = oCfg

      for i in range(len(tmpOpts)):
         if tmpOpts[i].find('_') != -1:
            aTmp = tmpOpts[i].split('_')
            if len(aTmp) > 1:
               if not this.__dCfgGroups.has_key(aTmp[0]): this.__dCfgGroups[aTmp[0]] = {}
               if oCfg.has_option(seccion,tmpOpts[i]):
                  this.__dCfgGroups[aTmp[0]][aTmp[1]] = oCfg.get(seccion,tmpOpts[i])
               else:
                  this.__dCfgGroups[aTmp[0]][aTmp[1]] = oCfg.get(this.mainsection,tmpOpts[i])
         else:
            if oCfg.has_option(seccion,tmpOpts[i]):
               this.__dCfgVars[tmpOpts[i]] = oCfg.get(seccion,tmpOpts[i])
            else:
               this.__dCfgVars[tmpOpts[i]] = oCfg.get(this.mainsection,tmpOpts[i])

      if this.aRequiredFields and len(this.aRequiredFields):
         for i in range(len(this.aRequiredFields)):
            fld = this.aRequiredFields[i]
            if not fld: continue
            if oCfg.has_option(seccion,fld):
               sval = oCfg.get(seccion,fld)
            else: sval=None

            if fld.find('_') != -1:
               aTmp = fld.split('_')
               if len(aTmp) > 1:
                  if sval: this.setCfgVarFromGroup(aTmp[0],aTmp[1],sval)
                  val = this.getCfgVarFromGroup(aTmp[0],aTmp[1])
                  if not val:
                     print "Campo obligatorio ",fld," no cumplimentado "
                     this.bStatusOK = False
                     return None
            else:
               if sval: this.setCfgVar(fld,sval)
               val = this.getCfgVar(fld)
               if not val:
                  print "Campo obligatorio ",fld," no cumplimentado "
                  this.bStatusOK = False
                  return None

      if this.aRequiredPaths and len(this.aRequiredPaths):
         for i in range(len(this.aRequiredPaths)):
            tmppath = this.aRequiredPaths[i]
            if not tmppath: continue
            if oCfg.has_option(seccion,tmppath): sval = oCfg.get(seccion,tmppath)
            else: sval=None

            if tmppath.find('_') != -1:
               aTmp = tmppath.split('_')
               if len(aTmp) > 1:
                  if sval: this.setCfgVarFromGroup(aTmp[0],aTmp[1],sval)
                  val = this.getCfgVarFromGroup(aTmp[0],aTmp[1])
                  if not val:
                     print "Campo obligatorio ",tmppath," no cumplimentado "
                     this.bStatusOK = False
                     return None
                  if not os.path.isdir(val):
                     this.setCfgVarFromGroup(aTmp[0],aTmp[1],None)
                     print "Path inexistente ",val
                     continue
            else:
               if sval: this.setCfgVar(tmppath,sval)
               val = this.getCfgVar(tmppath)
               if not val:
                  print "Campo obligatorio ",tmppath," no cumplimentado ", val
                  this.bStatusOK = False
                  return None
               if not os.path.isdir(val):
                  this.setCfgVarFromGroup(aTmp[0],aTmp[1],None)
                  print "Path inexistente ",val
                  this.bStatusOK = False
                  continue

      if this.aLocalGroups and len(this.aLocalGroups):
         tmpOpts = oCfg.options(seccion)
         for i in range(len(tmpOpts)):
            if tmpOpts[i].find('_') == -1:
               this.dCfg[tmpOpts[i]] = oCfg.get(seccion,tmpOpts[i])
            else:
               aTmp = tmpOpts[i].split('_')
               if len(aTmp) > 1:
                  if aTmp[0] in this.aLocalGroups:
                     if not this.dCfg.has_key(aTmp[0]) or type(this.dCfg[aTmp[0]]) is not DictType: this.dCfg[aTmp[0]] = {}
                     this.dCfg[aTmp[0]][aTmp[1]] = oCfg.get(seccion,tmpOpts[i])
                  else: this.dCfg[tmpOpts[i]] = oCfg.get(seccion,tmpOpts[i])

   def getCfgGroup (this,gname):
      if not gname: return None
      if not this.__dCfgGroups.has_key(gname): return None
      return this.__dCfgGroups[gname]

   def getCfgVar (this,vname):
      if not vname: return None
      if not this.__dCfgVars.has_key(vname): return None
      return this.__dCfgVars[vname]

   def setCfgVar (this,vname,val):
      if not vname or not val: return False
      this.__dCfgVars[vname] = val
      return True

   def getCfgVarFromGroup (this,gname,vname):
      if not gname: return None
      if not this.__dCfgGroups.has_key(gname): return None
      if type(this.__dCfgGroups[gname]) is not DictType: return None
      if not this.__dCfgGroups[gname].has_key(vname): return None
      return this.__dCfgGroups[gname][vname]

   def setCfgVarFromGroup (this,gname,vname,val):
      if not gname or not vname or not this.__dCfgGroups.has_key(gname) or \
         type(this.__dCfgGroups[gname]) is not DictType : return False
      this.__dCfgGroups[gname][vname] = val
      return True

   def getVar(this,gname,vname = None):
      if not vname and gname: 
         vname = gname
         gname = None
      if not vname: return None
      if gname and vname :
         if not this.dCfg.has_key(gname) or \
            type(this.dCfg[gname]) is not DictType or \
            not this.dCfg[gname].has_key(vname): return None
         return this.dCfg[gname][vname]
      else:
         if not this.dCfg.has_key(vname): return None
         return this.dCfg[vname]

   def ResultsFromSQLFile(this,fuente):
      path = this.getCfgVarFromGroup('sql','path')
      if not os.path.isfile(path + '/' + fuente):
         print "No se ha posido localizar el fichero (",path+'/'+fuente,") "
         return None
      dMysql = this.getCfgGroup('mysql')
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


class SQLFileQuery (CrontabParams):
   aRequiredFields = ('mysql_server','mysql_user','mysql_pass','mysql_dbase')
   aRequiredPaths = ('sql_path','base-path')

   def __init__ (this,oCfg,seccion):
      # TODO: Esto deberia ser un rais (en todos los sitios)
      if not seccion: return None

      this.aLocalGroups = ('mysql')
      CrontabParams.__init__ (this,oCfg,seccion)
      dMysql = this.getCfgGroup('mysql')
      if not len(dMysql): return None

   def getMimeResult (this):
      if not this.bStatusOK: return None

      fuente = this.getVar('fuente')
      if not fuente:
         print "No se ha indicado el fichero con la consulta. "
         return None


      nombre_out = this.getVar('nombre-adjunto')
      sec = this.getVar('__seccion__')
      if not nombre_out:
         if fuente.find('.') != -1:
            aTmp = fuente.split('.')
            nombre_out = aTmp[0] 
         else: nombre_out = fuente 

      aRS = this.ResultsFromSQLFile(fuente)
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
      tipo_mime = this.getVar('tipo-mime')
      if not tipo_mime or not len(tipo_mime): tipo_mime = 'application/vnd.ms-excel'
      disp = this.getCfgVar('disposicion')
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

   def __init__ (this,oCfg,seccion):
      # TODO: Esto deberia ser un rais (en todos los sitios)
      if not seccion: return None
      this.aLocalGroups = ('form','get')
      CrontabParams.__init__ (this,oCfg,seccion)

   def getMimeResult (this):
      if not this.bStatusOK: return None

      servername = this.getCfgVar('servidor')
      relurl = this.getVar('url-relativa')
      nombre_out = this.getVar('nombre-adjunto')
      sec = this.getVar('__seccion__')
      if not nombre_out: nombre_out = servername
      if not relurl: url = servername
      else: url = servername + '/' + relurl

      bSQLGet = False
      fuentesql = this.getVar('form','fuentesql')
      prefix = this.getVar('fuentesql-prefijo')
      namefld = None
      if not fuentesql: 
         fuentesql = this.getVar('get','fuentesql')
         if fuentesql: 
            bSQLGet = True
            emailfld = this.getVar('get','fuentesql-campoemail')
            namefld = this.getVar('get','fuentesql-camponombre')
      else:
         emailfld = this.getVar('form','fuentesql-campoemail')
         namefld = this.getVar('form','fuentesql-camponombre')

      if not fuentesql: ntimes = 1
      else:
         aRS = this.ResultsFromSQLFile(fuentesql)
         aVal = aRS['ResultSet']
         ntimes = len(aVal)

      defaultemail = this.getVar('email')
      if not defaultemail: defaultemail = this.getCfgVar('email')
      tipo_mime = this.getVar('tipo-mime')
      if not tipo_mime: tipo_mime = 'text/html'
      disp = this.getCfgVar('disposicion')
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
         vars = this.getVar('form','vars')
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
               dTmp[vname] = this.getVar(vname)
               sec = this.getVar('__seccion__')
               if not dTmp[vname] and sec and this.oConfig.has_option(sec,vname): dTmp[vname] = this.oConfig.get(sec,vname)
            encodedform = urllib.urlencode(dTmp)
         else: encodedform = ''
         #Obtenemos Variables GET
         vars = this.getVar('get','vars')
         dTmp = {}
         if fuentesql and bSQLGet:
            aTmp = aV.keys()
            for k in aTmp:
               if (not emailfld or emailfld != k) and (not namefld or namefld != k):
                  dTmp[k] = aV[k]
         if vars and len(vars):
            aTmp = vars.split(' ')
            for vname in aTmp: 
               dTmp[vname] = this.getVar(vname)
               sec = this.getVar('__seccion__')
               if not dTmp[vname] and sec and this.oConfig.has_option(sec,vname): dTmp[vname] = this.oConfig.get(sec,vname)
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

   def __init__ (this,oCfg,seccion):
      # TODO: Esto deberia ser un RaiseError (en todos los sitios)
      if not seccion: return None
      this.aLocalGroups = ('form','get')
      CrontabParams.__init__ (this,oCfg,seccion)

   def getMimeResult (this):
      if not this.bStatusOK: return None
      # TODO: Permmitir enviar parametros al script

      fuente = this.getVar('fuente')
      path = this.getCfgVar('scripts-path')

      tipo_mime = this.getVar('tipo-mime')
      if not tipo_mime: tipo_mime = 'text/plain'
      disp = this.getCfgVar('disposicion')
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

