""" Core definition of a Materials Document """
from __future__ import annotations

from datetime import datetime
from functools import partial
from typing import ClassVar, Mapping, Optional, Sequence, Type, TypeVar, Union

from pydantic import BaseModel, Field, create_model
from pymatgen.analysis.magnetism import CollinearMagneticStructureAnalyzer, Ordering
from pymatgen.core import Structure as STRUCTURE


from matvirdkit.model.structure import StructureMP
from matvirdkit.model.provenance import LocalProvenance,GlobalProvenance,Origin

T = TypeVar("T", bound="CoreMaterialsDoc")

class CoreMaterialsDoc(BaseModel):
    """
    Definition for a core Materials Document
    """

    # Only material_id is required for all documents
    material_id: str = Field(
        ...,
        description="The ID of this material, used as a universal reference across proeprty documents."
        "This comes in the form and str or int",
    )

    structure: StructureMP = Field(
        ..., description="The best structure for this material"
    )

    deprecated: bool = Field(
        False,
        description="Whether this materials document is deprecated.",
    )

    initial_structures: Sequence[StructureMP] = Field(
        [],
        description="Initial structures used in the DFT optimizations corresponding to this material",
    )

    task_ids: Sequence[str] = Field(
        [],
        title="Calculation IDs",
        description="List of Calculations IDs used to make this Materials Document",
    )

    deprecated_tasks: Sequence[str] = Field([], title="Deprecated Tasks")

    calc_types: Mapping[str, str] = Field(
        None,
        description="Calculation types for all the calculations that make up this material",
    )

    last_updated: datetime = Field(
        description="Timestamp for when this document was last updated",
        default_factory=datetime.utcnow,
    )

    created_at: datetime = Field(
        description="Timestamp for when this material document was first created",
        default_factory=datetime.utcnow,
    )

    origins: Sequence[Origin] = Field(
        None, description="Dictionary for tracking the provenance of properties"
    )

    warnings: Sequence[str] = Field(
        [], description="Any warnings related to this material"
    )

    @classmethod
    def from_structure(  # type: ignore[override]
        cls: Type[T], structure: STRUCTURE, dimension: int,material_id: str, **kwargs
    ) -> T:
        """
        Builds a materials document using the minimal amount of information
        """

        #_st=.from_structure(dimension=dimension, structure=structure,**kwargs)
        return cls(  # type: ignore
            structure=structure.as_dict(),
            material_id=material_id,
            include_structure=True,
            **kwargs
        )


if __name__=='__main__':
   import os
   from matvirdkit.model.utils import test_path
   from monty.serialization import loadfn,dumpfn
   st=STRUCTURE.from_file(os.path.join(test_path(),'relax/CONTCAR'))
   cmd=CoreMaterialsDoc.from_structure(structure=st,material_id='m2d-1',dimension=3)
   print(cmd.json())
   dumpfn(cmd.dict(),'t.json')
