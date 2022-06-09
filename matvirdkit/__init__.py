#!/usr/bin/env python
# coding: utf-8
import os
import logging
from decouple import AutoConfig
from logging.handlers import RotatingFileHandler
try:
   from ._version import version as __version__
except ImportError:
   from .__about__ import __version__

try:
    from ._date import date as __date__
except ImportError:
    __date__ = 'unkown'

NAME="matvirdkit"
SHORT_CMD="mvdkit"
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
#tm = time.strftime('%Y%m%d%H%M', time.localtime(time.time()))
logfile = os.getcwd()+os.sep+'mvdkit.log'
fsc = logging.FileHandler(logfile, mode='w') 
#fsc = RotatingFileHandler(logfile, maxBytes=1, backupCount=2)  
fsc.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG) 

formatter = logging.Formatter('%(asctime)s - %(levelname)s : %(message)s')
#formatter=logging.Formatter('%(asctime)s - %(name)s - [%(filename)s:%(funcName)s - %(lineno)d ] - %(levelname)s \n %(message)s')
fsc.setFormatter(formatter)
ch.setFormatter(formatter)

log.addHandler(fsc)
log.addHandler(ch)


HOME_DIR   = os.path.expanduser('~')
BASE_DIR   = os.path.realpath(__file__) 
CONFIG_DIR = os.path.join(HOME_DIR)
config     = AutoConfig(CONFIG_DIR)
 
DEBUG      = config('DEBUG', default=False, cast=bool)
REPO_DIR   = config('REPOSITORY',default=os.path.join(HOME_DIR,'.repository'),cast=str) 
DATASETS_DIR = os.path.join(REPO_DIR,'datasets')
META_DIR = os.path.join(REPO_DIR,'meta')
TASKS_DIR = os.path.join(REPO_DIR,'tasks')
for _dir in [REPO_DIR,DATASETS_DIR,META_DIR,TASKS_DIR]:
    if os.path.isdir(_dir):
       pass
    else:
       os.mkdir(_dir)

API_KEY    = config('API_KEY',default='',cast=str)
MONGODB_URI= config('MONGO_DATABASE_URI',default='',cast=str)  

log.info('Mode: %s'%DEBUG)
log.info('Repository directory: %s'%REPO_DIR)
log.info('API key: %s'%API_KEY)
log.info('MongoDB :%s'%MONGODB_URI)
 
EMAIL_HOST = config('EMAIL_HOST', default='localhost')
EMAIL_PORT = config('EMAIL_PORT', default=25, cast=int)
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=False, cast=bool)
 
