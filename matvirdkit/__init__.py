#!/usr/bin/env python
# coding: utf-8
import os
import logging
from logging.handlers import RotatingFileHandler
try:
   from ._version import version as __version__
except ImportError:
   from .__about__ import __version__

try:
    from ._date import date as __date__
except ImportError:
    __date__ = 'unkown'

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
#tm = time.strftime('%Y%m%d%H%M', time.localtime(time.time()))
logfile = os.getcwd()+os.sep+'mvdkit.log'
fsc = logging.FileHandler(logfile, mode='w') 
#fsc = RotatingFileHandler(logfile, maxBytes=1, backupCount=2)  
fsc.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.INFO) 

formatter = logging.Formatter('%(asctime)s - %(levelname)s : %(message)s')
#formatter=logging.Formatter('%(asctime)s - %(name)s - [%(filename)s:%(funcName)s - %(lineno)d ] - %(levelname)s \n %(message)s')
fsc.setFormatter(formatter)
ch.setFormatter(formatter)

log.addHandler(fsc)
log.addHandler(ch)

