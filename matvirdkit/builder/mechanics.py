import os
import subprocess
import numpy as np
from uuid import uuid4
from glob import glob
from monty.serialization import loadfn,dumpfn
from matvirdkit.model.utils import jsanitize
from matvirdkit import log
from matvirdkit.model.mechanics import Mechanics2d, Mechanics2dDoc,Mechanics2dSummary,Elc2nd2d
from matvirdkit.model.common import DataFigure,JFData
from matvirdkit.model.utils import create_path,transfer_file,jsanitize
from matvirdkit import REPO_DIR as repo_dir
from matvirdkit.builder.task import VaspTask

def mechanics2d_from_directory(task_dir,dst_dir,prop, root_meta={}, code= 'vasp'):

    ret={'summary':{},
         'polar_EV':{},
         'deformations':{},
         'stress_strain':{},
         'meta':{}
         }

    pwd=os.getcwd()
    assert prop in ['elc_energy','elc_stress','ssc_stress']
    log.debug("task_dir: %s"%(task_dir))  
    os.chdir(task_dir)
    if prop=='elc_energy':
       log.debug('-'*20)
       log.info('Processing %s '%prop)
       log.debug(task_dir)
       log.debug(os.path.join(dst_dir,prop))
       with open("m2d.ana.log","wb") as out, open("m2d.ana.err","wb") as err:
            p=subprocess.Popen(["m2d","post","--plot","-f","png"],stdout=out,stderr=err)
            p.communicate()

       defs=list(map(os.path.basename,glob(os.path.join(task_dir,prop,'Def_*'))))
       defs.sort()
       os.chdir(pwd)
       create_path(os.path.join(dst_dir,prop))
       deformations={}
       for _def in defs:
           create_path(os.path.join(dst_dir,prop,_def))
           transfer_file(_def+'_Energy.dat',        os.path.join(task_dir,prop,_def) , os.path.join(dst_dir,prop,_def) , rename= False)
           transfer_file(_def+'_Energy_Strain.png', os.path.join(task_dir,prop,_def) , os.path.join(dst_dir,prop,_def) , rename= False)
           data = np.loadtxt(os.path.join(dst_dir,prop,_def,_def+'_Energy.dat')).tolist()
           def_data=JFData(description='Energy v.s. strain data', json_data= {'data':data},
             json_file_name=None,json_id=None,meta={})
           def_fig=JFData(description='Energy v.s. strain figure',
             ile_fmt='png', file_name=os.path.join(dst_dir,prop,_def, _def+'_Energy_Strain.png'),file_id=None)
           def_datafig=DataFigure(data=[def_data],figure=def_fig)
           deformations[_def]=def_datafig
       os.chdir(pwd)
       for f in ['EV_theta.dat','Result.json','energy-EV.png']:
           transfer_file(f, task_dir , os.path.join(dst_dir,prop) , rename= False)
       transfer_file('energy-EV.png', task_dir , os.path.join(dst_dir,prop) , rename= False)
       transfer_file(os.path.join(task_dir,'elc_energy','Mech2D.json'), task_dir , dst_dir , rename= False)
        
       data=np.loadtxt(os.path.join(dst_dir,prop,'EV_theta.dat')).tolist()
       ev_data=JFData(description='Angle dependent Young\'s modulus and Poisson\'s ratio figure', json_data= {'data':data},
             json_file_name=None,json_id=None,meta={})
       summary=Mechanics2dSummary.from_file(os.path.join(dst_dir,prop,'Result.json'))
       ev_fig=JFData(description='Angle dependent Young\'s modulus and Poisson\'s ratio figure',
             file_fmt='png', file_name=os.path.join(dst_dir,prop,'energy-EV.png'),file_id=None)
       ev_datafig=DataFigure(data=[ev_data],figure=ev_fig)
         
       ret['summary'] = summary
       ret['polar_EV'] = ev_datafig
       ret['deformations']=deformations
       #dumpfn(jsanitize(Elc2nd2d(**ret)),'test.json')
       
    elif prop=='elc_stress':
       log.debug('-'*20)
       log.info('Processing %s '%prop)
       log.debug(task_dir)
       log.debug(os.path.join(dst_dir,prop))
       with open("m2d.ana.log","wb") as out, open("m2d.ana.err","wb") as err:
            p=subprocess.Popen(["m2d","post","-a","stress","-p","elc","--plot","-f","png"],stdout=out,stderr=err)
            p.communicate()
       defs=list(map(os.path.basename,glob(os.path.join(task_dir,prop,'Def_*'))))
       defs.sort()
       os.chdir(pwd)
       create_path(os.path.join(dst_dir,prop))
       deformations={}
       for _def in defs:
           create_path(os.path.join(dst_dir,prop,_def))
           transfer_file(_def+'_Physical_Stress.dat',   os.path.join(task_dir,prop,_def) , os.path.join(dst_dir,prop,_def) , rename= False)
           transfer_file(_def+'_Lagrangian_Stress.dat', os.path.join(task_dir,prop,_def) , os.path.join(dst_dir,prop,_def) , rename= False)
           transfer_file(_def+'_Lagrangian_Stress.png', os.path.join(task_dir,prop,_def) , os.path.join(dst_dir,prop,_def) , rename= False)
           data_Lag = np.loadtxt(os.path.join(dst_dir,prop,_def,_def+'_Lagrangian_Stress.dat')).tolist()
           def_Lag_data=JFData(description='Energy v.s. strain data', json_data= {'data':data_Lag},
             json_file_name=None,json_id=None,meta={})
           data_Phy = np.loadtxt(os.path.join(dst_dir,prop,_def,_def+'_Physical_Stress.dat')).tolist()
           def_Phy_data=JFData(description='Energy v.s. strain data', json_data= {'data':data_Phy},
             json_file_name=None,json_id=None,meta={})
           def_fig=JFData(description='Energy v.s. strain figure',
             ile_fmt='png', file_name=os.path.join(dst_dir,prop,_def, _def+'_Energy_Strain.png'),file_id=None)
           def_datafig=DataFigure(data=[def_Lag_data, def_Phy_data],figure=def_fig)
           deformations[_def]=def_datafig
       os.chdir(pwd)
       for f in ['EV_theta.dat','Result.json','stress-EV.png']:
           transfer_file(f, task_dir , os.path.join(dst_dir,prop) , rename= False)
       transfer_file(os.path.join(task_dir,'elc_stress','Mech2D.json'), task_dir , dst_dir , rename= False)
        
       data=np.loadtxt(os.path.join(dst_dir,prop,'EV_theta.dat')).tolist()
       ev_data=JFData(description='Angle dependent Young\'s modulus and Poisson\'s ratio figure', json_data= {'data':data},
             json_file_name=None,json_id=None,meta={})
       summary=Mechanics2dSummary.from_file(os.path.join(dst_dir,prop,'Result.json'))
       ev_fig=JFData(description='Angle dependent Young\'s modulus and Poisson\'s ratio figure',
             file_fmt='png', file_name=os.path.join(dst_dir,prop,'stress-EV.png'),file_id=None)
       ev_datafig=DataFigure(data=[ev_data],figure=ev_fig)
         
       ret['summary'] = summary
       ret['polar_EV'] = ev_datafig
       ret['deformations']=deformations
       #dumpfn(jsanitize(Elc2nd2d(**ret)),'test1.json')

    elif prop=='ssc_stress':
       log.debug('-'*20)
       log.info('Processing %s '%prop)
       log.debug(task_dir)
       log.debug(os.path.join(dst_dir,prop))
       with open("m2d.ana.log","wb") as out, open("m2d.ana.err","wb") as err:
            p=subprocess.Popen(["m2d","post","-a","stress","-p","ssc","--plot","-f","png"],stdout=out,stderr=err)
            p.communicate()
       sscs=map(os.path.basename,glob(os.path.join(task_dir,prop,'Def_*')) )
       os.chdir(pwd)
       create_path(os.path.join(dst_dir,prop))
       for ssc in sscs:
           log.debug('pwd: %s'%os.getcwd())
           task_infos=[]
           log.info('SSC direction: %s '%ssc)
           create_path(os.path.join(dst_dir,prop,ssc))
           transfer_file(ssc+'_Lagrangian_Stress.dat', os.path.join(task_dir,prop,ssc) , os.path.join(dst_dir,prop,ssc) , rename= False)
           transfer_file(ssc+'_Lagrangian_Stress.png', os.path.join(task_dir,prop,ssc) , os.path.join(dst_dir,prop,ssc) , rename= False)
           transfer_file(ssc+'_Physical_Stress.dat', os.path.join(task_dir,prop,ssc) , os.path.join(dst_dir,prop,ssc) , rename= False)
           SS_Lag=np.loadtxt(os.path.join(dst_dir,prop,ssc,ssc+'_Lagrangian_Stress.dat')).tolist()
           SS_Phy=np.loadtxt(os.path.join(dst_dir,prop,ssc,ssc+'_Physical_Stress.dat')).tolist()
           data=JFData(description='SS data', json_data= {'SS_Lagrangian':SS_Lag,'SS_Physical':SS_Phy},
                 json_file_name=None,json_id=None,meta={})
           fig=JFData(description='SS Lag figure',
             file_fmt='png', file_name=os.path.join(dst_dir,prop,ssc,ssc+'_Lagrangian_Stress.png'),file_id=None)
           data_fig=DataFigure(data=[data],figure=fig)
           ret['stress_strain'][ssc]=data_fig
       
            
    else:
       raise RuntimeError('Unknow combination of approach and property : %s '%(prop))

    transfer_file('Mech2D.json', os.path.join(task_dir,prop) , os.path.join(dst_dir,prop) , rename= False)
    meta=JFData(description='meta data',
             json_file_name=os.path.join(dst_dir,prop,'Mech2D.json'),json_id=None,meta={})
    ret['meta']=meta
    return ret

if __name__== '__main__':
   from matvirdkit.model.utils import test_path
   from datetime import datetime
   task_dir=os.path.join(test_path(),'alpha-P-R')
   dst_dir='m2d-1/mechanics'
   tasks_dir='m2d-1/tasks'
   
   create_path(dst_dir)
   ret1=mechanics2d_from_directory(task_dir,dst_dir,prop='elc_energy', code= 'vasp')
   print(ret1.keys())
   ret2=mechanics2d_from_directory(task_dir,dst_dir,prop='elc_stress', code= 'vasp')
   ret3=mechanics2d_from_directory(task_dir,dst_dir,prop='ssc_stress', code= 'vasp')
   print(ret3['stress_strain'])
   ret=Mechanics2d(elc2nd_stress=Elc2nd2d(**ret2),elc2nd_energy=Elc2nd2d(**ret1),stress_strain=ret3['stress_strain'])
   dumpfn(jsanitize(ret),'ret.json')
 
