import uuid
from datetime import datetime
from typing import ClassVar, Dict, List, Optional, Union, Tuple, Any
from pydantic import BaseModel, Field
from matvirdkit.model.provenance import LocalProvenance,GlobalProvenance,Origin
from matvirdkit.model.common import MatvirdBase

class BMS(MatvirdBase):
    provenance: Dict[str,LocalProvenance] = Field({}, description="Property provenance")
    delta_1: float = Field(...,description='the spin-flip gap in valence band')
    delta_2: float = Field(...,description='the spin-flip gap in conduction band')
    delta_3: float = Field(...,description='the band gap')

class BMSDoc(BaseModel):
    """
    An BMS property block
    """

    property_name: ClassVar[str] = "bms"
    bms: Dict[str,BMS] = Field({}, description='BMS information')

if __name__=='__main__': 
   import os
   #ustr=str(uuid.uuid4())
   provenance=LocalProvenance(
      origins=[Origin(name='bms',task_id='task-112')],
      tags = ['experimental phase'],
      created_at=datetime.now(),
      )
   pd=BMSDoc(
      bms={'HSE-Static': BMS(delta_1=0.2, delta_2=0.3, delta_3= 0.4 ,description='hse static calculation')},
      provenance={'HSE-Static':provenance}
      )
   print(pd.json())
   from monty.serialization import loadfn,dumpfn
   dumpfn(pd.dict(),'bms.json',indent=4)
