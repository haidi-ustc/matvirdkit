import os
import uuid
from datetime import datetime
from typing import ClassVar, Dict, List, Optional, Union, Tuple,TypeVar,Type , Any
from pydantic import BaseModel, Field
from monty.serialization import loadfn,dumpfn
from matvirdkit.model.properties import PropertyDoc,PropertyOrigin
from matvirdkit.model.utils import VoigtVector,Matrix3D,Vector3D,YesOrNo
from matvirdkit.model.utils import ElasticTensor, ValueEnum
from matvirdkit.model.common import DataFigure,JFData,MatvirdBase

M2S = TypeVar("M2", bound="Mechanics2dSummary")
M3S = TypeVar("M3", bound="Mechanics3DSummary")

class ApproachAndProperty(ValueEnum):
      elc_energy="elc_energy"
      elc_stress="elc_stress"
      ssc_stress="ssc_stress"

class Direction2d(ValueEnum):
      xx='Def_xx'
      xy='Def_xy'
      yy='Def_yy'
      bi='Def_bi'

class MechanicsBase(MatvirdBase):
    s_tensor : ElasticTensor = Field(None, description='stiffness tensor ') 
    c_tensor : ElasticTensor = Field(None, description='compliance tensor ') 

class Mechanics2dSummary(MechanicsBase):
      Lm:   float = Field(None,description='2d layer modulus (N/m)')
      Y10:  float = Field(None,description='2d Young\'s modulus Y[10] (N/m)')
      Y01:  float = Field(None,description='2d Young\'s modulus Y[01] (N/m)')
      Gm:   float = Field(None,description='2d Shear modulus G (N/m)')
      V10:  float = Field(None,description='2d Poisson ratio v[10]')
      V01:  float = Field(None,description='2d Poisson ratio v[01]')
      stability:  YesOrNo = Field(None,description='stable or not')
      @classmethod
      def from_file(
          cls: Type[M2S],
	  fname: str='Result.json',
          **kwargs
          ) -> M2S:
          fields =  [
                "s_tensor",
                "c_tensor",
                "Lm",
                "Y01",
                "Y10",
                "Gm",
                "V01",
                "V10",
                "stability",
              ]
          if not os.path.isfile(fname):
             raise RuntimeError('File : %s not exits !'%(fname))
          else:
             d=loadfn(fname,cls=None)
          data={
                "s_tensor" : d['Stiffness_tensor'],
                "c_tensor": d['Compliance_tensor'],
                "Lm": d['Lm'],
                "Y01":d['Y01'],
                "Y10":d['Y10'],
                "Gm": d['Gm'],
                "V01": d['V10'],
                "V10": d['V01'],
                "stability": YesOrNo.yes if d['Stability']=='Stable' else YesOrNo.no
              }
          #dumpfn(cls.schema(),'schema-2d.json')
          return cls(**{k: v for k, v in data.items() if k in fields}, **kwargs)


class Mechanics3D(BaseModel):
      description : Optional[str] = ''

class Mechanics2d(BaseModel):
      summary:  Dict[ApproachAndProperty,Mechanics2dSummary] = Field(None, description='Summary of 2d mechanical properties')
      polar_EV: Dict[ApproachAndProperty,DataFigure] = Field(None, description='Angle dependent Young\'s modulus and Poisson\'s ratio information')
      stress_strain: Dict[ApproachAndProperty,Dict[Direction2d,DataFigure]] = Field(None, description='Stress-strain Curve for different direction')
      meta:  Dict[ApproachAndProperty,Any] = Field(None, description='meta information for mechanical properties calculation')

class Mechanics2dDoc(PropertyDoc):
    """
    An Mechanics  property block
    """
    property_name: ClassVar[str] = "mechanics2d"
    mechanics2d: List[Mechanics2d] = Field([], description='2d Mechanics information')

class Mechanics3DDoc(PropertyDoc):
    """
    An Mechanics  property block
    """
    property_name: ClassVar[str] = "mechanics3d"
    mechanics3d: List[Mechanics3D] = Field([], description='3D Mechanics information')

if __name__=='__main__': 
   ustr=str(uuid.uuid4())
   import numpy as np
   from matvirdkit.model.utils import jsanitize,ValueEnum
   from matvirdkit.model.utils import test_path
   task_dir=os.path.join(test_path(),'alpha-P-R')
   print(task_dir)
   
   data=JFData(description='EV data',
        json_file_name='./dataset.mech2d/m2d-1/EV.json',json_id=None,meta={})
   meta=JFData(description='meta data',
        json_file_name='./dataset.mech2d/m2d-1/meta.json',json_id=None,meta={})
   fig=JFData(description='EV figure',
        file_fmt='png', file_name='./dataset.mech2d/m2d-1/EV.png',file_id=None)
   summary= Mechanics2dSummary.from_file(fname=os.path.join(task_dir,'Result.json'),link=['2312abc'])
   _Mechanics2d = Mechanics2d(**{ 
         'summary':  {'elc_energy':summary},
         'polar_EV': {"elc_energy": DataFigure(data=[data],figure=fig)},
         'meta': {"elc_energy": meta},
        })
   pd=Mechanics2dDoc(created_at=datetime.now(),
      mechanics2d= [_Mechanics2d],
      origins=[
            PropertyOrigin(name='static',task_id='task-110',link=[ustr]),
            PropertyOrigin(name='static',task_id='task-111',link=[ustr]),
            PropertyOrigin(name='static',task_id='task-112',link=[ustr])
           ],
      material_id='m2d-1',
      tags = ['experimental phase','NPR']
 
      )
   dumpfn(jsanitize(pd),'mech.json',indent=4)
   print(jsanitize(pd.dict()))
