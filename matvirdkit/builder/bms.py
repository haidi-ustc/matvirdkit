#!/usr/bin/env python
# coding: utf-8

"""
This Drone tries to generate the data OBJ. for BMS materials calculation.
"""
import os,sys
import re
from hashlib import sha1
from monty.json import jsanitize
import numpy as np
from monty.serialization import loadfn, dumpfn
from base import Drone,LabeledData

__author__ = 'Haidi Wang'
__email__ = 'haidi@hfut.edu.cn'
__date__ = 'Dec 21, 2021'
__version__ = "0.1.0"


class BMSDrone(Drone):
    """
    Derivate class for parsing and preparing dataset of BMS materials
    """

    def __init__(self,
                 matid : str,
                 dataset : str = 'bms.dataset',
                 sysdim :  int = 3 ,
                 bms_feature = {} )  :      

        """
        Initialize a Vasp drone to parse vasp outputs
        Args:
            matid (str): unique ID for material
            dataset (str): the path to hold the output dataset 
            sysdim (int): the dimension of system, should be 0,1,2,3
            bms_feature  (dict): the feature parameter for BMS materials
        """
        super().__init__( matid, dataset, sysdim)
        self._bms_feature = bms_feature

    @LabeledData("BMS features")
    def get_bms_feature(self):
        return self._bms_feature


def main():
    tasks=loadfn('./examples/bms/tasks-1.json')
    #format of tasklist.json 
    """
    "mp-771246": [
        {
            "label": "UNITCELL-AFM-SCF-0",
            "description": "This is a static calculation with AFM order with PBE+U",
            "path": "/home/wang/work/FM/AFM/mp-771246/afm-0"
        }
    ]
    """
    data=loadfn('./examples/bms/bms.json')
    """
    {
    "mp-771246": {
        "mp_id": "mp-771246",
        "mp_url": "https://materialsproject.org/materials/mp-771246",
        "source_id": "mp-771246",
        "source_db": null,
        "source_url": null,
        "decomposition_energy": 0.045,
        "magnetic_moment": 6.0,
        "magnetic_order": "FM",
        "formation_energy": -2.27,
        "number_magnetic_atom": 3,
        "exchange_energy": 180.0,
        "delta1": 0.855,
        "delta2": 1.259,
        "delta3": 0.254
    }
    }
    """
    path="./examples/bms/vasp"
    dos_path=os.path.join(path,'dos')
    for _id in tasks.keys():
        print(_id)
        _data=data[_id]
        bms_feature={"delta_1": _data['delta1'],
                     "delta_2": _data['delta2'],
                     "delta_3": _data['delta3']}
        bmsdrone=BMSDrone(matid=_id,sysdim=3,
                          bms_feature = bms_feature)
        
        keys=[ii['label'] for ii in tasks[_id]] 
        struct_path=tasks[_id][keys.index('UNITCELL-GROUNDSTATE-HSE-SCF')]['path']
        Eabh= _data[ "decomposition_energy"]
        Ef= _data[ "formation_energy"]
        band_gaps= {"PBE+U": _data['delta3']}
        source = [
             {'Source_DB': 'Materials Project',
              'Source_ID': _data['mp_id'],
              'Source_url':_data['mp_url']
              }
            ]
        meta={"user": "haidi", "machine": "cluster@HFUT"}
        bmsdrone.set_prop(struct_path=struct_path,
                          Eabh=Eabh,
                          Ef=Ef,
                          magnetic_moment = _data["magnetic_moment"], 
                          magnetic_order  = _data["magnetic_order"], 
                          exchange_energy = _data["exchange_energy"],
                          band_gaps = band_gaps,
                          source = source,
                          meta = meta
                           )
        dbms=bmsdrone.get_bms_feature()
        bmsdrone.set_dos(path = dos_path,
                       label  = 'HSE06',
                       code   = 'vasp',
                       auto   = False)
        bmsdrone.update_props('DOS')
        bmsdrone.update_props({'BMS':dbms})
        #dprop=bmsdrone.get_props()
        #dumpfn(dprop,'dprop.json',indent=4)

        for task in tasks[_id]:
            path=task['path']
            describ=task['describ']
            label=task['label']
            bmsdrone.set_task(path,label,describ=describ,code='vasp')
        #dtask=bmsdrone.get_tasks()
        #dumpfn(dtask,'dtask.json',indent=4)
        doc=bmsdrone.get_doc()
        dumpfn(doc,os.path.join(bmsdrone.workpath,bmsdrone.matid+'.json'),indent=4)

if __name__ == '__main__':
   main()
