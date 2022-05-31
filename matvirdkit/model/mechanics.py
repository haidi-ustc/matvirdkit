import os
import uuid
from datetime import datetime
from typing import ClassVar, Dict, List, Optional, Union, Tuple,TypeVar,Type , Any
from pydantic import BaseModel, Field
from monty.serialization import loadfn,dumpfn
from matvirdkit.model.provenance import LocalProvenance,GlobalProvenance,Origin
from matvirdkit.model.utils import VoigtVector,Matrix3D,Vector3D,YesOrNo
from matvirdkit.model.utils import ElasticTensor, ValueEnum
from matvirdkit.model.common import DataFigure,JFData,MatvirdBase

M2S = TypeVar("M2", bound="Mechanics2dSummary")
M3S = TypeVar("M3", bound="Mechanics3dSummary")

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


class Mechanics3d(BaseModel):
      description : Optional[str] = ''

class Mechanics3dSummary(MechanicsBase):
      pass

class Elc3nd2d(BaseModel):
      summary: Dict = Field({})
      polar_EV: Dict = Field({})
      meta: Dict[str,Any] = Field({})
     
class Elc2nd2d(BaseModel):
      summary:  Mechanics2dSummary = Field(None, description='Summary of 2d mechanical properties')
      polar_EV: DataFigure = Field(None, description='Angle dependent Young\'s modulus and Poisson\'s ratio information')
      # e.g.   {'Def_2': DataFigure(data=[data],figure=figure)}
      deformations: Dict[str,DataFigure] = Field(None, description='Used to save the deformation information and corresponding figure')
      meta: Dict[str,Any] = Field({})
     
class EOS(BaseModel):
      minmum: float = Field(None)
      equilibrium: float = Field(None)  
      data:  DataFigure = Field(None)

class StressStrain(BaseModel):
      deformations: Dict[Direction2d,DataFigure] =  Field(None, description='Used to save the deformation information and corresponding figure')
      meta: Dict[str,Any] = Field({})

class Mechanics2d(MatvirdBase):
      provenance: Dict[str,LocalProvenance] = Field({}, description="Property provenance")
      elc2nd_stress: Elc2nd2d = Field (None, description='2nd elastic constant calculation info obtained via stress method')
      elc2nd_energy: Elc2nd2d =  Field(None, description='2nd elastic constant calculation info obtained via energy method')
      elc3nd_stress: Elc3nd2d = Field (None, description='2nd elastic constant calculation info obtained via stress method')
      stress_strain: StressStrain = Field(None, description='Stress-strain Curve for different direction')
      eos: Dict[str,EOS] = Field(None, description='EOS Curve for different direction')

class Mechanics2dDoc(BaseModel):
    """
    An Mechanics  property block
    """
    property_name: ClassVar[str] = "mechanics2d"
    mechanics2d: Dict[str,Mechanics2d] = Field({}, description='2d Mechanics information')

class Mechanics3dDoc(BaseModel):
    """
    An Mechanics  property block
    """
    property_name: ClassVar[str] = "mechanics3d"
    mechanics3d: List[Mechanics3d] = Field([], description='3d Mechanics information')

if __name__=='__main__': 
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
   data_def=JFData(description='Def data',
        json_file_name='./dataset.mech2d/m2d-1/elc_energy/Def_1/Def_1_Energy.dat',json_id=None,meta={})
   fig_def=JFData(description='Def figure',
        file_fmt='png', file_name='./dataset.mech2d/m2d-1/elc_energy/Def_1/Def_1_Energy_Strain.png',file_id=None)
   

   summary= Mechanics2dSummary.from_file(fname=os.path.join(task_dir,'Result.json'))
   _elc2nd2d = Elc2nd2d(**{ 
         'summary':  summary,
         'polar_EV':  DataFigure(data=[data],figure=fig),
         'deformations': {'Def_1':DataFigure(data=[data_def],figure=fig_def)}
        })
   _mechanics2d_energy = Mechanics2d(elc2nd_energy = _elc2nd2d)
   _mechanics2d_stress = Mechanics2d(elc2nd_stress = _elc2nd2d)
   origins=[
            Origin(name='static',task_id='task-110'),
            Origin(name='static',task_id='task-111'),
            Origin(name='static',task_id='task-112')
           ]
   provenance=LocalProvenance(origins=origins,
                              created_at=datetime.now())
   pd=Mechanics2dDoc(
      mechanics2d= {'PBE':_mechanics2d_energy, 'HSE': _mechanics2d_stress},
      provenance={'PBE':provenance}
      )
   dumpfn(jsanitize(pd),'mech.json',indent=4)
   print(jsanitize(pd.dict()))
