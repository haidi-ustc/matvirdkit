import uuid
from datetime import datetime
from typing import ClassVar, Dict, List, Optional, Union, Tuple, Any
from pydantic import BaseModel, Field, validator
from matvirdkit.model.properties import PropertyDoc,PropertyOrigin
from matvirdkit.model.utils import Vector3D
from matvirdkit.model.common import JFData, DataFigure,MatvirdBase

def get_vasp_dos(workpath,**kwargs):
    from matvirdkit.builder.vasp.electronic_structure import ElectronicStructure
    electronic_structure=ElectronicStructure(workpath,**kwargs)
    return electronic_structure.get_dos_auto(workpath)

class Workfunction(MatvirdBase):
      value : float = Field(..., description= 'value of workfunction')

class Bandgap(MatvirdBase):
      value: float = Field(...,description= 'value of band gap')
      direct: bool = Field(..., description="If this material has direct band gap or not")
      cbm_loc: Union[str,Vector3D]= Field(None,description='conducation band min kpoint location, e.g. Gamma or [0,0,0]')
      vbm_loc: Union[str,Vector3D]= Field(None,description='valence band max kpoint location, e.g. Gamma or [0,0,0]')

class EMC(MatvirdBase):
      value:  float = Field(..., description='value of effective mass')
      k_loc: Union[str,Vector3D]= Field(...,description='kpoint location, e.g. Gamma or [0,0,0]')
      b_loc: Union[str,int]= Field(...,description='band location, e.g. "VB", "CB", 2')

class Mobility(MatvirdBase):
      value:  float = Field(..., description='value of carrier mobility')
      direction: Union[str,Vector3D]= Field(...,description='direction for carrier.  e.g. "armchair", "zigzag", or [1,0,0]')

class ElectronicStructureDoc(PropertyDoc):
    """
    An elctronic structure  property block
    """

    property_name: ClassVar[str] = "electronic structure"

    bandgaps: List[Bandgap] = Field(None, title='band gap value in eV')
    emcs: List[EMC]  = Field(None, title = 'effective mass')
    mobilities: List[Mobility] = Field(None, title = 'carrier mobility')
    workfunctions: List[Workfunction] = Field(None,title='work function')
    doses: List[DataFigure] = Field([],title='density of states')
    bands: List[DataFigure] = Field([],title='band structure')


if __name__=='__main__': 
   from monty.serialization import loadfn,dumpfn
   ustr=str(uuid.uuid4())
   data_hse=JFData(description='DOS data', 
        file_fmt='txt', file_name='./dataset.bms/bms-1/DOSCAR-hse',file_id=None,  
        json_file_name='dos.json',json_id=None,meta={} )
   fig_hse=JFData(description='DOS figure', 
        file_fmt='png', file_name='./dataset.bms/bms-1/dos-hse.png',file_id=None)
   data_pbe=JFData(description='DOS data', 
        file_fmt='txt', file_name='./dataset.bms/bms-1/DOSCAR-pbe',file_id=None,  
        json_file_name='dos.json',json_id=None,meta={})
   fig_pbe=JFData(description='DOS figure', 
        file_fmt='png', file_name='./dataset.bms/bms-1/dos-pbe.png',file_id=None)
   pd=ElectronicStructureDoc(created_at=datetime.now(),
      bandgaps=[Bandgap(value=1.1,direct=True,description='HSE-low-kp'),
                Bandgap(value=0.8,direct=True,description='PBE') 
               ],
      origins=[PropertyOrigin(name='band',task_id='task-1123'),
               PropertyOrigin(name='band',task_id='task-1124'),
               ],
      emcs =[ EMC(k_loc='Gamma',b_loc='VB',value=0.3,description='PBE'),
            ],
      mobilities =[ Mobility(k_loc='Gamma',b_loc='VB',value=0.3,description='PBE',direction='x'),
            ],
      workfunctions=[Workfunction(value=4.5)],
      doses=[
               DataFigure(data= [data_hse], figure=data_hse),
               DataFigure(data= [data_pbe], figure=data_pbe)
      ],
      material_id='rsb-1',
      warnings = ['low encut'],
      tags = ['experimental phase'],
      database_IDs={'icsd':['11023'],'mp':['mp-771246']})
   print(pd.json())
   dumpfn(pd.dict(),'elctronic.json',indent=4)
