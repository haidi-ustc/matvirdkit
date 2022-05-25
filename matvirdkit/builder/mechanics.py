import os
import subprocess
import numpy as np
from uuid import uuid4
from glob import glob
from monty.serialization import loadfn,dumpfn
from matvirdkit import log
from matvirdkit.model.mechanics import Mechanics2D, Mechanics2DDoc,Mechanics2DSummary
from matvirdkit.model.common import DataFigure,JFData
from matvirdkit.model.utils import create_path,transfer_file,jsanitize
from matvirdkit import REPO_DIR as repo_dir
from matvirdkit.builder.task import parsing_task
from matvirdkit.model.properties import PropertyOrigin

def get_mechanicis2D_from_directory(task_dir,prop_dir,lprops=None):
    ret={'summary':{},
         'polar_EV':{},
         'meta':{},
         'stress_strain': {}
         }
    pwd=os.getcwd()
    lprops= lprops if lprops else ['elc_energy','elc_stress','ssc_stress']
    task_dirs=[ os.path.join(task_dir,prop) for prop in lprops if \
                os.path.isdir(os.path.join(task_dir,prop))]
    log.debug("task_dirs: %s"%('\n'+'\n'.join(task_dirs)) ) 
    #log.info("task_dirs: %s"%('\n'+'\n'.join(task_dirs)) ) 
    origins=[]
    for task_dir in task_dirs:
        os.chdir(task_dir)
        prop=os.path.basename(task_dir) 
        task_dir=task_dir.replace(prop,'')
        if prop=='elc_energy':
           log.debug('-'*20)
           log.info('Processing %s '%prop)
           log.debug(task_dir)
           log.debug(os.path.join(prop_dir,prop))
           with open("m2d.ana.log","wb") as out, open("m2d.ana.err","wb") as err:
                p=subprocess.Popen(["m2d","post","--plot","-f","png"],stdout=out,stderr=err)
                p.communicate()
           tasks=glob(os.path.join(os.getcwd(),'Def_*','Def_*_[0-9][0-9][0-9]') )
           tasks.sort()
           log.debug('pwd: %s'%os.getcwd())
           log.debug('\n'+'\n'.join(tasks))
           log.info('Parsing task ...')
           task_ids=[]
           for task in tasks: 
               log.info('%s'%task)
               log.info('/'.join(task.split('/')[-2:]))
               tag='/'.join(task.split('/')[-2:])
               task_id=parsing_task(task_dir=task,tags=[tag])
               task_ids.append(task_id)
           log.debug('task ids\n'+'\n'.join(task_ids))
           os.chdir(pwd)
           create_path(os.path.join(prop_dir,prop))
           transfer_file('EV_theta.dat', task_dir , os.path.join(prop_dir,prop) , rename= False)
           transfer_file('Result.json', task_dir , os.path.join(prop_dir,prop) , rename= False)
           transfer_file('energy-EV.png', task_dir , os.path.join(prop_dir,prop) , rename= False)
           transfer_file(os.path.join(task_dir,'elc_energy','Mech2D.json'), task_dir , prop_dir , rename= False)
            
           EV=np.loadtxt(os.path.join(prop_dir,prop,'EV_theta.dat')).tolist()
           data_link=str(uuid4())
           data=JFData(description='EV data', json_data= {'EV':EV},
                 json_file_name=None,json_id=None,meta={},link=[data_link])
           summary=Mechanics2DSummary.from_file(os.path.join(prop_dir,prop,'Result.json'))
           fig_link=str(uuid4())
           fig=JFData(description='EV figure',
                 file_fmt='png', file_name=os.path.join(prop_dir,prop,'Result.json'),file_id=None,link=[fig_link])
           data_fig=DataFigure(data=[data],figure=fig)
           origins.extend([PropertyOrigin(name='',task_id=task_id,link=[data_link,fig_link]) for task_id in task_ids])
           #print(data)
           #print(summary)
           #print(fig)
           ret['summary']['elc_energy'] = summary
           ret['polar_EV']['elc_energy'] = data_fig
           
        elif prop=='elc_stress':
           log.debug('-'*20)
           log.info('Processing %s '%prop)
           log.debug(task_dir)
           log.debug(os.path.join(prop_dir,prop))
           with open("m2d.ana.log","wb") as out, open("m2d.ana.err","wb") as err:
                p=subprocess.Popen(["m2d","post","-a","stress","-p","elc","--plot","-f","png"],stdout=out,stderr=err)
                p.communicate()
           tasks=glob(os.path.join(os.getcwd(),'Def_*','Def_*_[0-9][0-9][0-9]') )
           tasks.sort()
           log.debug('pwd: %s'%os.getcwd())
           log.debug('\n'+'\n'.join(tasks))
           log.info('Parsing task ...')
           task_ids=[]
           for task in tasks: 
               log.info('%s'%task)
               log.info('/'.join(task.split('/')[-2:]))
               tag='/'.join(task.split('/')[-2:])
               task_id=parsing_task(task_dir=task,tags=[tag])
               task_ids.append(task_id)
           os.chdir(pwd)
           create_path(os.path.join(prop_dir,prop))
           create_path(os.path.join(prop_dir,prop))
           transfer_file('EV_theta.dat', task_dir , os.path.join(prop_dir,prop) , rename= False)
           transfer_file('Result.json', task_dir , os.path.join(prop_dir,prop) , rename= False)
           transfer_file('stress-EV.png', task_dir , os.path.join(prop_dir,prop) , rename= False)
           transfer_file(os.path.join(task_dir,'elc_stress','Mech2D.json'), task_dir , prop_dir , rename= False)
           EV=np.loadtxt(os.path.join(prop_dir,prop,'EV_theta.dat')).tolist()
           data_link=str(uuid4())
           data=JFData(description='EV data', json_data= {'EV':EV},
                 json_file_name=None,json_id=None,meta={})
           summary=Mechanics2DSummary.from_file(os.path.join(prop_dir,prop,'Result.json'))
           fig_link=str(uuid4())
           fig=JFData(description='EV figure',
                 file_fmt='png', file_name=os.path.join(prop_dir,prop,'Result.json'),file_id=None)
           
           data_fig=DataFigure(data=[data],figure=fig)
           origins.extend([PropertyOrigin(name='',task_id=task_id,link=[data_link,fig_link]) for task_id in task_ids])
           ret['summary']['elc_stress'] = summary
           ret['polar_EV']['elc_stress'] = data_fig
        elif prop=='ssc_stress':
           log.debug('-'*20)
           log.info('Processing %s '%prop)
           log.debug(task_dir)
           log.debug(os.path.join(prop_dir,prop))
           with open("m2d.ana.log","wb") as out, open("m2d.ana.err","wb") as err:
                p=subprocess.Popen(["m2d","post","-a","stress","-p","ssc","--plot","-f","png"],stdout=out,stderr=err)
                p.communicate()
           sscs=map(os.path.basename,glob(os.path.join(task_dir,prop,'Def_*')) )
           os.chdir(pwd)
           create_path(os.path.join(prop_dir,prop))
           ret['stress_strain']['ssc_stress'] = {}
           for ssc in sscs:
               tasks=glob(os.path.join(task_dir,prop,ssc,'Def_*_[0-9][0-9][0-9]') )
               tasks.sort()
               log.debug('pwd: %s'%os.getcwd())
               log.debug('\n'+'\n'.join(tasks))
               log.info('Parsing task ...')
               task_ids=[]
               for task in tasks: 
                   log.info('%s'%task)
                   log.info('/'.join(task.split('/')[-2:]))
                   tag='/'.join(task.split('/')[-2:])
                   task_id=parsing_task(task_dir=task,tags=[tag])
                   task_ids.append(task_id)
               log.info('SSC direction: %s '%ssc)
               create_path(os.path.join(prop_dir,prop,ssc))
               transfer_file(ssc+'_Lagrangian_Stress.dat', os.path.join(task_dir,prop,ssc) , os.path.join(prop_dir,prop,ssc) , rename= False)
               transfer_file(ssc+'_Lagrangian_Stress.png', os.path.join(task_dir,prop,ssc) , os.path.join(prop_dir,prop,ssc) , rename= False)
               transfer_file(ssc+'_Physical_Stress.dat', os.path.join(task_dir,prop,ssc) , os.path.join(prop_dir,prop,ssc) , rename= False)
               SS_Lag=np.loadtxt(os.path.join(prop_dir,prop,ssc,ssc+'_Lagrangian_Stress.dat')).tolist()
               SS_Phy=np.loadtxt(os.path.join(prop_dir,prop,ssc,ssc+'_Physical_Stress.dat')).tolist()
               data_link=str(uuid4())
               data=JFData(description='SS data', json_data= {'SS_Lagrangian':SS_Lag,'SS_Physical':SS_Phy},
                     json_file_name=None,json_id=None,meta={},
                     link=[data_link])
               fig_link=str(uuid4())
               fig=JFData(description='SS Lag figure',
                 file_fmt='png', file_name=os.path.join(prop_dir,prop,ssc,ssc+'_Lagrangian_Stress.png'),file_id=None,link=[fig_link])
               data_fig=DataFigure(data=[data],figure=fig)
               ret['stress_strain']['ssc_stress'][ssc]=data_fig
               origins.extend([PropertyOrigin(name='',task_id=task_id,link=[data_link,fig_link]) for task_id in task_ids])
                
        else:
           raise RuntimeError('Unknow combination of approach and property : %s '%(prop))

        transfer_file('Mech2D.json', os.path.join(task_dir,prop) , os.path.join(prop_dir,prop) , rename= False)
        meta=JFData(description='meta data',
                 json_file_name=os.path.join(prop_dir,prop,'Mech2D.json'),json_id=None,meta={})
        ret['meta'][prop]=meta
    return ret,origins

if __name__== '__main__':
   from matvirdkit.model.utils import test_path
   from datetime import datetime
   task_dir=os.path.join(test_path(),'alpha-P-R')
   #print(task_dir)
   prop_dir='m2d-1/mechanics'
   tasks_dir='m2d-1/tasks'
   
   create_path(prop_dir)
   ret,origins=get_mechanicis2D_from_directory(task_dir,prop_dir,lprops=None)
   dumpfn(jsanitize(ret),'mech2.json',indent=4)
   mechanics2d=Mechanics2D(**ret,description='2d test')
   mechdoc=Mechanics2DDoc(mechanics2d=[mechanics2d],
                          material_id='m2d-1',
                          created_at=datetime.now(),
                          origins=origins )
   dumpfn(jsanitize(mechdoc.dict()),'mech1.json',indent=4)
