import os
import datetime
from hashlib import sha1
from abc import ABCMeta, abstractmethod
from monty.json import MSONable
from pymatgen.symmetry.analyzer import SpacegroupAnalyzer
from typing import Dict, List, Tuple, Optional, Union, Iterator, Set, Sequence, Iterable
from functools import wraps

#from matvirdkit.model.

__version__ = "0.1.0"
__author__ = "Matvird"

class Drone(metaclass=ABCMeta):

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

        self._thermo = None

        self._magnetism= None

        self._stability = None

        self._sources = []

        self._mechanics = {}

        self._customer = {}

        self._band_gaps= {}
        self._electronics= {}

        self._meta= None

        self._properties = {}

        self._tasks = {}
        self._doses=  []
        self._bands=  []

    def get_doc(self) -> Dict:
        return { 
                 "@module": self.__class__.__module__,
                 "@class": self.__class__.__name__,
                 "ID":self.material_id,
                 "Properties": self.get_properties(),
                 "Tasks": self.get_tasks(),
                 "generatedBy": __author__,
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


    def set_Eabh_and_Ef_via_MPDB(self,save_pd=False):
        Eabh=None
        Ef=None
        try:
           Eabh,Ef=calc_pd(self._ce,self._chemsys,save_pd=save_pd)
        except:
           pass
        self._Eabh = Eabh 
        self._Ef = Ef 

    def set_structure(self, fname='POSCAR'):
        self._structure = structure_from_file(fname)

    def set_computed_entry(self,energy,correction=0):
        self._ce=ComputedEntry(self._structure.composition, energy, correction)

    def get_structure(self,**kargs) -> Dict:
        return StructureMatvird.from_structure(
                           dimension=self.dimension,
                           structure=self._structure
                           **kargs)
          
    def get_input(self, src_path, code='vasp', save_raw  = False):
        if code.lower() =='vasp':
           j_id= VaspInputs(src_path).parse_input(dst_path = self.workpath, save_raw = save_raw)
        elif code.lower() == 'siesta':
           pass
        return j_id

    def get_output(self, src_path,  code='vasp', save_raw = True):
        if code.lower() =='vasp':
           j_id= VaspOutputs(src_path).parse_output(dst_path = self.workpath, save_raw = save_raw)
        elif code.lower() == 'siesta':
           pass
        return j_id
    
    def set_task(self,path,label,describ='Ups!!!',code='vasp',save_raw_input=False,save_raw_output=True):
        j_id1=self.get_input(src_path=path,code=code,save_raw = save_raw_input)
        j_id2=self.get_output(src_path=path,code=code, save_raw = save_raw_output)

        @LabeledData(describ)
        def _set_task(j_id1,j_id2):
            d={}
            d['Input']={'j_id':j_id1}
            d['Output']={'j_id':j_id2}
            d['task_id']=sha1(str(j_id1+j_id2).encode('utf-8')).hexdigest()
         
            return d

        self._tasks [label]= _set_task(j_id1,j_id2)       

    def set_band_gaps(self,  band_gaps : Dict):
        # the label can be "PBE,LDA,GW,HSE06 et al."
           #d={"label":label,"bandgap":gap}
           self._band_gaps = band_gaps

    @LabeledData('Band gap')
    def get_band_gaps(self):
        # the label can be "PBE,LDA,GW,HSE06 et al."
           #d={"label":label,"bandgap":gap}
        return self._band_gaps

    def set_magnetic(self,magnetic_moment = None, magnetic_order = None, exchange_energy = None):
        # magnetic_order : NM, FM, AFM, Fim
        self._magnetic_moment = magnetic_moment
        self._magnetic_order = magnetic_order
        self._exchange_energy = exchange_energy

    @LabeledData('Magnetic infomation')
    def get_magnetic(self):
        d={"Magnetic_moment": self._magnetic_moment, 
           "Magnetic_order": self._magnetic_order,
           "Exchange_energy": self._exchange_energy}
          
        return d

    @LabeledData('Energy infomation')
    def get_energy(self):

        d = {"Decomposition_energy":self._Eabh,
             "Formation_energy":self._Ef
             }
        if self.dimension==2:
           d.update({"Exfoliation_energy": self._Exfol})
        
        return d 

    def get_XRay_diffraction(self):
        pass

    def get_XRay_absorptionSpectra(self):
        pass

    def get_substrates(self):
        pass

    def set_elasticity(self,path,label):

        # set the elasticity by using the results from mech2d calculation
        if self.dimension==2: 
           keys={"Stiffness_tensor", "Compliance_tensor", "Lm",
                 "Y10", "Y01", "Gm", "V10", "V01", "Stability"
                 }
           d={'ElasticConstant_properties':{},"ElasticConstant_meta":{}}
           os.chdir(path)
           with open("m2d.ana.log","wb") as out, open("m2d.ana.err","wb") as err:
                p=subprocess.Popen(["m2d","post","--plot","-f","png"],stdout=out,stderr=err)
                p.communicate()

           os.chdir(self.rootpath)
           if os.path.exists(os.path.join(path,'Result.json')):
              ret = loadfn(os.path.join(path,'Result.json'))
              if ret["Stability"]=="Stable":
                 self._dynamic_stiff = 'HIGH'
                 EV=np.loadtxt(os.path.join(path,'EV_theta.dat')).tolist()
                 filename = os.path.join(path,"energy-EV.png")
                 if os.path.exists(filename):
                    pass
                 else:
                    filename = None
              else:
                 filename=None
                 EV=None
              for key in keys:
                  d['ElasticConstant_properties'][key]=ret[key]
              d['ElasticConstant_properties']["EV"]={"data":EV,"f_id":filename}
              self.Mechanics=d
              return d
           else:
              print("File %s"%os.path.join(self.workpath,'Result.json')+" no exist." )
              os._exit(0)

        pass

    def get_stress_strain_curve(self):
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

    @LabeledData('Density of states')
    def get_dos(self):
        return self._doses   

    @LabeledData('Band structure')
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
      tgas = ['high temperature phase']
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


