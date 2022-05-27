import inspect

def get_current_function_name():
    return inspect.stack()[1][3]

class A():
    def __init__(self,var=[]):
        self._ldoc=var
    
    @property
    def ldoc(self):
        return self._ldoc

    #@ldoc.setter
    #def ldoc(self,value):
    #    if value not in self._ldoc:
    #       print(type(self._ldoc))
    #       self._ldoc.append(value)

    def sets(self):
        self._ldoc.append(23)
    def function_one(self):
        print("%s.%s invoked"%(self.__class__.__name__, get_current_function_name()))




a=A()
print(a.ldoc)
a.sets()
print(a.ldoc)
a.function_one()
