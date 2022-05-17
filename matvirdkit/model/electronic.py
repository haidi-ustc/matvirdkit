import uuid
from datetime import datetime
from typing import ClassVar, Dict, List, Optional, Union, Tuple, Any
from pydantic import BaseModel, Field, validator
from matvirdkit.model.properties import PropertyDoc,PropertyOrigin
from matvirdkit.model.common import ReferenceDB,Author,Reference,History,DOI
from matvirdkit.model.utils import Vector3D
from matvirdkit.model.common import JFData, DataFigure

def get_vasp_dos(workpath,**kargs):
    from matvirdkit.builder.vasp.electronic_structure import ElectronicStructure
    electronic_structure=ElectronicStructure(workpath,**kargs)
    return electronic_structure.get_dos_auto(workpath)

class DOSDoc(PropertyDoc):
    """
    A DOS property block
    """

    property_name: ClassVar[str] = "dos"

    dos: List[DataFigure] = Field(None, description='DOS information')

class BandDoc(PropertyDoc):
    """
    A band property block
    """

    property_name: ClassVar[str] = "band"

    band: List[DataFigure] = Field(None, description='Band information')

class Workfunction(BaseModel):
      description : Optional[str] = 'Work function information'
      value : float = Field(..., description= 'value of workfunction')

class Bandgap(BaseModel):
      description : Optional[str] = 'Band gap information'
      value: float = Field(...)
      direct: bool = Field(..., description="If this material has direct band gap or not")
      cbm_loc: Union[str,Vector3D]= Field(None,description='conducation band min kpoint location, e.g. Gamma or [0,0,0]')
      vbm_loc: Union[str,Vector3D]= Field(None,description='valence band max kpoint location, e.g. Gamma or [0,0,0]')
      link: str = Field(None)

class EMC(BaseModel):
      description:  Optional[str] =Field(None)
      link: str = Field(None)
      value:  float = Field(..., description='value of effective mass')
      k_loc: Union[str,Vector3D]= Field(...,description='kpoint location, e.g. Gamma or [0,0,0]')
      b_loc: Union[str,int]= Field(...,description='band location, e.g. "VB", "CB", 2')

class Mobility(EMC):
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


if __name__=='__main__': 
   from monty.serialization import loadfn,dumpfn
   ustr=str(uuid.uuid4())
   pd=ElectronicStructureDoc(created_at=datetime.now(),
      bandgaps=[Bandgap(value=1.1,direct=True,description='HSE-low-kp'),
                Bandgap(value=0.8,direct=True,description='PBE',link=ustr) 
               ],
      origins=[PropertyOrigin(name='band',task_id='task-1123',link=ustr),
               PropertyOrigin(name='band',task_id='task-1124'),
               ],
      emcs =[ EMC(k_loc='Gamma',b_loc='VB',value=0.3,description='PBE'),
            ],
      mobilities =[ Mobility(k_loc='Gamma',b_loc='VB',value=0.3,description='PBE',direction='x'),
            ],
      workfunctions=[Workfunction(value=4.5)],
      material_id='rsb-1',
      warnings = ['low encut']
      )
#,database_IDs={'icsd':['11023'],'mp':['mp-771246']})
   print(pd.json())


   data_hse=JFData(description='DOS data', 
        file_fmt='txt', file_name='./dataset.bms/bms-1/DOSCAR-hse',file_id=None,  
        json_file_name='dos.json',json_id=None,meta={})
   fig_hse=JFData(description='DOS figure', 
        file_fmt='png', file_name='./dataset.bms/bms-1/dos-hse.png',file_id=None)
   data_pbe=JFData(description='DOS data', 
        file_fmt='txt', file_name='./dataset.bms/bms-1/DOSCAR-pbe',file_id=None,  
        json_file_name='dos.json',json_id=None,meta={})
   fig_pbe=JFData(description='DOS figure', 
        file_fmt='png', file_name='./dataset.bms/bms-1/dos-pbe.png',file_id=None)
   ustr=str(uuid.uuid4())
   pd=DOSDoc(created_at=datetime.now(),
      dos=[
               DataFigure(data=data_hse, figure=data_hse ,description='hse-dos',link=ustr),
               DataFigure(data=data_pbe, figure=data_pbe ,description='pbe-dos',link=ustr),
               ],
      origins=[PropertyOrigin(name='static',task_id='task-112',link=ustr)],
      material_id='bms-1',
      tags = ['experimental phase']
      )
   print(pd.json())
   dumpfn(pd.dict(),'t.json',indent=4)
