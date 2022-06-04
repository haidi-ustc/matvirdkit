import os
import shutil
from uuid import uuid4
from typing import Dict,Union
from importlib import import_module
from monty.serialization import loadfn,dumpfn
from matvirdkit import log,TASKS_DIR,REPO_DIR
from matvirdkit.model.utils import jsanitize
from matvirdkit.model.utils import create_path,sepline
#from matvirdkit.model.vasp.task import TaskDocument as VaspTaskDocument
from matvirdkit.model.utils import sha1encode,task_tag

class TaskDocument():
      def __init__(self,code):
          self.code = code
          self.module_str = f'matvirdkit.model.{self.code}.task'
          self.hook = None
          self.set_hook()

      def set_hook(self):
          module=import_module(self.module_str)
          self.hook=getattr(module,'TaskDocument')

      def from_dict(self,**kwargs):
          return self.hook(**kwargs) 
          
      def from_directory(self,task_id,task_dir,dst_dir,**kwargs):
          log.debug('task_id %s'%task_id)
          log.debug('task_dir %s'%task_dir)
          log.debug('task_dst %s'%dst_dir)
          return self.hook.from_directory(task_id=task_id,
                                           task_dir=task_dir,
                                           dst_dir=dst_dir,**kwargs)

class GeneralTask():
    def __init__(self,task_dir,code,repo_dir=None,**kwargs):
        self.task_dir= os.path.abspath(task_dir)
        self.code = code
        self.root_dst_dir = os.path.abspath(repo_dir) if repo_dir else os.path.join(TASKS_DIR,code)
        self.tmp_task_id = str(uuid4()) 
        self.task_id = None
        self.tmp_dst_dir = os.path.join(self.root_dst_dir,self.tmp_task_id)
        self.dst_dir = None
        self.kwargs = kwargs
        self._set_tmp_dst_dir()

    def set_task_info(self, task_id):
        self.task_id = task_id
        self.dst_dir = os.path.join(self.root_dst_dir, self.task_id)

    def _rename(self):
        assert self.dst_dir is not None
        if os.path.isdir(self.dst_dir):
           shutil.rmtree(self.dst_dir)
        shutil.move(self.tmp_dst_dir, self.dst_dir)

    def _set_tmp_dst_dir(self) -> None:
        if os.path.isdir(self.tmp_dst_dir):
           pass
        else:
           backup=self.kwargs.get('backup',False)
           create_path(self.tmp_dst_dir,backup=backup) 

    def validated_task(self,task_encode,f_task='task.json'):
        if not task_encode:
           return False
        fname=os.path.join(self.root_dst_dir,task_encode,f_task)
        log.debug('fname %s'%fname)
        if os.path.isfile(fname):
           try:
              ret=loadfn(fname,cls=None)          
              _hash = self.task_hash(ret['input'])
              if _hash == task_encode:
                 # rewrite the task_id , maker sure the directory 
                 # name is the task_id
                 ret['task_id'] = _hash
                 dumpfn(ret,fname)
                 return True
              else:
                 return False
           except:
              return False          
        else:
           return False

   
    def parse_task(self,mode):

        _td=TaskDocument(code=self.code)
        assert mode in ['skip','new']
        if mode=='skip':
           log.debug("task.json: %s"%os.path.join(self.dst_dir,'task.json'))
           data=loadfn(os.path.join(self.dst_dir,'task.json'),cls=None)
           return _td.from_dict(**data)
        else:
           return _td.from_directory(task_id=self.tmp_task_id,
                                  task_dir=self.task_dir,
                                  dst_dir=self.tmp_dst_dir,**self.kwargs)

    def get_task(self,**kwargs):
        tag=self.task_tag(status='check')
        if tag:
           task_encode=tag.get('encode','')
           log.info('task_encode %s'%task_encode)
           if self.validated_task(task_encode):
              log.debug('From json !')
              self.set_task_info(task_encode)
              td = self.parse_task(mode='skip')
              log.debug(sepline(std=False))
              log.debug('tmp_task_id: %s'%self.tmp_task_id)
              log.debug('pem_task_id: %s'%self.task_id)
              shutil.rmtree(self.tmp_dst_dir)
              return task_encode, td.calc_type
           else:
              log.debug('From directory !')
              td = self.parse_task(mode='new')
        else:
           log.debug('From directory !')
           td = self.parse_task(mode='new')

        calc_type=td.calc_type
        td=jsanitize(td)
        info=td['input']
        task_encode = self.task_hash(info)
        td['task_id']=task_encode
        self.set_task_info(task_encode)         
        self._rename() 
        log.debug(sepline(std=False))
        log.debug('tmp_task_id: %s'%self.tmp_task_id)
        log.debug('pem_task_id: %s'%self.task_id)
        if kwargs.get('indent',False):
           dumpfn(td,os.path.join(self.dst_dir,'task.json'),indent=4)
        else:
           dumpfn(td,os.path.join(self.dst_dir,'task.json'))
        log.info('write tag.json file')
        self.task_tag(status='write',info={'encode':task_encode})
        return task_encode, calc_type

    def task_tag(self, status : str,info : Dict = {}):
        if status=='write':
           dumpfn(info,os.path.join(self.task_dir,'tag.json')),
           return None
        elif status=='check':
           if os.path.isfile(os.path.join(self.task_dir,'tag.json')):
              return loadfn(os.path.join(self.task_dir,'tag.json'))
           else:
              return None
        elif status=='remove':
           if os.path.isfile(os.path.join(self.task_dir,'tag.json')):
              os.remove(os.path.join(self.task_dir,'tag.json'))
              return None
           else:
              return None
        else:
           return None

    def task_hash(self,info):
        return sha1encode(info)

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
   #task_dir=os.path.join(test_path(),'relax')
   #encode,calc_type=VaspTask(task_dir,tags=['relax']) 
   #print('encode : %s  calc_type: %s'%(encode,calc_type))


   from matvirdkit.builder.task import TaskDocument
   from monty.serialization import loadfn,dumpfn
   from matvirdkit.model.utils import jsanitize
   from matvirdkit.model.utils import test_path
   from matvirdkit.model.utils import test_path,create_path
   import os
   from uuid import uuid4
   
   relax_dir=os.path.join('./relax')
   #-------------------------test--------------------------
   #td=TaskDocument('vasp')
   #out_dir=os.path.join('tasks',str(uuid4()))
   #create_path(out_dir)
   #doc1=td.from_directory(task_id='t-1',task_dir=relax_dir,dst_dir=out_dir)
   #dumpfn(jsanitize(doc1),'task1.json')
   #doc2=td.from_dict(**jsanitize(doc1))
   #dumpfn(jsanitize(doc2),'task2.json')
   #-------------------test--------------------
   gt=GeneralTask(task_dir=relax_dir,code='vasp',repo_dir='./tasks')
   encode, calc_type=gt.get_task(indent=True) 
   print("calc: %s  ID: %s"%(calc_type, encode)) 
