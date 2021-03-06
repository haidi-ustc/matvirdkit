""" Module to define various calculation types as Enums for VASP """
import datetime
from itertools import groupby, product
from pathlib import Path
from typing import Dict, Iterator, List

import bson
import numpy as np
from monty.json import MSONable
from monty.serialization import loadfn
from pydantic import BaseModel
from pymatgen.analysis.structure_matcher import ElementComparator, StructureMatcher
from pymatgen.core.structure import Structure
from typing_extensions import Literal

from matvirdkit.model.vasp.calc_types.enums import CalcType, RunType, TaskType

_RUN_TYPE_DATA = loadfn(str(Path(__file__).parent.joinpath("run_types.yaml").resolve()))


def run_type(parameters: Dict) -> RunType:
    """
    Determines the run_type from the VASP parameters dict
    This is adapted from pymatgen to be far less unstable

    Args:
        parameters: Dictionary of VASP parameters from Vasprun.xml
    """

    if parameters.get("LDAU", False):
        is_hubbard = "+U"
    else:
        is_hubbard = ""

    def _variant_equal(v1, v2) -> bool:
        """
        helper function to deal with strings
        """
        if isinstance(v1, str) and isinstance(v2, str):
            return v1.strip().upper() == v2.strip().upper()
        else:
            return v1 == v2

    # This is to force an order of evaluation
    for functional_class in ["HF", "VDW", "METAGGA", "GGA"]:
        for special_type, params in _RUN_TYPE_DATA[functional_class].items():
            if all(
                [
                    _variant_equal(parameters.get(param, None), value)
                    for param, value in params.items()
                ]
            ):
                return RunType(f"{special_type}{is_hubbard}")

    return RunType(f"LDA{is_hubbard}")


def task_type(
    inputs: Dict[Literal["incar", "poscar", "kpoints", "potcar"], Dict]
) -> TaskType:
    """
    Determines the task type

    Args:
        inputs: inputs dict with an incar, kpoints, potcar, and poscar dictionaries
    """

    calc_type = []

    incar = inputs.get("incar", {})

    if incar.get("ICHARG", 0) > 10:
        try:
            kpts = inputs.get("kpoints") or {}
            kpt_labels = kpts.get("labels") or []
            num_kpt_labels = len(list(filter(None.__ne__, kpt_labels)))
        except Exception as e:
            raise Exception(
                "Couldn't identify total number of kpt labels: {}".format(e)
            )

        if num_kpt_labels > 0:
            calc_type.append("NSCF Line")
        else:
            calc_type.append("NSCF Uniform")

    elif incar.get("LEPSILON", False):
        if incar.get("IBRION", 0) > 6:
            calc_type.append("DFPT")
        calc_type.append("Dielectric")

    elif incar.get("IBRION", 0) > 6:
        calc_type.append("DFPT")

    elif incar.get("LCHIMAG", False):
        calc_type.append("NMR Nuclear Shielding")

    elif incar.get("LEFG", False):
        calc_type.append("NMR Electric Field Gradient")

    elif incar.get("NSW", 1) == 0:
        calc_type.append("Static")

    elif incar.get("ISIF", 2) == 3 and incar.get("IBRION", 0) > 0:
        calc_type.append("Structure Optimization")

    elif incar.get("ISIF", 3) == 2 and incar.get("IBRION", 0) > 0:
        calc_type.append("Deformation")

    if len(calc_type) == 0:
        return TaskType("Unrecognized")

    return TaskType(" ".join(calc_type))


def calc_type(
    inputs: Dict[Literal["incar", "poscar", "kpoints", "potcar"], Dict],
    parameters: Dict,
) -> CalcType:
    """
    Determines the calc type

    Args:
        inputs: inputs dict with an incar, kpoints, potcar, and poscar dictionaries
        parameters: Dictionary of VASP parameters from Vasprun.xml
    """
    rt = run_type(parameters).value
    tt = task_type(inputs).value
    return CalcType(f"{rt} {tt}")

if __name__== '__main__':
   import os
   from pymatgen.io.vasp import Incar
   from pymatgen.io.vasp import Vasprun,VaspInput
   from matvirdkit.model.utils import test_path,create_path
   from monty.serialization import loadfn,dumpfn
   #relax_dir=os.path.join(test_path('..'),'relax')
   #print(relax_dir)
   #os._exit(0)
   vr=Vasprun('../../../../tests/relax/vasprun.xml',  parse_potcar_file= True)
   rt=run_type(vr.parameters)
   vi=VaspInput.from_directory('../../../../tests/relax/')
   vid=vi.as_dict()
   d={}
   for _input in [ "poscar", "kpoints", "potcar"]:
       d[_input]=vid[_input.upper()]
   d["incar"]=vr.parameters
   tt=task_type(d)
   ct=calc_type(d,vr.parameters)
   print("run  type: %s"%rt)
   print("task type: %s"%tt)
   print("calc type: %s"%ct)
