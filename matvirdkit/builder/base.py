import os
import datetime
from hashlib import sha1
from abc import ABCMeta, abstractmethod
from monty.json import MSONable
from matvirdkit.model.utils import jsanitize
from typing import Dict, List, Tuple, Optional, Union, Iterator, Set, Sequence, Iterable
from mvdkit.builder.readstructure import structure_from_file
from matvirdkit.model.electronicstructure import EMC,Bandgap,Mobility,Workfunction
from matvirdkit.model.properties import PropertyOrigin

__version__ = "0.1.0"
__author__ = "Matvird"

class Builder(metaclass=ABCMeta):
    supported_props=['thermo','electronicstructure','mechanics',
                     'magnetism','xrd','raman','polar','sources',
                     'customer','provenance','meta'
                     ]
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
        #self._structure_mp = None

        self._thermo       = {}  #thermo
        self._electronicstructure  = {}  #
        self._mechanics    = {}
        self._stability    = {}
        self._magnetism    = {}
        self._xrd          = {}
        self._raman        = {}
        self._polar        = {}
        self._sources      = {}
        self._customer     = {}
        self._provenance   = {}
        self._meta         = {}

        self._origins      = {}

        self._properties   = {}

        self._emcs =  []
        self._bandgaps =  []
        self._mobilities =  []
        self._workfunctions =  []

        self._ThermoDoc   = {}
        self._ElectronicStructureDoc = {}
        self._XRDDoc = {}
        self._RamanDoc = {}
        #self._tasks = {}
        #self._doses=  []
        #self._bands=  []

    def get_doc(self) -> Dict:
        return { 
                 "@module": self.__class__.__module__,
                 "@class": self.__class__.__name__,
                 "material_id":self.material_id,
                 'structure': self.get_StructureDoc()
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

    def update_tasks(self,val):
        if isinstance(val,str):
              pass
              #self._tasks.update({val:self._doses})
        elif isinstance(val,dict):
              self._tasks.update(val)
        else:
             raise RuntimeError('Only support string and dict')


    def set_structure(self, fname='POSCAR') -> None:
        self._structure = structure_from_file(fname)
        #StructureMatvird.from_structure(self._structure)

    def get_structure(self,**kargs) -> Structure:
        return self._structure

    def get_StructureDoc(self,**kargs) -> Dict:
        return StructureMatvird.from_structure(
                           dimension=self.dimension,
                           structure=self._structure
                           **kargs)

    def set_thermos(self,formation_energy_per_atom=None,
                         energy_above_hull=None,
                         energy_per_atom=None,
                         **kargs) -> None:
        self._thermos.append( Thermo(formation_energy_per_atom=formation_energy_per_atom,
                                     energy_above_hull=energy_above_hull,
                                     energy_per_atom=energy_per_atom,**kargs))

    def get_thermos(self) -> Dict:
         return self._thermos

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
    
    def set_ThermoDoc(self, created_at, **kargs) -> None:
        created_at = created_at if created_at else datetime.now()  
        self._ThermoDoc=ThermoDoc(created_at = created_at ,
                         thermos = self.get_thermos(),
                         origins = self.get_origins('thermo'),
                         material_id = self._material_id,
                         **kargs)

    def get_ThermoDoc(self) -> ThermoDoc:
        return self._ThermoDoc

    def set_emcs(self,value,k_loc,b_loc,**kargs) -> None:
        self._emcs.append( EMC(k_loc=k_loc,b_loc=b_loc,value=value,**kargs))

    def get_emcs(self) -> Dict:
        log.info('Number of emcs: %d'%(len(self._emcs)))
        return self._emcs
    
    def set_bandgaps(self,value,direct,**kargs) -> None:
        self._bandgaps.append(Bandgap(value=value,direct=direct,**kargs))

    def get_bandgaps(self) -> Dict:
        log.info('Number of bandgaps: %d'%(len(self._bandgaps)))
        return self._bandgaps

    def set_bandgaps(self,value,direct,**kargs) -> None:
        self._bandgaps.append(Bandgap(value=value,direct=direct,**kargs))
        
    def set_mobilities(self,value,k_loc,b_loc,direction,**kargs) -> None:
        self._mobilities.append(Mobility(k_loc=k_loc,b_loc=b_loc,value=value,direction=direction,**kargs))
 
    def get_mobilites(self) -> Dict:
        log.info('Number of mobilites: %d'%(len(self._mobilites)))
        return self._mobilites

    def set_workfunctions(self,value,**kargs) -> None:
        self._workfunctions.append(Workfunction(value=value,**karg))

    def get_workfunctions(self) -> Dict:
        log.info('Number of workfunctions: %d'%(len(self._mobilites)))
        return self._workfunctions

    def set_ElectronicStructureDoc(self,  created_at, **kargs) -> None: 
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
                         **kargs)
                           
    def get_ElectronicStructureDoc(self) -> ElectronicStructureDoc:
        return self._ElectronicStructureDoc

    def set_magnetism(self,magneatic_moment = None, magnetic_order = None, exchange_energy = None, magnetic_anisotropy= {},**kargs) -> None:
        self._magnetism.append(Magnetism(magneatic_moment = magneatic_moment ,
                                         magnetic_order = magnetic_order ,
                                         exchange_energy = exchange_energy ,
                                         magnetic_anisotropy = magnetic_anisotropy,
                                         **kargs))

    def get_magnetism(self) -> Dict:
        return self._magnetism

    def set_MagnetismDoc(self,  created_at, **kargs) -> None:
        created_at = created_at if created_at else datetime.now()
        self._MagnetismDoc=MagnetismDoc(created_at = created_at ,
                         material_id = self._material_id,
                         magnetism = self.get_magnetism(),
                         origins  = self.get_origins('magnetism'),
                         **kargs)

    def set_xrd(self, target='Cu', edge='Ka', min_two_theta=0, max_two_theta = 180,**kargs) -> None:
        self._xrd.append(XRD.from_target(
                         material_id= self.material_id,
                         structure = self.get_structure(),
                         target = target,
                         edge = edge,
                         min_two_theta = min_two_theta,
                         max_two_theta = mix_two_theta,
                         **kargs
                       ))  

    def get_xrd(self) -> Dict:
        return self._xrd

    def set_XRDDoc(self,  created_at, **kargs) -> None:
        created_at = created_at if created_at else datetime.now()
        self._XRDDoc= XRDDoc(created_at = created_at ,
                         material_id = self._material_id,
                         xrd = self.get_xrd(),
                         origins  = self.get_origins('xrd'),
                         **kargs)

    def get_XRDDoc(self) -> XRDDoc:
        return self._XRDDOc   
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
  
    #----------------- Sources ------------


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

    def set_dos(self,path, label='',  code= 'vasp', auto = False, **kargs):
        d={}
        if code.lower() =='vasp':
           if auto:
              electronic_structure=ElectronicStructure(path,**kargs)
              d=electronic_structure.get_dos_auto(self.workpath)
           else:
              d=ElectronicStructure(path,**kargs).get_dos_manually(self.material_id,src_path=path,dst_path=self.workpath)

        elif code.lower() == 'siesta':
           pass
        self._doses.append({label+'-'+code:d})

    def get_dos(self):
        return self._doses   

    def get_band(self,path, label='', code = 'vasp'):
        return self._bands   
    
    def set_stability(self):
        
        pd=StabilityDoc(created_at=datetime.now(),
        stiff_stability=[
              StiffnessStability(value='low',description='scan-static',link=ustr1) ,
              StiffnessStability.from_dict(min_eig_tensor=0.1)
                         ],
      thermo_stability= [
              ThermoDynamicStability.from_dict (e_f=-0.1, e_abh=0.0,description='pbe-static',link=ustr2) ,
              ThermoDynamicStability.from_dict (e_f=0.2, e_abh=0.1,description='lda-static') ,
                         ] ,
      origins=[
              PropertyOrigin(name='static',task_id='task-112',link=ustr1),
              PropertyOrigin(name='static',task_id='task-113',link=ustr2),
               ],
      material_id='rsb-1',
      tags = ['high temperature phase']
      )
        #set up the value manually 
        # E_abh=0.0  high
        # E_abh=[0,0.15] MIDDLE
        # E_abh=[0,1,inf] LOW 
        if thermo<=1e-2 and thermo >0:
           self._thermodynamic = "HIGH"
        elif thermo<=1.5e-1 and thermo >1e-2:
           self._thermodynamic = "MIDDLE"
        else:
           self._thermodynamic = "LOW"


    @LabeledData('Stability infomation')
    def get_stability(self):
        d = {}
        d["Thermodynamic"] = self._thermodynamic 
        d["Dynamical_phonons"] = self._dynamic_phon 
        d["Dynamical_stiffness"] = self._dynamic_stiff 
        return d
    
    def insert_customer_data(self,label,data):
        #d={"label":label,"data":data}
        self._customer[label]=data
  
    @LabeledData('Customer infomation')
    def get_customer(self):
        return self._customer

    def set_source(self,source):
        #  the format of source is a List[Dict]
        #   d=[{'Source_DB':db_name,
        #      'Source_ID':db_id,
        #      'Source_url':url
        #     }]
        self._sources = source
           
    @LabeledData('Source infomation')
    def get_source(self):
        return self._sources

    def set_meta(self,user=None, machine=None, ctime=None, utime=None):
        self._user=user if user else None
        self._machine=machine if machine else None
        self._ctime = ctime if ctime else str(datetime.datetime.now()) 
        self._utime = utime if ctime else str(datetime.datetime.now()) 

    def get_meta(self):
        return {"User": self._user,
                "Machine": self._machine,
                "Create_time": self._ctime,
                "Update_time": self._utime}

    @LabeledData("Basic properties")
    def set_prop(self,struct_path, **kargs):
        d={}
        fname=os.path.join(struct_path,'POSCAR')
        self.set_structure(fname=fname)

        d['Structure']=self.get_structure()
        d['Symmetry']=self.get_symmetry()
        # calculate the Phase diagram via MP database
        if "auto_pd" in kargs.keys():
            auto_pd = kargs["auto_pd"]
        else:
            auto_pd = False

        if auto_pd:
           try:
              energy=kargs['energy']
           except KeyError:
              raise RuntimeError('Energy of structure should be supplied!')
           self.set_computed_entry(energy=energy)
           self.set_Eabh_and_Ef_via_MPDB(save_pd=False)
           self.set_thermo_stability(thermo=Eabh)
        else:
           try:
              Eabh=kargs['Eabh']
              self.set_Eabh(Eabh)
              self.set_thermo_stability(thermo=Eabh)
           except KeyError:
              pass

           try:
              Ef=kargs['Ef']
              self.set_Ef(Ef)
           except KeyError:
              pass

        if 'Exfol' in kargs.keys() and self._dimension == 2:
            self.set_Exfol(kargs['Exfol'])

        d['Energy']=self.get_energy()

        try:
           magnetic_moment=kargs['magnetic_moment']
        except KeyError:
           magnetic_moment=None
        
        try:
           magnetic_order=kargs['magnetic_order']
        except KeyError:
           magnetic_order=None

        try:
           exchange_energy=kargs['exchange_energy']
        except KeyError:
           exchange_energy=None
        
        self.set_magnetic( magnetic_moment = magnetic_moment, 
                           magnetic_order = magnetic_order,
                           exchange_energy = exchange_energy)

        d['Stability']=self.get_stability()
        if all(val is None for val in self.get_magnetic().values()):
           pass
        else: 
           d['Magnetism']=self.get_magnetic()

        if 'band_gaps'  in kargs.keys():
            self.set_band_gaps( kargs['band_gaps'])
        d['Bandgap']=self.get_band_gaps()

        if 'source'  in kargs.keys():
            self.set_source( kargs['source'])
        d['Source']=self.get_source()

        if 'meta'  in kargs.keys():
            self.set_meta(**kargs['meta'])
        d['Meta']=self.get_meta()
        
        #dumpfn(ret,'ret.json',indent=4)
        self._properties=d

    #@abstractmethod
    #def task_doc(self,*arg,**karg):
    #    """
    #    Returns a dict for single task.
    #    """

    #def generate_doc(self):
    #    proc_doc=self.

    def as_dict(self):
        init_args = {
            "ID": self.material_id,
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


