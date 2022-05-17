import os
import uuid
from datetime import datetime
from typing import ClassVar, Dict, List, Optional, Union, Tuple,TypeVar,Type , Any
from pydantic import BaseModel, Field
from monty.serialization import loadfn,dumpfn
from matvirdkit.model.properties import PropertyDoc,PropertyOrigin
from matvirdkit.model.utils import VoigtVector,Matrix3D,Vector3D,YesOrNo
from matvirdkit.model.utils import ElasticTensor
from matvirdkit.model.common import DataFigure,JFData

M2 = TypeVar("M2", bound="Mechanics2D")
M3 = TypeVar("M3", bound="Mechanics3D")

class Mechanics(BaseModel):
    description : Optional[str] = 'mechanical information'
    link: str = Field(None)     
    s_tensor : ElasticTensor = Field(..., description='stiffness tensor ') 
    c_tensor : ElasticTensor = Field(..., description='compliance tensor ') 

class Mechanics3D(Mechanics):
      stability:  YesOrNo = Field(...,description='stable or not')

class Mechanics2D(Mechanics):
      Lm:   float = Field(...,description='2D layer modulus (N/m)')
      Y10:  float = Field(...,description='2D Young\'s modulus Y[10] (N/m)')
      Y01:  float = Field(...,description='2D Young\'s modulus Y[01] (N/m)')
      Gm:   float = Field(...,description='2D Shear modulus G (N/m)')
      V10:  float = Field(...,description='2D Poisson ratio v[10]')
      V01:  float = Field(...,description='2D Poisson ratio v[01]')
      stability:  YesOrNo = Field(...,description='stable or not')
      @classmethod
      def from_file(
          cls: Type[M2],
	  fname: str='Result.json',
          **kwargs
          ) -> M2:
          fields =  [
                "link",
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
             d=loadfn(fname)
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

class Mechanics2DDoc(PropertyDoc):
    """
    An Mechanics  property block
    """
    property_name: ClassVar[str] = "mechanics2d"
    mechanics2d: List[Mechanics3D] = Field(None, description='2D Mechanics information')
    polar_EV: List[DataFigure] = Field(None, description='Angle dependent Young\'s modulus and Poisson\'s ratio information')
    meta:  Dict[str,Any] = Field(None, description='meta information for mechanical properties calculation')

class Mechanics3DDoc(PropertyDoc):
    """
    An Mechanics  property block
    """
    property_name: ClassVar[str] = "mechanics3d"
    mechanics2d: List[Mechanics2D] = Field(None, description='2D Mechanics information')
    meta:  Dict[str,Any] = Field(None, description='meta information for mechanical properties calculation')

if __name__=='__main__': 
   ustr=str(uuid.uuid4())
   data=JFData(description='EV data',
        json_file_name='./dataset.mech2d/m2d-1/EV.json',json_id=None,meta={})
   fig=JFData(description='EV figure',
        file_fmt='png', file_name='./dataset.mech2d/m2d-1/EV.png',file_id=None)
   pd=Mechanics2DDoc(created_at=datetime.now(),
      mechanics2d=[
               Mechanics2D.from_file(fname='tests/Result.json',link=ustr)
                  ],
      polar_EV = [ 
               DataFigure(data=data,figure=fig)
                ],
      origins=[
            PropertyOrigin(name='static',task_id='task-110',link=ustr),
            PropertyOrigin(name='static',task_id='task-111',link=ustr),
            PropertyOrigin(name='static',task_id='task-112',link=ustr)
           ],
      material_id='m2d-1',
      tags = ['experimental phase','NPR']
      )
   print(pd.json())
   from monty.serialization import loadfn,dumpfn
   from matvirdkit.model.utils import jsanitize,ValueEnum
   dumpfn(jsanitize(pd),'t.json',indent=4)
