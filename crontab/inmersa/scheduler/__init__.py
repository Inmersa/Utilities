__author__="tite"
__date__ ="$Jul 18, 2014 7:48:18 AM$"

import os
import sys
import string
import datetime
import traceback
from types import *

import ConfigParser
import smtplib
import logging
import logging.config

import extractors
import formatters

from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEImage import MIMEImage
import email

class Schedule():
    config = None
    mainsection = 'General'
    odate = datetime.datetime.today()
    activeJobs = list()
    logger = None
    activeJob = None

    def __init__(self,cfgfile):
        # Constructor
        docroot = '/root/crons'
        self.config = ScheduleParams(self.mainsection)
        if os.path.isfile(cfgfile):
            self.config.read(cfgfile)
        elif os.path.isfile(docroot + '/' + cfgfile):
            self.config.read(docroot + '/' + cfgfile)
        else:
            raise Exception("No config file (",cfgfile,") found in "+docroot)
            #sys.exit(0) 
        # Establecemos las variables por defecto
        self.config.set('DEFAULT','fecha',str(self.odate.day)+'/'+str(self.odate.month)+'/'+str(self.odate.year))
        self.config.set('DEFAULT','fechahora',str(self.odate.day)+'/'+str(self.odate.month)+'/'+str(self.odate.year)+' '+str(self.odate.hour)+':'+str(self.odate.minute))
        #print "Buscando el condig: ",self.config.get(self.mainsection,'logging-config')
        if not self.config.logger and self.config.get(self.mainsection,'logging-config'):
            tmpfile = self.config.get(self.mainsection,'logging-config')
            if not os.path.isfile(tmpfile): tmpfile = self.config.get(self.mainsection,'rootdir')+tmpfile
            if os.path.isfile(tmpfile): logging.config.fileConfig(tmpfile)
            else: print "ERROR: config log file not found"
            self.logger = logging.getLogger(str(self.__class__))
        else:
            self.logger = logging.getLogger(str(self.__class__))
            self.logger.debug("reaprovechando la definicion hecha del logger")
        self.logger.debug("Scheduler constructor loaded. Using %(file)s for logging" % {'file':tmpfile} )
    
    def _setupLog(self):
        if not self.logger:
            self.logger = logging.getLogger(str(self.__class__))
    
    def load(self):
        # Metodo Start?? 
        aRawList = self.config.sections()
        self.logger.debug("Checking on the following jobs: %s " % (aRawList))
        for i in range(len(aRawList)):
            if len(aRawList[i]):
                if aRawList[i] == self.mainsection: continue;
                seccion = aRawList[i]

                # Los no activos, ni los miramos
                if self.config.has_option(seccion,'activo'):
                    act = self.config.get(seccion,'activo')
                    if act in ('no','NO','nones','No','nO'): continue
                self.logger.debug("%s : is active" % (seccion))
                
                bHoraOK = False
                if not self.config.has_option(seccion,'hora'): bHoraOK = True
                else:
                    hora = self.config.get(seccion,'hora')
                    aTmp = hora.split(' ')
                    for h in aTmp: 
                        if str(self.odate.hour) == h :
                            bHoraOK = True
                            break;
                self.logger.debug("%s : hora?(%s)" % (seccion,bHoraOK))
                
                if bHoraOK and self.config.has_option(seccion,'diasemana'):
                    bHoraOK = False
                    diahoy = self.odate.weekday()+1
                    tmpstr = self.config.get(seccion,'diasemana')
                    aTmp = tmpstr.split(' ')
                    if len(aTmp):
                        for d in aTmp:
                            if str(diahoy) == d:
                                bHoraOK = True
                                break;
                self.logger.debug("%s check diasemana: sigue activo ?(%s)" % (seccion,bHoraOK))

                if bHoraOK and self.config.has_option(seccion,'dia'):
                    bHoraOK = False
                    diahoy = self.odate.day
                    tmpstr = self.config.get(seccion,'dia')
                    aTmp = tmpstr.split(' ')
                    if len(aTmp):
                        for d in aTmp:
                            if str(diahoy) == d:
                                bHoraOK = True
                                break;
                self.logger.debug("%s check dia: sigue activo ?(%s)" % (seccion,bHoraOK))

                if bHoraOK and self.config.has_option(seccion,'mes'):
                    bHoraOK = False
                    diahoy = self.odate.month
                    tmpstr = self.config.get(seccion,'mes')
                    aTmp = tmpstr.split(' ')
                    if len(aTmp):
                        for d in aTmp:
                            if str(diahoy) == d:
                                bHoraOK = True
                                break;
                self.logger.debug("%s check mes: sigue activo ?(%s)" % (seccion,bHoraOK))
                
                if bHoraOK:
                    if self.config.has_option(seccion,'extractor'): self.activeJobs.append(seccion)
        self.logger.debug("Loaded the following jobs: %s " % (self.activeJobs))
    
    
    
    def loadJob(self,seccion):
        self._setupLog()
        self.logger.debug("%s: startup with dCfg %s " % (seccion,self.config.dCfg))
        if not self.activeJob: self.config._loadMain()
        self.logger.debug("%s: after loadMain with dCfg %s " % (seccion,self.config.dCfg))
        self.config.initialize(seccion)
        self.logger.debug("%s: after initialize with dCfg %s " % (seccion,self.config.dCfg))
        self.activeJob = Job(self.config)
        self.logger.debug("method end - seccion(%(sec)s) with this config: %(dic)s " % {'sec':seccion, 'dic':self.config.dCfg} )
    
    
    
    def run(self):
        # Validacion para un metodo de test
        #ruben
        if  not len(self.activeJobs):
                #print "Nothing to do at ",self.odate.hour
                self.logger.info("Nothing to do. No active jobs for this execution")
                return

        # Mandando el correo
        # Metodo run, para hacer los temas
        
        ### TODO: With all these validations, raise errors, instead of assigning default values
        if self.config.has_option('General','remite'):
           varfrom = self.config.get('General','remite')
        else: varfrom = 'IEmpresa-biomundo@biomundo'
        if self.config.has_option('General','tema'):
           subject = self.config.get('General','tema')
        else: subject = 'Informe de las '+str(self.odate.hour)
        if self.config.has_option('General','smtp-server'):
           servidor_correo = self.config.get('General','smtp-server')
        else: servidor_correo = 'mail.wol'

        aEmailDef = list()
        if self.config.has_option('General','email'):
           tmp = self.config.get('General','email')
           aTmp = tmp.split(' ')
           for e in aTmp: aEmailDef.append(e)

        dEmailList = {}
        for i in range(len(self.activeJobs)):
            seccion = self.activeJobs[i]

            try:
                self.loadJob(seccion)
                oI = self.activeJob
                self.logger.debug("retrieved job %s " % oI)
                if not oI: continue
                oI.run()
                oTmpMsg = oI.getMimeResult()
#                if not isinstance(oTmpMsg,(list)): self.logger.debug("%s: Before closing .. Here is our message!\n%s"%(self.config.seccion(),oTmpMsg.as_string()))
                oI.close()
                
                #TODO: Here, issue and log an error before continuing
                if not oTmpMsg or (type(oTmpMsg) is not DictType and type(oTmpMsg) is not InstanceType) : 
                    self.logger.debug("No message! ")
                    continue
#                if not isinstance(oTmpMsg,(list)): self.logger.debug("%s: Here is our message!\n%s"%(self.config.seccion(),oTmpMsg.as_string()))

                aEmails = list()
                if self.config.has_option(seccion,'email'):
                    tmp = self.config.get(seccion,'email')
                    aTmp = tmp.split(' ')
                    for e in aTmp: aEmails.append(e)
                else: aEmails = aEmailDef
                self.logger.debug("%s: Standard recipients on this section: %s " % (self.config.seccion(),aEmails))

                if type(oTmpMsg) is InstanceType:
                    if aEmails and len(aEmails):
                        for e in aEmails:
                            bAttach = True
                            if not dEmailList.has_key(e):
                                if False and isinstance(oTmpMsg,(MIMEMultipart)):
                                    self.logger.debug("%s: turns out we already have a multipart"%(self.config.seccion()))
                                    dEmailList[e] = oTmpMsg
                                    bAttach = False
                                else:
                                    self.logger.debug("%s: building a new Multipart for %s " % (self.config.seccion(),e))
                                    dEmailList[e] = MIMEMultipart('mixed')
                                dEmailList[e].add_header('Subject',subject)
                                dEmailList[e].add_header('To',e)
#                            self.logger.debug("%s: Adding %s to destination %s . now having:\n%s" % (self.config.seccion(),oTmpMsg.__class__,e,dEmailList[e].as_string()))
                            if bAttach: dEmailList[e].attach( oTmpMsg )
                else:
                    """
                       Si existe la opcion email en la seccion, ademas de a los indicados por la SQL (si hay) se manda
                       email a estos.
                    """
                    self.logger.debug("%s: the sepecific job is a multi-destination " % (self.config.seccion()))
                    for (e,oMsg) in oTmpMsg.items():
                        #self.logger.debug("List of parts ? To: %s " % (e))
                        self.logger.debug("%s: job destination %s over class %s " % (self.config.seccion(),e,oMsg.__class__))
                        if not dEmailList.has_key(e):
                            self.logger.debug("%s: building a new Multipart for %s " % (self.config.seccion(),e))
                            dEmailList[e] = MIMEMultipart()
                            dEmailList[e].add_header('Subject',subject)
                            dEmailList[e].add_header('To',e)
                        dEmailList[e].attach( oMsg )
#                        if self.config.has_option(seccion,'email'):
                        if aEmails and len(aEmails):
                            for ee in aEmails:
                                if ee == e: continue;
                                self.logger.debug("%s: Topping with additional destination %s " % (self.config.seccion(),ee))
                                if not dEmailList.has_key(ee):
                                    self.logger.debug("%s: building a new Multipart for %s " % (self.config.seccion(),ee))
                                    dEmailList[ee] = MIMEMultipart()
                                    dEmailList[ee].add_header('Subject',subject)
                                    dEmailList[ee].add_header('To',ee)
                                dEmailList[ee].attach( oMsg )

            except Exception as err:
                self.logger.exception("When loading job %s " % (seccion))
                continue
                
        self.logger.info("ALL Jobs ran. ready to transport the output")
        #FIXME: Credentials to authenticate on the SMTP Server need to be on config file!
        if self.config.has_option('General','smtp-user'):
            user = self.config.get('General','smtp-user')
        else: user = None
        if self.config.has_option('General','smtp-password'):
            pwd = self.config.get('General','smtp-password')
        else: pwd = None
        if self.config.has_option('General','smtp-port'):
            port = self.config.get('General','smtp-port')
        else: port = 587

        if True:
            for (e,oBody) in dEmailList.items():
                try:
                    #print e, oBody
                    self.logger.debug("Preparing email for %s" % (e))
                    for part in oBody.walk():
                        try:
                            self.logger.debug("\t%s / %s boundary %s " % (part.get_content_maintype(),part.get_content_subtype(),part.get_boundary()))
                            self.logger.debug("\tContent Disposition : %s - Content ID: %s " % (part.get_all('Content-disposition'),part.get_all('Content-ID')))
                            self.logger.debug("\tsample: %s\n----- next -----" % (part.get_payload(decode=False)[:75]))
                        except:
                            self.logger.debug("----- next -----")
                    smtpserver = smtplib.SMTP(servidor_correo,port)
                    #smtpserver = smtplib.SMTP("mail.biomundo.eu",587)
                    smtpserver.ehlo()
                    smtpserver.starttls()
                    smtpserver.ehlo
                    if user: smtpserver.login(user, pwd)
                    self.logger.debug("transfering data for %s" % (e))
                    smtpserver.sendmail(varfrom,e,oBody.as_string())
                    #smtp.sendmail(varfrom,e,oBody.as_string())
                    self.logger.debug('done!')
                    smtpserver.close()
                except Exception,e:
                    self.logger.exception("Error sending email")
                    continue
        else:
            for (e,oBody) in dEmailList.items():
                self.logger.debug("this is a dry run email to %s with content:\n%s" % (e,oBody))
        self.logger.debug("End of Schedule run")


class ScheduleParams(ConfigParser.ConfigParser):
    mainsection = 'General'
    __dCfgGroups = {}
    __dCfgVars = {}
    aRequiredFields = None
    aRequiredPaths = None
    dCfg = {}
    aLocalGroups = None
    bStatusOK = True
    mainConfigOptions = None
    logger = None
    _aliases = { 'disposition': ['disposicion'] }
    
    """
    def __init__ (self,oCfg,seccion) :
    """
    def __init__(self,general=None):
        " quizas forzar el nombre de file  "
        if general: self.mainsection = general
        ConfigParser.ConfigParser.__init__(self)
        #super(ScheduleParams, self).__init__()
        try:
            #print "Buscando el condig: ",self.config.get(self.mainsection,'logging-config')
            if self.get(self.mainsection,'logging-config'):
                tmpfile = self.get(self.mainsection,'logging-config')
                if not os.path.isfile(tmpfile):
                    tmpfile = self.get(self.mainsection,'rootdir')+tmpfile
                if os.path.isfile(tmpfile):
                    logging.config.fileConfig(tmpfile)
                else:
                    print "ERROR: config log file not found"
            self.logger = logging.getLogger(str(self.__class__))
            self.logger.debug("Constructor loaded. Using %(file)s for logging" % {'file':tmpfile} )
        except ConfigParser.NoSectionError,e:
            # ok
            print "ScheduleParams::__init__() - with no config to get a logger"
            
    
    
    def _setupLog(self):
        if not self.logger:
            self.logger = logging.getLogger(str(self.__class__))

    
    
    def _loadMain(self):
        self._setupLog()
        if not self.mainConfigOptions:
            self.logger.debug("mainConfigOptions empty. Loading them")
            self.mainConfigOptions = self.options(self.mainsection)
            if not len(self.mainConfigOptions): 
               self.bStatusOK = False
               return None
        self.__dCfgGroups = {}
        self.__dCfgVars = {}

        self.logger.debug("we should not be entering here more than once per execution .... ")
        for i in range(len(self.mainConfigOptions)):
            self.logger.debug("Iterator4mainConfigOptions %s - %s"%(i,self.mainConfigOptions[i]))
            if self.mainConfigOptions[i].find('_') != -1:
                aTmp = self.mainConfigOptions[i].split('_')
                if len(aTmp) > 1:
                    if not self.__dCfgGroups.has_key(aTmp[0]): self.__dCfgGroups[aTmp[0]] = {}
                    if self.has_option(self.seccion(),self.mainConfigOptions[i]):
                        self.__dCfgGroups[aTmp[0]][aTmp[1]] = self.get(seccion,self.mainConfigOptions[i])
                    else:
                        self.__dCfgGroups[aTmp[0]][aTmp[1]] = self.get(self.mainsection,self.mainConfigOptions[i])
            else:
                # maybe this is the only part that should be executed over and over ??
                if self.seccion() and self.has_option(self.seccion(),self.mainConfigOptions[i]):
                    self.__dCfgVars[self.mainConfigOptions[i]] = self.get(self.seccion(),self.mainConfigOptions[i])
                else:
                    self.__dCfgVars[self.mainConfigOptions[i]] = self.get(self.mainsection,self.mainConfigOptions[i])
        self.logger.debug("dCfgGroups is %s \ndCfgVars is %s"%(self.__dCfgGroups,self.__dCfgVars))

    
    
    def initialize(self,seccion):
        self._setupLog()
        self.logger.debug("%s Initializing with dCfg %s " % (seccion,self.dCfg))
        self.dCfg = {}
#        self.__dCfgVars = {}
        self.dCfg['__seccion__'] = seccion
        self.logger.debug("seccion(%(sec)s)" % {'sec':seccion} )

    
    
    def seccion(self):
        self._setupLog()
        if not self.dCfg or not self.dCfg.has_key('__seccion__'): return None
        return self.dCfg['__seccion__']

    
    
    def getCfgGroup (self,gname):
        self._setupLog()
        if not gname: return None
        if not self.__dCfgGroups.has_key(gname): return None
        return self.__dCfgGroups[gname]

    
    
    def getCfgVar (self,vname):
        self._setupLog()
        if not vname: return None
        if not self.__dCfgVars.has_key(vname): return None
        return self.__dCfgVars[vname]

    
    
    def setCfgVar (self,vname,val):
        self._setupLog()
        if not vname or not val: return False
        self.__dCfgVars[vname] = val
        return True
    
    
    def getCfgVarFromGroup (self,gname,vname):
        self._setupLog()
        self.logger.debug("%s gname(%s) vname(%s) sobre __dCfgGroup(%s)"%(self.seccion(),gname,vname,self.__dCfgGroups))
        if not gname: return None
        if not self.__dCfgGroups.has_key(gname): return None
        if type(self.__dCfgGroups[gname]) is not DictType: return None
        if not self.__dCfgGroups[gname].has_key(vname): return None
        return self.__dCfgGroups[gname][vname]
    
    
    def setCfgVarFromGroup (self,gname,vname,val):
        self._setupLog()
        self.logger.debug("%s gname(%s) vname(%s) sobre dCfg(%s)"%(self.seccion(),gname,vname,self.dCfg))
        if not gname or not vname or not self.__dCfgGroups.has_key(gname) or \
           type(self.__dCfgGroups[gname]) is not DictType : return False
        self.__dCfgGroups[gname][vname] = val
        return True
    
    
    def getVar(self,gname,vname = None):
        self._setupLog()
        if not vname and gname: 
           vname = gname
           gname = None
        if not vname: return None
        self.logger.debug("%s vname(%s) gname(%s) sobre dCfg(%s)"%(self.seccion(),vname,gname,self.dCfg))
        if gname and vname :
           if not self.dCfg.has_key(gname) or \
              type(self.dCfg[gname]) is not DictType or \
              not self.dCfg[gname].has_key(vname): return None
           return self.dCfg[gname][vname]
        else:
           if not self.dCfg.has_key(vname): return None
           return self.dCfg[vname]

    def param(self,param):
        #First we normalize the parameter.
        #self.logger.debug("%s con aliases tot %s " % (param,self._aliases))
        if param in self._aliases.keys(): vars = self._aliases[param] + [param]
        else: vars = [param]
        aTmp = []
        for v in vars:
            rval = self.getVar(v)
            self.logger.debug("buscando %s nos da %s " % (v,rval))
            if not rval and v == vars[-1]: 
                rval = self.getCfgVar(v)
                self.logger.debug("Ahora si que lo buscamos en el general %s nos da %s " % (v,rval))
                if not rval and len(aTmp):
                    self.logger.debug("Buscando los resstos: %s " % (aTmp))
                    for ts in aTmp:
                        self.logger.debug("we are going to use ... %s " % (ts))
                        rval = ts
                        break
            else:
                tmpstr = self.getCfgVar(v)
                if tmpstr: aTmp.append(tmpstr)
                tmpstr = self.getCfgVar(v)
                if tmpstr: aTmp.append(tmpstr)
            if rval: break
        if not rval: return rval
        if param in ('disposition'): 
            if rval in ('adjunto'): rval = 'attachment'
            elif rval in ('interno','in','dentro'): rval = 'inline'
            else: rval = 'attachment'
        return rval

class Job:
    dTipos = None
    params = None
    logger = None
    #TODO: this list needs to change from static to a dynamic list. That is,
    #   there needs to be a way of registering entries/classes as a module is
    #   imported. So there would be a config path on which module paths to load
    #   and when loading them, they would add whatever classes to a tuple 
    extractores = {
                'sql':extractors.SQLFileQuery,
                'html':extractors.HTMLFetch,
                'web':extractors.HTMLFetch,
                'sqltoweb':extractors.SQLValuesToWebFetch,
                'system':extractors.SysExec
            }
    formateadores = {
                'csv':formatters.CSVFormat,
                'text':formatters.TextFormat,
                'txt':formatters.TextFormat,
                'html':formatters.HTMLFormat,
                'xls':formatters.ExcelFormat
            }
    Extractor = None
    Formatter = None
            
    def __init__(self,config):
        self.logger = logging.getLogger(str(self.__class__))
        if config:
            self.logger.debug("Asignando el atributo params ..")
            self.params = config
            #self.logger.debug("hecho. ahora vamos a cargar los parametros ")
            #self._load()
            
        tipo = self.params.get(self.params.seccion(),'extractor')
        logger = logging.getLogger(str(self.__class__))
        if not tipo:
            raise Exception(str(cls)+"::factory wrong argument tipo :"+str(tipo))

        if tipo not in self.extractores.keys(): 
            raise Exception("Tipo "+str(tipo)+" desconocido ")
        try:
            ## El job deberia recibir en realidad 3 parametros de tipo: 1) extractor a usar 2) formateador a usar 3) transporte a usar (y correrlo)
            ##   quizas esta clase deberia ser un Wrapper, que luego llame al resto. 
            ##   Es probable que asi evitemos la incongruencia de tener una factoria que construye instancias que no estan definidas en momento de preproceso
            self.Extractor = self.extractores[tipo](config)
            
        except Exception, e:
            self.logger.exception("Excepcion creando el tipo %s con clase %s  " % (tipo,self.extractores[tipo]))
            # traceback.print_exc()
            raise e
            oTmpMsg = MIMEText("Error en %s : %s " % (config.seccion(),str(e)),'plain','ISO-8859-15')


    def run(self):
        try:
            self.logger.debug("%s : Calling extract ..." % (self.params.seccion()))
            self.extract()
            self.logger.debug("%s : Calling format ..." % (self.params.seccion()))
            self.format()
            self.logger.debug("%s : Execution (includes formatting) finished!" % (self.params.seccion()))
        except Exception,e:
            self.logger.exception("%s : problems Extracting and Formatting data." % (self.params.seccion()))
            raise e
    
    
    def extract(self):
        self.Extractor.extract()
    
    
    def format(self):
        ## Here we have to check configuration and select the appropiate class
        try:
            fmt = self.params.get(self.params.seccion(),'formatter')
            Extract = self.Extractor
            self.logger.debug("formato %s con extractor %s y parametros %s " % (fmt,self.Extractor,self.params))
            self.Formatter = self.formateadores[fmt](self.Extractor,self.params)
        except Exception,e:
            self.logger.exception("%s : Problems loading formatter" % (self.params.seccion()))
            #self.logger.exception("%s : Problems loading formatter %s " % (self.params.seccion(),fmt))
            raise e
    
    
    def getMimeResult(self):
        if not self.Formatter:
            txt = "%s : no formatter available , can't get Mime " % (self.params.seccion())
            self.logger.error(txt)
            raise Exception("%s : no formatter available , can't get Mime " % (self.params.seccion()))
        return self.Formatter.getMimeResult()
    
    def close(self):
        self.Formatter.close()
