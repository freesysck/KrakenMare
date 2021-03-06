"""
(C) Copyright 2020 Hewlett Packard Enterprise Development LP.

Licensed under the Apache License, Version 2.0 (the "License"); you may
not use this file except in compliance with the License. You may obtain
a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
License for the specific language governing permissions and limitations
under the License.
"""

'''
Created on Aug 11, 2019

@author: torsten
'''


# system imports
import os
import gzip
import unittest
import logging 
from colorlog import ColoredFormatter
from logging.handlers import RotatingFileHandler

# project imports


class NoLogger(Exception):
    # Exception for tracking the log file via name fetching failures 
    pass

class RotatingFileHandlerWithCompression(RotatingFileHandler):
    """
        Class enabling log file rotation with gzip compression.
    """    

    def __init__(self, *args, **kws):
    
        try:
            self.compress_cls = gzip
        except KeyError:
            raise ValueError('gzip compression method is not supported.')
        
        RotatingFileHandler.__init__(self, *args, **kws)
    
    def doRollover(self):
        RotatingFileHandler.doRollover(self)
    
        # Compress the old log file
        if self.backupCount > 0:
            for i in range(self.backupCount - 1, 0, -1):
                sfn = "%s.%d.%s" % (self.baseFilename, i, 'gz')
                dfn = "%s.%d.%s" % (self.baseFilename, i + 1, 'gz')
                if os.path.exists(sfn):
                    if os.path.exists(dfn):
                        os.remove(dfn)
                    os.rename(sfn, dfn)
        
            old_log = self.baseFilename + ".1"
            with open(old_log) as log:
                with self.compress_cls.open(old_log + '.gz', 'wb') as comp_log:
                    comp_log.writelines(log)
        
            os.remove(old_log)



class KrakenMareLogger:
    
    """
        This class defines KrakenMare logger options. Should be initialized only once.
    
        Multiple log files are allowed.
    """
    
    global loggers
    loggers = {} 

    
    def setLogger(self, name, loggingLevel, loggingDirectory, logFileSize, logFileArchiveCount):
        """
            creates a new logger object
            with given parameters
        """
        logger=logging.getLogger(name)
        
        hdlr = RotatingFileHandlerWithCompression(loggingDirectory+name, maxBytes=logFileSize, backupCount=logFileArchiveCount)
        
        #formatter = logging.Formatter("%(asctime)s [%(threadName)s] %(levelname)s %(message)s", "%Y-%m-%d %H:%M:%S")
        formatter = ColoredFormatter(
                                     "%(log_color)s%(asctime)s [%(threadName)s] %(levelname)s %(message)s", "%Y-%m-%d %H:%M:%S",
                                    log_colors={
                                                'DEBUG':    'cyan',
                                                'INFO':     'white',
                                                'WARNING':  'yellow',
                                                'ERROR':    'red',
                                                'CRITICAL': 'red,bg_white',
                                                },
                                     )
        hdlr.setFormatter(formatter)
        logger.addHandler(hdlr)
        logger = self.setLoggingLevel(logger, loggingLevel)
        loggers[name] = logger
        logger.propagate = False
        return logger
    
    def getLogger(self, name, loggingLevel=None): 
        """
            returns a logger object and optionally modifies its log level
        """
        if loggers.get(name): 
            # reuses the logger
            if(loggingLevel == None):
                # use previously defined logging level
                return loggers.get(name)
            else:
                # reset the logging level
                modifiedLogger = loggers.get(name)
                modifiedLogger = self.setLoggingLevel(modifiedLogger, loggingLevel)
                loggers[name] = modifiedLogger
                return modifiedLogger
        else:
            raise NoLogger()
               
    def setLoggingLevel(self, logger, level):
        '''
            Sets the level of the logger file according to the specification.
            
            WARNING level by default.
        '''
        
        if(level.upper() == 'DEBUG'):
            logger.setLevel(logging.DEBUG)
            return logger
        elif(level.upper() == 'INFO'):
            logger.setLevel(logging.INFO)
            return logger
        elif(level.upper() == 'WARNING'):
            logger.setLevel(logging.WARNING)
            return logger
        elif(level.upper() == 'ERROR'):
            logger.setLevel(logging.ERROR)
            return logger
        elif(level.upper() == 'CRITICAL'):
            logger.setLevel(logging.CRITICAL)
            return logger
        else:
            # default
            print("WARNING: Unknown logging level. Taking WARNING as default logging level.")
            logger.setLevel(logging.WARNING)
            return logger


class KrakenMareLoggerTest(unittest.TestCase):
    
    def testLoggerCreation(self):
        '''
            test the rotation routine (i.e. 'zipping') 
            for logger files
        '''
        
        loggerName = "KrakenMareTestLogger.log"
        logDirectory = ""
        logLevel = "Info"
        logSize = 1024
        logArchCount = 5
        
        testlogger = KrakenMareLogger().setLogger(loggerName, logLevel, 
                                            logDirectory, logSize, logArchCount)
        
        self.assertNotEqual(None, testlogger, "Failed to create a log file")
        
        testlogger.info("TestData: {0}".format("info data"))
        
        self.cleanTmpData()
    
    def testLoggFilePopulation(self):
        
        loggerName = "KrakenMareTestLogger.log"
        logDirectory = ""
        logLevel = "Info"
        logSize = 1024
        logArchCount = 5
        
        logger = KrakenMareLogger().setLogger(loggerName, logLevel, 
                                            logDirectory, logSize, logArchCount)
        
        i = 0
        print("Populating test data ...")
        while(i < 1):
            logger.info("TestData1: {0}".format(i))
            i += 1
        print("Test data populated - zip files should be visible now")
        
        loggerNew = KrakenMareLogger().getLogger("KrakenMareTestLogger.log")
        
        i = 0
        print("Populating test data from new logger ...")
        while(i < 1):
            loggerNew.info("TestData2 From New Logger: {0}".format(i))
            i += 1
        print("Test data from new logger populated - zip files should be visible now")
        
        i = 0
        print("Populating test data from new logger ...")
        while(i < 5):
            loggerNew.info("TestData3 From New Logger: {0}".format(i))
            i += 1
        print("Test data from new logger populated - zip files should be visible now")
 
        self.cleanTmpData()
         
    def testLoggerColoring(self):
        
        loggerName = "KrakenMareTestLoggerColor.log"
        logDirectory = ""
        logLevel = "DEBUG"
        logSize = 1024
        logArchCount = 5
        
        testlogger = KrakenMareLogger().setLogger(loggerName, logLevel, 
                                            logDirectory, logSize, logArchCount)
        
        self.assertNotEqual(None, testlogger, "Failed to create a log file")
        
        testlogger.debug("TestData: {0}".format("debug data"))
        testlogger.info("TestData: {0}".format("info data"))
        testlogger.warning("TestData: {0}".format("warning data"))
        testlogger.error("TestData: {0}".format("error data"))
        testlogger.critical("TestData: {0}".format("critical error data"))
        testlogger.info("TestData: {0}".format("info data"))
        testlogger.warning("TestData: {0}".format("warning data"))
        
        self.cleanTmpData()
    
    def cleanTmpData(self):
        '''
            removes temporary created logger and associated zip files
        '''
        import glob
        
        for filename in glob.glob("KrakenMareTestLogger*"):
            
            print("removing {0} file ...".format(filename))
            
            try:
                os.remove(filename)
            except Exception as e:
                print("Could not remove {0} file. Reason: {1}".format(filename, e))
                 
            print("{0} file removed".format(filename))
   
def mainTest():
    '''
        Main routine for unit tests
    '''
    
    unittest.main()
    

if __name__ == '__main__':
    
    mainTest()
    
    
