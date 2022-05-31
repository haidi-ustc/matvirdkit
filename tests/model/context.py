import sys,os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from matvirdkit.model.bms import BMS
def setUpModule():
    os.chdir(os.path.abspath(os.path.dirname(__file__)))
