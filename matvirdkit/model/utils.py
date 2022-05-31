import datetime
from enum import Enum
from itertools import groupby, product
from pathlib import Path
from typing import Dict, Iterator, List, Tuple

import os
from monty.shutil import compress_file
import shutil
from shutil import SameFileError
from hashlib import sha1
import bson
import numpy as np
from monty.json import MSONable
from monty.serialization import loadfn,dumpfn
from pydantic import BaseModel
from pymatgen.analysis.structure_matcher import ElementComparator, StructureMatcher
from pymatgen.core.structure import Structure
from typing_extensions import Literal

from matvirdkit.model.settings import SYMPREC,LTOL,STOL,ANGLE_TOL

Len = 40
Vector3D = Tuple[float, float, float]
Vector3D.__doc__ = "Real space vector"  # type: ignore

Matrix3D = Tuple[Vector3D, Vector3D, Vector3D]
Matrix3D.__doc__ = "Real space Matrix"  # type: ignore

VoigtVector = Tuple[float, float, float, float, float, float]
Tensor = Tuple[VoigtVector, VoigtVector, VoigtVector]
Tensor.__doc__ = "Rank 3 real space tensor in Voigt notation"  # type: ignore
ElasticTensor = Tuple[VoigtVector, VoigtVector, VoigtVector,VoigtVector, VoigtVector, VoigtVector]
ElasticTensor.__doc__ = "Rank 6 real space tensor in Voigt notation"  # type: ignore

def task_tag(task_dir,status='write',info={}):
    if status=='write':
       dumpfn(info,os.path.join(task_dir,'tag.json')),
    elif status=='check':
       if os.path.isfile(os.path.join(task_dir,'tag.json')):
          return True
       else:
          return False
    elif status=='remove':
       if os.path.isfile(os.path.join(task_dir,'tag.json')):
          os.remove(os.path.join(task_dir,'tag.json'))
          return None
       else:
          return None  
    else:
       return None  
    
def sha1encode(data):
    return  sha1(str(data).encode('utf-8')).hexdigest()

def get_sg(struc, symprec=SYMPREC) -> int:
    """helper function to get spacegroup with a loose tolerance"""
    try:
        return struc.get_space_group_info(symprec=symprec)[1]
    except Exception:
        return -1

def group_structures(
    structures: List[Structure],
    ltol: float = LTOL,
    stol: float = STOL,
    angle_tol: float = ANGLE_TOL,
    symprec: float = SYMPREC,
) -> Iterator[List[Structure]]:
    """
    Groups structures according to space group and structure matching

    Args:
        structures ([Structure]): list of structures to group
        ltol (float): StructureMatcher tuning parameter for matching tasks to materials
        stol (float): StructureMatcher tuning parameter for matching tasks to materials
        angle_tol (float): StructureMatcher tuning parameter for matching tasks to materials
        symprec (float): symmetry tolerance for space group finding
    """

    sm = StructureMatcher(
        ltol=ltol,
        stol=stol,
        angle_tol=angle_tol,
        primitive_cell=True,
        scale=True,
        attempt_supercell=False,
        allow_subset=False,
        comparator=ElementComparator(),
    )

    def _get_sg(struc):
        return get_sg(struc, symprec=symprec)

    # First group by spacegroup number then by structure matching
    for _, pregroup in groupby(sorted(structures, key=_get_sg), key=_get_sg):
        for group in sm.group_structures(list(pregroup)):
            yield group


def jsanitize(obj, strict=False, allow_bson=False):
    """
    This method cleans an input json-like object, either a list or a dict or
    some sequence, nested or otherwise, by converting all non-string
    dictionary keys (such as int and float) to strings, and also recursively
    encodes all objects using Monty's as_dict() protocol.
    Args:
        obj: input json-like object.
        strict (bool): This parameters sets the behavior when jsanitize
            encounters an object it does not understand. If strict is True,
            jsanitize will try to get the as_dict() attribute of the object. If
            no such attribute is found, an attribute error will be thrown. If
            strict is False, jsanitize will simply call str(object) to convert
            the object to a string representation.
        allow_bson (bool): This parameters sets the behavior when jsanitize
            encounters an bson supported type such as objectid and datetime. If
            True, such bson types will be ignored, allowing for proper
            insertion into MongoDb databases.
    Returns:
        Sanitized dict that can be json serialized.
    """
    if allow_bson and (
        isinstance(obj, (datetime.datetime, bytes))
        or (bson is not None and isinstance(obj, bson.objectid.ObjectId))
    ):
        return obj
    if isinstance(obj, (list, tuple, set)):
        return [jsanitize(i, strict=strict, allow_bson=allow_bson) for i in obj]
    if np is not None and isinstance(obj, np.ndarray):
        return [
            jsanitize(i, strict=strict, allow_bson=allow_bson) for i in obj.tolist()
        ]
    if isinstance(obj, Enum):
        return obj.value
    if isinstance(obj, dict):
        return {
            k.__str__(): jsanitize(v, strict=strict, allow_bson=allow_bson)
            for k, v in obj.items()
        }
    if isinstance(obj, MSONable):
        return {
            k.__str__(): jsanitize(v, strict=strict, allow_bson=allow_bson)
            for k, v in obj.as_dict().items()
        }

    if isinstance(obj, BaseModel):
        return {
            k.__str__(): jsanitize(v, strict=strict, allow_bson=allow_bson)
            for k, v in obj.dict().items()
        }
    if isinstance(obj, (int, float)):
        if np.isnan(obj):
            return 0
        return obj

    if obj is None:
        return None

    if not strict:
        return obj.__str__()

    if isinstance(obj, str):
        return obj.__str__()

    return jsanitize(obj.as_dict(), strict=strict, allow_bson=allow_bson)


class ValueEnum(Enum):
    """
    Enum that serializes to string as the value
    """

    def __str__(self):
        return str(self.value)
    def __repr__(self):
        return str(self.value)


class DocEnum(ValueEnum):
    """
    Enum with docstrings support
    from: https://stackoverflow.com/a/50473952
    """

    def __new__(cls, value, doc=None):
        """add docstring to the member of Enum if exists

        Args:
            value: Enum member value
            doc: Enum member docstring, None if not exists
        """
        self = object.__new__(cls)  # calling super().__new__(value) here would fail
        self._value_ = value
        if doc is not None:
            self.__doc__ = doc
        return self

class YesOrNo(Enum):
      yes: str = 'YES'  
      no: str = 'NO'  

def create_path(path, backup=False):
    #print(path)
    if path[-1] != "/":
        path += '/'
    if os.path.isdir(path):
        if backup:
            dirname = os.path.dirname(path)
            counter = 0
            while True:
                bk_dirname = dirname + ".bk%06d" % counter
                if not os.path.isdir(bk_dirname):
                    shutil.move(dirname, bk_dirname)
                    break
                counter += 1
            os.makedirs(path)
            return path
        else:
            return path
    os.makedirs(path)
    return path

def transfer_file(fname, src_path, dst_path, rename = True, path_type = 'base', compress = True, compression='gz'):
    assert path_type in ['relative', 'base', 'abs'] 
    # relative    ./dataset.bms/bms-1/01a77054-63e1-428a-b016-9619620792d4.json
    # base   01a77054-63e1-428a-b016-9619620792d4.json
    # abs   /home/wang/dev/dataset.bms/bms-1/01a77054-63e1-428a-b016-9619620792d4.json  
    abs_path=False
    dst_fname = os.path.join(dst_path,fname)
    fname=os.path.join(src_path,fname)
    if rename:
       if os.path.isfile(fname):
           with open(fname,'rb') as fid:
                data=fid.read()
           encode_fname = sha1(str(data).encode('utf-8')).hexdigest()
           dst_fname = os.path.join(dst_path, encode_fname + '-' + os.path.basename(fname))
           try:
              shutil.copyfile(src=fname, dst=dst_fname)
           except SameFileError:
              pass
           if compress:
              compress_file(dst_fname, compression=compression)
              dst_fname = dst_fname.replace(dst_path,'')

              if path_type == 'base':
                  return dst_fname[1:] + '.' + compression
              elif path_type == 'relative':
                  return os.path.join(dst_path,dst_fname[1:] + '.' + compression)
              else:
                  return os.path.abspath(os.path.join(dst_path,dst_fname[1:] + '.' + compression))
           else:
              if path_type == 'base':
                  return dst_fname[1:] 
              elif path_type == 'relative':
                  return os.path.join(dst_path,dst_fname[1:] )
              else:
                  return os.path.abspath(os.path.join(dst_path,dst_fname[1:] ))
              
       else:
           raise RuntimeError('%s is not a file'%(fname))
    else:
       try:
          shutil.copyfile(src=fname, dst=dst_fname)
       except SameFileError:
          pass

def sepline(ch='-',sp='-'):
    r'''
    seperate the output by '-'
    '''
    print(ch.center(Len,sp))

def box_center(ch='',fill=' ',sp="|"):
    r'''
    put the string at the center of |  |
    '''
    strs=ch.center(Len,fill)
    print(sp+strs[1:len(strs)-1:]+sp)


def test_path(f='.'):
    #fpath=os.path.abspath(__file__) 
    fpath=os.getcwd()
    if f=='.' or f== './':
       return os.path.abspath(os.path.join(fpath,'../../tests_files'))
    elif f=='..' or f=='../':
       return os.path.abspath(os.path.join(fpath,'../../../tests_files'))

if __name__ == '__main__':
   print(test_path())
