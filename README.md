#  Matvird Tookit

matvirdkit stands for Material virtual design kit. This toolkit has been developed for 3 purpose. 

* Describing the data schema

* Parsing data from DFT calculation raw data

* Supplying API request information.

### Folders
```
matvirdkit
├── api
├── builder
├── creator
└── model

```

### description

*api*     api interface 

*builder* basic parser for data generating

*creator* used for writing data into database

*model*   define the model of `material`,  `task` and `properties`
         

basic rules:

* properties definition: 
 
if you want to add a set of properties named  *Abc* into the model. You may add a new class
for the new set *Abc* and corresponding document *AbcDoc*, e.g.

```
from typing import ClassVar, Dict
from pydantic import BaseModel, Field
from matvirdkit.model.provenance import LocalProvenance
from matvirdkit.model.common import MatvirdBase

class Abc(MatvirdBase):
    provenance: Dict[str,LocalProvenance] = Field({}, description="Property provenance, make sure keep this!")
    sub_property_1: float = Field(...)
    sub_property_2: int = Field(...)

class AbcDoc(BaseModel):
    """
    ABC property block
    """
    property_name: ClassVar[str] = "Abc"
    abc: Dict[str,Abc] = Field({}, description='abc information')
```

or, you may just add the *sub_prop* to the existed property class. For example,
we can add new property *update_time* to the set *Abc* above. 

```
from typing import ClassVar, Dict
from pydantic import BaseModel, Field
from matvirdkit.model.provenance import LocalProvenance
from matvirdkit.model.common import MatvirdBase

class Abc(MatvirdBase):
    provenance: Dict[str,LocalProvenance] = Field({}, description="Property provenance, make sure keep this!")
    sub_property_1: float = Field(...)
    sub_property_2: int = Field(...)
    update_time: str = Field(...)

class AbcDoc(BaseModel):
    """
    ABC property block
    """
    property_name: ClassVar[str] = "Abc"
    abc: Dict[str,Abc] = Field({}, description='abc information')
```
To set up a instance of AbcDoc, we can use the following code:

```
     doc=AbcDoc(
      abc={'label': Abc(sub_property_1=0.2, sub_property_2=0.3, update_time= str(datetime.now()) ,description='This is a test')},
      provenance={'label':{}}
     )
     print(doc.dict())
```
Generally speaking, the key of Dict for property AbcDoc.abc can be functional of calculation or calcuation method,
such as "GGA-PBE", "GW", "PBE+U".

* tasks definition: 
 
  Currently, we only support the VASP task. 
