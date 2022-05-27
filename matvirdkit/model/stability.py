import uuid
from datetime import datetime
from typing import ClassVar, Dict, List, Optional, Union, Tuple, TypeVar, Type
from pydantic import BaseModel, Field, validator
from matvirdkit.model.utils import jsanitize,ValueEnum
from matvirdkit.model.properties import PropertyDoc,PropertyOrigin
from matvirdkit.model.common import MatvirdBase

class LMH(ValueEnum):
      low='low'
      middle='middle'
      high='high'

T = TypeVar("T", bound="ThermoDynamicStability")
P = TypeVar("P", bound="PhononStability")
S = TypeVar("S", bound="StiffnessStability")

class ThermoDynamicStability(MatvirdBase):
      value: LMH = Field(None, description='stability from thermodynamic')
      @classmethod
      def from_key(
          cls: Type[T],
	  formation_energy_per_atom: float,
	  energy_above_hull: float,
	  fields: Optional[List[str]] = None,
          **kwargs
          ) -> T:

          fields = (
              [
                "value",
              ]
              if fields is None
              else fields
          )

          if formation_energy_per_atom > 0.2 :
             value=LMH.low           
          elif   formation_energy_per_atom > 0.2+ energy_above_hull and formation_energy_per_atom < 0.2:
             value=LMH.middle
          else:
             value=LMH.high
          data={
                'value': value,
                }
          return cls(**{k: v for k, v in data.items() if k in fields}, **kwargs)

class PhononStability(MatvirdBase):
      value: LMH = Field(None, description='stability from phonons')
      @classmethod
      def from_key(
          cls: Type[P],
	  max_hessian: float,
	  fields: Optional[List[str]] = None,
          **kwargs
          ) -> P:

          fields = (
              [
                "value",
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

class StiffnessStability(MatvirdBase):
      value: LMH = Field(None, description='stability from stiffness')
      @classmethod
      def from_key(
          cls: Type[S],
	  min_eig_tensor: float,
	  fields: Optional[List[str]] = None,
          **kwargs
          ) -> S:

          fields = (
              [
                "value",
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


class StabilityDoc(PropertyDoc):
    """
    Stability  property block
    """
    property_name: ClassVar[str] = "stability"
    stiff_stability: List[StiffnessStability]  = Field([StiffnessStability()], description='stiff stability information')
    thermo_stability: List[ThermoDynamicStability]  = Field([ThermoDynamicStability()], description='thermo stability information')
    phonon_stability: List[PhononStability]  = Field([PhononStability()], description='phon stability information')

if __name__=='__main__': 
   ustr1=str(uuid.uuid4())
   ustr2=str(uuid.uuid4())
   pd=StabilityDoc(created_at=datetime.now(),
           stiff_stability =  [  StiffnessStability.from_key(min_eig_tensor=0.1) ],
           thermo_stability=  [ ThermoDynamicStability.from_key (formation_energy_per_atom=-0.1, energy_above_hull=0.0,description='pbe-static',link= [ustr2 ]) ],
      origins=[
              PropertyOrigin(name='static',task_id='task-112',link=[ustr1]),
              PropertyOrigin(name='static',task_id='task-113',link=[ustr2]),
               ],
      material_id='rsb-1',
      tags = ['high temperature phase']
      )
   print(pd.json())
   from monty.serialization import loadfn,dumpfn
   dumpfn(jsanitize(pd),'stab.json',indent=4)
