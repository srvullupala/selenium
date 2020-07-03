#!/usr/bin/env python

"""
This module provides the function or operations that can be performed on the
subclient of the Oracle iDA on the AdminConsole
Class:
    OracleSubclient() -> Subclient() -> BackupsetLevel() -> iDA() -> ClientDetails() --
        -> Clients() -> Server() -> AdminPage() -> LoginPage() -> AdminConsoleBase() -> object()
Functions:
OracleSubclient()               -- Runs backup for the subclient
ContinuousBuild()               -- Run Continuous Build of the page to traverse all the links on this page.
NextPage()                      -- Returns a dictionary containing the pages that can be visited from this page.
"""

from Helper.Imports import *
from ContinuousBuild.ParamsDict import *
from OraclePages.CVPages import *
from AutomationUtils import loghelper

class OracleSubclient(Subclient, OracleInstance):

    def OracleBackup(self, bkpLevel):
        """Runs backup for the subclient
            bkpLevel    : a string, the backup to be performed on the subclient
            Returns (True,1), if successful
                    (False,fnc_name,err_msg), otherwise
        """
        log = loghelper.getLog()
        try:
            log.info("Submitting the backup job for the subclient")
            if self.Check_If_Entity_Exists("link", "Back up now"):
                self.driver.find_element_by_xpath(
                    "//a[contains(text(),'" +
                    subclient +
                    "')]/../../div[3]/div/ul/li[1]/a[contains(text(),'Back up now')]").click()
                self.Wait_for_Completion()

                self.SubmitOracleBackup(bkpLevel, cumulative)
                retcode = self.JobId()
                if not retcode[0]:
                    return retcode[0], retcode[1], retcode[2]
                else:
                    JID = retcode[1]
                    return True, retcode[1]
            else:
                e = "there is no option to submit a backup"
                log.error(e)
                fn = sys._getframe().f_code.co_name
                return False, fn, e
        except Exception as e:
            log.exception(str(e))
            fn = sys._getframe().f_code.co_name
            return False, fn, str(e)

    def ContinuousBuild(self):
        """Run Continuous Build of the page to traverse all the links on this page."""
        print "Inside continuous build of Subclient page"
        ParsedPage.append(self.__class__.__name__)
        self.ExceptionHandling(self.__class__.__name__,
                               *(self.BackupEnabled()))
        self.ExceptionHandling(self.__class__.__name__,
                               *(self.BackupEnabled()))
        self.ExceptionHandling(self.__class__.__name__,
                               *(self.EditStorage(UserConstants['newLibrary'])))
        self.ExceptionHandling(self.__class__.__name__,
                               *(self.EditStorage(UserConstants['oldLibrary'])))
        # self.ExceptionHandling(self.__class__.__name__,*(self.AddSchedule("schedule1","Incremental","weekly",['Monday','Friday'],12,21,"AM")))
        # self.ExceptionHandling(self.__class__.__name__,*(self.DeleteSchedule("schedule1")))
        self.ExceptionHandling(self.__class__.__name__, *(self.BackupJobs()))
        self.driver.back()
        self.Wait_for_Completion()
        self.ExceptionHandling(self.__class__.__name__, *(self.ContentInfo()))
        self.ExceptionHandling(self.__class__.__name__, *(self.Restore()))
        self.driver.back()
        self.Wait_for_Completion()

    def NextPage(self):
        """Returns a dictionary containing the pages that can be visited from this page."""
        return {
            'Restore_SelectVolume': 'Restore'
        }
