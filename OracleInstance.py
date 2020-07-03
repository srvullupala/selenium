#!/usr/bin/env python
"""
This module provides the function or operations that can be performed on the
Oracle instance on the AdminConsole
Class:
    OracleInstance() -> Oracle() -> iDA() -> ClientDetails() -> Clients() -> Server() --
            -> AdminPage() -> LoginPage() -> AdminConsoleBase() -> object()
Functions:
EditInstance()                  -- Edits the instance with the given name.
OpenSubclient()                 -- Opens the subclient with the given name.
AddSubclient()                  -- Adds a subclient with the specified content under the given backupset.
ActionAddSubclient()            -- Creates subclient from the action menu.
SubClientForm()                 -- Subclient form to fill up during subclient creation.
Refresh()                       -- Refreshes the status of the instance
ActionBackup()                  -- Backups the subclient
SubmitOracleBackup()            -- Submits a backup job
ActionOracleBackupHistory()     -- Opens the backup history of the subclient in an oracle instance
ActionOracleRestoreHistory()    -- Opens the restore history of the subclient in an oracle instance
Delete()                        -- Deletes the instance and its subclients
ActionDeleteSub()                 -- Deletes the subclient.
ContinuousBuild()               -- Run Continuous Build of the page to traverse all the links on this page.
NextPage()                      -- Returns a dictionary containing the pages that can be visited from this page.
"""

from Helper.Imports import *
from ContinuousBuild.ParamsDict import *
from OraclePages.CVPages import *
from AutomationUtils import loghelper
JID = ''

class OracleInstance(BackupsetLevel, Oracle):

    def EditInstance(self,
            Instance,
            oracleHome,
            osusername,
            osuserpassword,
            dbusername,
            dbpassword,
            instanceName,
            dbStoragePolicy,
            logStoragePolicy):
        """ Edits the instance with the given name.
            Instance        : a string, name of the Instance we want to add
            oracleHome      : a string, name of the Oracle home
            osusername      : a string, name of the oracle user
            osuserpassword  : a string, name of the oracle user password
            dbusername      : a string, the database username
            dbpassword      : a string, the database password
            instanceName    : a string, database instance name
                Return (True, 1) on successfull completion
                        (False, func_name, error_msg) otherwise
        """
        log = loghelper.getLog()
        try:
            log.info("Editing the required Instance")
            if self.Check_If_Entity_Exists("xpath", "//a[@data-ng-click = 'editInstance(instanceDetails.instance,true,instanceDetails)']"):
                self.driver.find_element_by_xpath("//a[@data-ng-click = 'editInstance(instanceDetails.instance,true,instanceDetails)']").click()
                self.Wait_for_Completion()
                self.driver.find_element_by_id("instanceName").clear()
                self.driver.find_element_by_id("instanceName").send_keys(Instance)
                self.driver.find_element_by_id("oracleHome").clear()
                self.driver.find_element_by_id("oracleHome").send_keys(oracleHome)
                self.driver.find_element_by_id("osUserName").clear()
                self.driver.find_element_by_id("osUserName").send_keys(osusername)
                #self.driver.find_element_by_id("osUserPassword").clear()
                #self.driver.find_element_by_id("osUserPassword").send_keys(osuserpassword)
                self.driver.find_element_by_id("dbUserName").clear()
                self.driver.find_element_by_id("dbUserName").send_keys(dbusername)
                self.driver.find_element_by_id("dbPassword").clear()
                self.driver.find_element_by_id("dbPassword").send_keys(dbpassword)
                self.driver.find_element_by_id("dbInstanceName").clear()
                self.driver.find_element_by_id("dbInstanceName").send_keys(instanceName)
                '''Submitting the form'''
                self.driver.find_element_by_xpath("//button[@type='submit']").click()
                '''checking if any error message after filling the form.'''
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
                '''
                Old form
                self.driver.find_element_by_id(
                    "osUserPassword").send_keys(OSpwd)
                self.driver.find_element_by_id("dbPassword").send_keys(OSpwd)
                self.driver.find_element_by_id("dbInstanceName").clear()
                self.driver.find_element_by_id("dbInstanceName").send_keys(SID)

                Select(self.driver.find_element_by_id("DBStoragePolicy")
                       ).select_by_visible_text(cmdlineSP)
                Select(self.driver.find_element_by_id(
                    "LogStoragePolicy")).select_by_visible_text(LogSP)

                self.driver.find_element_by_xpath(
                    "//form/div[2]/button[2]").click()
                self.Wait_for_Completion()

                return True, 1'''
            else:
                e = "There is no way to edit the instnace: ", Instance
                log.error(e)
                fn = sys._getframe().f_code.co_name
                return False, fn, e

        except Exception as e:
            fn = sys._getframe().f_code.co_name
            log.exception(str(e))
            return False, fn, str(e)

    def OpenSubclient(self, sbclnt):
        """ Opens the subclient with the given name.
            sbclnt   : a string, name of the subclient we want to open
            Return (True, 1) on successfull completion
                    (False, func_name, error_msg) otherwise """
        log = loghelper.getLog()
        try:
            log.info("opening SubClient " + sbclnt)
            #self.SearchFor(instance)
            if self.Check_If_Entity_Exists("link", sbclnt):
                self.driver.find_element_by_link_text(sbclnt).click()
                self.Wait_for_Completion()
                return True, 1
            else:
                self.ErroroutScreenShot()
                e = "There is no subclient with the name " + sbclnt
                log.error(e)
                fn = sys._getframe().f_code.co_name
                return False, fn, e
        except Exception as e:
            self.ErroroutScreenShot()
            fn = sys._getframe().f_code.co_name
            log.exception(str(e))
            return False, fn, str(e)
    def GetSubclientDetails(self,sbclnt):#remove entityName and remove if
        log = loghelper.getLog()
        try:
            if sbclnt is not None:
                log.info("Fetching the details of the subclient- %s" %sbclnt)
                '''ret,InstanceDetails=self.GetValuesForEntity()#rename
                if not ret:
                    log.error("Could not get details of the instance")
                    raise Exception(InstanceDetails)'''
                SubclientDetails = {}
                displayedTitle=self.driver.find_element_by_xpath("//h1[@class='float-left ng-binding']")
                SubclientDetails.update({"SubclientName":(displayedTitle.text.encode('utf-8'))})
                #Plan = self.driver.find_element_by_xpath("/div/div[3]/div/div[2]/span/p[@class='info-place-holder']/span/a[@class='ng-binding']")
                #SubclientDetails.update({"Plan": (Plan.text.encode('utf-8'))})
                log.info("Checking content for subclient.")
                self.driver.find_element_by_xpath("//div/div/div/span/cv-subclient-content/div/a[contains(text(),'Edit')]").click()
                if self.driver.find_element_by_id('dataBackup').is_selected():
                    SubclientDetails.update({"dataBackup": 'True'})
                    if self.driver.find_element_by_id('onlineData').is_selected():
                        SubclientDetails.update({"dataBackuptype": 'onlineData'})
                    elif self.driver.find_element_by_id('onlineSubset').is_selected():
                        SubclientDetails.update({"dataBackuptype": 'onlineSubset'})
                    elif self.driver.find_element_by_id('offlineData').is_selected():
                        SubclientDetails.update({"dataBackuptype": 'offlineData'})
                else:
                    SubclientDetails.update({"dataBackup": 'False'})

                if self.driver.find_element_by_id('logBackup').is_selected():
                    SubclientDetails.update({"ArchlogBackup": 'True'})
                    if self.driver.find_element_by_id('deleteArchiveLogs').is_selected():
                        SubclientDetails.update({"deleteArchiveLogs": 'True'})
                    else:
                        SubclientDetails.update({"deleteArchiveLogs": 'False'})
                else:
                    SubclientDetails.update({"ArchlogBackup": 'False'})
                    SubclientDetails.update({"deleteArchiveLogs": 'False'})

                log.info("Subclient details fetched: %s" %SubclientDetails)
                return SubclientDetails
        except Exception as e:
            fn = sys._getframe().f_code.co_name
            log.exception(str(e))
            return False, fn, str(e)
    def AddSubclient(
            self,
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
            if self.Check_If_Entity_Exists("link", "Add subclient"):
                self.driver.find_element_by_link_text("Add subclient").click()
                self.Wait_for_Completion()
                ret = self.SubClientForm(subclientName,storagePolicy,dataStreams,dataBackup,dataBackupType,ArchiveLog,DeleteArchiveLog)
                if ret[0]:
                    return True, 1
                else:
                    e = "the subclient creation failed"
                    log.error(e)
                    fn = sys._getframe().f_code.co_name
                    return False, fn, e
            else:
                e = "there is no option to create subclient"
                log.error(e)
                fn = sys._getframe().f_code.co_name
                return False, fn, e
        except Exception as e:
            log.exception(str(e))
            fn = sys._getframe().f_code.co_name
            return False, fn, str(e)
    def SubClientForm(
            self,
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
            self.Wait_for_Completion()
            log.info('Fills the subclient form')
            self.driver.find_element_by_xpath("//input[@name = 'subclientName']").clear()
            self.driver.find_element_by_xpath("//input[@name = 'subclientName']").send_keys(subclientName)
            # /html/body/div[1]/div/div/div[2]/form/div/label[2]/span[2]/isteven-multi-select/span/button
            self.driver.find_element_by_xpath("//div[1]/div/div/div/form/div[1]/div/div[2]/div/isteven-multi-select/span/button[@type='button' and @class='ng-binding']").click()
            #self.driver.find_element_by_xpath("//div[1]/div/div/div[2]/form/div/label[2]/span[2]/isteven-multi-select/span/button[@type='button' and @class='ng-binding']").click()
            parent = self.driver.find_elements_by_xpath("//div/div[@class='checkBoxContainer']/div")
            for i in parent:
                t = i.find_element_by_xpath("./div/label/span").text
                t = t.strip()
                t = t.replace(" ","")
                #log.info("Found plan:"+t)
                if t.find(storagePolicy)>=0:
                    log.info("matched")
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
        except Exception as e:
            log.exception(str(e))
            fn = sys._getframe().f_code.co_name
            return False, fn, str(e)
    def Refresh(self):
        """Refreshes the status of the instance
            Returns (True,status), if the refresh was successful
                    (False, fnc_name, error_msg), otherwise """
        log = loghelper.getLog()
        try:
            log.info("Refreshing the status")
            if self.Check_If_Entity_Exists("link", "Refresh"):
                self.driver.find_element_by_link_text("Refresh").click()
                self.Wait_for_Completion()
            else:
                e = "There is no option to refresh the instance."
                log.error(e)
                fn = sys._getframe().f_code.co_name
                return False, fn, e
            return True, 0
        except Exception as e:
            log.exception(str(e))
            fn = sys._getframe().f_code.co_name
            return False, fn, str(e)

    def ActionBackup(self, subclient, bkpLevel, cumulative):
        """Backups the subclient
            subclient   : a string, name of the subclient to be backed up
            bkpLevel    : a string, the type of backup to be performed
            cumulative  : a boolean, to decide if cumulative incremental backup needs to be done
            Return  (True,jobID), if the backup was submitted successfully
                    (False, func_name, error_msg), otherwise
        """
        log = loghelper.getLog()
        try:
            log.info("Backing up the subclient " + subclient)
            if self.Check_If_Entity_Exists("link", subclient):
                self.driver.find_element_by_xpath("//a[contains(text(),'" +subclient +"')]/../../div[3]/div/a/span[@class='grid-action-icon']").click()
                if self.Check_If_Entity_Exists("link", "Back up now"):
                    #self.driver.find_element_by_xpath("//div[1]/div[2]/div[2]/div/div[3]/div/div[3]/div/ul/li[1]/a[contains(text(),'Back up now')]").click()
                    self.driver.find_element_by_link_text('Back up now').click()
                    self.Wait_for_Completion()
                    #self.SubmitOracleBackup(bkpLevel, cumulative)
                    if bkpLevel == "FULL":
                        log.info('Full backup')
                        self.driver.find_element_by_xpath("//div[1]/div/div/div[2]/span[3]/div[2]/label[1]/input[@type='radio' and @value='" + bkpLevel + "']").click()
                    elif bkpLevel == "INCREMENTAL":
                        log.info('cumulative: '+ cumulative)
                        if cumulative == "True":
                            #self.driver.find_element_by_xpath("//input[@id='cumulative']").click()
                            self.Wait_for_Completion()
                            self.driver.find_element_by_xpath("//div[1]/div/div/div[2]/span[3]/div[2]/label[3]/label[@for ='cumulative']").click()
                            log.info('Cumulative also checked with Incremental')
                        else:
                            log.info('Only Incremental backup')
                    else:
                        e = "Please type the correct backup option"
                        log.error(e)
                        fn = sys._getframe().f_code.co_name
                        return False, fn, e
                    self.driver.find_element_by_xpath("/html/body/div[1]/div/div/div[2]/div/button[3]").click()
                    log.info('Backup Job submitted, Fetching job details...')
                    self.Wait_for_Completion()
                    JobText = self.driver.find_element_by_xpath("//div[@class='global-options remove-border-padding ng-binding']").text
                    log.info(JobText)
                    JobId = JobText.split("Job ")[-1].split(".")[0].strip()
                    JobID = int(JobId)
                    JID = str(JobID)
                    log.info("Backup job " + str(JobID) + " has started")
                    log.info("Checking status: ")
                    self.driver.find_element_by_xpath("//div[1]/div/div/div[2]/span[1]/div/a[contains(text(),' View job details')]").click()
                    self.Wait_for_Completion()
                    return True, str(JobID)
                else:
                    e = "there is no option to submit a backup"
                    log.error(e)
                    fn = sys._getframe().f_code.co_name
                    return False, fn, e
            else:
                e = "Could not find the subclient: " + subclient
                log.error(e)
                fn = sys._getframe().f_code.co_name
                return False, fn, e
        except Exception as e:
            log.exception(str(e))
            fn = sys._getframe().f_code.co_name
            return False, fn, str(e)

    def SubmitOracleBackup(self,bkpType, cumulative = False):
        """Submits a backup job """
        log = loghelper.getLog()
        try:
            log.info("Submitting Oracle backup")
            bkpType = bkpType.lower()
            if bkpType == "full":
                bkpType = "FULL"
            #elif bkpType == "incr":
            elif bkpType == "incremental":
                bkpType = "INCREMENTAL"
            else:
                e = "Please type the correct backup option"
                log.error(e)
                fn = sys._getframe().f_code.co_name
                return False, fn, e
            self.driver.find_element_by_xpath(
                "//input[@type='radio' and @value='" + bkpType + "']").click()
            if bkpType == "INCREMENTAL":
                if cumulative:
                    #if not self.driver.find_element_by_xpath("//input[@id='cumulative']").is_selected():
                    self.driver.find_element_by_xpath("//input[@id='cumulative']").click()
            self.driver.find_element_by_xpath("/html/body/div[1]/div/div/div[2]/div/button[3]").click()
            self.Wait_for_Completion()
            return True,1
        except Exception as e:
            log.exception(str(e))
            fn = sys._getframe().f_code.co_name
            return False,fn,str(e)

    def ActionOracleBackupHistory(self, subclient):
        """Opens the backup history of the subclient in an oracle instance
            subclient   : a string, the name of the subclient whose backup history is to be opened
            Returns (True,1), if successful
                    (False, func_name, error_msg), otherwise
        """
        log = loghelper.getLog()
        try:
            log.info(
                "Opening the backup history of the subclient " +
                subclient)
            if self.Check_If_Entity_Exists("link", subclient):
                self.driver.find_element_by_xpath(
                    "//a[contains(text(),'" +
                    subclient +
                    "')]/../../div[3]/div/a/span[@class='grid-action-icon']").click()
                self.Wait_for_Completion()
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

    def ActionOracleRestoreHistory(self, subclient):
        """Opens the restore history of the subclient in an oracle instance
            subclient   : a string, the name of the subclient whose restore history is to be opened
            Returns (True,1), if successful
                    (False, func_name, error_msg), otherwise
        """
        log = loghelper.getLog()
        try:
            log.info(
                "Opening the restore history of the subclient " +
                subclient)
            if self.Check_If_Entity_Exists("link", subclient):
                self.driver.find_element_by_xpath(
                    "//a[contains(text(),'" +
                    subclient +
                    "')]/../../dvi[3]/div/a/span[@class='grid-action-icon']").click()
                self.Wait_for_Completion
                if self.Check_If_Entity_Exists(
                        "xpath",
                        "//a[contains(text(),'" +
                        subclient +
                        "']/../../div[3]/div/ul/li[3]/a[contains(text(),'Backup History')]"):
                    self.driver.find_element_by_xpath(
                        "//a[contains(text(),'" +
                        subclient +
                        "']/../../div[3]/div/ul/li[3]/a[contains(text(),'Backup History')]").click()
                    self.Wait_for_Completion()
                else:
                    e = "There is no option to view the restore history of the subclient from the action menu"
                    log.error(e)
                    fn = sys._getframe().f_code.co_name
                    return False, fn, e
            else:
                e = "There is no subclient with the given name"
                log.error(e)
                fn = sys._getframe().f_code.co_name
                return False, fn, e
            return True, 1
        except Exception as e:
            log.exception(str(e))
            fn = sys._getframe().f_code.co_name
            return False, fn, str(e)

    def Delete(self):
        """ Deletes the instance and its subclients """
        log = loghelper.getLog()
        try:
            log.info("Deleting the instance")
            if self.Check_If_Entity_Exists("link","Delete"):
                self.driver.find_element_by_link_text("Delete").click()
                self.Wait_for_Completion()
                #self.driver.find_element_by_xpath("//input[@id='confirm']/following-sibling::label").click()
                #self.driver.find_element_by_xpath("//button[@class = 'btn btn-primary'").click()
                self.driver.find_element_by_xpath("//body/div[1]/div/div/div[2]/div[3]/input[@type = 'text']").send_keys('DELETE')

                #self.driver.find_element_by_xpath("/html/body/div[1]/div/div/div[2]/div[2]/label[@for ='confirm']").click()
                self.driver.find_element_by_xpath("//div[1]/div/div/div[3]/button[2]").click()
                self.Wait_for_Completion()
                return True,1
            else:
                e = "There is no option to delete the instance"
                log.error(e)
                fn = sys._getframe().f_code.co_name
                return False,fn,e
        except Exception as e:
            log.exception(str(e))
            fn = sys._getframe().f_code.co_name
            return False,fn,str(e)

    def DeleteSub(self, subclient):
        """ Deletes the Subclient from instance properties."""
        log = loghelper.getLog()
        try:
            log.info("Deleting the subclient")
            #self.driver.find_element_by_xpath("//a[text()='" +subclient).click()
            self.driver.find_element_by_link_text(subclient).click()
            self.Wait_for_Completion()
            if self.Check_If_Entity_Exists("link","Delete"):
                self.driver.find_element_by_link_text("Delete").click()
                self.Wait_for_Completion()
                self.driver.find_element_by_xpath("//div[1]/div/div/div[2]/div[3]/input[@type = 'text']").clear()
                self.driver.find_element_by_xpath("//div[1]/div/div/div[2]/div[3]/input[@type = 'text']").send_keys('DELETE')
                self.driver.find_element_by_xpath("//div[1]/div/div/div[3]/button[2][contains(text(), 'Save')]").click()
                self.Wait_for_Completion()
                return True,1
            else:
                e = "Could not delete this subclient"
                log.error(e)
                fn = sys._getframe().f_code.co_name
                return False,fn,e
        except Exception as e:
            log.exception(str(e))
            fn = sys._getframe().f_code.co_name
            return False,fn,str(e)
    def ManagingClones(self):
        """ Manages Clones."""
        log = loghelper.getLog()
        try:
            if self.Check_If_Entity_Exists("link","Manage clones"):
                self.driver.find_element_by_link_text("Manage clones").click()
                self.Wait_for_Completion()
                log.info("Go for Refresh")
                ret = self.Refresh()
                if ret:
                    log.info("Checking the list of Clones for an instance")
                    jids= self.driver.find_elements_by_class_name("ui-grid-canvas")
                    JobID = []
                    for i in jids:
                        t = i.find_element_by_xpath("./div/div/div/a").text
                        JobID.append(t)
                    if JobID == []:
                        return False
                    else:
                        for i in JobID:
                            log.info(str(i))
                        log.info("printed all the job Ids")
                        return True
                    log.info("Create clone if needed.....")
                    return True,1
                else:
                    return False
            else:
                e = "Could not find the option Manage clones"
                log.error(e)
                fn = sys._getframe().f_code.co_name
                return False,fn,e
        except Exception as e:
            log.exception(str(e))
            fn = sys._getframe().f_code.co_name
            return False,fn,str(e)

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
