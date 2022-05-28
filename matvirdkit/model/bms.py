import uuid
from datetime import datetime
from typing import ClassVar, Dict, List, Optional, Union, Tuple, Any
from pydantic import BaseModel, Field
from matvirdkit.model.properties import PropertyDoc,PropertyOrigin
from matvirdkit.model.common import MatvirdBase

class BMS(MatvirdBase):
    delta_1: float = Field(...,description='the spin-flip gap in valence band')
    delta_2: float = Field(...,description='the spin-flip gap in conduction band')
    delta_3: float = Field(...,description='the band gap')

class BMSDoc(PropertyDoc):
    """
    An BMS property block
    """

    property_name: ClassVar[str] = "bms"

    bms: List[BMS] = Field([], description='BMS information')

if __name__=='__main__': 
   import os
   #ustr=str(uuid.uuid4())
   pd=BMSDoc(created_at=datetime.now(),
      bms=[
               BMS(delta_1=0.2, delta_2=0.3, delta_3= 0.4 ,description='hse static calculation',label='HSE-Static'),
               ],
      origins=[PropertyOrigin(name='bms',task_id='task-112')],
      material_id='bms-1',
      tags = ['experimental phase']
      )
   print(pd.json())
   from monty.serialization import loadfn,dumpfn
   dumpfn(pd.dict(),'bms.json')
