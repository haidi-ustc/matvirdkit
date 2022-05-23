import uuid
from datetime import datetime
from typing import ClassVar, Dict, List, Optional, Union, Tuple, TypeVar, Type
from pydantic import BaseModel, Field, validator
from matvirdkit.model.utils import jsanitize,ValueEnum
from matvirdkit.model.properties import PropertyDoc,PropertyOrigin

class LMH(ValueEnum):
      low='low'
      middle='middle'
      high='high'

T = TypeVar("T", bound="ThermoDynamicStability")
P = TypeVar("P", bound="PhononStability")
S = TypeVar("S", bound="StiffnessStability")

class ThermoDynamicStability(BaseModel):
      description : Optional[str] = 'Stability informaion'
      value: LMH = Field(None, description='stability from thermodynamic')
      link: str = Field(None)     
      @classmethod
      def from_dict(
          cls: Type[T],
	  e_f: float,
	  e_abh: float,
	  fields: Optional[List[str]] = None,
          **kwargs
          ) -> T:

          fields = (
              [
                "value",
                "link"
              ]
              if fields is None
              else fields
          )

          if e_f > 0.2 :
             value=LMH.low           
          elif   e_f > 0.2+ e_abh and e_f < 0.2:
             value=LMH.middle
          else:
             value=LMH.high
          data={
                'value': value,
                }
          return cls(**{k: v for k, v in data.items() if k in fields}, **kwargs)

class PhononStability(BaseModel):
      description : Optional[str] = 'Stability informaion'
      value: LMH = Field(None, description='stability from phonons')
      link: str = Field(None)     
      @classmethod
      def from_dict(
          cls: Type[P],
	  max_hessian: float,
	  fields: Optional[List[str]] = None,
          **kwargs
          ) -> P:

          fields = (
              [
                "value",
                "link"
              ]
              if fields is None
              else fields
          )

          if max_hessian <= -0.01 :
             value=LMH.low           
          else:
             value=LMH.high
          data={
                'value': value,
                }
          return cls(**{k: v for k, v in data.items() if k in fields}, **kwargs)

class StiffnessStability(BaseModel):
      description : Optional[str] = 'Stability informaion'
      value: LMH = Field(None, description='stability from stiffness')
      link: str = Field(None)     
      @classmethod
      def from_dict(
          cls: Type[S],
	  min_eig_tensor: float,
	  fields: Optional[List[str]] = None,
          **kwargs
          ) -> S:

          fields = (
              [
                "value",
                "link"
              ]
              if fields is None
              else fields
          )

          if min_eig_tensor <= 0 :
             value=LMH.low           
          else:
             value=LMH.high
          data={
                'value': value,
                }
          return cls(**{k: v for k, v in data.items() if k in fields}, **kwargs)

class Stability(BaseModel):
    """
    An magntic  property block
    """
    stiff_stability: StiffnessStability  = Field(StiffnessStability(), description='stiff stability information')
    thermo_stability: ThermoDynamicStability  = Field(ThermoDynamicStability(), description='thermo stability information')
    phon_stability: PhononStability  = Field(PhononStability(), description='phon stability information')

class StabilityDoc(PropertyDoc):
    """
    An magntic  property block
    """

    property_name: ClassVar[str] = "stability"
    stability: List[Stability] = Field([], description='stiff stability information')

if __name__=='__main__': 
   ustr1=str(uuid.uuid4())
   ustr2=str(uuid.uuid4())
   pd=StabilityDoc(created_at=datetime.now(),
      stability = [ 
           Stability ( 
           #stiff_stability =  StiffnessStability(value='low',description='scan-static',link=ustr1) ,
           stiff_stability =   StiffnessStability.from_dict(min_eig_tensor=0.1),
           thermo_stability=  ThermoDynamicStability.from_dict (e_f=-0.1, e_abh=0.0,description='pbe-static',link=ustr2)
               ) 
                         ] ,
      origins=[
              PropertyOrigin(name='static',task_id='task-112',link=ustr1),
              PropertyOrigin(name='static',task_id='task-113',link=ustr2),
               ],
      material_id='rsb-1',
      tgas = ['high temperature phase']
      )
   print(pd.json())
   print(pd.json())
   from monty.serialization import loadfn,dumpfn
   dumpfn(jsanitize(pd),'stab.json',indent=4)
