""" Core definition of a VASP Task Document """
import os
import shutil
from pprint import pprint
from datetime import datetime
from functools import lru_cache, partial
from typing import Any, ClassVar, Dict, List, Optional, Union,Sequence,Tuple
from monty.serialization import loadfn,dumpfn
from pydantic import BaseModel, Field, validator
from pymatgen.analysis.magnetism import CollinearMagneticStructureAnalyzer, Ordering
from pymatgen.analysis.structure_analyzer import oxide_type
from pymatgen.core import Composition, Structure
from pymatgen.entries.computed_entries import ComputedEntry, ComputedStructureEntry
from pymatgen.io.vasp import VaspInput,Vasprun,Outcar,Oszicar,Elfcar,Locpot,Chgcar,Procar,Poscar

from matvirdkit import log
from matvirdkit.model.utils import Matrix3D, Vector3D,ValueEnum
from matvirdkit.model.structure import StructureMetadata,StructureMP
from matvirdkit.model.vasp.calc_types.enums import CalcType, RunType, TaskType 
from matvirdkit.model.vasp.calc_types.utils import calc_type, run_type,  task_type
from matvirdkit.builder.vasp.outputs import VaspOutputs
from matvirdkit.model.common import JFData
from matvirdkit.model.utils import transfer_file,sha1encode,task_tag

class Status(ValueEnum):
    """
    VASP Calculation State
    """

    SUCCESS = "successful"
    FAILED = "failed"


class InputSummary(BaseModel):
    """
    Summary of inputs for a VASP calculation
    """

    structure: StructureMP = Field(None, description="The input structure object")
    parameters: Dict = Field(
        {},
        description="Input parameters from VASPRUN for the last calculation in the series",
    )
    pseudo_potentials: Dict = Field(
        {}, description="Summary of the pseudopotentials used in this calculation"
    )

    potcar_spec: List[Dict] = Field(
        [], description="Potcar specification as a title and hash"
    )

    is_hubbard: bool = Field(False, description="Is this a Hubbard +U calculation.")

    hubbards: Dict = Field({}, description="The hubbard parameters used.")

class InputData(BaseModel) :
    INCAR: Dict = Field({},description="INCAR file")
    POSCAR: Dict = Field({},description="POSCAR file")
    POTCAR: Dict = Field({},description="POTCAR file")
    KPOINTS: Dict = Field({},description="KPOINTS file")
    @classmethod
    def from_directory(cls,
                   task_dir:str) -> 'InputData':
         vi=VaspInput.from_directory(task_dir)
         return cls(**vi.as_dict())
  
class OutputData(BaseModel):
    VASPRUN: JFData = Field(JFData(),description="vasprun file, json_id, file_id")
    OSZICAR: JFData = Field(JFData(),description="OSZICAR file, json_id, file_id")
    OUTCAR:  JFData = Field(JFData(),description="OUTCAR file, json_id, file_id")
    CONTCAR: JFData = Field(JFData(),description="CONTCAR file, json_id, file_id")
    PROCAR:  JFData = Field(JFData(),description="PROCAR file, json_id, file_id")
    ELFCAR:  JFData = Field(JFData(),description="ELFCAR file, json_id, file_id")
    LOCPOT:  JFData = Field(JFData(),description="LOCPOT file, json_id, file_id")
    @classmethod
    def from_directory(cls,
                   task_dir:str,
                   dst_dir:str,
                   fields: Optional[List[str]] = None,**kwargs) -> 'OutputData':
        fields = (
            [
                "VASPRUN",
                "OSZICAR",
                "OUTCAR",
                "CONTCAR"
            ]
            if fields is None
            else fields
        )
       
        #d={field:{} for field in fields}
        #foutputs=[field for field in fields if field != 'VASPRUN']
        #if 'VASPRUN' in fields:
        #   foutputs.append('vasprun.xml')
        vout = VaspOutputs(task_dir,fields,**kwargs)
        #print('ok') 
        d=vout.parse_output(dst_path = dst_dir, save_raw = True)
        #print(d.keys())
        #pprint(d)
        #print('**'*20)
        return cls(**d)


class OutputSummary(BaseModel):
    """
    Summary of the outputs for a VASP calculation
    """

    structure: Structure = Field(None, description="The output structure object")
    energy: float = Field(
        None, description="The final total DFT energy for the last calculation"
    )
    energy_per_atom: float = Field(
        None, description="The final DFT energy per atom for the last calculation"
    )
    eigen_band: Tuple[float,float,float,bool] = Field(None, description="The DFT eigenvalue and bandgap for the last calculation")
    forces: List[Vector3D] = Field(
        [], description="Forces on atoms from the last calculation"
    )
    stress: Matrix3D = Field(
        [], description="Stress on the unitcell from the last calculation"
    )

class RunStatistics(BaseModel):
    """
    Summary of the Run statistics for a VASP calculation
    """

    average_memory: float = Field(None, description="The average memory used in kb")
    max_memory: float = Field(None, description="The maximum memory used in kb")
    elapsed_time: float = Field(None, description="The real time elapsed in seconds")
    system_time: float = Field(None, description="The system CPU time in seconds")
    user_time: float = Field(
        None, description="The user CPU time spent by VASP in seconds"
    )
    total_time: float = Field(
        None, description="The total CPU time for this calculation"
    )
    cores: Union[int, str] = Field(
        None,
        description="The number of cores used by VASP (some clusters print `mpi-ranks` here)",
    )
    @classmethod
    def from_vaspout_dict(cls, d : Dict ) -> 'RunStatistics':
        ret={}
        #print(d)
        ret['average_memory']=d['Average memory used (kb)']
        ret['max_memory']=d['Maximum memory used (kb)']
        ret['elapsed_time']=d['Elapsed time (sec)']
        ret['user_time']=d['User time (sec)']
        ret['system_time']=d['System time (sec)']
        ret['total_time']=d['Total CPU time used (sec)']
        ret['cores']=d['cores']
        return cls(**ret)


class TaskDocument(StructureMetadata):
    """
    Definition of VASP Task Document
    """

    label: str = Field('', description='Label of a task')
    description: str = Field('', description='Description of a task')
    dir_name: str = Field('', description="The directory for this VASP task")
    run_stats: Dict[str, RunStatistics] = Field(
        {},
        description="Summary of runtime statisitics for each calcualtion in this task",
    )
    completed_at: datetime = Field(
        None, description="Timestamp for when this task was completed"
    )
    last_updated: datetime = Field(
        None, description="Timestamp for this task document was last updateed"
    )

    is_valid: bool = Field(
        True, description="Whether this task document passed validation or not"
    )

    input: InputSummary = Field(InputSummary())
    output: OutputSummary = Field(OutputSummary())

    state: Status = Field(None, description="State of this calculation")

    orig_inputs: InputData = Field(
        {}, description="raw data of the original VASP inputs"
    )
    #orig_inputs: Dict[str, Any] = Field(
    #    {}, description="Summary of the original VASP inputs"
    #)
    orig_outputs: OutputData = Field(
        {}, description="raw data of the original VASP outputs"
    )
    task_id: str = Field(None, description="the Task ID For this document")
    short_id: str =  Field(None, description="the short Task ID For this document")
    tags: List[str] = Field([], description="Metadata tags for this task document")

    calcs_reversed: List[Dict] = Field(
        [], description="The 'raw' calculation docs used to assembled this task"
    )

    @property
    def run_type(self) -> RunType:
        return run_type(self.input.parameters)

    @property
    def task_type(self):
        d={}
        d['incar']=self.input.parameters
        d['kpoints']=self.orig_inputs.KPOINTS
        d['poscar']=self.orig_inputs.POSCAR
        d['potcar']=self.orig_inputs.POTCAR
        return task_type(d)

    @property
    def calc_type(self):
        d={}
        d['incar']=self.input.parameters
        d['kpoints']=self.orig_inputs.KPOINTS
        d['poscar']=self.orig_inputs.POSCAR
        d['potcar']=self.orig_inputs.POTCAR
        return calc_type(d, self.input.parameters)

    @property
    def entry(self) -> ComputedEntry:
        """ Turns a Task Doc into a ComputedEntry"""
        entry_dict = {
            "correction": 0.0,
            "entry_id": self.task_id,
            "composition": self.output.structure.composition,
            "energy": self.output.energy,
            "parameters": {
                "potcar_spec": self.input.potcar_spec,
                "is_hubbard": self.input.is_hubbard,
                "hubbards": self.input.hubbards,
                # This is done to be compatible with MontyEncoder for the ComputedEntry
                "run_type": str(self.run_type),
            },
            "data": {
                "oxide_type": oxide_type(self.output.structure),
                "aspherical": self.input.parameters.get("LASPH", True),
                "last_updated": self.last_updated,
            },
        }

        return ComputedEntry.from_dict(entry_dict)

    @property
    def structure_entry(self) -> ComputedStructureEntry:
        """ Turns a Task Doc into a ComputedStructureEntry"""
        entry_dict = self.entry.as_dict()
        entry_dict["structure"] = self.output.structure

        return ComputedStructureEntry.from_dict(entry_dict)

    @classmethod
    def from_directory(
        cls,
        task_id: str,
        task_dir: str,
        dst_dir: str,
        f_inputs : List[str]= [],
        f_outputs :  List[str] = [],
        **kwargs
    ) -> "TaskDocument":
       # if task_tag(task_dir,status='check'):
       #    tag=loadfn(os.path.join(task_dir,'tag.json'))
       #    f_task=os.path.join(tag['path'],'task.json')
       #    if os.path.isfile(f_task):
       #       _dtask=loadfn(os.path.join(tag['path'],'task.json'),cls=None)
       #       _dtask.update(kwargs)
       #       log.info('Skip parsing !!!')
       #       return cls(**_dtask)
       #    else:
       #       pass

        f_inputs = f_inputs if f_inputs else ['INCAR','KPOINTS','POTCAR','POSCAR'],
        f_outputs = f_outputs if f_outputs else  ['vasprun.xml','OSZICAR','OUTCAR','CONTCAR']
        
        try:
           vr=Vasprun(os.path.join(task_dir,'vasprun.xml'))
        except:
           raise RuntimeError('Bad vasprun.xml')
        try:
           out=Outcar(os.path.join(task_dir,'OUTCAR'))
        except:
           out={}
        try:
           if os.path.isfile(os.path.join(task_dir,'CONTCAR') ):
              contcar=Poscar.from_file(os.path.join(task_dir,'CONTCAR'))
           else:
              contcar=Poscar(vr.final_structure,comment='from vasprun.xml')
        except:
           raise RuntimeError('Bad CONTCAR')
        d={}
        if vr.converged:
           status=Status.SUCCESS
        else:
           status=Status.FAILED
        potcar_symbols=vr.potcar_symbols
        pseudo_potentials={'functional':potcar_symbols[0].split()[0].split('_')[1]      ,
               'pot_type': potcar_symbols[0].split()[0].split('_')[0]  ,
               'labels': [ potcar_symbol.split()[1]  for potcar_symbol in potcar_symbols]
        }       
        input_summary={
          "structure": vr.initial_structure.as_dict(),
          "parameters": vr.parameters, 
          "pseudo_potentials": pseudo_potentials,
          "potcar_spec":  vr.potcar_spec,
          "is_hubbard": vr.is_hubbard,
          "hubbards":vr.hubbards}
        output_summary={
          "structure":vr.final_structure.as_dict(),
          "energy":vr.final_energy,
          "energy_per_atom":vr.final_energy/len(vr.final_structure),
          "eigen_band": vr.eigenvalue_band_properties,
          "forces":vr.as_dict()['output']['ionic_steps'][-1]['forces'],
          "stress":vr.as_dict()['output']['ionic_steps'][-1]['stress'],
         }
        orig_inputs=InputData.from_directory(task_dir)
        try:
            run_statistics=RunStatistics.from_vaspout_dict(out.as_dict()['run_stats'])
        except:
            run_statistics=RunStatistics()
           
        structure_meta=StructureMetadata.from_structure(vr.initial_structure)
        orig_outputs=OutputData.from_directory(task_dir=task_dir, dst_dir=dst_dir)
        #print('='*20)
        #print(structure_meta.dict())
        #print('='*20)

        d={
         "dir_name": task_dir,
         "run_stats": {'standard':run_statistics},
         "task_id": task_id,
         "state": status,
         "input": input_summary,
         "output": output_summary,
         "orig_inputs": orig_inputs,
         "orig_outputs": orig_outputs,
         "last_updated": datetime.now()
         }
        d.update(structure_meta)
        d.update(kwargs)
    
        return cls(**d)
           
if __name__== '__main__':
   import os
   from matvirdkit.model.utils import jsanitize,ValueEnum
   from matvirdkit.model.utils import test_path,create_path
   from monty.serialization import loadfn,dumpfn
   from uuid import uuid4
   out_dir=os.path.join('tasks',str(uuid4()))
   print('we create dir: %s'%(out_dir))
   create_path(out_dir)
   relax_dir=os.path.join(test_path('..'),'relax')
   td=TaskDocument.from_directory(task_id='t-1',task_dir=relax_dir,dst_dir=out_dir)
   td=jsanitize(td)
   encode=sha1encode(td['input'])
   encode_dir=os.path.join('tasks',encode)
   if os.path.isdir(encode_dir):
      print('we delete dir: %s'%(out_dir))
      shutil.rmtree(out_dir)
   else:
      print('we rename dir: %s to %s'%(out_dir,encode_dir))
      shutil.move(out_dir,encode_dir)
      info={'path':os.path.abspath(out_dir.replace(out_dir,encode_dir)),
             'encode': encode}
      dumpfn(td,os.path.join(encode_dir,'task.json'),indent=4)
      task_tag(relax_dir,status='write',info=info)
 
   print('finished!')

