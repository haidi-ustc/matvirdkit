import uuid
from datetime import datetime
from typing import ClassVar, Dict, List, Optional, Union, Tuple
from pydantic import BaseModel, Field
from matvirdkit.model.properties import PropertyDoc,PropertyOrigin

class BMS(BaseModel):
    description : Optional[str] = 'Bi-polar magnetic semiconductor information'
    delta_1: float = Field(...,description='the spin-flip gap in valence band')
    delta_2: float = Field(...,description='the spin-flip gap in conduction band')
    delta_3: float = Field(...,description='the band gap')
    link: str = Field(None)     

class BMSDoc(PropertyDoc):
    """
    An BMS property block
    """

    property_name: ClassVar[str] = "bms"

    bms: List[BMS] = Field(None, description='BMS information')

if __name__=='__main__': 
   import os
   ustr=str(uuid.uuid4())
   pd=BMSDoc(created_at=datetime.now(),
      bms=[
               BMS(delta_1=0.2, delta_2=0.3, delta_3= 0.4 ,description='hse-static',link=ustr),
               ],
      origins=[PropertyOrigin(name='static',task_id='task-112',link=ustr)],
      material_id='bms-1',
      tags = ['experimental phase']
      )
   print(pd.json())
   from monty.serialization import loadfn,dumpfn
   dumpfn(pd.dict(),'t.json')
