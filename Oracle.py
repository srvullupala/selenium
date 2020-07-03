#!/usr/bin/env python
'''
This module provides the function or operations that can be performed on the
Oracle iDA on the AdminConsole
Class:
    Oracle() -> iDA() -> ClientDetails() -> Clients() -> Server() --
            -> AdminPage() -> LoginPage() -> AdminConsoleBase() -> object()
Functions:
OpenInstance()              -- Opens the instance with the given name.
AddInstance()               -- Adds a new instance to the iDA
ActionAddInstance()         -- Adds a new instance from action menu
ActionAddSubclient()        -- Creates a Oracle subclient from Action menu of the instance
OracleRestore()             -- Restores the content of the instance
ActionClone()               -- Clones the instance with the given name
CloneDB()                   -- Clones a instance of oracle
ActionCloudMigration()      -- Migrates the specified instance to cloud from action menu.
AddDBserv()                 -- Adds a DB Instance
ContinuousBuild()           -- Run Continuous Build of the page to traverse all the links on this page.
NextPage()                  -- Returns a dictionary containing the pages that can be visited from this page.
'''
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from Helper.Imports import *
from ContinuousBuild.ParamsDict import *
from OraclePages.CVPages import *
from AutomationUtils.loghelper import *
from AdminConsole.Helper.Exception import *
from AdminConsole.Helper.Exception import AppException
import ast, re
from AdminConsolePages.AdminPage import *
from Helper.AdminConsoleBase import *
from AutomationUtils import loghelper
from selenium.common.exceptions import NoSuchElementException

class Oracle(iDA):

    def OpenInstance(self, instance):
        """ Opens the instance with the given name.
            instance   : a string, name of the instance we want to open
            Return (True, 1) on successfull completion
                    (False, func_name, error_msg) otherwise """
        log = loghelper.getLog()
        try:
            log.info("opening Instance " + instance)
            #self.SearchFor(instance)
            if self.Check_If_Entity_Exists("link", instance):
                self.driver.find_element_by_link_text(instance).click()
                self.Wait_for_Completion()
                return True, 1
            else:
                self.ErroroutScreenShot()
                e = "There is no instance with the name " + instance
                log.error(e)
                fn = sys._getframe().f_code.co_name
                return False, fn, e
        except Exception as e:
            self.ErroroutScreenShot()
            fn = sys._getframe().f_code.co_name
            log.exception(str(e))
            return False, fn, str(e)

    def getServInstances(self):
        """ Fetches the instances for the added server """
        log = loghelper.getLog()
        try:
            inst=[]
            log.info("instance under the given client ")
            parent = self.driver.find_elements_by_xpath("//div[2]/div[@class='ui-grid-canvas']/div")
            for i in parent:
                t = i.find_element_by_xpath("./div/div[1]/a").text
                t = t.strip()
                t = t.replace(" ","")
                inst.append(t)
            self.Wait_for_Completion()
            log.info(str(inst))
            for i in inst:
                log.info(str(i))
            return True
        except Exception as e:
            self.ErroroutScreenShot()
            fn = sys._getframe().f_code.co_name
            log.exception(str(e))
            return False, fn, str(e)

    def GetInstanceDetails(self,instance):#remove entityName and remove if
        log = loghelper.getLog()
        try:
            if instance is not None:
                log.info("Fetching the details of the instance- %s" %instance)
                InstanceDetails = {}
                displayedTitle=self.driver.find_element_by_xpath('//h1[@class="float-left ng-binding"]')
                InstanceDetails.update({"InstanceName":(displayedTitle.text)})
                oraHome = self.driver.find_element_by_xpath('//div/div[1]/ul/li[2]/span[2][@class="pageDetailColumn ng-binding"]')
                InstanceDetails.update({"Oracle home": (oraHome.text.encode('utf-8'))})
                log.info("Instance details fetched")
                return InstanceDetails
        except Exception as e:
            fn = sys._getframe().f_code.co_name
            log.exception(str(e))
            return False, fn, str(e)

    def AddInstance(
            self,
            Instance,
            oracleHome,
            osusername,
            osuserpassword,
            dbusername,
            dbpassword,
            instanceName,
            dbStoragePolicy,
            logStoragePolicy,
            os):
        """ Adds a new Instance to the iDA.
            Instance        : a string, name of the Instance we want to add
            oracleHome      : a string, name of the Oracle home
            osusername      : a string, name of the oracle user
            osuserpassword  : a string, name of the oracle user password
            dbusername      : a string, the database username
            dbpassword      : a string, the database password
            instanceName    : a string, database instance name
                Return (True, 1) on successfull completion
                        (False, func_name, error_msg) otherwise"""
        log = loghelper.getLog()
        try:
            log.info("Adding a new Instance")
            '''Adds only the non-existing instance.'''
            if not self.Check_If_Entity_Exists("link", Instance):
                self.driver.find_element_by_link_text("Add instance").click()
                self.Wait_for_Completion()
                '''Filling the form with all the required parameters.'''
                self.driver.find_element_by_id("instanceName").clear()
                self.driver.find_element_by_id("instanceName").send_keys(Instance)
                self.driver.find_element_by_id("oracleHome").clear()
                self.driver.find_element_by_id("oracleHome").send_keys(oracleHome)
                self.driver.find_element_by_id("osUserName").clear()
                self.driver.find_element_by_id("osUserName").send_keys(osusername)
                log.info(os)
                if os != 'Linux':
                    self.driver.find_element_by_id("osUserPassword").clear()
                    self.driver.find_element_by_id("osUserPassword").send_keys(osuserpassword)
                self.Wait_for_Completion()
                self.driver.find_element_by_id("dbUserName").clear()
                self.driver.find_element_by_id("dbUserName").send_keys(dbusername)
                self.driver.find_element_by_id("dbPassword").clear()
                self.driver.find_element_by_id("dbPassword").send_keys(dbpassword)
                self.driver.find_element_by_id("dbInstanceName").clear()
                self.driver.find_element_by_id("dbInstanceName").send_keys(instanceName)
                self.Wait_for_Completion()
                '''Submitting the form'''
                self.driver.find_element_by_xpath("//button[@type='submit']").click()
                '''checking if any error message after filling the form.'''
                self.Wait_for_Completion()
                self.Wait_for_Completion()
                if self.Check_If_Entity_Exists("xpath", "//span[@class='error']"):
                    warn = self.driver.find_element_by_xpath("//span[@class='error']").text
                    log.info(str(warn))
                    '''Closing the input form'''
                    self.driver.find_element_by_xpath("//button[@type='button']").click()
                    self.Wait_for_Completion()
                    log.error(str(warn))
                    fn = sys._getframe().f_code.co_name
                    return False, fn, str(warn)
                else:
                    return True, 1
            else:
                self.ErroroutScreenShot()
                e = "Entry already exists for: " ,Instance
                log.error(e)
                fn = sys._getframe().f_code.co_name
                return False, fn, str(e)
        except Exception as e:
            log.exception(str(e))
            fn = sys._getframe().f_code.co_name
            return False, fn, str(e)

    def ActionAddInstance(
            self,
            Instance,
            oracleHome,
            osusername,
            osuserpassword,
            dbusername,
            dbpassword,
            instanceName,
            dbStoragePolicy,
            logStoragePolicy,
            os):
        """ Adds a new Instance to the iDA.

            Instance   : a string, name of the Instance we want to add
            oracleHome  : a string, name of the Oracle home
            osusername  : a string, name of the oracle user
            osuserpassword  : a string, name of the oracle user password
            dbusername  : a string, the database username
            dbpassword  : a string, the database password
            instanceName: a string, database instance name
            dbStoragePolicy : a string, storage policy to use for db
            logStoragePolicy: a string, storage policy to use for logs

            Return (True, 1) on successfull completion
                    (False, func_name, error_msg) otherwise
        """
        log = loghelper.getLog()
        try:
            log.info("Adding a new Instance from action menu")
            if self.Check_If_Entity_Exists("link", "Oracle"):
                self.driver.find_element_by_xpath("//div[1]/div[2]/div[2]/div/div[2]/div/div[3]/div/a[@class = 'uib-dropdown-toggle dropdown-toggle']").click()
                self.driver.find_element_by_link_text("Add instance").click()
                self.Wait_for_Completion()
                self.driver.find_element_by_id("instanceName").clear()
                self.driver.find_element_by_id("instanceName").send_keys(Instance)

                self.driver.find_element_by_id("oracleHome").clear()
                self.driver.find_element_by_id("oracleHome").send_keys(oracleHome)

                self.driver.find_element_by_id("osUserName").clear()
                self.driver.find_element_by_id("osUserName").send_keys(osusername)

                log.info(os)
                if os != 'Linux':
                    self.driver.find_element_by_id("osUserPassword").clear()
                    self.driver.find_element_by_id("osUserPassword").send_keys(osuserpassword)

                self.driver.find_element_by_id("dbUserName").clear()
                self.driver.find_element_by_id("dbUserName").send_keys(dbusername)

                self.driver.find_element_by_id("dbPassword").clear()
                self.driver.find_element_by_id("dbPassword").send_keys(dbpassword)

                self.driver.find_element_by_id("dbInstanceName").clear()
                self.driver.find_element_by_id("dbInstanceName").send_keys(instanceName)

                '''
                # No Storage Policy used for this form.
                Select(self.driver.find_element_by_id("DBStoragePolicy")
                       ).select_by_visible_text(dbStoragePolicy)
                Select(self.driver.find_element_by_id(
                    "LogStoragePolicy")).select_by_visible_text(logStoragePolicy)
                #retVal = self.driver.find_element_by_xpath("//button[@type='submit']").click()
                #retVal = self.OracleInstance(Instance,oracleHome,osusername,osuserpassword,dbusername,dbpassword,instanceName,dbStoragePolicy,logStoragePolicy)
                #if not retVal:
                #   return retVal[0],retval[1],retVal[2]
                '''
                '''Submitting form'''
                self.driver.find_element_by_xpath("//button[@type='submit']").click()
                self.Wait_for_Completion()
                '''Checking for Warnings when saving instance.'''
                if self.Check_If_Entity_Exists("xpath", "//span[@class='error']"):
                    warn = self.driver.find_element_by_xpath("//span[@class='error']").text
                    log.info(str(warn))
                    '''Closing the input form'''
                    self.driver.find_element_by_xpath("//button[@type='button']").click()
                    self.Wait_for_Completion()
                    log.error(str(warn))
                    fn = sys._getframe().f_code.co_name
                    return False, fn, str(warn)
                else:
                    return True, 1
            else:
                self.ErroroutScreenShot()
                e = "Add instance not selected."
                log.error(e)
                fn = sys._getframe().f_code.co_name
                return False, fn, str(e)
        except Exception as e:
            log.exception(str(e))
            fn = sys._getframe().f_code.co_name
            return False, fn, str(e)

    def ActionAddSubclient(
            self,
            instanceName,
            subclientName,
            storagePolicy,
            dataStreams,
            dataBackup,
            dataBackupType,
            ArchiveLog,
            DeleteArchiveLog):
        """Creates a Oracle subclient
            subClient       : a string, name of the subclient we want to associate the backupset to
            storagePolicy   : a string, storage policy we want to associate to with this subclient
            streams         : a string,   the number of streams to be allocated
            dataBackup      : a boolean, True if the data needs to be backedup
            datatype        : a string, type of data to be backed up
            ArchiveLog      : a boolean, True if archive logs needs to be backedup
            DeleteArchiveLog: a boolean, True if archive logs needs to be deleted
            Return (True, 1) on successfull completion
                    (False, func_name, error_msg) otherwise
        """
        log = loghelper.getLog()
        try:
            log.info("Adding a new oracle subclient")
            self.Wait_for_Completion()
            log.info('instanceName:' +instanceName)
            self.driver.find_element_by_xpath("//a[contains(text(),'" +instanceName +"')]/../../div[3]/div/a/span[@class='grid-action-icon']").click()
            if self.Check_If_Entity_Exists("link", "Add subclient"):
                self.driver.find_element_by_link_text('Add subclient').click()
                self.Wait_for_Completion()
                log.info('Fills the subclient form')
                self.driver.find_element_by_xpath("//input[@name = 'subclientName']").clear()
                self.driver.find_element_by_xpath("//input[@name = 'subclientName']").send_keys(subclientName)
                # /html/body/div[1]/div/div/div[2]/form/div/label[2]/span[2]/isteven-multi-select/span/button
                self.driver.find_element_by_xpath("//div[1]/div/div/div[2]/form/div/label[2]/span[2]/isteven-multi-select/span/button[@type='button' and @class='ng-binding']").click()
                parent = self.driver.find_elements_by_xpath("//div[@class='checkBoxContainer']/div")
                for i in parent:
                    t = i.find_element_by_xpath("./div/label/span").text
                    t = t.strip()
                    t = t.replace(" ","")
                    #log.info("Found plan:"+t)
                    #log.info(storagePolicy)
                    if t.find(storagePolicy)>=0:
                        log.info("it matched")
                        i.find_element_by_xpath("./div/label/input/following-sibling::span").click()
                        break
                    else:
                        continue
                self.Wait_for_Completion()
                self.driver.find_element_by_id('numberBackupStreams').clear()
                self.driver.find_element_by_id('numberBackupStreams').send_keys(dataStreams)
                if dataBackup == "False":
                    log.info("Databackup is not required, so unchecking it")
                    self.driver.find_element_by_xpath("//div[1]/div/div/div[2]/form/div/label[4]/span[1]/label[@for = 'dataBackup']").click()
                else:
                    log.info("Databackup is true, selecting the datatype: " +dataBackupType)
                    #self.driver.find_element_by_xpath("//input[@id='" + dataBackupType + "' and @type='radio']").click()
                    self.driver.find_element_by_xpath("//input[@id='" + dataBackupType + "']").click()
                if ArchiveLog == "False":
                    log.info("Archivelog is not required, so unchecking it")
                    self.driver.find_element_by_xpath("//div[1]/div/div/div[2]/form/div/label[5]/span[1]/label[@for = 'logBackup']").click()
                else:
                    log.info("Archivelog is required, checking if delete archive logs is required")
                    if DeleteArchiveLog == "False":
                        log.info("DeleteArchivelog is not required so unchecking it")
                        self.driver.find_element_by_xpath("//div[1]/div/div/div[2]/form/div/label[6]/span[1]/label[@for = 'deleteArchiveLogs']").click()
                self.driver.find_element_by_xpath("//form/div/div[3]/button[2][@type = 'submit' and @class='btn btn-primary cvBusyOnAjax']").click()
                self.Wait_for_Completion()
                if self.Check_If_Entity_Exists("xpath", "//span[@class='error']"):
                    warn = self.driver.find_element_by_xpath("//span[@class='error']").text
                    log.info(str(warn))
                    '''Closing the input form'''
                    self.driver.find_element_by_xpath("//button[@type='button']").click()
                    self.Wait_for_Completion()
                    log.error(str(warn))
                    fn = sys._getframe().f_code.co_name
                    return False, fn, str(warn)
                else:
                    return True, 1
            else:
                e = "there is no option to create subclient"
                log.error(e)
                fn = sys._getframe().f_code.co_name
                return False, fn, e
        except Exception as e:
            log.exception(str(e))
            fn = sys._getframe().f_code.co_name
            return False, fn, str(e)

    def OracleRestore(self,instance, PITime, SCNvalue, Files, destinationHost, database = True, controlFile = False, PIT = False, SCN = False, currtime = False):
        """Restores the content of the instance
            instance    : a string, name of the instance to be restored
            Files       : a list, the list of tables to restore, if "All" is given then all the tablespaces are selected for restore
            Return (True, 1) on successfull completion
                    (False, func_name, error_msg) otherwise
        """
        log = loghelper.getLog()
        try:
            log.info("Restoring the instance content")
            self.Wait_for_Completion()
            if self.Check_If_Entity_Exists("xpath", "//a[text()='" + instance + "']/../../div[2]/span/a[text()='Restore']"):
                self.driver.find_element_by_xpath("//a[text()='" + instance + "']/../../div[2]/span/a[text()='Restore']").click()
                self.Wait_for_Completion()
                if Files != "All":
                    if self.driver.find_element_by_xpath("//div[@class='ui-grid-contents-wrapper']/div[1]/div/div[1]//div[@class='ng-scope']/div/div").is_selected():
                        self.driver.find_element_by_xpath("//div[@class='ui-grid-contents-wrapper']/div[1]/div/div[1]//div[@class='ng-scope']/div/div").click()
                    Selected = []
                    while(True):
                        elements = self.driver.find_elements_by_xpath("//div[1]/div[2]/div[2]/div[@class='ui-grid-canvas']/div")
                        i = 1
                        flag = []
                        for elem in elements:
                            f = elem.find_element_by_xpath("./div/div[1]").text
                            for File in Files:
                                if f == File:
                                    flag.append(i)
                                    Selected.append(f)
                                else:
                                    continue
                            i = i + 1
                        for flg in flag:
                            flg = str(flg)
                            self.driver.find_element_by_xpath("//div[1]/div/div[2]/div[@class='ui-grid-canvas']/div[" + flg + "]/div/div/div/div/div").click()
                            Files = list(set(Files) - set(Selected))
                        if self.CVTable_NextButtonExists():
                            if self.driver.find_element_by_xpath(
                                    "//button[@ng-disabled='cantPageForward()']").is_enabled():
                                self.CVTable_ClickNextButton()
                                continue
                            else:
                                if Files != []:
                                    e = "Could not find the item " + str(Files)
                                    log.error(e)
                                    self.NotifyBuildBreak(
                                        self.__class__.__name__, sys._getframe().f_code.co_name, e)
                                    break
                                else:
                                    break
                        else:
                            if Files != []:
                                e = "Could not find the items " + str(Files)
                                log.error(e)
                                self.NotifyBuildBreak(
                                    self.__class__.__name__, sys._getframe().f_code.co_name, e)
                                break
                            else:
                                break
                self.driver.find_element_by_xpath("//div[@id='browseActions']/a[contains(text(),'Restore')]").click()
                self.Wait_for_Completion()
                Select(self.driver.find_element_by_id("destinationServer")
                       ).select_by_visible_text(destinationHost)
                self.Wait_for_Completion()
                Select(self.driver.find_element_by_id("destinationInstance")
                       ).select_by_visible_text(instance)
                self.Wait_for_Completion()
                self.Wait_for_Completion()
                if not database:
                    if self.driver.find_element_by_id("database").is_selected():
                        self.driver.find_element_by_xpath("//input[@id='database']/following-sibling::label").click()
                if not controlFile:
                    if self.driver.find_element_by_id("controlfile").is_selected():
                        self.driver.find_element_by_xpath("//input[@id='controlfile']/following-sibling::label").click()
                self.driver.find_element_by_xpath("//div[1]/div/div/div/form/div[1]/div/div[5]/div/label[@for = 'spfile']").click()
                if currtime:
                    log.info("Restoring in Current Time")
                    self.driver.find_element_by_xpath("//input[@id='currentTime']/following-sibling::label").click()
                if PIT:
                    log.info("Restoring with Point in Time")
                    self.driver.find_element_by_xpath("//input[@id='pitDate1']/following-sibling::label").click()
                    self.driver.find_element_by_id("dateTimeValue").clear()
                    self.driver.find_element_by_id("dateTimeValue").send_keys(PITime)
                if SCN:
                    log.info("Restoring with SCN")
                    self.driver.find_element_by_xpath("//input[@id='scn']/following-sibling::label").click()
                    self.driver.find_element_by_id("pitScn").clear()
                    self.driver.find_element_by_id("pitScn").send_keys(SCNvalue)
                self.Wait_for_Completion()
                #Select(self.driver.find_element_by_id("destinationInstance")
                      # ).select_by_visible_text(instance)
                self.Wait_for_Completion()
                self.driver.find_element_by_xpath("//div[1]/div/div/div/form/div[2]/button[2][@type = 'submit']").click()
                self.Wait_for_Completion()
                '''if self.Check_If_Entity_Exists("xpath", "/html/body/div[3]/div/div/div/div"):
                    jtext = self.driver.find_element_by_xpath(
                        "/html/body/div[3]/div/div/div/div").text
                    jobID = jtext.split(": ")[1].split("\n")[0]
                    log.info("Restore job " + str(jobID) + " has started")
                    //*[@id="wrapper"]/div/div/app-root/div/div/div/div/div'''
                #//*[@id="wrapper"]/div[1]/div/div/div/div/a
                if self.Check_If_Entity_Exists("xpath", "//div[1]/div/div/div/div/a[contains(text(), 'View jobs')]"):
                    self.driver.find_element_by_xpath("//div[1]/div/div/div/div/a[contains(text(), 'View jobs')]").click()
                    jtext = self.driver.find_element_by_xpath("//div/div/span/div/div[1]/div/h1").text
                    log.info(jtext)
                    #jobID = jtext.split(": ")[1].split("\n")[0]
                    jobID = re.findall('\d+', jtext.encode('utf-8'))
                    log.info("Restore job " + str(jobID) + " has started")
                    return True, jobID
            else:
                e = "there is no option to restore the instance"
                log.error(e)
                fn = sys._getframe().f_code.co_name
                return False, fn, e
        except Exception as e:
            log.exception(str(e))
            fn = sys._getframe().f_code.co_name
            return False, fn, str(e)
    def ActionClone(self,Reqinstance,FmT,ToT,jid,instance,orahomepath,pFile,sPath,resDays,resHrs,copyPrec,cmdFPath,PIT=False,ORR=False ):
        """Clones the instance with the given name
            instance    : a string, name of the instance to be cloned
            Returns (True,1) on succesful completion
                    (False, func_name, error_msg) otherwise
        """
        log = loghelper.getLog()
        try:
            log.info("Cloning the instance " + Reqinstance)
            self.driver.find_element_by_xpath(
                "//a[text()='" +
                Reqinstance +
                "']/../../div[3]/div/a/span[@class='grid-action-icon']").click()
            if self.Check_If_Entity_Exists("link", "Instant clone"):
                self.driver.find_element_by_link_text('Instant clone').click()
                self.Wait_for_Completion()
                if PIT:
                    log.info('Taking PIT')
                    self.driver.find_element_by_xpath("//input[@id='pitDate' and @type='radio']").click()
                    #SP10 from time removed
                    #self.driver.find_element_by_id("fromTime").clear()
                    #self.driver.find_element_by_id("fromTime").send_keys(FmT)
                    self.driver.find_element_by_id("toTime").clear()
                    self.driver.find_element_by_id("toTime").send_keys(ToT)
                    self.Wait_for_Completion()
                    self.driver.find_element_by_xpath("//button[contains(text(),'Next')]").click()
                    '''
                    #No content check as per SP10
                    log.info('Checking Content for PIT')
                    self.Wait_for_Completion()
                    if self.Check_If_Entity_Exists("id", "jobId+"+jid):
                        log.info("selecting job "+jid)
                        self.driver.find_element_by_xpath("//input[@value="+jid+" and @type='radio']").click()
                        self.driver.find_element_by_xpath("//button[contains(text(),'Next')]").click()
                    else:
                        log.info('Could not find any given job for PIT')
                        self.driver.find_element_by_xpath("//button[contains(text(),'Next')]").click()
                    '''
                else:
                    log.info('Taking most recent backup to clone')
                    #self.driver.find_element_by_xpath("//input[@id='mostRecent' and @type='radio']").click()
                    self.driver.find_element_by_xpath("//button[contains(text(),'Next')]").click()
                self.Wait_for_Completion()
                log.info('Destination details')
                #source and destination clients are same so commenting out
                #Select(self.driver.find_element_by_name(
                #"destClient")).select_by_visible_text(client)
                self.driver.find_element_by_id("destInstance").clear()
                self.driver.find_element_by_id("destInstance").send_keys(instance)
                self.driver.find_element_by_id("oraHome").clear()
                self.driver.find_element_by_id("oraHome").send_keys(orahomepath)
                self.Wait_for_Completion()
                '''
                self.driver.find_element_by_id("oraPfile").clear()
                self.driver.find_element_by_id("oraPfile").send_keys(pFile)
                self.driver.find_element_by_id("stagingPath").clear()
                self.driver.find_element_by_id("stagingPath").send_keys(sPath)
                self.Wait_for_Completion()
                '''
                self.driver.find_element_by_xpath("//button[contains(text(),'Next')]").click()
                log.info('Clone options')
                self.driver.find_element_by_id("rsvTPDays").clear()
                self.driver.find_element_by_id("rsvTPDays").send_keys(resDays)
                self.driver.find_element_by_id("rsvTPHours").clear()
                self.driver.find_element_by_id("rsvTPHours").send_keys(resHrs)
                self.driver.find_element_by_id("copyPrec").clear()
                self.driver.find_element_by_id("copyPrec").send_keys(copyPrec)
                if ORR:
                    #self.driver.find_element_by_xpath("//input[@id='forceCleanup' and @type='checkbox']").click()
                    self.driver.find_element_by_xpath("//div/div/span/cv-wizard-component/div/div[2]/div/div/div/div/div/form/div/data-ng-include/div/div/div[3]/div/label[@for ='forceCleanup']").click()
                    log.info('Overrided the existing ones')
                log.info('Post Clone Operation not used for now, uncomment the code in oracle.py as needed.')
                #self.driver.find_element_by_id("commondFilePath").clear()
                #self.driver.find_element_by_id("commondFilePath").send_keys(cmdFPath)
                self.Wait_for_Completion()
                self.driver.find_element_by_xpath("//button[contains(text(),'Next')]").click()
                self.Wait_for_Completion()
                self.driver.find_element_by_xpath("//button[contains(text(),'Finish')]").click()
                self.Wait_for_Completion()
                return True

                '''if self.Check_If_Entity_Exists("xpath", "//div/div/app-root/div/div/div/div/div/a"):
                    msg = self.driver.find_element_by_xpath("//div/div/app-root/div/div/div/div/div/a").text
                    log.info(msg)
                    JobId = re.findall("\d+",msg.encode('utf-8'))
                    for i in JobId:
                        JobID = str(i)
                    return True, JobID
                else:
                    log.info("could not fetch jobid")
                    return False'''
            else:
                e = "there is no option to restore the instance"
                log.error(e)
                fn = sys._getframe().f_code.co_name
                return False, fn, e
        except Exception as e:
            log.exception(str(e))
            fn = sys._getframe().f_code.co_name
            return False, fn, str(e)

    def ActionCloudMigration(self,
                       instance,
                       cloudType,
                       AllocPolicyId,
                       oraHomeText,ami,instancetype,
                       Network,
                       mountPathName,
                       volumeSize,
                       volumeType,
                       iopsLimit,
                       volumeTag,
                       oracleHome,
                       proxyClient,
                       Migrationpt,
                       Baseline,
                       noOfStreams,
                       copyPreceDenc,
                       httpsTunnelPort,
                       validationScript,
                       addVolume = False,
                       CloneFrmSrc = True,
                       firewall= True,
                       commServTunnel= False,
                       commServTowardsClient = True,
                       throughProxy = False,
                       standByMode = False,
                       Copyprecedence = False,
                       ValidationScript = False ):
        """Migrates the specified instance to cloud.
            instance    : a string, name of the instance to be cloned
            Returns (True,1) on succesful completion
                    (False, func_name, error_msg) otherwise
        """
        log = loghelper.getLog()
        try:
            log.info("Migrating the instance " + instance)
            self.driver.find_element_by_xpath(
                "//a[text()='" +
                instance +
                "']/../../div[3]/div/a/span[@class='grid-action-icon']").click()
            if self.Check_If_Entity_Exists("link", "Migrate to cloud"):
                self.driver.find_element_by_link_text('Migrate to cloud').click()
                self.Wait_for_Completion()
                log.info('Server Configuration Details:')
                #self.driver.find_element_by_id('cloudType').click()
                #self.driver.find_element_by_link_text(cloudType).click()
                Select(self.driver.find_element_by_id('cloudType')).select_by_visible_text(cloudType)
                #self.driver.find_element_by_id('AllocPolicyId').click()
                #self.driver.find_element_by_link_text(AllocPolicyId).click()
                Select(self.driver.find_element_by_id('AllocPolicyId')).select_by_visible_text(AllocPolicyId)
                #to create new VM
                self.driver.find_element_by_id('oraHomeText').click()
                self.driver.find_element_by_id('oraHomeText').send_keys(oraHomeText)
                self.driver.find_element_by_id('oraHomeText').click()
                '''
                #to select the exiting VM
                self.driver.find_element_by_id('oraHomeText').click()
                self.driver.find_element_by_link_text(oraHomeText).click()
                '''
                self.Wait_for_Completion()
                self.driver.find_element_by_xpath("//div[2]/div/div/button[@title = 'Next']").click()
                self.Wait_for_Completion()
                log.info('Cloud compute configuration:')
                self.Wait_for_Completion()
                '''
                Select(self.driver.find_element_by_id('amiName')).select_by_visible_text(ami)
                Select(self.driver.find_element_by_id('instanceType')).select_by_visible_text(instancetype)
                if not Network == 'none':
                    self.driver.find_element_by_xpath("//span[@class = 'multiSelect inlineBlock buttonClicked']/button[@type = 'button']").click()
                    #self.driver.find_element_by_xpath("//span/div/div[1]/div[2]/div[1]/input[@placeholder = 'Search']").click()
                    parent = self.driver.find_elements_by_xpath("//div[@class='checkBoxContainer']/div")
                    for i in parent:
                        t = i.find_element_by_xpath("./div/label/span").text
                        t = t.strip()
                        t = t.replace(" ","")
                        log.info("Found Network:"+t)
                        log.info(Network)
                        if t.find(Network)>=0:
                            log.info("it matched")
                            i.find_element_by_xpath("./div/label/input/following-sibling::span").click()
                            break
                        else:
                            continue
                    self.Wait_for_Completion()
                if addVolume:
                    self.driver.find_element_by_xpath("//button[contains(text(),'Add storage')]").click()
                    if cloudType == 'Amazon':
                        log.info("Adding Storage for Amazon: ")
                        self.driver.find_element_by_id('mountPathName').clear()
                        self.driver.find_element_by_id('mountPathName').send_keys(mountPathName)
                        self.driver.find_element_by_id('volumeSize').clear()
                        self.driver.find_element_by_id('volumeSize').send_keys(volumeSize)
                        self.driver.find_element_by_id('volumeType').click()
                        self.driver.find_element_by_link_text(volumeType).click()
                        self.driver.find_element_by_id('iopsLimit').clear()
                        self.driver.find_element_by_id('iopsLimit').send_keys(iopsLimit)
                        self.driver.find_element_by_id('volumeTag').clear()
                        self.driver.find_element_by_id('volumeTag').send_keys(volumeTag)
                        self.driver.find_element_by_xpath("//button[@type='submit']").click()
                    else:
                        log.info("Adding Storage for given cloud type: ")
                        self.driver.find_element_by_id('mountPathName').clear()
                        self.driver.find_element_by_id('mountPathName').send_keys(mountPathName)
                        self.driver.find_element_by_id('volumeSize').clear()
                        self.driver.find_element_by_id('volumeSize').send_keys(volumeSize)
                        self.driver.find_element_by_id('volumeTag').clear()
                        self.driver.find_element_by_id('volumeTag').send_keys(volumeTag)
                        self.driver.find_element_by_xpath("//button[@type='submit']").click()
                '''
                self.driver.find_element_by_xpath("//button[contains(text(),'Next')]").click()
                self.Wait_for_Completion()
                log.info('Software configuration:')
                if not CloneFrmSrc:
                    self.driver.find_element_by_xpath("//input[@id='installedOracleHome' and @type='radio']").click()
                #self.driver.find_element_by_id('oracleHome').clear()
                #self.driver.find_element_by_id('oracleHome').send_keys(oracleHome)
                self.driver.find_element_by_xpath("//button[contains(text(),'Next')]").click()
                self.Wait_for_Completion()
                log.info('Firewall configuration:')
                if firewall:
                    #self.driver.find_element_by_id('There is firewall between client machine and CommServe').click()

                    self.driver.find_element_by_xpath("//div/div[1]/label[@for = 'enableFirewall']").click()
                    if commServTunnel:
                        self.driver.find_element_by_id('commServTunnel').click()
                        self.driver.find_element_by_id('httpsTunnelPort').clear()
                        self.driver.find_element_by_id('httpsTunnelPort').send_keys(httpsTunnelPort)
                    if commServTowardsClient:
                        self.driver.find_element_by_id('commServTowardsClient').click()
                        self.driver.find_element_by_id('httpsTunnelPort').clear()
                        self.driver.find_element_by_id('httpsTunnelPort').send_keys(httpsTunnelPort)
                    if throughProxy:
                        self.driver.find_element_by_id('throughProxy').click()
                        '''as per sp10 - proxy settings'''
                        Select(self.driver.find_element_by_id('proxyClient')).select_by_visible_text(proxyClient)
                self.Wait_for_Completion()
                self.driver.find_element_by_xpath("//button[@type = 'submit' and @class='btn btn-primary cvBusyOnAjax']").click()
                log.info('Migration options:')
                log.info(str(Migrationpt)+','+str(Baseline))
                if Migrationpt != 'onlineData':
                    self.driver.find_element_by_id('onlineSubset').click()
                if Baseline != 'mostRecentBackup':
                    self.driver.find_element_by_id('runFullBackup').click()
                if standByMode:
                    self.driver.find_element_by_xpath("//div/cv-tile-component[1]/div/div/div/span[5]/label[1]/span/label[@for = 'standByMode']").click()
                self.driver.find_element_by_id('noOfStreams').clear()
                self.driver.find_element_by_id('noOfStreams').send_keys(noOfStreams)
                if Copyprecedence:
                    #self.driver.find_element_by_link_text('Copy precedence').click()
                    self.driver.find_element_by_xpath("//div/div[2]/div/cv-tile-component[1]/div/div/div/span[6]/label/span[1]/label[@for = 'copyPreceDencSect']").click()
                    self.driver.find_element_by_id('copyPreceDenc').clear()
                    self.driver.find_element_by_id('copyPreceDenc').send_keys(copyPreceDenc)
                if ValidationScript:
                    self.driver.find_element_by_id('validationScript').clear()
                    self.driver.find_element_by_id('validationScript').send_keys(validationScript)
                self.Wait_for_Completion()
                self.driver.find_element_by_xpath("//button[contains(text(),'Finish')]").click()
                self.Wait_for_Completion()
                return True
                '''
                if self.Check_If_Entity_Exists("xpath", "//div[1]/div/div/div/div/a"):
                    msg = self.driver.find_element_by_xpath("//div[1]/div/div/div/div/a").text
                    log.info(msg)
                    JobId = re.findall("\d+",msg.encode('utf-8'))
                    for i in JobId:
                        JobID = str(i)
                    self.driver.find_element_by_xpath("//div[1]/div/div/div/div/a").click()
                    self.Wait_for_Completion()
                    self.Wait_for_Completion()
                    return True, JobID
                else:
                    log.info("could not fetch jobid")
                    return False
                '''

            else:
                e = "there is no option for 'Migrate to cloud'."
                log.error(e)
                fn = sys._getframe().f_code.co_name
                return False, fn, e
        except Exception as e:
            log.exception(str(e))
            fn = sys._getframe().f_code.co_name
            return False, fn, str(e)

    def CloneDB(
            self,
            client,
            instance,
            oraHome,
            user,
            pFile,
            stagingPath,
            resDays,
            resHrs,
            copyPres,
            PIT=False,
            year=None,
            month=None,
            date=None,
            hours=None,
            mins=None,
            session=None):
        """Clones a instance of oracle
            client      :   a string, the name of the client
            instance    :   a string, the name of the instance to be cloned
            oraHome     :   a string, the path to the oracle Home
            pFile       :   a string, the path to tehe pFile
            stagingPath :   a string, the location where the cloned instance has to be staged
            resDays     :   an integer, the no of days the cloned instance has to be reserved
            resHrs      :   an integer, the hours the cloned instance has to be reserver for
            copyPres    :   an integer, the copy precedence from which the instance has to be cloned
            PIT         :   a boolean, true if the instance has to cloned from a backup done in point in time
            year        :   an integer, year on which the backup was run
            month       :   an integer, month on which the backup was run
            date        :   an integer, date on which the backup was run
            hours       :   an integer, time in hours on which the backup was run
            mins        :   an integer, time in mins on which the backup was run
            session     :   a string, AM or PM indicating the time of the day
            Returns (True,1), if clone is successful
                    (False,fnc_name,error_msg), otherwise
        """
        log = loghelper.getLog()
        try:
            log.info("Cloning an oracle instance")

            Select(self.driver.find_element_by_name(
                "destClient")).select_by_visible_text(client)
            Select(self.driver.find_element_by_name(
                "orclInstance")).select_by_visible_text(instance)
            self.driver.find_element_by_id("oraHome").clear()
            self.driver.find_element_by_id("oraHome").send_keys(oraHome)
            self.driver.find_element_by_id("userName").clear()
            self.driver.find_element_by_id("userName").send_keys(user)
            self.driver.find_element_by_id("oraPfile").send_keys(pFile)
            self.driver.fin_element_by_id("stagingPath").send_keys(stagingPath)
            self.driver.find_element_by_link_text("Options").click()
            self.driver.find_element_by_id("rsvTPDays").clear()
            self.driver.find_element_by_id("rsvTPDays").send_keys(resDays)
            self.driver.find_element_by_id("rsvTPHours").clear()
            self.driver.find_element_by_id("rsvTPHours").send_keys(resHrs)
            self.driver.find_element_by_id("copyPrec").clear()
            self.driver.find_element_by_id("copyPrec").send_keys(copyPres)

            if PIT:
                self.driver.find_element_by_id("pitDate1").click()
                y = str(datetime.datetime.now()).rsplit("-", 2)[0]
                self.driver.find_element_by_xpath(
                    "//div[2]/div/table/thead/tr[1]/th[2]/button/strong[contains(text(),'" + y + "')]").click()
                if year:
                    self.driver.find_element_by_xpath(
                        "//div[2]/div/table/thead/tr/th[2]/button/strong[contains(text(),'" + y + "')]").click()
                    self.driver.find_element_by_xpath(
                        "//button/span[contains(text(),'" + year + "')]").click()
                self.driver.find_element_by_xpath(
                    "//button/span[contains(text(),'" + month + "')]").click()
                self.driver.find_element_by_xpath(
                    "//div[2]/div/table/tbody//button/span[contains(text(),'" + date + "')]").click()
                self.driver.find_element_by_xpath(
                    "//div[2]/table/tbody/tr[2]/td[1]/input").clear()
                self.driver.find_element_by_xpath(
                    "//div[2]/table/tbody/tr[2]/td[1]/input").send_keys(hours)
                self.driver.find_element_by_xpath(
                    "//div[2]/table/tbody/tr[2]/td[3]/input").clear()
                self.driver.find_element_by_xpath(
                    "//div[2]/table/tbody/tr[2]/td[3]/input").send_keys(mins)
                sess = self.driver.find_element_by_xpath(
                    "//div[2]/table/tbody/tr[2]/td[4]/button")
                if not session == sess.text:
                    sess.click()
                self.driver.find_element_by_xpath(
                    "//div[3]/button[contains(text(),'OK')]").click()
                self.Wait_for_Completion()

            self.driver.find_element_by_link_text("Summary").click()
            self.driver.find_element_by_xpath("//form/div/button[2]").click()
            self.Wait_for_Completion()

            return True, 1
        except Exception as e:
            log.exception(str(e))
            fn = sys._getframe().f_code.co_name
            return False, fn, str(e)
    def AddDBserver(self, ostype, Dbservnme, hstm, usrnme, psswrd, plan):
        """ Adds a DB Instance.
            OSType          : a string, type of OS Windows or Unix/Linux
            DB server name  : a string, name of the Oracle DB
            Hostname        : a string, Host name
            Username        : a string, Username to connect to host
            Password        : a string, Password to connect to host
            Plan            : a string, the DB plan
                Return (True, 1) on successfull completion
                        (False, func_name, error_msg) otherwise"""
        log = loghelper.getLog()
        try:
            log.info("Adding details into form to create Oracle DB instance")
            if self.Check_If_Entity_Exists("link", 'Add database server'):
                self.driver.find_element_by_link_text("Add database server").click()
                self.driver.find_element_by_link_text("Oracle").click()
                self.Wait_for_Completion()
                '''Filling the form with all the required parameters.'''
                if ostype != "UNIX":
                    self.driver.find_element_by_xpath("//input[@type='radio' and @value='WINDOWS']").click()
                else:
                    log.info("Unknown OS Type, cannot fill the form further")
                    return False
                self.driver.find_element_by_name("serverName").clear()
                self.driver.find_element_by_name("serverName").send_keys(Dbservnme)
                #self.driver.find_element_by_name("hostname").clear()
                #self.driver.find_element_by_name("hostname").send_keys(hstm)
                self.driver.find_element_by_name("userName").clear()
                self.driver.find_element_by_name("userName").send_keys(usrnme)
                self.driver.find_element_by_name("password").clear()
                self.driver.find_element_by_name("password").send_keys(psswrd)
                self.driver.find_element_by_id("plan").click()
                self.driver.find_element_by_id("plan").send_keys(plan)
                self.Wait_for_Completion()
                self.driver.find_element_by_xpath("//div[1]/div/div/div[2]/ng-include/div/form/div[2]/button[2]").click()
                #return True
                self.Wait_for_Completion()
                return True
                '''if self.Check_If_Entity_Exists("xpath", "//div[1]/div/div/div/div/a"):
                    msg = self.driver.find_element_by_xpath("//div[1]/div/div/div/div/a").text
                    log.info(msg)
                    JobId = re.findall("\d+",msg.encode('utf-8'))
                    for i in JobId:
                        JobID = str(i)
                    return True, JobID
                else:
                    log.info("could not fetch jobid")
                    return False'''
            else:
                self.ErroroutScreenShot()
                e = "Cannot add oracle db instance "
                log.error(e)
                fn = sys._getframe().f_code.co_name
                return False, fn, str(e)
        except Exception as e:
            log.exception(str(e))
            fn = sys._getframe().f_code.co_name
            return False, fn, str(e)

    def ActionRestoreHistoryOracleAgent(self):
        """Opens the Restore history of the Oracle agent for the given client.
            Returns (True,1), if successful
                    (False, func_name, error_msg), otherwise
        """
        log = loghelper.getLog()
        try:
            log.info("Opens the Restore history of the Oracle agent for the given client. ")
            if self.Check_If_Entity_Exists("link", "Oracle"):
                self.driver.find_element_by_xpath("//div[1]/div[2]/div[2]/div/div[2]/div/div[3]/div/a[@class = 'uib-dropdown-toggle dropdown-toggle']").click()
                self.driver.find_element_by_link_text("Restore history").click()
                self.Wait_for_Completion()
                self.driver.find_element_by_xpath("//span[@class = 'dropdownArrow right']").click()
                self.driver.find_element_by_link_text('All Jobs').click()
                self.Wait_for_Completion()
                jids= self.driver.find_elements_by_class_name("ui-grid-render-container")
                JobID = []
                for i in jids:
                    m = re.findall("\d+",i.text.encode('utf-8'))
                    for j in m:
                        if int(j)>100:
                            JobID.append(j)
                            log.info(str(j))
                if JobID == []:
                    return False
                else:
                    return True
            else:
                e = "There is no option to view the Restore history for Oracle agent under action menu"
                log.error(e)
                fn = sys._getframe().f_code.co_name
                return False, fn, e
        except Exception as e:
            log.exception(str(e))
            fn = sys._getframe().f_code.co_name
            return False, fn, str(e)
    def JobsOA(self):
        """Opens the Jobs of the Oracle agent for the given client.
            Returns (True,1), if successful
                    (False, func_name, error_msg), otherwise
        """
        log = loghelper.getLog()
        try:
            log.info("Opens the Restore history of the Oracle agent for the given client. ")
            if self.Check_If_Entity_Exists("link", "Jobs"):
                self.driver.find_element_by_link_text("Jobs").click()
                self.Wait_for_Completion()
                self.driver.find_element_by_xpath("//span[@class = 'dropdownArrow right']").click()
                self.driver.find_element_by_link_text('All Jobs').click()
                self.Wait_for_Completion()
                jids= self.driver.find_elements_by_class_name("ui-grid-render-container")
                JobID = []
                for i in jids:
                    m = re.findall("\d+",i.text.encode('utf-8'))
                    for j in m:
                        if int(j)>100:
                            JobID.append(j)
                            log.info(str(j))
                if JobID == []:
                    return False
                else:
                    return True
            else:
                e = "There is no option to view Jobs for Oracle agent under action menu"
                log.error(e)
                fn = sys._getframe().f_code.co_name
                return False, fn, e
        except Exception as e:
            log.exception(str(e))
            fn = sys._getframe().f_code.co_name
            return False, fn, str(e)
    def BackuphistoryOracleAgent(self):
        """Opens the backup history for Oracle Agent
            Returns (True,1), if successful
                    (False, func_name, error_msg), otherwise
        """
        log = loghelper.getLog()
        try:
            log.info(
                "Opening the backup history for the Oracle Agent ")
            if self.Check_If_Entity_Exists("link", 'Backup history'):
                self.driver.find_element_by_link_text('Backup history').click()
                self.Wait_for_Completion()
                self.driver.find_element_by_xpath("//span[@class = 'dropdownArrow right']").click()
                self.driver.find_element_by_link_text('All Jobs').click()
                self.Wait_for_Completion()
                jids= self.driver.find_elements_by_class_name("ui-grid-render-container")
                JobID = []
                for i in jids:
                    m = re.findall("\d+",i.text.encode('utf-8'))
                    for j in m:
                        if int(j)>100:
                            JobID.append(j)
                            log.info(str(j))
                if JobID == []:
                    return False
                else:
                    return True
            else:
                e = "There is no option to view the backup history of the subclient from the action menu"
                log.error(e)
                fn = sys._getframe().f_code.co_name
                return False, fn, e
        except Exception as e:
            log.exception(str(e))
            fn = sys._getframe().f_code.co_name
            return False, fn, str(e)
    def RestoreHistoryOracleAgent(self):
        """Opens the Restore history of the Oracle agent for the given client.
            Returns (True,1), if successful
                    (False, func_name, error_msg), otherwise
        """
        log = loghelper.getLog()
        try:
            log.info("Opens the Restore history of the Oracle agent for the given client. ")
            if self.Check_If_Entity_Exists("link", "Oracle"):
                self.driver.find_element_by_link_text("Restore history").click()
                self.Wait_for_Completion()
                self.driver.find_element_by_xpath("//span[@class = 'dropdownArrow right']").click()
                self.driver.find_element_by_link_text('All Jobs').click()
                self.Wait_for_Completion()
                jids= self.driver.find_elements_by_class_name("ui-grid-render-container")
                JobID = []
                for i in jids:
                    m = re.findall("\d+",i.text.encode('utf-8'))
                    for j in m:
                        if int(j)>100:
                            JobID.append(j)
                            log.info(str(j))
                if JobID == []:
                    return False
                else:
                    return True
            else:
                e = "There is no option to view the Restore history for Oracle agent under action menu"
                log.error(e)
                fn = sys._getframe().f_code.co_name
                return False, fn, e
        except Exception as e:
            log.exception(str(e))
            fn = sys._getframe().f_code.co_name
            return False, fn, str(e)

    def ContinuousBuild(self):
        """Run Continuous Build of the page to traverse all the links on this page."""
        ParsedPage.append(self.__class__.__name__)
        self.ExceptionHandling(self.__class__.__name__,
                               *(self.BackupHistory()))
        self.driver.back()
        self.Wait_for_Completion()
        self.ExceptionHandling(self.__class__.__name__,
                               *(self.RestoreHistory()))
        self.driver.back()
        self.Wait_for_Completion()
        self.ExceptionHandling(self.__class__.__name__,
                               *(self.AddBackupSet("hello")))

        self.ExceptionHandling(self.__class__.__name__,
                               *(self.iDADataManagement()))
        self.ExceptionHandling(self.__class__.__name__,
                               *(self.iDADataRecovery()))
        self.ExceptionHandling(self.__class__.__name__,
                               *(self.iDADataManagement()))
        self.ExceptionHandling(self.__class__.__name__,
                               *(self.iDADataRecovery()))

        self.ExceptionHandling(self.__class__.__name__,
                               *(self.ActionAddSubclient("sub1",
                                                         "newbkpset",
                                                         "MegaMind_SP_Dedup",
                                                         ["websymbols"])))
        self.ExceptionHandling(self.__class__.__name__,
                               *(self.ActionBackupHistory("defaultBackupSet")))
        self.driver.back()
        self.Wait_for_Completion()
        self.ExceptionHandling(self.__class__.__name__,
                               *(self.ActionRestoreHistory("defaultBackupSet")))
        self.driver.back()
        self.Wait_for_Completion()
        # self.ExceptionHandling(self.__class__.__name__,*(self.AddSecurityAssociations(UserConstants['userroles'])))

    def NextPage(self):
        """Returns a dictionary containing the pages that can be visited from this page."""
        return {
            'Backupset': 'OpenBackupset'
        }
