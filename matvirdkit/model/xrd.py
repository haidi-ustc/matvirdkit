from enum import Enum
from datetime import datetime
from monty.serialization import loadfn,dumpfn
from typing import Dict, List, Optional, Tuple, Union,Any, ClassVar

import numpy as np
from pydantic import BaseModel, Field, root_validator, ValidationError, validator
from pymatgen.analysis.diffraction.xrd import (
    WAVELENGTHS,
    DiffractionPattern,
    XRDCalculator,
)
from pymatgen.core import Structure
from pymatgen.core.periodic_table import Element

from matvirdkit.model.common import MatvirdBase
from matvirdkit.model.utils import ValueEnum, jsanitize
from matvirdkit.model.provenance import LocalProvenance,Origin

class Edge(ValueEnum):
    K_Alpha = "Ka"
    K_Alpha1 = "Ka1"
    K_Alpha2 = "Ka2"
    K_Beta = "Kb"
    K_Beta1 = "Kb1"
    K_Beta2 = "Kb2"

class Xrd(MatvirdBase):
    provenance: Dict[str,LocalProvenance] = Field({}, description="Property provenance")
    spectrum_id: str = Field(
        ...,
        title="Spectrum Document ID",
        description="The unique ID for this spectrum document",
    )

    spectrum: Any #DiffractionPattern
    min_two_theta: float
    max_two_theta: float
    wavelength: float = Field(..., description="Wavelength for the diffraction source")
    target: Element = Field(
        None, description="Target element for the diffraction source"
    )
    edge: Edge = Field(None, description="Atomic edge for the diffraction source")
    @root_validator(pre=True)
    def get_target_and_edge(cls, values: Dict):
        #print("Validations")
        # Only do this if neither target not edge is defined
        if "target" not in values and "edge" not in values:
            print("Are we even getting here?")
            try:
                pymatgen_wavelength = next(
                    k
                    for k, v in WAVELENGTHS.items()
                    if np.allclose(values["wavelength"], v)
                )
                values["target"] = pymatgen_wavelength[:2]
                values["edge"] = pymatgen_wavelength[2:]

            except Exception:
                return values
        return values

    @classmethod
    def from_structure(  
        cls,
        #created_at: datetime,
        #material_id: str,
        spectrum_id: str,
        structure: Structure,
        wavelength: float,
        min_two_theta: float=0,
        max_two_theta: float=180,
        symprec : float =0.1,
        **kwargs,
    ) -> "XrdDoc":
        calc = XRDCalculator(wavelength=wavelength, symprec=symprec)
        pattern = calc.get_pattern(
            structure, two_theta_range=(min_two_theta, max_two_theta)
        )
        #dumpfn(pattern.as_dict(),'xrd.json',indent=4)
        _pattern=pattern.as_dict()
        _pattern['x']=_pattern['x'].tolist()
        _pattern['y']=_pattern['y'].tolist()
        #del _pattern['@module']
        #del _pattern['@class']

        return cls(
            #created_at=created_at,
            #material_id=material_id,
            spectrum_id=spectrum_id,
            spectrum=_pattern,
            wavelength=wavelength,
            min_two_theta=min_two_theta,
            max_two_theta=max_two_theta,
            **kwargs
        )


    @classmethod
    def from_target(
        cls,
        material_id: str,
        structure: Structure,
        target: Element = 'Cu',
        edge: Edge = 'Ka',
        min_two_theta=0,
        max_two_theta=180,
        symprec=0.1,
        **kwargs,
    ) -> "XrdDoc":
        if f"{target}{edge}" not in WAVELENGTHS:
            raise ValueError(f"{target}{edge} not in pymatgen wavelenghts dictionarty")

        wavelength = WAVELENGTHS[f"{target}{edge}"]
        spectrum_id = f"{material_id}-{target}{edge}"

        return cls.from_structure(
            #material_id=material_id,
            spectrum_id=spectrum_id,
            structure=structure,
            wavelength=wavelength,
            target=target,
            edge=edge,
            min_two_theta=min_two_theta,
            max_two_theta=max_two_theta,
            **kwargs,
        )
     
class XrdDoc(BaseModel):
    """
    Document describing a XRD Diffraction Pattern
    """
    property_name: ClassVar[str] = "spectrum"
    xrd: Dict[str,Xrd] = Field({}, description='Xrd List')


if __name__ == '__main__':
   import os
   from matvirdkit.model.utils import jsanitize,ValueEnum
   from matvirdkit.model.utils import test_path
   from monty.serialization import loadfn,dumpfn
   st=Structure.from_file(os.path.join(test_path(),'relax/CONTCAR'))
   provenance= {'standard':LocalProvenance(tags=['abc'])}
   xrddoc=XrdDoc( 
         xrd = {'stanard': Xrd.from_target( 
                              material_id='bms-1',
                              structure=st,
                              target= 'Cu',
                              edge= "Ka", 
                              min_two_theta=0,
                              provenance=provenance,
                              max_two_theta=180)  
          },
      )

   #print(xrddoc.json())
   from monty.serialization import loadfn,dumpfn
   from matvirdkit.model.utils import jsanitize,ValueEnum
   dumpfn(jsanitize(xrddoc),'xrd.json',indent=4)
