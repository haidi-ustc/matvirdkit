""" Core definition for Polar property Document """
from datetime import datetime
from typing import ClassVar, Dict, List, Tuple

import numpy as np
from pydantic import BaseModel, Field
from pymatgen.analysis.piezo import PiezoTensor as BasePiezoTensor

from matvirdkit.model.settings import MAX_PIEZO_MILLER
from matvirdkit.model.structure import StructureMetadata
from matvirdkit.model.utils import VoigtVector,Matrix3D,Vector3D
from matvirdkit.model.utils import Tensor as PiezoTensor


class Dielectric(BaseModel):
    """
    A dielectric property block
    """

    property_name: ClassVar[str] = "dielectric"

    total: Matrix3D = Field(description="Total dielectric response")
    ionic: Matrix3D = Field(
        description="Dielectric response due to atomic rearrangement"
    )
    electronic: Matrix3D = Field(
        description="Dielectric response due to electron rearrangement"
    )

    e_total: float = Field(description="Total electric permittivity")
    e_ionic: float = Field(
        description="Electric permittivity from atomic rearrangement"
    )
    e_electronic: float = Field(
        description="Electric permittivity due to electrons rearrangement"
    )

    n: float = Field(title="Refractive index")

    @classmethod
    def from_ionic_and_electronic(cls, ionic: Matrix3D, electronic: Matrix3D):

        total = np.sum(ionic, electronic).tolist()  # type: ignore

        return cls(
            **{
                "total": total,
                "ionic": ionic,
                "electronic": electronic,
                "e_total": np.average(np.diagonal(total)),
                "e_ionic": np.average(np.diagonal(ionic)),
                "e_electronic": np.average(np.diagonal(electronic)),
                "n": np.sqrt(np.average(np.diagonal(electronic))),
            }
        )


class Piezoelectric(BaseModel):
    """
    A dielectric package block
    """

    property_name: ClassVar[str] = "piezoelectric"

    total: PiezoTensor = Field(None, description="")
    ionic: PiezoTensor = Field(None, description="")
    electronic: PiezoTensor = Field(None, description="")

    e_ij_max: float = Field(None, description="")
    max_direction: Tuple[int, int, int] = Field(
        None, description="Miller direction for maximum piezo response"
    )
    strain_for_max: Matrix3D = Field(
        None, description="Normalized strain direction for maximum piezo repsonse"
    )

    @classmethod
    def from_ionic_and_electronic(cls, ionic: Matrix3D, electronic: Matrix3D):

        total = BasePiezoTensor.from_voigt(np.sum(ionic, electronic))  # type: ignore

        directions, charges, strains = np.linalg.svd(total, full_matrices=False)
        max_index = np.argmax(np.abs(charges))

        max_direction = directions[max_index]

        # Allow a max miller index of 10
        min_val = np.abs(max_direction)
        min_val = min_val[min_val > (np.max(min_val) / MAX_PIEZO_MILLER)]
        min_val = np.min(min_val)

        return cls(
            **{
                "total": total.zeroed().voigt,
                "ionic": ionic,
                "static": electronic,
                "e_ij_max": charges[max_index],
                "max_direction": np.round(max_direction / min_val),
                "strain_for_max": strains[max_index],
            }
        )
