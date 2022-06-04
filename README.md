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
 
if you want to add a set of properties named  *A* into the model. You may add a new class
for the new set *A* and corresponding document *ADoc*, e.g.

```
class A(MatvirdBase):
    provenance: Dict[str,LocalProvenance] = Field({}, description="Property provenance, make sure keep this!")
    sub_property_1: float = Field(...)
    sub_property_2: int = Field(...)

class ADoc(BaseModel):
    """
    A property block
    """
    property_name: ClassVar[str] = "A"
    bms: Dict[str,A] = Field({}, description='A information')
```

or, you may just add the *sub_prop* to the existed property class. For example,
we can add new property *update_time* to the set *A* above. 

```
class A(MatvirdBase):
    provenance: Dict[str,LocalProvenance] = Field({}, description="Property provenance, make sure keep this!")
    sub_property_1: float = Field(...)
    sub_property_2: int = Field(...)
    update_time: str = Filed(...)

class ADoc(BaseModel):
    """
    A property block
    """
    property_name: ClassVar[str] = "A"
    bms: Dict[str,A] = Field({}, description='A information')
```

