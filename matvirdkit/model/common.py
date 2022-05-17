""" Core definition of a Provenance Document """
import warnings
from collections import defaultdict
from datetime import datetime
from typing import ClassVar, Dict, List, Optional, Union, Tuple, Any

#from pybtex.database import BibliographyData, parse_string
from pydantic import BaseModel, EmailStr, Field, validator,constr
from matvirdkit.model.utils import ValueEnum

class JFData(BaseModel):
     description : Optional[str]= Field('',description='Data description')
     # format can be : png, jpg / json, yaml / txt  / mp4, avi 
     file_fmt: Optional['str'] = Field(None,description='file format of, which will be linked with f_id')
     file_id: Optional['str'] = Field(None,description='If the file is saved in the mongoDB by file then the corresponding ID will be recorded')
     file_name: Optional['str'] = Field(None,description='The file name for figure or raw data that will be saved in Mongo File')
     json_id: Optional['str'] = Field(None,description='If the data is saved in the mongoDB by json then the corresponding ID will be recorded')
     json_file_name: Optional['str'] = Field(None,description='The file name for json data that will be saved in Mongo directly by ref ID')
     json_data: Optional[Dict] = Field(None,description='json data that will be saved in current data structure')
     meta : Any = Field({})

class DataFigure(BaseModel):
    description : Optional[str] = Field('', description='data information')
    data: JFData = Field(...,description='data')
    figure: JFData = Field(...,description='figure')
    link: str = Field(None)

class JData(BaseModel):
    description : Optional[str] = ''
    fmt: str = Field('json', description='data format ')
    j_id: str = Field(None, description='file name or entry id in mongo DB')

class FData(BaseModel):
    description : Optional[str] = ''
    fmt: str = Field('png', description='file format ')
    f_id: str = Field(None, description='file name or entry id in mongo DB')

class Data(BaseModel):
    description : Optional[str] = 'figure and data '
    fdata: List[Dict[str,Tuple[List[JData],List[FData]]]] = Field(None,
                                      description='A dict record the f_id and corresponding j_id')

class Meta(BaseModel):
      description : Optional[str] = 'Meta information'
      user : str
      machine: str

class Database(ValueEnum):
    """
    Database identifiers for provenance IDs
    """

    ICSD = "icsd"
    Pauling_Files = "pf"
    COD = "cod"
    MP = 'mp'
    OQMD = 'oqmd'
    MatPedia2D='2dmatpedia'
    C2DB='c2db'

class ReferenceDB(BaseModel):
    database_IDs: Dict[str, List[str]] = Field(
        dict(), description="Database IDs corresponding to this material"
    )

class Author(BaseModel):
    """
    Author information
    """
    name: str = Field(None)
    email: EmailStr = Field(None)

class DOI(BaseModel):
      value: constr(regex=r"^10\.\d{4,9}/[-._;()/:a-zA-Z0-9]+$")

class Reference(BaseModel):
    bibstr: str = Field(
       ..., description="Bibtex reference strings for this material"
    )
    doi: DOI = Field(
       ..., description="doi strings for this material"
    )

class History(BaseModel):
    """
    History of the material provenance
    """

    name: str
    url: str
    description: Optional[Dict] = Field(
        None, description="Dictionary of exra data for this history node"
    )


if __name__=='__main__':
   xfd=Data(fdata=[{"XRD-Cu-Alpha":
              [
              [JData(j_id='/home/test/xrd.json')],
              [
              FData(f_id='/home/test/XRD.png',fmt='png'),
              FData(f_id='/home/test/XRD.jpg',fmt='jpg',description='jpg format')
              ],
              ]}
             ]
                   )
   print(xfd.json())
   from monty.serialization import loadfn,dumpfn
   dumpfn(xfd.dict(),'t.json')
