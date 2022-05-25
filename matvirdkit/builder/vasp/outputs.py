#!/usr/bin/env python
# coding: utf-8

"""
This Drone tries to generate the data OBJ. for BMS materials calculation.
"""
import os
import sys
import copy
import warnings
import numpy as np
from typing import List
from hashlib import sha1
from pprint import pprint
from warnings import filterwarnings
from monty.json import jsanitize
from monty.serialization import loadfn, dumpfn

from pymatgen.io.vasp.inputs import Poscar, Potcar, Incar, Kpoints
from pymatgen.io.vasp.outputs import Oszicar, Outcar, Vasprun, Elfcar, Procar, Chgcar
from pymatgen.io.vasp.inputs import UnknownPotcarWarning

from matvirdkit.model.common import JFData
from matvirdkit.model.utils import transfer_file

filterwarnings(action='ignore', category=UnknownPotcarWarning, module='pymatgen')

STORE_ADDITIONAL_JSON = True

__author__ = 'Haidi Wang'
__email__ = 'haidi@hfut.edu.cn'
__date__ = 'Dec 21, 2021'
__version__ = "0.1.0"

class VaspOutputs(object):
    def __init__(self, 
           work_path : str,
           foutputs: List[str]= [],
           sufix : str ='' ,
           relax : bool = True,
           allow_fail : bool =False,
           **kargs
        ):
 
        foutputs = foutputs if foutputs else ["CONTCAR", "OSZICAR", "OUTCAR", "vasprun.xml"] 
        print(foutputs)
        if 'VASPRUN' in foutputs:
            foutputs[foutputs.index('VASPRUN')]='vasprun.xml'
        print('---------')
        print(foutputs)
        self.rootpath = os.getcwd()
        self.foutputs = [ii+'.'+sufix for ii in foutputs ] if sufix else foutputs
        self.work_path = os.path.abspath(work_path)
        #self.parse_potcar_file= parse_potcar_file
        self.allow_fail = allow_fail
        #self.save_raw = save_raw
        self.relax = relax
        self.kargs = kargs

    def parse_output(self, dst_path, save_raw=True):
        doutput = {}
        for foutput in self.foutputs:
            cfname = None
            data = None
            fname = os.path.join(self.work_path, foutput)
            if "OUTCAR" in foutput:
                data = self.get_outcar(fname)
            elif "CONTCAR" in foutput:
                data = self.get_contcar(fname,relax=self.relax)
            elif "OSZICAR" in foutput:
                data = self.get_oszicar(fname)
                print('OSZICAR: ',data)
            elif "CHGCAR" in foutput:
                data = self.get_chgcar(fname)
            elif "ELFCAR" in foutput:
                data = self.get_elfcar(fname)
                #print('here',data)
            elif "PROCAR" in foutput:
                data = self.get_procar(fname)
            elif "vasprun.xml" in foutput:
                data = self.get_vasprun(fname, allow_fail=self.allow_fail,**self.kargs)
            else:
                data = {}
               # with open(fname, 'r') as f:
               #     warnings.warn('The output will be saved in str format')           
               #     data =  {"@module":  cls.__class__.__module__,
               #              "@class": cls.__class__.__name__,
               #              "@version" = __version__
               #              "data": f.read()}
            if save_raw and data:
               #print('===',foutput)
               cfname = transfer_file(foutput, self.work_path, dst_path)
               #print(cfname)
            else:
               cfname = ''
            print(foutput, ' : raw-->', cfname)

            if data:
               json_file_name=sha1(str(data).encode('utf-8')).hexdigest()
               json_file_name=os.path.join(dst_path,json_file_name+'-'+foutput+'.json')
               dumpfn(data,json_file_name,indent=4)
            else:
               json_file_name = ''
            print(foutput, ' : jsanitize-->', json_file_name)
            jfd=JFData(file_fmt='.gz',file_id=None, file_name=cfname,
                   json_id=None, json_file_name=os.path.basename(json_file_name),json_data={})
            pprint(jfd.dict())
            doutput[foutput]=jfd
        _doutput=copy.deepcopy(doutput)      
        if 'vasprun.xml' in _doutput.keys():
           _doutput.pop('vasprun.xml')
           _doutput['VASPRUN']= doutput['vasprun.xml']
        return _doutput

    @classmethod
    def get_contcar(cls,fname='CONTCAR',relax=True):
        if relax:
           pass
        else:
           warnings.warn('The output configuration will be parsed from POSCAR')           
           fname=fname.replace('CONTCAR','POSCAR')
        if os.path.exists(fname):
            try:
                contcar = Poscar.from_file(fname)
                return contcar.as_dict()
            except:
                return {}
        else:
            return {}

    @classmethod
    def get_outcar(cls,  fname='OUTCAR'):
        #print("OUTCAR %s" % fname)
        if os.path.exists(fname):
            try:
                out = Outcar(fname)
                return out.as_dict()
            except:
                return {}
        else:
            return {}
    @classmethod
    def get_procar(cls,  fname='PROCAR'):

        if os.path.exists(fname):
            try:
                pro = Procar(fname)
            except:
                return {}
        else:
            return {}
        d = {"@module": cls.__class__.__module__, "@class": cls.__class__.__name__}
        d["@version"] = __version__
        d['nkpoints']=pro.knpoints
        d['nbands']=nbands
        d['nions']=nions
        d['weights']=weights
        d['orbitals']=orbitals
        d['data']=data
        return d

    @classmethod
    def get_chgcar(cls,  fname='CHGCAR'):

        if os.path.exists(fname):
            try:
                chg = Chgcar.from_file(fname)
                return chg.as_dict()
            except:
                return {}
        else:
            return {}

    @classmethod
    def get_elfcar(cls,  fname='ELFCAR'):
        if os.path.exists(fname):
            try:
                elf = Elfcar.from_file(fname)
                return elf.as_dict()
            except:
                return {}
        else:
            return {}

    @classmethod
    def get_oszicar(cls,  fname='OSZICAR'):

        #print("OSZI %s" % fname)
        if os.path.exists(fname):
            try:
                osz = Oszicar(fname)
                return osz.as_dict()
            except:
                return {}
        else:
            return {}

    @classmethod
    def get_vasprun(cls, fname='vasprun.xml', allow_fail=False, parse_potcar_file=True):
        if os.path.exists(fname):
            try:
                vr = Vasprun(fname, parse_potcar_file=parse_potcar_file)
                if allow_fail:
                    return vr.as_dict()
                else:
                    if vr.converged:
                        return vr.as_dict()
                    else:
                        return {}
            except:
                return {}
        else:
            return {}

    def as_dict(self):
        init_args = {
            "work_path": self.work_path
        }
        return {"@module": self.__class__.__module__,
                "@class": self.__class__.__name__,
                "version": self.__class__.__version__,
                "init_args": init_args
                }

    @classmethod
    def from_dict(cls, d):
        return cls(**d["init_args"])

if __name__ == '__main__':
   foutputs=["CONTCAR", "OSZICAR", "OUTCAR", "vasprun.xml",'ELFCAR']
   #foutputs=['ELFCAR']
   outputs=VaspOutputs(work_path='/home/wang/dev/matvirdkit/matvirdkit/model/scf',foutputs=foutputs,parse_potcar_file=True)
   d=outputs.parse_output(dst_path = './dataset/2', save_raw = True)
   #print(d)
   dumpfn(d,'out.json',indent=4)
   
   #outputs.parse_output(dst_path = './dataset/3', save_raw = True)


