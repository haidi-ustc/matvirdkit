import os
import inspect
import datetime
from hashlib import sha1
from monty.json import MSONable

from abc import ABCMeta, abstractmethod
from typing import Dict, List, Tuple, Optional, Union, Iterator, Set, Sequence, Iterable
from pymatgen.core import Structure
from matvirdkit.model.utils import jsanitize
from matvirdkit.builder.readstructure import structure_from_file
from matvirdkit.model.electronic import EMC,Bandgap,Mobility,Workfunction,ElectronicStructureDoc
from matvirdkit.model.properties import PropertyOrigin
from matvirdkit.model.thermo import Thermo,ThermoDoc
from matvirdkit.model.xrd import XRD,XRDDoc
from matvirdkit.model.stability import ThermoDynamicStability,PhononStability,StiffnessStability,StabilityDoc
from matvirdkit.model.common import Meta,MetaDoc,Source,SourceDoc
from matvirdkit.model.magnetism import Magnetism,MagnetismDoc
from matvirdkit.model.structure import StructureMatvird

__version__ = "0.1.0"
__author__ = "Matvird"

def function_name():
    return inspect.stack()[1][3]

class Builder(metaclass=ABCMeta):
    def __init__(self, material_id : str, dataset :str ='dataset', dimension : int= 3):
        self.material_id = material_id
        self.rootpath = os.getcwd()
        self.workpath = os.path.join(self.rootpath,dataset,material_id)
        if os.path.isdir(self.workpath):
           pass
        else:
           create_path(self.workpath,backup=False)

        self.dimension = dimension

        self._structure = None

        self._registered_doc=[]

        self._thermo       = []  #thermo
        self._electronicstructure  = []  #
        self._mechanics    = []
        
        self._stability    = []
        self._thermo_stability = []
        self._stiffness_stability = []
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

        self._properties   = {}

        self._emcs =  []
        self._bandgaps =  []
        self._mobilities =  []
        self._workfunctions =  []

        self._StructureDoc   = {}
        self._ThermoDoc   = {}
        self._ElectronicStructureDoc = {}
        self._XRDDoc = {}
        self._RamanDoc = {}
        self._SourceDoc = {}
        self._MagnetismDoc={}
        self._MetaDoc = {}
        self._StabilityDoc = {}

        #self._tasks = {}
        self._doses=  []
        self._bands=  []

    @property 
    def registered_doc(self) -> Dict:
        return self._registered_doc

    def registery_doc(self,value) -> None:
        if value not in self._registered_doc:
           self._registered_doc.append(value)

    def get_doc(self) -> Dict:
        return { 
                 "@module": self.__class__.__module__,
                 "@class": self.__class__.__name__,
                 "material_id":self.material_id,
                 'structure': self.get_StructureDoc(),
                 "properties": self.get_properties(),
                 "generated": __author__,
                 "version": __version__
               }

    def get_properties(self) -> Dict:
        return self._properties
    
    def get_tasks(self) -> Dict:
        return self._tasks

    def update_properties(self,val):
        if isinstance(val,str):
           if val=='DOS':
              self._properties.update({val:self.get_dos()})
           elif val=='Band':
              self._properties.update({val:self.get_band()})
           else:
              pass
        elif isinstance(val,dict):
              self._properties.update(val)
        else:
             raise RuntimeError('Only support string and dict')

    def update_tasks(self,val) -> None:
        if isinstance(val,str):
              pass
              #self._tasks.update({val:self._doses})
        elif isinstance(val,dict):
              self._tasks.update(val)
        else:
             raise RuntimeError('Only support string and dict')

    def set_structure(self, fname='POSCAR') -> None:
        self._structure = structure_from_file(fname)

    def get_structure(self,**kwargs) -> Structure:
        return self._structure

    def set_StructureDoc(self,**kwargs) -> Union[Dict , StructureMatvird]:
        self.__StructureDoc=StructureMatvird.from_structure(
                           dimension=self.dimension,
                           structure=self._structure
                           **kwargs)

    def get_StructureDoc(self,**kwargs) -> Union[Dict , StructureMatvird]:
        return self._StructureDoc

    def set_origins(self,key,task_id,name='',link=[],append=False) -> None:
        if  key in self._origins.keys():
             self._origins[key].append(PropertyOrigin(name=name,task_id=task_id,link=link))
        else:
             self._origins[key]=[PropertyOrigin(name=name,task_id=task_id,link=link)]
    def get_origins(self,key=None) -> Union[Dict,List]:
        if key:
           if key in self._origins.keys():
              return self._origins[key]
           else:
              return []
        else:
           return self._origins
 
    def set_thermos(self,formation_energy_per_atom=None,
                         energy_above_hull=None,
                         energy_per_atom=None,
                         **kwargs) -> None:
        self._thermos.append( Thermo(formation_energy_per_atom=formation_energy_per_atom,
                                     energy_above_hull=energy_above_hull,
                                     energy_per_atom=energy_per_atom,**kwargs))

    def get_thermos(self) -> Dict:
         return self._thermos
    
    def set_ThermoDoc(self, created_at, **kwargs) -> None:
        created_at = created_at if created_at else datetime.now()  
        self._ThermoDoc=ThermoDoc(created_at = created_at ,
                         thermos = self.get_thermos(),
                         origins = self.get_origins('thermo'),
                         material_id = self._material_id,
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
                         material_id = self._material_id,
                         origins  = self.get_origins('eletronicstructure'),
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

    def set_magnetism(self,magneatic_moment = None, magnetic_order = None,
                           exchange_energy = None, magnetic_anisotropy= {},
                           **kwargs) -> None:
        self._magnetism.append(Magnetism(magneatic_moment = magneatic_moment ,
                                         magnetic_order = magnetic_order ,
                                         exchange_energy = exchange_energy ,
                                         magnetic_anisotropy = magnetic_anisotropy,
                                         **kwargs))

    def get_magnetism(self) -> Dict:
        return self._magnetism

    def set_MagnetismDoc(self,  created_at, **kwargs) -> None:
        created_at = created_at if created_at else datetime.now()
        self._MagnetismDoc=MagnetismDoc(created_at = created_at ,
                         material_id = self._material_id,
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
                         max_two_theta = mix_two_theta,
                         **kwargs
                       ))  

    def get_xrd(self) -> Dict:
        return self._xrd

    def set_XRDDoc(self,  created_at, **kwargs) -> None:
        created_at = created_at if created_at else datetime.now()
        self._XRDDoc= XRDDoc(created_at = created_at ,
                         material_id = self._material_id,
                         xrd = self.get_xrd(),
                         origins  = self.get_origins('xrd'),
                         **kwargs)
        self.registery_doc(function_name().split('_')[-1])

    def get_XRDDoc(self) -> Union[Dict , XRDDoc]:
        return self._XRDDOc   

    #----------------- Sources ------------

    def set_sources(self, db_name, material_id, material_url, description=''):
        self._sources.append(Source(
                                   db_name=db_name,   
                                   material_id = material_id,   
                                   material_url = material_url,   
                                   description = description   
                                   ))
    def get_sources(self) -> Dict:
        return self._sources
    
    def set_SourceDoc(self) -> None:
        self._SourceDoc =  SourceDoc(source=self.get_sources())
        self.registery_doc(function_name().split('_')[-1])

    def get_SourceDoc(self) -> Union[Dict , SourceDoc]:
        return self._SourceDoc

    #----------------- Meta ------------

    def set_meta(self, user, machine, cpuinfo, description='') -> None:
        self._meta.append(Meta(
                              user=user,   
                              machine = machine,   
                              cpuinfo = cpuinfo,   
                              description = description   
                                   ))
    def get_meta(self) -> Dict:
        return self._meta
    
    def set_MetaDoc(self) -> None:
        self._MetaDoc =  MetaDoc(meta=self.get_meta())
        self.registery_doc(function_name().split('_')[-1])

    def get_MetaDoc(self) -> Union[Dict, MetaDoc]:
        return self._MetaDoc


    def set_dos(self,path, label='',  code= 'vasp', auto = False, **kwargs):
        d={}
        if code.lower() =='vasp':
           if auto:
              electronic_structure=ElectronicStructure(path,**kwargs)
              d=electronic_structure.get_dos_auto(self.workpath)
           else:
              d=ElectronicStructure(path,**kwargs).get_dos_manually(self.material_id,src_path=path,dst_path=self.workpath)

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

    def set_StabilityDoc(self,  created_at, **kwargs) -> None:

        # the origin of stiff, thermo and origins can be distinct by name .e.g.
        # set_origins('stability',task_id,name='stiff',link=[])
        # set_origins('stability',task_id,name='phonon',link=[])
        # set_origins('stability',task_id,name='thermo',link=[])

        created_at = created_at if created_at else datetime.now()
        self._StabilityDoc= StabilityDoc(created_at = created_at ,
                         material_id = self._material_id,
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

    def get_properties(self):
        return self._properties
    
    #---------------------------------------
    def set_properties(self):
        d={}
        for doc in self.registered_doc:
            func = getattr(self, 'get_'+doc)
            log.debug('function name %s'%func.__name__)
            d[doc] = func()
        self._properties=d

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
   from matvirdkit.model.utils import test_path
   task_dir=os.path.join(test_path(),'relax')
   #parsing_task(task_dir,tags=['relax'])
