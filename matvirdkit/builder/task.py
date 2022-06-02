import os
import shutil
from uuid import uuid4
from monty.serialization import loadfn,dumpfn
from matvirdkit import log,REPO_DIR 
from matvirdkit.model.utils import jsanitize
from matvirdkit.model.utils import create_path
from matvirdkit.model.vasp.task import TaskDocument as VaspTaskDocument
from matvirdkit.model.utils import sha1encode,task_tag

def VaspTask(task_dir,repo_dir=REPO_DIR,**kwargs):
      
    if os.path.isdir(repo_dir):
       pass
    else:
       create_path(repo_dir,backup=False) 
    log.info('Start')
    pwd=os.getcwd()
    log.debug('Current dir: %s'%pwd)
    log.debug('Parsing Task from : %s'%task_dir)
    os.chdir(repo_dir)
    task_id = str(uuid4())
    log.info('Temperory task id is : %s'%task_id)
    # tasks-->vasp-->
    out_dir=os.path.join('tasks','vasp',task_id)

    log.debug('Temperory dir: %s'%(out_dir))
    create_path(out_dir)
    td=VaspTaskDocument.from_directory(task_id=task_id,
                                  task_dir=task_dir,
                                  dst_dir=out_dir,**kwargs)
    calc_type =  td.calc_type
    td=jsanitize(td)
    encode=sha1encode(td['input'])
    log.info('Self-encode task id is : %s'%encode)
    td['task_id']=encode
    encode_dir=os.path.join('tasks','vasp',encode)
    if os.path.isdir(encode_dir):
       log.debug('Delete temp. dir: %s'%(out_dir))
       shutil.rmtree(out_dir)
    else:
       log.debug('Rename dir: %s to %s'%(out_dir,encode_dir))
       shutil.move(out_dir,encode_dir)
       info={'path':os.path.abspath(out_dir.replace(out_dir,encode_dir)),
              'encode': encode}
       dumpfn(td,os.path.join(encode_dir,'task.json'),indent=4)
       task_tag(task_dir,status='write',info=info)
     
    os.chdir(pwd)
    log.info('finished!')
    return encode, calc_type

if __name__ == '__main__':
   from matvirdkit.model.utils import test_path
   task_dir=os.path.join(test_path(),'relax')
   encode,calc_type=VaspTask(task_dir,tags=['relax']) 
   print('encode : %s  calc_type: %s'%(encode,calc_type))
