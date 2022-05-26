""" Core definition of a Provenance Document """
import warnings
from collections import defaultdict
from datetime import datetime
from typing import ClassVar, Dict, List, Optional, Union, Tuple, Any

#from pybtex.database import BibliographyData, parse_string
from pydantic import BaseModel, EmailStr, Field, validator,constr
from matvirdkit.model.utils import ValueEnum

class MatvirdBase(BaseModel):
      description : Optional[str] = ''
      label: Optional[str] = ''
      link: List[str] = Field([])
      meta: Dict[str,Any]  = Field({}, description='meta information')

class JFData(MatvirdBase):
     """
     Json File Data --> JFData. 
     This class is used to store several types of data
     file_fmt : str   The file format can be png, jpg / json, yaml / txt  / mp4, avi  / 'txt.gz'
     file_id  : str   This value will be set when data is inserted into MongoDB GridFS system
     file_name: str   This file will be saved into GridFS
     json_id :  str   This value will be set when data is inserted  into MongoDB GridFS system
     json_file_name: str   If this value is set, then it means the corresponding file will  be  saved into GridFS, and the entry id will be saved in json_id 
     json_data: dict   If this value is set, the data will be saved directly into the MongoDB in JFData entry. The json_data has priority compared with json_file_name

     1. General txt data. For example, we can save the OUTCAR via following command:
        JFData(description='This is OUTCAR file',
               file_fmt = 'txt.gz', 
               file_id  = '',  
               file_name= '2eaf9fas0xa23-OUTCAR.gz',
               json_id  = '', 
               json_file_name ='ada92fdasl02x.json', 
               json_data = {} ) 
                
     2. Json data type 1.
        JFData(description='This is json file',
               file_fmt = 'json', 
               file_id  = '', 
               file_name= ''
               json_id  = '',
               json_file_name ='ada92fdasl02x.json', 
               json_data = {} ) 

     3. Json data type 2.
        JFData(description='This is json file',
               file_fmt = 'json', 
               file_id  = '', 
               file_name= ''
               json_id  = '',
               json_file_name ='', 
               json_data = {'a':1,'b':2} ) 

     4. figure file. Here we only store the figure file and the corresponding data for plotting will not be saved.
        JFData(description='This is figure file',
               file_fmt = 'png', 
               file_id  = '', 
               file_name= './dataset/bms-1/dos.png'
               json_id  = '',
               json_file_name ='', 
               json_data = {} ) 
     """
     file_fmt: Optional['str'] = Field('',description='file format of, which will be linked with f_id')
     file_id: Optional['str'] = Field('',description='If the file is saved in the mongoDB by file then the corresponding ID will be recorded')
     file_name: Optional['str'] = Field('',description='The file name for figure or raw data that will be saved in Mongo File')
     json_id: Optional['str'] = Field('',description='If the data is saved in the mongoDB by json then the corresponding ID will be recorded')
     json_file_name: Optional['str'] = Field('',description='The file name for json data that will be saved in Mongo directly by ref ID')
     json_data: Optional[Dict] = Field({},description='json data that will be saved in current data structure')

class DataFigure(BaseModel):
    data: List[JFData] = Field(None,description='data')
    figure: JFData = Field(...,description='figure')

class Meta(BaseModel):
      description : Optional[str] = Field(None,description='Meta information')
      user : Optional [ str ]
      machine: Optional[ str ]
      cpuinfo: Optional[ Dict ]

class MetaDoc(BaseModel):
      property_name: ClassVar[str] = "meta"
      source: List[Meta] = Field([],description='list of sources')


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

class Source(BaseModel):
      description : Optional[str] =  Field(None,description='Meta information')
      db_name: ReferenceDB = Field(...,description='database name')
      material_id: str = Field(...,description='material id')
      material_url: str = Field(...,description='material url')

class SourceDoc(BaseModel):
      property_name: ClassVar[str] = "source"
      source: List[Source] = Field([],description='list of sources')

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

