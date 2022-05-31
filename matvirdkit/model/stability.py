import uuid
from datetime import datetime
from typing import ClassVar, Dict, List, Optional, Union, Tuple, TypeVar, Type
from pydantic import BaseModel, Field, validator
from matvirdkit.model.utils import jsanitize,ValueEnum
from matvirdkit.model.provenance import LocalProvenance,Origin
from matvirdkit.model.common import MatvirdBase

T = TypeVar("T", bound="ThermoDynamicStability")
P = TypeVar("P", bound="PhononStability")
S = TypeVar("S", bound="StiffnessStability")

class StabilityLevel(ValueEnum):
      low='low'
      middle='middle'
      high='high'

class ThermoDynamicStability(MatvirdBase):
      value: StabilityLevel = Field(None, description='stability from thermodynamic')
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
             value=StabilityLevel.low           
          elif   formation_energy_per_atom > 0.2+ energy_above_hull and formation_energy_per_atom < 0.2:
             value=StabilityLevel.middle
          else:
             value=StabilityLevel.high
          data={
                'value': value,
                }
          return cls(**{k: v for k, v in data.items() if k in fields}, **kwargs)

class PhononStability(MatvirdBase):
      value: StabilityLevel = Field(None, description='stability from phonons')
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
             value=StabilityLevel.low           
          else:
             value=StabilityLevel.high
          data={
                'value': value,
                }
          return cls(**{k: v for k, v in data.items() if k in fields}, **kwargs)

class StiffnessStability(MatvirdBase):
      value: StabilityLevel = Field(None, description='stability from stiffness')
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
             value=StabilityLevel.low           
          else:
             value=StabilityLevel.high
          data={
                'value': value,
                }
          return cls(**{k: v for k, v in data.items() if k in fields}, **kwargs)


class Stability(BaseModel):
    provenance: Dict[str,LocalProvenance] = Field({}, description="Property provenance")
    stiff_stability: StiffnessStability  = Field(StiffnessStability(), description='stiff stability information')
    thermo_stability: ThermoDynamicStability  = Field(ThermoDynamicStability(), description='thermo stability information')
    phonon_stability: PhononStability  = Field(PhononStability(), description='phon stability information')
      
class StabilityDoc(BaseModel):
    """
    Stability  property block
    """
    property_name: ClassVar[str] = "stability"
    stability: Dict[str,Stability] = Field({}, description='2d Mechanics information')

if __name__=='__main__': 
   from monty.serialization import loadfn,dumpfn
   origins=[
            Origin(name='pbe-static',task_id='task-112'),
            Origin(name='pbe-static-d2',task_id='task-112'),
            ]
   provenance=LocalProvenance(origins=origins,
                              created_at=datetime.now(),
                              tags = ['high temperature phase'])
   stability = Stability(
           stiff_stability =  StiffnessStability.from_key(min_eig_tensor=0.1) ,
           thermo_stability=  ThermoDynamicStability.from_key (formation_energy_per_atom=-0.1, energy_above_hull=0.0,description='pbe-static') ,
      provenance = {"stiff_stability": provenance} 
               )
   pd=StabilityDoc(
      stability  = {"PBE": stability }
      )
   print(pd.json())
   dumpfn(jsanitize(pd),'stab.json',indent=4)
