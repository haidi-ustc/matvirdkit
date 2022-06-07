from uuid import uuid4
from snowflake import client as SFClient

def get_snowflake_id(prefix=''):
    host = 'localhost'
    port = 8910
    SFClient.setup(host, port)
    if prefix:
       return prefix+'-'+str(SFClient.get_guid())
    else:
       return str(SFClient.get_guid())

def get_uuid(prefix=''):
    if prefix:
       return prefix+'-'+str(uuid4())
    else:
       return str(uuid4())

if __name__ == '__main__':
  print(get_snowflake_id())
  print(get_uuid())
