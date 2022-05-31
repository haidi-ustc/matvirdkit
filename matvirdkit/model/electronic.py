import uuid
from datetime import datetime
from pydantic import BaseModel, Field, validator
from typing import ClassVar, Dict, List, Optional, Union, Tuple, Any

from matvirdkit.model.utils import Vector3D
from matvirdkit.model.common import JFData, DataFigure,MatvirdBase
from matvirdkit.model.provenance import LocalProvenance,GlobalProvenance,Origin

def get_vasp_dos(workpath,**kwargs):
    from matvirdkit.builder.vasp.electronic_structure import ElectronicStructure
    electronic_structure=ElectronicStructure(workpath,**kwargs)
    return electronic_structure.get_dos_auto(workpath)

class Workfunction(MatvirdBase):
      value : float = Field(None, description= 'value of workfunction')

class Bandgap(MatvirdBase):
      value: float = Field(None,description= 'value of band gap')
      direct: bool = Field(None, description="If this material has direct band gap or not")
      cbm_loc: Union[str,Vector3D]= Field(None,description='conducation band min kpoint location, e.g. Gamma or [0,0,0]')
      vbm_loc: Union[str,Vector3D]= Field(None,description='valence band max kpoint location, e.g. Gamma or [0,0,0]')

class EMC(MatvirdBase):
      value:  float = Field(None, description='value of effective mass')
      k_loc: Union[str,Vector3D]= Field(None,description='kpoint location, e.g. Gamma or [0,0,0]')
      b_loc: Union[str,int]= Field(None,description='band location, e.g. "VB", "CB", 2')

class Mobility(MatvirdBase):
      value:  float = Field(None, description='value of carrier mobility')
      direction: Union[str,Vector3D]= Field(None,description='direction for carrier.  e.g. "armchair", "zigzag", or [1,0,0]')

class ElectronicStructure(MatvirdBase):
    """
    An elctronic structure  property block
    """
    provenance: Dict[str,LocalProvenance] = Field({}, description="Property provenance")
    bandgap: Bandgap = Field(None, title='band gap value in eV')
    emc: EMC = Field(None, title = 'effective mass')
    mobility: Mobility = Field(None, title = 'carrier mobility')
    workfunction: Workfunction = Field(None,title='work function')
    dos: DataFigure = Field(None,title='density of states')
    band: DataFigure = Field(None,title='band structure')

class ElectronicStructureDoc(BaseModel):
    """
    An elctronic structure  property block
    """
    property_name: ClassVar[str] = "electronic structure"
    electronicstructure: Dict[str,ElectronicStructure]=Field({}, description='electronicstructure list')

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
   es={
       'pbe': ElectronicStructure(bandgap=Bandgap(value=1.1,direct=True,description='HSE-low-kp'),
               emc= EMC(k_loc='Gamma',b_loc='VB',value=0.3,description='PBE'),
               mobility= Mobility(k_loc='Gamma',b_loc='VB',value=0.3,description='PBE',direction='x'),
   provenance={"emc":LocalProvenance( 
      warnings = ['low encut'],
      tags = ['experimental phase'],
      database_IDs={'icsd':['11023'],'mp':['mp-771246']}) }
               ),
       'hse': ElectronicStructure(bandgap=Bandgap(value=1.2,direct=True,description='HSE-low-kp'),
               emc= EMC(k_loc='Gamma',b_loc='VB',value=0.4,description='PBE'),
               mobility= Mobility(k_loc='Gamma',b_loc='CB',value=0.3,description='PBE',direction='x'),
               dos=DataFigure(data= [data_hse], figure=data_hse)
               )
       }

   pd=ElectronicStructureDoc(
         electronicstructure= es
     )
   print(pd.json())
   dumpfn(pd.dict(),'electronic.json',indent=4)
