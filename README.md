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


### repository

Generally, the repository location can be  `~/.repository`, which can be setted in then `~/.env`.
The directory tree of repository:
```
.
├── datasets
│   └── mech2d
│       └── m2d-2
│           ├── 1794cb78e03147af65fb3a4f2110b8f92b915f12-mp-755811-dos.json
│           ├── c271afe290f282540eccf92dbd03530df9070de9-mp-755811-dos.png
│           ├── m2d-2.json
│           └── mechanics
│               ├── elc_energy
│               │   ├── Def_1
│               │   │   ├── Def_1_Energy.dat
│               │   │   └── Def_1_Energy_Strain.png
│               │   ├── Def_2
│               │   │   ├── Def_2_Energy.dat
│               │   │   └── Def_2_Energy_Strain.png
│               │   ├── Def_3
│               │   │   ├── Def_3_Energy.dat
│               │   │   └── Def_3_Energy_Strain.png
│               │   ├── Def_4
│               │   │   ├── Def_4_Energy.dat
│               │   │   └── Def_4_Energy_Strain.png
│               │   ├── energy-EV.png
│               │   ├── EV_theta.dat
│               │   ├── Mech2D.json
│               │   └── Result.json
│               ├── elc_stress
│               │   ├── Def_1
│               │   │   ├── Def_1_Lagrangian_Stress.dat
│               │   │   ├── Def_1_Lagrangian_Stress.png
│               │   │   └── Def_1_Physical_Stress.dat
│               │   ├── Def_2
│               │   │   ├── Def_2_Lagrangian_Stress.dat
│               │   │   ├── Def_2_Lagrangian_Stress.png
│               │   │   └── Def_2_Physical_Stress.dat
│               │   ├── EV_theta.dat
│               │   ├── Mech2D.json
│               │   ├── Result.json
│               │   └── stress-EV.png
│               └── ssc_stress
│                   ├── Def_bi
│                   │   ├── Def_bi_Lagrangian_Stress.dat
│                   │   ├── Def_bi_Lagrangian_Stress.png
│                   │   └── Def_bi_Physical_Stress.dat
│                   ├── Def_xx
│                   │   ├── Def_xx_Lagrangian_Stress.dat
│                   │   ├── Def_xx_Lagrangian_Stress.png
│                   │   └── Def_xx_Physical_Stress.dat
│                   ├── Def_xy
│                   │   ├── Def_xy_Lagrangian_Stress.dat
│                   │   ├── Def_xy_Lagrangian_Stress.png
│                   │   └── Def_xy_Physical_Stress.dat
│                   ├── Def_yy
│                   │   ├── Def_yy_Lagrangian_Stress.dat
│                   │   ├── Def_yy_Lagrangian_Stress.png
│                   │   └── Def_yy_Physical_Stress.dat
│                   └── Mech2D.json
├── meta
└── tasks
    ├── qe
    │   └── 3d3616d4-49f8-4c97-9084-5846e8dbc903
    └── vasp
        ├── 007d2c20b64b678e0d0fa1ff3f6950c0ceef8d5b
        │   ├── 1477eeae6f878e441588f86c42857c2b34580624-CONTCAR.gz
        │   ├── 3fcf67030e2044f6a74da9611778c0d9e7281642-CONTCAR.json
        │   ├── 81c8a4ade5c45aef52bb2eea3cdbf118d20c38bc-vasprun.xml.gz
        │   ├── 832f638ae8029d0ca099be0aa08b8519e0e98548-vasprun.xml.json
        │   └── task.json
        ├── 0446e56c-8f9c-49b9-9d09-a1bcfb24e585
        ├── 06a7163b7b14404c93f985bdf0079ff20edbefb7
        │   ├── 771be761164e4c5841e0eca173bddb4a01b410a1-CONTCAR.json
        │   ├── a6349f104781f34f1459d1ba6124cbebe291ef7d-vasprun.xml.json
        │   ├── d67ee17be51577b948a74dfd7769562cb3733970-vasprun.xml.gz
        │   ├── f6e1b58a62479f6db561a63af912ff8cb904af1d-CONTCAR.gz
        │   └── task.json
        ├── 071a0189883132bd8541b9430d073ffca5111860
        │   ├── 283126d3546db1a51aea3e9a2467ba893c0630d5-vasprun.xml.json
        │   ├── 4d8ff43e2ebabefa45eb204c308ded6eedb93ef9-CONTCAR.json
        │   ├── b3f32ff8e4d1a9fd9d3c489102e557f7fe9de57f-vasprun.xml.gz
        │   ├── cabd3d9c80a6ca864fc37dc7ab2932528c64b880-CONTCAR.gz
        │   └── task.json
        ├── 074cb012-764b-489f-bd0a-7dda570b907e
```


