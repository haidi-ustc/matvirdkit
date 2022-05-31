from datetime import datetime
from functools import partial
from typing import ClassVar, Mapping, Optional, Sequence, Type, TypeVar, Union,List, Dict

from pydantic import BaseModel, Field, create_model, validator
from pymatgen.analysis.magnetism import CollinearMagneticStructureAnalyzer, Ordering
from pymatgen.core import Structure
from matvirdkit.model.common import Author,Reference,History


class Origin(BaseModel):
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

class Provenance(BaseModel):
      property_name: ClassVar[str]

      last_updated: datetime = Field(
          description="Timestamp for the most recent calculation update for this property",
          default_factory=datetime.utcnow,
      )

      created_at: datetime = Field(
          None,
          description="creation date for the first structure corresponding to this material",
      )
      warnings: Sequence[str] = Field(
          None, description="Any warnings related to this property"
      )

      references: List[Reference] = Field([], description="List of Reference for this material")

      authors: List[Author] = Field([], description="List of authors for this material")

      remarks: List[str] = Field(
          [], description="List of remarks for the provenance of this material"
      )

      tags: List[str] = Field([])

      history: List[History] = Field(
          [],
          description="List of history nodes specifying the transformations or orignation"
          " of this material for the entry closest matching the material input",
      )

      @validator("authors")
      def remove_duplicate_authors(cls, authors):
          authors_dict = {entry.name.lower(): entry for entry in authors}
          return list(authors_dict.items())

class GlobalProvenance(Provenance):
    property_name: ClassVar[str] = 'globalprovenance'
      
class LocalProvenance(Provenance):
    property_name: ClassVar[str] = 'localprovenance'
    origins: Sequence[Origin] = Field(
        {}, description="Dictionary for tracking the provenance of properties"
    )

if __name__=='__main__':
   pd=LocalProvenance(created_at=datetime.now(),
      origins=[Origin(name='band',task_id='task-1123'),
               Origin(name='band',task_id='task-1124'),
               ],
      references=[Reference(bibstr="""Haidi Wang, Qingqing Feng, Xingxing Li, Jinlong Yang, "High-Throughput Computational Screening for Bipolar Magnetic Semiconductors", Research, vol. 2022, Article ID 9857631, 8 pages, 2022.""",doi=DOI(value="10.34133/2022/9857631"))],
      material_id='rsb-1',
      warnings = ['PBE low kpoints','low encut'],
      remarks = ['nature paper'],
      tags =['High temperature'],
      authors=[{'name':'haidi','email':'haidi@hfut.edu.cn'},{'name':'zhangsan','email':'zhangsan@ustc.edu.cn'}]
      )
#,database_IDs={'icsd':['11023'],'mp':['mp-771246']})
   print(pd.json())
   from monty.serialization import loadfn,dumpfn
   from matvirdkit.model.utils import jsanitize,ValueEnum
   dumpfn(jsanitize(pd),'provenance.json',indent=4)
                                                         
