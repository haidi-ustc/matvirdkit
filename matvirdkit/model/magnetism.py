import uuid
from enum import Enum
from datetime import datetime
from typing import ClassVar, Dict, List, Optional, Union, Tuple
from pydantic import BaseModel, Field, validator
from matvirdkit.model.properties import PropertyDoc,PropertyOrigin
from matvirdkit.model.utils import jsanitize,ValueEnum

class Order(ValueEnum):
    FM : str = 'FM'
    FiM : str= 'FiM'
    NM : str = 'NM'
    AFM : str = 'AFM'

class Magnetism(BaseModel):
    description : Optional[str] = 'Magnetic information'
    tot_moment: Optional[float]
    order: Order = Field(...,title='Magnetic order')
    link: str = Field(None)     

class MagnetismDoc(PropertyDoc):
    """
    An magntic  property block
    """

    property_name: ClassVar[str] = "magnetism"

    magnetisms: List[Magnetism] = Field(None, description='Magnetic information')


if __name__=='__main__': 
   ustr=str(uuid.uuid4())
   pd=MagnetismDoc(created_at=datetime.now(),
      magnetisms=[
                Magnetism(order='FM',tot_moment=1.3,description='pbe-static',link=ustr),
               ],
      origins=[PropertyOrigin(name='static',task_id='task-112',link=ustr)],
      material_id='rsb-1',
      tas = ['high temperature phase']
      )
   print(pd.json())
   from monty.serialization import loadfn,dumpfn
   dumpfn(jsanitize(pd),'t.json',indent=4)
