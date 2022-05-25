import numpy as np
from enum import  Enum
from pydantic import BaseModel, Field
from pymatgen.core import Composition #as COMPOSITION
from pymatgen.core import Structure   #as STRUCTURE
from pymatgen.core.periodic_table import Element
from pymatgen.analysis.dimensionality import get_dimensionality_gorai
from typing import List, Dict, Union, Tuple, Optional, Type, TypeVar, overload
from matvirdkit.model.symmetry import SymmetryData
from matvirdkit.model.utils import Vector3D, Matrix3D,ValueEnum

#Composition = Dict[str, float] 
#Composition.__doc__ = "Composition dict"  # type: ignore

T = TypeVar("T", bound="StructureMetadata")
M = TypeVar("M", bound="StructureMatvird")

class Lattice(BaseModel):
    """
    A lattice object represented as a 3x3 matrix of floats in Angstroms
    """

    a: float = Field(..., title="*a* lattice parameter")
    alpha: int = Field(..., title="Angle between a and b lattice vectors")
    b: float = Field(..., title="b lattice parameter")
    beta: int = Field(..., title="Angle between a and c lattice vectors")
    c: float = Field(..., title="c lattice parameter")
    gamma: int = Field(..., title="Angle between b and c lattice vectors")
    volume: float = Field(..., title="Lattice volume")

    matrix: Matrix3D  = Field(
        ..., description="Matrix representation of this lattice"
    )


class Specie(BaseModel):
    """
    An extension of Element with an oxidation state and other optional
    properties. Properties associated with Specie should be "idealized"
    values, not calculated values. For example, high-spin Fe2+ may be
    assigned an idealized spin of +5, but an actual Fe2+ site may be
    calculated to have a magmom of +4.5. Calculated properties should be
    assigned to Site objects, and not Specie.
    """

    symbol: str = Field(..., title="Element Symbol")
    oxidation_state: float = Field(..., title="Oxidation State")
    properties: Optional[Dict] = Field(..., title="Species Properties")

class SiteSpecie(Specie):
    """
    Adds site occupation to Species
    """

    occu: float = Field(..., title="Occupation")


class SiteElement(BaseModel):
    """
    Elements defined on site with an occupation
    """

    element: Element = Field(..., title="Element")
    occu: float = Field(..., title="Occupation")


class Site(BaseModel):
    """
    A generalized *non-periodic* site. This is essentially a composition
    at a point in space, with some optional properties associated with it. A
    Composition is used to represent the atoms and occupancy, which allows for
    disordered site representation. Coords are given in standard cartesian
    coordinates.
    """

    species: List[Union[SiteElement, SiteSpecie]] = Field(..., title="Species")
    xyz: Tuple[float, float, float] = Field(..., title="Cartesian Coordinates")
    label: str = Field(..., title="Label")
    properties: Optional[Dict] = Field(None, title="Properties")


class PeriodicSite(Site):
    """
    A generalized *periodic* site. This adds on fractional coordinates within the
    lattice to the generalized Site model
    """

    abc: Tuple[float, float, float] = Field(..., title="Fractional Coordinates")


class StructureMP(BaseModel):
    """
    Basic Structure object with periodicity. Essentially a sequence
    of Sites having a common lattice and a total charge.
    """

    charge: Optional[float] = Field(None, title="Total charge")
    lattice: Lattice = Field(..., title="Lattice for this structure")
    sites: List[PeriodicSite] = Field(..., title="List of sites in this structure")


class StructureMetadata(BaseModel):
    """
    Mix-in class for structure metadata
    """

    # Structure metadata
    nsites: int = Field(None, description="Total number of sites in the structure")
    elements: List[Element] = Field(
        None, description="List of elements in the material"
    )
    nelements: int = Field(None, title="Number of Elements")
    composition: Composition = Field(
        None, description="Full composition for the material"
    )
    composition_reduced: Composition = Field(
        None,
        title="Reduced Composition",
        description="Simplified representation of the composition",
    )
    formula_pretty: str = Field(
        None,
        title="Pretty Formula",
        description="Cleaned representation of the formula",
    )
    formula_anonymous: str = Field(
        None,
        title="Anonymous Formula",
        description="Anonymized representation of the formula",
    )
    chemsys: str = Field(
        None,
        title="Chemical System",
        description="dash-delimited string of elements in the material",
    )
    volume: float = Field(
        None,
        title="Volume",
        description="Total volume for this structure in Angstroms^3",
    )

    density: float = Field(
        None, title="Density", description="Density in grams per cm^3"
    )

    density_atomic: float = Field(
        None,
        title="Packing Density",
        description="The atomic packing density in atoms per cm^3",
    )

    symmetry: SymmetryData = Field(None, description="Symmetry data for this material")

    @classmethod
    def from_composition(
        cls: Type[T],
        #composition: COMPOSITION,
        composition: Composition,
        fields: Optional[List[str]] = None,
        **kwargs
    ) -> T:

        fields = (
            [
                "elements",
                "nelements",
                "composition",
                "composition_reduced",
                "formula_pretty",
                "formula_anonymous",
                "chemsys",
            ]
            if fields is None
            else fields
        )
        elsyms = sorted(set([e.symbol for e in composition.elements]))

        data = {
            "elements": elsyms,
            "nelements": len(elsyms),
            "composition": composition,
            "composition_reduced": composition,
            "formula_pretty": composition.reduced_formula,
            "formula_anonymous": composition.anonymized_formula,
            "chemsys": "-".join(elsyms),
        }

        return cls(**{k: v for k, v in data.items() if k in fields}, **kwargs)

    @classmethod
    def from_structure(
        cls: Type[T],
        #structure: STRUCTURE,
        structure: Structure,
        fields: Optional[List[str]] = None,
        include_structure: bool = False,
        **kwargs
    ) -> T:

        fields = (
            [
                "nsites",
                "elements",
                "nelements",
                "composition",
                "composition_reduced",
                "formula_pretty",
                "formula_anonymous",
                "chemsys",
                "volume",
                "density",
                "density_atomic",
                "symmetry",
            ]
            if fields is None
            else fields
        )
        comp = structure.composition
        elsyms = sorted(set([e.symbol for e in comp.elements]))
        symmetry = SymmetryData.from_structure(structure)

        data = {
            "nsites": structure.num_sites,
            "elements": elsyms,
            "nelements": len(elsyms),
            "composition": comp,
            #"composition_reduced": comp.reduced_composition,
            "composition_reduced": comp.to_reduced_dict,
            "formula_pretty": comp.reduced_formula,
            "formula_anonymous": comp.anonymized_formula,
            "chemsys": "-".join(elsyms),
            "volume": structure.volume,
            "density": structure.density,
            "density_atomic": structure.volume / structure.num_sites,
            "symmetry": symmetry,
        }
        if include_structure:
            kwargs.update({"structure": structure})

        return cls(**{k: v for k, v in data.items() if k in fields}, **kwargs)

class Dimension(ValueEnum):
      zero: int = 0   # quantom dot
      one: int =  1   # nano wire
      two: int =  2   # nano film 
      three: int= 3   # bulk

class StructureMatvird(BaseModel):
    """
    Structure object with periodicity for Matvird database. Essentially a sequence
    of Sites having a common lattice and a total charge.
    """
    description : Optional[str] = 'Structure information'
    dimension :  Optional[Dimension] = Field(None, title= 'Dimension of structure')
    structure: StructureMP = Field(..., title="Material project style structure")
    metadata:  StructureMetadata = Field(..., title="Structure meta data")
    @classmethod
    def from_structure(
        cls: Type[M],
        structure: Structure,
        dimension: Optional[Dimension]=None,
        fields: Optional[List[str]] = None,
        **kwargs
        ) -> M:

        fields = (
            [
              "dimension",
              "structure",
              "metadata"
            ]
            if fields is None
            else fields
        )
        if dimension:
           pass
        else:
           dimension=get_dimensionality_gorai(structure)
        _metadata=StructureMetadata.from_structure(structure)
        #if dimension == 2:
        #  _metadata['volume']=np.linalg.norm(np.cross(structure.lattice.matrix[0],structure.lattice.matrix[1]))
        data={"dimension": dimension,
              'structure': structure.as_dict(),
              'metadata':  _metadata
              }
        return cls(**{k: v for k, v in data.items() if k in fields}, **kwargs)

if __name__=='__main__':
  import os
  from matvirdkit.model.utils import jsanitize,ValueEnum
  from matvirdkit.model.utils import test_path
  from monty.serialization import loadfn,dumpfn
  st=Structure.from_file(os.path.join(test_path(),'relax/CONTCAR'))
 # mst=StructureMatvird.from_structure(dimension=3,structure=st)
  #decide the dimension automaticly
  mst=StructureMatvird.from_structure(structure=st,description='test structure')
  #input the dimension manually
  #mst=StructureMatvird.from_structure(dimension=3,structure=st,description='test structure')
  #print(mst.json())
  print(mst.dict())
  meta=StructureMetadata.from_structure(st,include_structure=True)
  print('--------')
  print(meta.dict())
  #print(meta.json())
  dumpfn(jsanitize(meta),'structure.json',indent=4)
