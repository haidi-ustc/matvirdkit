from datetime import datetime
from functools import partial
from typing import ClassVar, Mapping, Optional, Sequence, Type, TypeVar, Union,List

from pydantic import BaseModel, Field, create_model, validator
from pymatgen.analysis.magnetism import CollinearMagneticStructureAnalyzer, Ordering
from pymatgen.core import Structure
from matvirdkit.model.common import ReferenceDB,Author,Reference,History,DOI

class Source(BaseModel):
      description : Optional[str] = 'Source information'
      db_name: ReferenceDB = Field(...,description='database name')
      db_id: str = Field(...,description='material id')
      db_url: str = Field(...,description='material url')

class Sources(BaseModel):
      description : Optional[str] = 'Sources information'
      sources: List[Source] = Field([],description='list of sources')

S = TypeVar("S", bound="PropertyDoc")

class PropertyOrigin(BaseModel):
    """
    Provenance document for the origin of properties in a material document
    """

    name: str = Field(..., description="The property name")
    task_id: str = Field(
        ..., description="The calculation IDs this property comes from"
    )
    last_updated: datetime = Field(
        description="The timestamp when this calculation was last updated",
        default_factory=datetime.utcnow,
    )
    link: str= Field(None, description='a link to connect the properties')

class PropertyDoc(BaseModel):
    """
    Base model definition for any singular materials property. This may contain any amount
    of structure metadata for the purpose of search
    This is intended to be inherited and extended not used directly
    """

    property_name: ClassVar[str]
    material_id: str = Field(
        ...,
        description="The ID of the material, used as a universal reference across proeprty documents."
        "This comes in the form of an matvird or int",
    )

    last_updated: datetime = Field(
        description="Timestamp for the most recent calculation update for this property",
        default_factory=datetime.utcnow,
    )

    origins: Sequence[PropertyOrigin] = Field(
        [], description="Dictionary for tracking the provenance of properties"
    )

    warnings: Sequence[str] = Field(
        None, description="Any warnings related to this property"
    )
    created_at: datetime = Field(
        ...,
        description="creation date for the first structure corresponding to this material",
    )


    references: List[Reference] = Field([], description="List of Reference for this material")

    authors: List[Author] = Field([], description="List of authors for this material")

    remarks: List[str] = Field(
        [], description="List of remarks for the provenance of this material"
    )

    tags: List[str] = Field([])

    theoretical: bool = Field(
        True, description="If this material has any experimental entry or not"
    )

    history: List[History] = Field(
        [],
        description="List of history nodes specifying the transformations or orignation"
        " of this material for the entry closest matching the material input",
    )

    @validator("authors")
    def remove_duplicate_authors(cls, authors):
        authors_dict = {entry.name.lower(): entry for entry in authors}
        return list(authors_dict.items())

