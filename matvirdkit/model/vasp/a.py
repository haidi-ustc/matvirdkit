from matvirdkit.model.vasp.task import TaskDocument as VaspTaskDocument
import importlib

m='matvirdkit.model.vasp.task'
m1=importlib.import_module(m,'TaskDocument')
print(dir(m1))
