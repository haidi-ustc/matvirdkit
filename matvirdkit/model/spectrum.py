""" Core definition of Spectrum document """
from datetime import datetime
from functools import partial
from typing import ClassVar, Dict, List, Union

from pydantic import Field,BaseModel
#from structure import StructureMetadata
#from pymatgen.core.spectrum import Spectrum

class SpectrumDoc(BaseModel):
    """
    Base model definition for any spectra document. This should contain
    metadata on the structure the spectra pertains to
    """
    property_name: ClassVar[str] = "spectrum"

    material_id: str = Field(
        ...,
        description="The ID of the material, used as a universal reference across proeprty documents."
        "This comes in the form: m2d-*, rsb-*, npr-*",
    )

    spectrum_id: str = Field(
        ...,
        title="Spectrum Document ID",
        description="The unique ID for this spectrum document",
    )

    last_updated: datetime = Field(
        description="Timestamp for the most recent calculation update for this property",
        default_factory=datetime.utcnow,
    )

    warnings: List[str] = Field([], description="Any warnings related to this property")
