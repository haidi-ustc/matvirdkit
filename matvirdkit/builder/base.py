import os
import inspect
from datetime import datetime
from hashlib import sha1
from monty.json import MSONable

from abc import ABCMeta, abstractmethod
from typing import Dict, List, Tuple, Optional, Union, Iterator, Set, Sequence, Iterable
from pymatgen.core import Structure
from matvirdkit import log,REPO_DIR 
from matvirdkit.model.utils import jsanitize,create_path
from matvirdkit.model.electronic import EMC,Bandgap,Mobility,Workfunction,ElectronicStructureDoc
from matvirdkit.model.properties import PropertyOrigin
from matvirdkit.model.thermo import Thermo,ThermoDoc
from matvirdkit.model.xrd import XRD,XRDDoc
from matvirdkit.model.stability import ThermoDynamicStability,PhononStability,StiffnessStability,StabilityDoc
from matvirdkit.model.common import Meta,MetaDoc,Source,SourceDoc,Task,TaskDoc
from matvirdkit.model.magnetism import Magnetism,MagnetismDoc
from matvirdkit.model.structure import StructureMatvird
from matvirdkit.model.mechanics import Mechanics2d,Mechanics2dDoc
from matvirdkit.builder.readstructure import structure_from_file
from matvirdkit.builder.task import VaspTask
from matvirdkit.builder.mechanics import get_mechanics2d_info

__version__ = "0.1.0"
__author__ = "Matvird"

def function_name():
    return inspect.stack()[1][3]

supported_dataset = ['bms', 'mech2d', 'npr2d', 'penta',  'rashba'
                     'carbon2d', 'carbon3d', 'raman' ]
links = ['thermo', 'emcs', 'bandgaps', 'mobilities', 'workfunctions', 'magnetism', 'xrd',  'dos', 'stiff_stability', 'phonon_stability', 'thermo_stability', 'customer', 'raman', 'polar']

class Builder(metaclass=ABCMeta):
    def __init__(self, material_id : str, dataset :str , dimension = None, root_dir=None ):
        self.material_id = material_id
        assert dataset in supported_dataset
        self.root_dir =  root_dir if root_dir else REPO_DIR
        self.work_dir =  os.path.join(self.root_dir,dataset,material_id)
        if os.path.isdir(self.work_dir):
           pass
        else:
           create_path(self.work_dir,backup=False)
        self.dimension = dimension

        self._registered_doc=[]
        self._structure = None
        self._thermo      = []  #thermo
        self._electronicstructure  = []  #
        self._mechanics    = []
        self._mechanics2d  = []
        self._mechanics2d_origins = []
        
        self._stability    = []
        self._thermo_stability = []
        self._stiff_stability = []
        self._phonon_stability    = []

        self._magnetism    = []
        self._xrd          = []
        self._raman        = []
        self._polar        = []
        self._sources      = []
        self._provenance   = []
        self._meta         = []

        self._customer     = {}
        self._origins      = {}

        self._tasks = []
        self._properties   = {}

        self._emcs =  []
        self._bandgaps =  []
        self._mobilities =  []
        self._workfunctions =  []
        self._doses=  []
        self._bands=  []

        self._StructureDoc   = {}
        self._ThermoDoc   = {}
        self._ElectronicStructureDoc = {}
        self._XRDDoc = {}
        self._RamanDoc = {}
        self._SourceDoc = {}
        self._MagnetismDoc={}
        self._MetaDoc = {}
        self._StabilityDoc = {}
        self._TaskDoc = {}
        self._Mechanics2dDoc = {}


    @property 
    def registered_doc(self) -> Dict:
        return self._registered_doc

    def registery_doc(self,value) -> None:
        if value not in self._registered_doc:
           self._registered_doc.append(value)

    def get_doc(self) -> Dict:
        return { 
                 "@module":    self.__class__.__module__,
                 "@class":     self.__class__.__name__,
                 "material_id":self.material_id,
                 'structure':  self.get_StructureDoc(),
                 "properties": self.get_PropertiesDoc(),
                 "tasks":      self.get_TaskDoc(),
                 "generated":  __author__,
                 "version":    __version__
               }

    def get_PropertiesDoc(self) -> Dict:
        return self._properties
    
    def update_properties(self, key : str, val : Dict):
        self._properties[key] = val


    def set_structure(self, fname='POSCAR') -> None:
        self._structure = structure_from_file(fname)

    def get_structure(self,**kwargs) -> Structure:
        return self._structure

    def set_StructureDoc(self,**kwargs) -> Union[Dict , StructureMatvird]:
        self._StructureDoc=StructureMatvird.from_structure(
                           dimension=self.dimension,
                           structure=self._structure,
                           **kwargs)

    def get_StructureDoc(self,**kwargs) -> Union[Dict , StructureMatvird]:
        return self._StructureDoc

    def set_origins(self,key,task_id,name='',link=[]) -> None:
        if  key in self._origins.keys():
             self._origins[key].append(PropertyOrigin(name=name,task_id=task_id,link=link))
        else:
             self._origins[key]=[PropertyOrigin(name=name,task_id=task_id,link=link)]
    def get_origins(self, key : Union[str,List]) -> List:
        if isinstance(key,str):
           if key in self._origins.keys():
              return self._origins[key]
           else:
              return []
        elif isinstance(key,list):
             ret=[] 
             for _key in key:
                 if _key in self._origins.keys():
                    ret.extend( self._origins[_key] )
                 else:
                    pass
             return ret
        else:
            return []
 
    def set_thermo(self,formation_energy_per_atom=None,
                         energy_above_hull=None,
                         energy_per_atom=None,
                         **kwargs) -> None:
        self._thermo.append( Thermo(formation_energy_per_atom=formation_energy_per_atom,
                                     energy_above_hull=energy_above_hull,
                                     energy_per_atom=energy_per_atom,**kwargs))

    def get_thermo(self) -> Dict:
         return self._thermo
    
    def set_ThermoDoc(self, created_at = None, **kwargs) -> None:
        created_at = created_at if created_at else datetime.now()  
        self._ThermoDoc=ThermoDoc(created_at = created_at ,
                         thermo = self.get_thermo(),
                         origins = self.get_origins('thermo'),
                         material_id = self.material_id,
                         **kwargs)
        self.registery_doc(function_name().split('_')[-1])

    def get_ThermoDoc(self) -> Union[Dict , ThermoDoc]:
        return self._ThermoDoc

    def set_emcs(self,value,k_loc,b_loc,**kwargs) -> None:
        self._emcs.append( EMC(k_loc=k_loc,b_loc=b_loc,value=value,**kwargs))

    def get_emcs(self) -> Dict:
        log.info('Number of emcs: %d'%(len(self._emcs)))
        return self._emcs
    
    def set_bandgaps(self,value,direct,**kwargs) -> None:
        self._bandgaps.append(Bandgap(value=value,direct=direct,**kwargs))

    def get_bandgaps(self) -> Dict:
        log.info('Number of bandgaps: %d'%(len(self._bandgaps)))
        return self._bandgaps

    def set_bandgaps(self,value,direct,**kwargs) -> None:
        self._bandgaps.append(Bandgap(value=value,direct=direct,**kwargs))
        
    def set_mobilities(self,value,k_loc,b_loc,direction,**kwargs) -> None:
        self._mobilities.append(Mobility(k_loc=k_loc,b_loc=b_loc,value=value,direction=direction,**kwargs))
 
    def get_mobilites(self) -> Dict:
        log.info('Number of mobilites: %d'%(len(self._mobilites)))
        return self._mobilites

    def set_workfunctions(self,value,**kwargs) -> None:
        self._workfunctions.append(Workfunction(value=value,**karg))

    def get_workfunctions(self) -> Dict:
        log.info('Number of workfunctions: %d'%(len(self._mobilites)))
        return self._workfunctions

    def set_ElectronicStructureDoc(self,  created_at, **kwargs) -> None: 
        created_at = created_at if created_at else datetime.now()
        self._ElectronicStructureDoc=ElectronicStructureDoc(created_at = created_at ,
                         material_id = self.material_id,
                         origins  = self.get_origins(['eletronicstructure',
                                                      'emcs',
                                                      
                                                      ]),
                         bandgaps = self.get_bandgaps(),
                         emcs     = self.get_emcs(),
                         mobilities  = self.get_mobilities(),
                         workfunctions  = self.get_workfunctions(),
                         doses    = self.get_doses(),
                         bandstructures = self.get_bandstructures(),
                         **kwargs)
        self.registery_doc(function_name().split('_')[-1])
                           
    def get_ElectronicStructureDoc(self) -> Union[Dict ,ElectronicStructureDoc]:
        return self._ElectronicStructureDoc

    def set_mechanics2d_info(self,task_dir,prop_dir='mechanics',lprops=None , code= 'vasp'):
       # info --- origin
        _mechanics2d_info = get_mechanics2d_info(task_dir, 
                                        prop_dir=os.path.join(self.work_dir,prop_dir),
                                        lprops = lprops,
                                        code = code)

        self._mechanics2d_info.append( _mechanics2d_info)
        # Mechanics2d(**_mechanics2d_info[0]) )
   
    def get_mechanics2d_info(self): 
        return self._mechanics2d_info
                                        
    def set_Mechanics2dDoc(self, created_at = None, **kwargs) -> None:
        created_at = created_at if created_at else datetime.now()
        self._Mechanics2dDoc=Mechanics2dDoc(created_at = created_at ,
                         material_id = self.material_id,
                         mechanics2d = self.get_mechanics2d(),
                         origins = self.get_mechanics2d_origins(),
                         **kwargs)
        self.registery_doc(function_name().split('_')[-1])
    
    def get_Mechanics2dDoc(self):
        return self._Mechanics2dDoc

    def set_magnetism(self,magneatic_moment = None, magnetic_order = None,
                           exchange_energy = None, magnetic_anisotropy= {},
                           **kwargs) -> None:
        self._magnetism.append(Magnetism(magneatic_moment = magneatic_moment ,
                                         magnetic_order = magnetic_order ,
                                         exchange_energy = exchange_energy ,
                                         magnetic_anisotropy = magnetic_anisotropy,
                                         **kwargs))

    def get_magnetism(self) -> List:
        return self._magnetism

    def set_MagnetismDoc(self,  created_at = None, **kwargs) -> None:
        created_at = created_at if created_at else datetime.now()
        self._MagnetismDoc=MagnetismDoc(created_at = created_at ,
                         material_id = self.material_id,
                         magnetism = self.get_magnetism(),
                         origins  = self.get_origins('magnetism'),
                         **kwargs)
        self.registery_doc(function_name().split('_')[-1])

    def get_MagnetismDoc(self) -> Union[Dict ,MagnetismDoc]:
        return self._MagnetismDoc
 
    def set_xrd(self, target='Cu', edge='Ka', min_two_theta=0, max_two_theta = 180,**kwargs) -> None:
        self._xrd.append(XRD.from_target(
                         material_id= self.material_id,
                         structure = self.get_structure(),
                         target = target,
                         edge = edge,
                         min_two_theta = min_two_theta,
                         max_two_theta = max_two_theta,
                         **kwargs
                       ))  

    def get_xrd(self) -> List:
        return self._xrd

    def set_XRDDoc(self,  created_at = None, **kwargs) -> None:
        created_at = created_at if created_at else datetime.now()
        self._XRDDoc= XRDDoc(created_at = created_at ,
                         material_id = self.material_id,
                         xrd = self.get_xrd(),
                         origins  = self.get_origins('xrd'),
                         **kwargs)
        self.registery_doc(function_name().split('_')[-1])

    def get_XRDDoc(self) -> Union[Dict , XRDDoc]:
        return self._XRDDoc   

    #----------------- Sources ------------

    def set_sources(self, db_name , material_id, material_url = '', description=''):
        self._sources.append(Source(
                                   db_name=db_name,   
                                   material_id = material_id,   
                                   material_url = material_url,   
                                   description = description   
                                   ))
    def get_sources(self) -> List:
        return self._sources
    
    def set_SourceDoc(self) -> None:
        self._SourceDoc =  SourceDoc(source=self.get_sources())
        self.registery_doc(function_name().split('_')[-1])

    def get_SourceDoc(self) -> Union[Dict , SourceDoc]:
        return self._SourceDoc

    #----------------- Meta ------------

    def set_meta(self, user = '', machine = '', cpuinfo = {}, description='') -> None:
        self._meta.append(Meta(
                              user=user,   
                              machine = machine,   
                              cpuinfo = cpuinfo,   
                              description = description   
                                   ))
    def get_meta(self) -> List:
        return self._meta
    
    def set_MetaDoc(self) -> None:
        self._MetaDoc =  MetaDoc(meta=self.get_meta())
        self.registery_doc(function_name().split('_')[-1])

    def get_MetaDoc(self) -> Union[Dict, MetaDoc]:
        return self._MetaDoc

    #------------------------------------------------
    def set_dos(self,path, label='',  code= 'vasp', auto = False, **kwargs):
        d={}
        if code.lower() =='vasp':
           if auto:
              electronic_structure=ElectronicStructure(path,**kwargs)
              d=electronic_structure.get_dos_auto(self.work_dir)
           else:
              d=ElectronicStructure(path,**kwargs).get_dos_manually(self.material_id,src_path=path,dst_path=self.work_dir)

        elif code.lower() == 'siesta':
           pass
        self._doses.append({label+'-'+code:d})

    def get_dos(self):
        return self._doses   

    def get_band(self):
        return self._bands   
    
    #----------------- stability ------------
    def set_stiff_stability(self,min_eig_tensor=None,value=None,**kwargs) -> None:
        if value:
           self._stiff_stability.append(StiffnessStability(value=value,**kwargs))
        else:
           self._stiff_stability.append(StiffnessStability.from_key(min_eig_tensor=min_eig_tensor,**kwargs))

    def get_stiff_stability(self) -> StiffnessStability:
        return self._stiff_stability

    def set_phonon_stability(self,max_hessian=None,value=None,**kwargs) -> None:
        if value:
           self._phonon_stability.append(PhononStability(value=value,**kwargs))
        else:
           self._phonon_stability.append(PhononStability.from_key(max_hessian=max_hessian,**kwargs)) 

    def get_phonon_stability(self) -> PhononStability:
        return self._phonon_stability

    def set_thermo_stability(self,formation_energy_per_atom=None,
                                     energy_above_hull=None,
                                     value=None,**kwargs) -> None:
        if value:
           self._thermo_stability.append(ThermoDynamicStability(value=value,**kwargs))
        else:
           self._thermo_stability.append(ThermoDynamicStability.from_key(formation_energy_per_atom=formation_energy_per_atom,
 energy_above_hull=energy_above_hull,
  **kwargs)) 

    def get_thermo_stability(self) -> ThermoDynamicStability:
        return self._thermo_stability

    def set_StabilityDoc(self,  created_at= None, **kwargs) -> None:

        # the origin of stiff, thermo and origins can be distinct by name .e.g.
        # set_origins('stability',task_id,name='stiff',link=[])
        # set_origins('stability',task_id,name='phonon',link=[])
        # set_origins('stability',task_id,name='thermo',link=[])

        created_at = created_at if created_at else datetime.now()
        self._StabilityDoc= StabilityDoc(created_at = created_at ,
                         material_id = self.material_id,
                         stiff_stability = self.get_stiff_stability(),
                         thermo_stability = self.get_thermo_stability(),
                         phonon_stability = self.get_phonon_stability(),
                         origins  = self.get_origins('stability'),
                         **kwargs)
        self.registery_doc(function_name().split('_')[-1])

    def get_StabilityDoc(self) -> Union[StabilityDoc,Dict]:
        return self._StabilityDoc  

    #----------------- customer ------------
    def set_customer(self,label : str, data : Dict) -> None:
        #d={"label":label,"data":data}
        self._customer[label]=data
  
    def get_customer(self):
        return self._customer

    #---------------------------------------
    def get_PropertiesDoc(self):
        return self._properties

    def set_properties(self,exclude=['TaskDoc']):
        d={}
        for doc in self.registered_doc:
            if doc in exclude:
               func = getattr(self, 'get_'+doc)
               log.debug('skip function:  %s'%func.__name__)
            else:
               func = getattr(self, 'get_'+doc)
               log.debug('invoke function: %s'%func.__name__)
               d[doc] = func()
        self._properties=d

    #---------------------------------
    def as_dict(self):
        init_args = {
            "material_id": self.material_id,
            "dataset": self.dataset,
            'dimension': self.dimension
        }
        return {"@module": self.__class__.__module__,
                "@class": self.__class__.__name__,
                "version": self.__class__.__version__,
                "init_args": init_args
                }

    @classmethod
    def from_dict(cls, d):
        return cls(**d["init_args"])

    #----------------- Task ------------
    def encode_task(self,task_dir, code='vasp', **kwargs ):
        if code=='vasp':
           task_id,calc_type = VaspTask( task_dir = task_dir,
                                          root_dir = self.root_dir,
                                          **kwargs)
        return task_id, calc_type

    def set_task(self, task_id , code= 'vasp', calc_type = '' , description='') -> None:
        self._tasks.append(Task(
                              task_id=task_id,   
                              code = code,   
                              calc_type = calc_type,   
                              description = description   
                                   ))
    def get_task(self) -> List:
        return self._tasks
    
    def set_TaskDoc(self) -> None:
        self._TaskDoc =  TaskDoc(task=self.get_task())
        self.registery_doc(function_name().split('_')[-1])

    def get_TaskDoc(self) -> Union[Dict, TaskDoc]:
        return self._TaskDoc

    #-----------------Raman spetrum------------
    def get_raman(self):
        pass

    def set_raman(self):
        pass

    def get_RamanDoc(self):
        pass

    def set_RamanDoc(self):
        pass

    #-----------------Polar prop------------
    def get_polar(self):
        return {}

    def set_polar(self):
        pass

    def get_PolarDoc(self):
        return {}

    def set_PolarDoc(self):
        pass

    #----------------- Others ------------
    def get_XRay_absorptionSpectra(self):
        pass

    def get_substrates(self):
        pass

    def get_piezoelectricity(self):
        pass

    def get_equationsofState(self):
        pass

    def get_dielectricity(self):
        pass

    def get_phonons(self):
        pass

    def get_similar_structures(self):
        pass

if __name__ == '__main__':
   from monty.serialization import loadfn,dumpfn
   from matvirdkit.model.utils import test_path
   task_dir=os.path.join(test_path(),'relax')
   mech_dir=os.path.join(test_path(),'alpha-P-R')
   scf_dir=os.path.join(test_path(),'scf')
   builder=Builder(material_id = 'bms-1', dataset = 'bms')
   #------structure
   builder.set_structure(fname=os.path.join(task_dir,'CONTCAR'))
   builder.set_StructureDoc()
   #------tasks
#                         origins = self.get_origins('thermo'),
#                         origins  = self.get_origins('eletronicstructure'),
#                         origins  = self.get_origins('magnetism'),
#                         origins  = self.get_origins('xrd'),
#                         origins  = self.get_origins('stability'),
   task_id,calc_type = builder.encode_task(task_dir,code='vasp')
   print('task_id : %s  calc_type: %s'%(task_id,calc_type))
   builder.set_task( task_id = task_id, code= 'vasp', calc_type = str(calc_type) , description='This is a relax task')
   builder.set_origins(key='thermo', task_id=task_id, name=str(calc_type)) 
   task_id,calc_type = builder.encode_task(scf_dir,code='vasp')
   print('task_id : %s  calc_type: %s'%(task_id,calc_type))
   builder.set_task( task_id = task_id, code= 'vasp', calc_type = str(calc_type) , description='This is a scf task')
   builder.set_origins(key='elctronicstructure', task_id=task_id, name=str(calc_type)) 
   builder.set_TaskDoc()
   #------thermo
   builder.set_thermo(formation_energy_per_atom=-0.1,
                         energy_above_hull=0.01,
                         energy_per_atom=-3.2)
   builder.set_ThermoDoc()
   #------magnetism
   builder.set_magnetism(magneatic_moment = 3.0, magnetic_order = 'FiM',
                         exchange_energy = None, magnetic_anisotropy= {})
   builder.set_MagnetismDoc()
   #------mechanics
   builder.set_mechanics2d(task_dir=mech_dir,prop_dir='mechanics',lprops=None , code= 'vasp')
   builder.set_Mechanics2dDoc()
   #------stability
   builder.set_stiff_stability(value='low')
   builder.set_phonon_stability(value='high')
   #builder.set_thermo_stability(value='middle')
   builder.set_StabilityDoc()
   #------XRD
   builder.set_xrd()
   builder.set_XRDDoc()
   #------source
   builder.set_sources(db_name='c2db', material_id='As4Ca4-bf7bbbdbefe0', material_url='https://cmrdb.fysik.dtu.dk/c2db/row/As4Ca4-bf7bbbdbefe0')
   builder.set_sources(db_name='icsd', material_id='22388')
   builder.set_SourceDoc()
   #------meta
   builder.set_meta(user ='haidi', machine ='cluster@HFUT',  description='cluster-88')
   builder.set_meta(user ='ergouzi', machine ='cluster@USTC',  description='cluster-10')
   builder.set_MetaDoc()

   builder.set_properties()
   builder.update_properties(key='TestDoc',val={'name':'wang','age':18})
   doc=jsanitize(builder.get_doc())
   dumpfn(doc,'doc.json',indent=4)
   dumpfn(doc,'toc.json')

   #set_origins(self,key,task_id,name='',link=[],append=False)
