""" Core definition of a Provenance Document """
import warnings
from collections import defaultdict
from datetime import datetime
from typing import ClassVar, Dict, List, Optional, Union

#from pybtex.database import BibliographyData, parse_string
from pydantic import BaseModel, EmailStr, Field, validator,constr
from matvirdkit.model.properties import PropertyDoc,PropertyOrigin
from matvirdkit.model.common import Reference,DOI

class ProvenanceDoc(PropertyDoc):
    """
    A provenance property block
    """

    property_name: ClassVar[str] = "provenance"

if __name__=='__main__': 
   pd=ProvenanceDoc(created_at=datetime.now(),
      origins=[PropertyOrigin(name='band',task_id='task-1123'),
               PropertyOrigin(name='band',task_id='task-1124'),
               ],
      references=[Reference(bibstr="""Haidi Wang, Qingqing Feng, Xingxing Li, Jinlong Yang, "High-Throughput Computational Screening for Bipolar Magnetic Semiconductors", Research, vol. 2022, Article ID 9857631, 8 pages, 2022.""",doi=DOI(value="10.34133/2022/9857631"))],
      material_id='rsb-1',
      warnings = ['PBE low kpoints','low encut'],
      remarks = ['nature paper'],
      tags =['High temperature'],
      authors=[{'name':'haidi','email':'haidi@hfut.edu.cn'},{'name':'zhangsan','email':'zhangsan@ustc.edu.cn'}]
      )
#,database_IDs={'icsd':['11023'],'mp':['mp-771246']})
   print(pd.json())
   from monty.serialization import loadfn,dumpfn
   from matvirdkit.model.utils import jsanitize,ValueEnum
   dumpfn(jsanitize(pd),'t.json',indent=4)
