import os
import sys
from ase.io import read
from pymatgen.core import Structure
from pymatgen.io.ase import AseAtomsAdaptor
#from code.abinit import AbinitInput

def structure_from_file(filename):
    """
    Attempts to reconstruct a Structure from the contents of any given file. Valid entries
    :param filename: The path to a file where the structure can be reconstructed
    :type filename: str
    :return: Pymatgen Structure if succeed, None otherwise
    """
    st = None
    basename = os.path.basename(filename)
    if not os.path.isfile(filename):
        raise ValueError("ERROR: Could not open file '%s'" % filename)
    if basename[-4:].lower() == 'json':
        st = Structure.from_file(filename)
    elif basename[-3:].lower() == 'cif':
        st = Structure.from_file(filename)
    elif 'poscar' in basename.lower():
        st = Structure.from_file(filename)
    elif 'contcar' in basename.lower():
        st = Structure.from_file(filename)
    elif 'abinit' in basename.lower():
        ai = AbinitInput(filename)
        st = ai.get_structure()
    else:
        try:
            aaa=AseAtomsAdaptor()
            atom=read(filename)
            st=aaa.get_structure(atom)
        except ValueError:
            raise ValueError('Could not convert file as POSCAR')
    return st
