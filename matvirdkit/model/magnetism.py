import uuid
from enum import Enum
from datetime import datetime
from typing import ClassVar, Dict, List, Optional, Union, Tuple
from pydantic import BaseModel, Field, validator
from matvirdkit.model.properties import PropertyDoc,PropertyOrigin
from matvirdkit.model.utils import jsanitize,ValueEnum
from matvirdkit.model.common import MatvirdBase

class Order(ValueEnum):
    FM : str = 'FM'
    FiM : str= 'FiM'
    NM : str = 'NM'
    AFM : str = 'AFM'

class Magnetism(MatvirdBase):
    magneatic_moment: Optional[float] = Field(None, description='total manetic moment of system')
    magnetic_order: Order = Field(None,title='Magnetic magnetic_order')
    exchange_energy: Optional[float] = Field(None)
    # unit meV/unit cell
    # ref https://cmrdb.fysik.dtu.dk/c2db/row/Br2Cr2O2-40d95997a4f9
    #{'Ez-Ex': 0.12 , 'Ez-Ey': 0.05}
    magnetic_anisotropy: Dict[str,float] = Field({},description='mgnetic anisotropy energy')

class MagnetismDoc(PropertyDoc):
    """
    An magntic  property block
    """
    property_name: ClassVar[str] = "magnetism"

    magnetism: List[Magnetism] = Field(None, description='Magnetic information')


if __name__=='__main__': 
   ustr=str(uuid.uuid4())
   pd=MagnetismDoc(created_at=datetime.now(),
      magnetisms=[
                Magnetism(magnetic_order='FM',magneatic_moment=1.3,label='pbe-static'),
               ],
      origins=[PropertyOrigin(name='static',task_id='task-112')],
      material_id='rsb-1',
      tags = ['high temperature phase']
      )
   print(pd.json())
   from monty.serialization import loadfn,dumpfn
   dumpfn(jsanitize(pd),'mag.json',indent=4)
