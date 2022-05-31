import os
import inspect
import pandas as pd
from pprint import pprint
from datetime import datetime
from hashlib import sha1
from monty.json import MSONable
from matvirdkit.model.utils import jsanitize

from abc import ABCMeta, abstractmethod
from typing import Dict, List, Tuple, Optional, Union, Iterator, Set, Sequence, Iterable
from pymatgen.core import Structure
from matvirdkit import log,REPO_DIR 
from matvirdkit.model.utils import jsanitize,create_path
from matvirdkit.model.electronic import EMC,Bandgap,Mobility,Workfunction,ElectronicStructureDoc
from matvirdkit.model.properties import PropertyOrigin
from matvirdkit.model.thermo import Thermo,ThermoDoc
from matvirdkit.model.xrd import Xrd,XrdDoc
from matvirdkit.model.stability import ThermoDynamicStability,PhononStability,StiffnessStability,StabilityDoc
from matvirdkit.model.common import Meta,MetaDoc,Source,SourceDoc,Task,TaskDoc,DataFigure, JFData
from matvirdkit.model.magnetism import Magnetism,MagnetismDoc
from matvirdkit.model.structure import StructureMatvird
from matvirdkit.model.mechanics import Mechanics2d,Mechanics2dDoc
from matvirdkit.model.provenance import LocalProvenance,GlobalProvenance,Origin
from matvirdkit.model.electronic import Workfunction, Bandgap, EMC, Mobility, ElectronicStructureDoc,ElectronicStructure
from matvirdkit.builder.readstructure import structure_from_file
from matvirdkit.builder.task import VaspTask
from matvirdkit.builder.mechanics import mechanics2d_parser
__version__ = "0.1.0"
__author__ = "Matvird"

def function_name():
    return inspect.stack()[1][3]

supported_dataset = ['bms', 'mech2d', 'npr2d', 'penta',  'rashba'
                     'carbon2d', 'carbon3d', 'raman' ]
DocKeys = ['thermo', 'magnetism', 'electronic', 'xrd', 'mechanics2d', 'meta','source']

class Builder(metaclass=ABCMeta):
    def __init__(self, material_id : str, dataset :str , dimension = None, root_dir=None ):
        self.material_id = material_id
        assert dataset in supported_dataset
        self.root_dir =  root_dir if root_dir else REPO_DIR
        self.work_dir =  os.path.join(self.root_dir,dataset,material_id)
        self.mech_dir =  os.path.join(self.root_dir,dataset,material_id,'mechanics')
        if os.path.isdir(self.work_dir):
           pass
        else:
           create_path(self.work_dir,backup=False)
        if os.path.isdir(self.mech_dir):
           pass
        else:
           create_path(self.mech_dir,backup=False)
        self.dimension = dimension

        self._registered_doc=[]
        self._structure = None
        self._thermo      = {}  #thermo
        self._electronicstructure  = {}  #
        self._mechanics2d  = {}
        self._mechanics    = []
        self._mechanics2d_origins = []
        
        self._stability    = []
        self._thermo_stability = []
        self._stiff_stability = []
        self._phonon_stability    = []

        self._magnetism    = {}
        self._xrd          = {}
        self._raman        = {}
        self._polar        = {}
        self._source      = []
        self._provenance   = []
        self._meta         = []

        self._customer     = {}
        self._origins      = {}
        self._provenance   = {}

        self._tasks = []
        self._properties   = {}

        self._doses=  []
        self._bands=  []

        self._StructureDoc   = {}
        self._ThermoDoc   = {}
        self._ElectronicStructureDoc = {}
        self._XrdDoc = {}
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

    def save_doc(self,**kwargs):
        dumpfn(self.get_doc(),self.material_id+'.json',**kwargs)

    def get_doc(self,json=True) -> Dict:
        ret =   { 
                 "@module":    self.__class__.__module__,
                 "@class":     self.__class__.__name__,
                 "material_id":self.material_id,
                 'structure':  self.get_StructureDoc(),
                 "properties": self.get_PropertiesDoc(),
                 "tasks":      self.get_TaskDoc(),
                 "generated":  __author__,
                 "version":    __version__
               }
        if json:
           return jsanitize(ret)
        else:
           return ret

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
 
    #--------- thermo -------------------
    def set_thermo(self, infos) -> None:
        func_name=function_name().split('_')[-1]
        log.debug('Func name: set_%s()'%func_name) 
        for label in infos.get(func_name,{}).keys():
            info=infos[func_name].get(label,{})
            prov=info.get('provenance',{})
            info.pop('provenance',0)
            #description=info.get('description','')
            #root_meta=info.get('meta',{})
            provenance=self._get_provenance(prov)
            thermo=Thermo(provenance=provenance,**info) 
            self._thermo [label] = thermo

    def get_thermo(self) -> Dict:
         return self._thermo

    def set_ThermoDoc(self) -> None:
        self._ThermoDoc=ThermoDoc(thermo=self.get_thermo())
        self.registery_doc(function_name().split('_')[-1])

    def get_ThermoDoc(self) -> Union[Dict,ThermoDoc]:
        return self._ThermoDoc       

    def _get_mechanics2d_provenance(self,prov={}):
        provenance={}
        if prov:
           pass

    def _get_provenance(self,prov={}):
        provenance={}
        if prov:
           for key in prov.keys():
               task_infos=prov[key].get('task_infos',[])
               meta=prov[key].get("meta",{})
               log.debug(meta)
               origins=[]
               for task_info in task_infos:
                   task_dir=task_info.get('task_dir','')
                   code=task_info.get('code','vasp')
                   description=task_info.get('description','')
                   log.debug('task_dir :%s'%task_dir)
                   if task_dir:
                      task_id,calc_type = self.encode_task(task_dir,code=code)
                      self.set_task( task_id = task_id, code= code, calc_type = str(calc_type) , description=description)
                      log.info('task_id: %s calc_type: %s'%(task_id,calc_type))
                      origins.append(Origin(name=str(calc_type),
                                            task_id = str(task_id)))
                   else:
                      pass
               provenance[key]=LocalProvenance(origins=origins,**meta)
        else:
            pass
        return provenance

    #---------electronic structure-------------------
    def set_electronic(self, infos) -> None:
        func_name=function_name().split('_')[-1]
        log.debug('Func name: set_%s()'%func_name) 
        for label in infos.get(func_name,{}).keys():
            info=infos[func_name].get(label,{})
            bandgap=Bandgap(**info.get('bandgap',{}))
            emc=EMC(**info.get('emc',{}))
            mobility=Mobility(**info.get('mobility',{}))
            workfunction=Workfunction(**info.get('workfunction',{}))
            band=DataFigure(**info.get('band',{}))
            dos=DataFigure(**info.get('dos',{}))
            description=info.get('description','')
            root_meta=info.get('meta',{})
            prov=info.get('provenance',{})
            info.pop('provenance',0)
            provenance=self._get_provenance(prov)
            self._electronicstructure  [label] = ElectronicStructure(provenance=provenance,
                                      bandgap=bandgap,
                                      emc=emc,
                                      mobility=mobility,
                                      workfunction=workfunction,
                                      band=band,
                                      dos=dos,
                                      description=description,
                                      meta=root_meta) 
    def get_electronic(self):
        return self._electronicstructure
    
    def set_ElectronicDoc(self) -> None: 
        self._ElectronicStructureDoc=ElectronicStructureDoc(
               electronicstructure=self.get_electronic()
               )
        self.registery_doc(function_name().split('_')[-1])
                           
    def get_ElectronicDoc(self) -> Union[Dict ,ElectronicStructureDoc]:
        return self._ElectronicStructureDoc

    #-------------mechanics------------------------
    def set_mechanics2d(self, infos) -> None:
        func_name=function_name().split('_')[-1]
        log.debug('Func name: set_%s()'%func_name) 
        for label in infos.get(func_name,{}).keys():
            info=infos[func_name].get(label,{})
            elc2nd_stress_dir=info.get('elc2nd_stress',{}).get('task_dir','')
            elc2nd_energy_dir=info.get('elc2nd_stress',{}).get('task_dir','')
            stress_strain_dir=info.get('stress_strain',{}).get('task_dir','')
            description=info.get('description','')
            root_meta=info.get('meta',{})
            elc2nd_stress = mechanics2d_parser(elc2nd_stress_dir,self.mech_dir,'elc_stress')
            elc2nd_energy = mechanics2d_parser(elc2nd_energy_dir,self.mech_dir,'elc_energy')
            stress_strain = mechanics2d_parser(stress_strain_dir,self.mech_dir,'ssc_stress')
            prov=info.get('provenance',{})
            info.pop('provenance',0)
            #provenance=self._get_mechanics2d_provenance(prov)
            provenance={}
            self._mechanics2d  [label] = Mechanics2d(provenance=provenance,
                                      elc2nd_stress=elc2nd_stress,
                                      elc2nd_energy=elc2nd_energy,
                                      stress_strain=stress_strain,
                                      description=description,
                                      meta=root_meta) 
    def get_mechanics2d(self):
        return self._mechanics2d
                                        
    def set_Mechanics2dDoc(self) -> None:
        self._Mechanics2dDoc=Mechanics2dDoc(
                         mechanics2d = self.get_mechanics2d()
                         )
        self.registery_doc(function_name().split('_')[-1])
    
    def get_Mechanics2dDoc(self):
        return self._Mechanics2dDoc

    #-----------------magnetism--------------------
    def set_magnetism(self, infos) -> None:
        func_name=function_name().split('_')[-1]
        log.debug('Func name: set_%s()'%func_name) 
        for label in infos.get(func_name,{}).keys():
            info=infos[func_name].get(label,{})
            prov=info.get('provenance',{})
            info.pop('provenance',0)
            provenance=self._get_provenance(prov)
            self._magnetism [label] = Magnetism(provenance=provenance,**info) 

    def get_magnetism(self) -> Dict:
        return self._magnetism

    def set_MagnetismDoc(self ) -> None:
        self._MagnetismDoc=MagnetismDoc(magnetism=self.get_magnetism())
        self.registery_doc(function_name().split('_')[-1])

    def get_MagnetismDoc(self) -> Union[Dict ,MagnetismDoc]:
        return self._MagnetismDoc

    # ---------------------Xrd--------------------------
    def set_xrd(self, infos) -> None:
        func_name=function_name().split('_')[-1]
        log.debug('Func name: set_%s()'%func_name) 
        for label in infos.get(func_name,{}).keys():
            info=infos[func_name].get(label,{})
           # target=info.get('target',"Cu")
           # edge=info.get('edge',"Ka")
           # min_two_theta=info.get('min_two_theta',0)
           # max_two_theta=info.get('max_two_theta',180)
            prov=info.get('provenance',{})
            info.pop('provenance',0)
            provenance=self._get_provenance(prov)
            self._xrd[label]=Xrd.from_target(provenance = provenance,
                                             material_id = self.material_id,
                                             structure = self.get_structure(),
                                             **info)

    def get_xrd(self) -> Dict:
        return self._xrd

    def set_XrdDoc(self,) -> None:
        self._XrdDoc= XrdDoc(xrd=self.get_xrd())
        self.registery_doc(function_name().split('_')[-1])

    def get_XrdDoc(self) -> Union[Dict , XrdDoc]:
        return self._XrdDoc   

    #----------------- Sources ------------

    def set_source(self,infos) -> None:
        func_name=function_name().split('_')[-1]
        log.debug('Func name: set_%s()'%func_name) 
        for info in infos[func_name]:
            self._source.append(Source(**info))

    def get_source(self) -> List:
        return self._source
    
    def set_SourceDoc(self) -> None:
        self._SourceDoc =  SourceDoc(source=self.get_source())
        self.registery_doc(function_name().split('_')[-1])

    def get_SourceDoc(self) -> Union[Dict , SourceDoc]:
        return self._SourceDoc

    #----------------- Meta ------------

    def set_meta(self,infos) -> None:
        func_name=function_name().split('_')[-1]
        log.debug('Func name: set_%s()'%func_name) 
        for info in infos[func_name]:
            self._meta.append(Meta(**info))

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
    def set_tasks(self, task_infos) -> None:
        for task_info in task_infos:
            log.debug(task_info)
            task_id,calc_type = self.encode_task(**task_info)
            if task_id:
               task_info['task_id'] = task_id
               task_info['calc_type'] = calc_type
               self._tasks.append(Task(**task_info)) 

    def encode_task(self,task_dir, code='vasp', **kwargs ):
        task_id=''
        calc_type=''
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

    @classmethod
    def from_file(cls,fname='info.yaml'):
        infos=loadfn(fname)
        parameters = infos['parameters']
        dataset = parameters['dataset'] 
        dimension = parameters['dimension'] 
        material_id = parameters['material_id'] if parameters['material_id']  else 'm2d-2'
        root_dir = parameters['root_dir'] 
        infos.pop('parameters')
        f_structure = infos['structure']['filename']
        infos.pop('structure')
        builder=cls(material_id = material_id, dataset = dataset, root_dir= root_dir)
        builder.set_structure(fname=f_structure)
        builder.set_StructureDoc()
        for key in infos.keys():
               log.info('--------set %s-------'%key)
               if key in DocKeys:     
                  func_set = getattr(builder, 'set_'+key)
                  func_set(infos)
                  Func_set = getattr(builder, 'set_'+key.capitalize()+'Doc' )
                  Func_set()
        tasks = infos.get('tasks',[])
        builder.set_tasks(tasks)     
        builder.set_TaskDoc()
        builder.set_properties()
        builder.update_properties(key='CustomerDoc',val=infos.get('customer',{}))
        return builder

if __name__ == '__main__':
   from monty.serialization import loadfn,dumpfn
   from matvirdkit.model.utils import test_path
   builder=Builder.from_file(fname='info.yaml')
   #doc=builder.get_doc()
   #dumpfn(doc,'doc.json',indent=4)
   builder.save_doc()
