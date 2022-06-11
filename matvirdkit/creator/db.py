import itertools
import json
import socket
from multiprocessing import Pool
import numpy as np
import gridfs
import pymongo
from pymongo.errors import ServerSelectionTimeoutError, OperationFailure
from bson.objectid import ObjectId
import ssl as SSL
from monty.serialization import loadfn,dumpfn
from monty.json import MSONable
from matvirdkit import MONGO_HOST, MONGO_PORT, MONGO_PASSWORD, MONGO_USER 

class MatvirdDB(MSONable):
    def __init__(self, name, host='localhost', port=27017, 
                 user=None, passwd=None, ssl=False, replicaset=None,
                 **kwargs):
        """
        Creates a MatvirdDB client to 'host' with 'port' and connect it to the database 'name'.
        Authentication can be used with 'user' and 'password'

        :param name: (str) The name of the database
        :param host: (str) The host as name or IP
        :param port: (int) The number of port to connect with the server (Default is 27017)
        :param user: (str) The user with read or write permissions to the database
        :param passwd: (str,int) Password to authenticate the user into the server

        """
        self.name = name
        self.user = user
        self.passwd = passwd
        self.host = host
        self.port = port
        self.ssl = ssl
        self.replicaset = replicaset
        self.kwargs = kwargs 
        self.name = name
        maxSevSelDelay = 2
        uri = 'mongodb://'
        if user is not None:
            uri += user
            if passwd is not None:
                uri += ':' + str(passwd)
            uri += '@'
        uri += host + ':' + str(port)
        if user is not None:
            uri += '/' + name
        try:
            if pymongo.version_tuple[0] == 4:
                self._client = pymongo.MongoClient(uri, ssl=ssl,
                                                   replicaSet=replicaset, serverSelectionTimeoutMS=maxSevSelDelay,**kwargs)
            else:
                raise ValueError('Wrong version of pymongo')

            try:
                self._client.server_info()
            except OperationFailure:
                raise RuntimeError("ERROR: Database '%s' on '%s' cannot be accessed, either the database does not "
                                   "exist or you need the right credentials to get access" % (name, host))

        except ServerSelectionTimeoutError:
            raise RuntimeError("ERROR: No connexion could be established to server: %s" % uri)

        self.db = self._client[name]
        self.fs = gridfs.GridFS(self.db)

    def set_collection(self,collection):
        self.entries = self.db.get_collection(collection)

    def __str__(self):
        ret = ' Database Name:       %s\n' % self.name
        ret += ' Host:                %s\n' % self.host
        ret += ' Port:                %s\n' % self.port
        ret += ' User:                %s\n' % self.user
        ret += ' SSL:                 %s\n' % self.ssl
        return ret

    def save_json(self, filename='db_settings.json'):
        dumpfn(self.as_dict(), filename, indent=4)

    def add_file(self, entry_id, location, filepath):

        assert (os.path.isfile(filepath))
        hashcode = hashfile(filepath)
        rf = open(filepath, 'rb')
        filename = os.path.basename(filepath)
        length = os.path.getsize(filepath)

        existing = self.db.fs.files.find_one({'hash': hashcode, 'length': length, 'filename': filename})

        if existing is None:

            file_id = self.fs.put(rf, filename=os.path.basename(filename), hash=hashcode)
            print('New file ', file_id)
            self.db.pychemia_entries.update_one({'_id': entry_id}, {'$addToSet': {location + '.files': {'file_id': file_id,
                                                                                                    'name': filename,
                                                                                                    'hash': hashcode}}})
        else:
            file_id = existing['_id']
            print('File already present ', file_id)
            self.db.pychemia_entries.update_one({'_id': entry_id}, {'$addToSet': {location + '.files': {'file_id': file_id,
                                                                                                    'name': filename,
                                                                                                    'hash': hashcode}}})

    def insert_one(self, data, entry_id=None):
        """
        Insert a pymatgen structure instance and properties
        into the database
        :param entry_id: Mongo ID for the entry
        :param status: (dict) Dictionary of status
        :return:
        """
        if entry_id is not None:
            entry['_id'] = entry_id
        result = self.entries.insert_one(data)
        return result.inserted_id

    def clean(self):
        self._client.drop_database(self.name)
        self.db = self._client[self.name]

    def update(self, entry_id, data=None):
        """
        Update the fields data for a given identifier 'entry_id'

        :param entry_id: (ObjectID, str)
        :param data: (dict) Data dictionary

        :return: The identifier for the entry that was updated

        :rtype : ObjectId

        """

        assert (self.entries.find_one({'_id': entry_id}) is not None)
        entry = self.entries.find_one({'_id': entry_id})
        self.entries.replace_one({'_id': entry_id}, entry)

    def get_entry(self, entry_id, projections={'Calculations':0,'Meta':0} ):
        return self.entries.find_one({'_id': entry_id},projections)

    @classmethod
    def from_uri(cls,uri):
        pass

    def map_to_all(self, function, nparal=6):

        pool = Pool(processes=nparal)
        cursor = self.entries.find({}, no_cursor_timeout=True)
        entries = [entry['_id'] for entry in cursor]
        ret = pool.map(function, itertools.izip(itertools.repeat(self.db_settings), entries))
        cursor.close()
        return ret

def get_database(db_settings):
    """
    Return a MatvirdDB object either by recovering the database from its name on MatvirdDB or
    by creating a new one. The argument is a single python dictionary that should contain
    keys and values to create or get the database.

    """
    if 'host' not in db_settings:
        db_settings['host'] = 'localhost'
    if 'port' not in db_settings:
        db_settings['port'] = 27017
    if 'ssl' not in db_settings:
        db_settings['ssl'] = False
    if 'replicaset' not in db_settings:
        db_settings['replicaset'] = None
    if 'user' not in db_settings:
        database = MatvirdDB(name=db_settings['name'], host=db_settings['host'], port=db_settings['port'],
                          ssl=db_settings['ssl'], replicaset=db_settings['replicaset'])
    else:
        if 'admin_name' in db_settings and 'admin_passwd' in db_settings:
            database = create_database(name=db_settings['name'], host=db_settings['host'], 
                                   port=db_settings['port'], ssl=db_settings['ssl'], 
                                   user_name=db_settings['user'], 
                                   user_passwd=db_settings['passwd'],
                                   admin_name=db_settings['admin_name'], 
                                   admin_passwd=db_settings['admin_passwd'],
                                   replicaset=db_settings['replicaset'])
        else:
            database = MatvirdDB(name=db_settings['name'], host=db_settings['host'], 
                              port=db_settings['port'], user=db_settings['user'], 
                              passwd=db_settings['passwd'], ssl=db_settings['ssl'],
                              replicaset=db_settings['replicaset'])
    return database

        
def create_database(name, admin_name, admin_passwd, user_name, user_passwd, 
                    host='localhost', port=27017, ssl=False, tls= False, replicaset=None):
    """
    Creates a new database for the database 'name'

    :param name: (str) The name of the database
    :param admin_name: (str) The administrator name
    :param admin_passwd: (str) Administrator password
    :param user_name: (str) Username for the database
    :param user_passwd: (str) Password for the user
    :param host: (str) Name of the host for the MatvirdDB server (default: 'localhost')
    :param port: (int) Port to connect to the MatvirdDB server (default: 27017)
    :param ssl: (bool) If True enable ssl encryption for communications to host (default: False)
    :param replicaset: (str, None) Identifier of a Replica Set

    """
    maxSevSelDelay = 2
    try:
       mc = pymongo.MongoClient(host=host, port=port, 
                                username=admin_name,
                                password=admin_passwd,
                                ssl=ssl, tls=tls,
                                replicaset=replicaset, serverSelectionTimeoutMS=maxSevSelDelay)
    except OperationFailure:
        raise RuntimeError("Could not authenticate with the provided credentials")

   
    mc[name].command("createUser",user_name, pwd=user_passwd, roles=["dbAdmin"])
    return MatvirdDB(name=name, user=user_name, passwd=user_passwd, host=host, port=port, ssl=ssl,
                      replicaset=replicaset)


def object_id(entry_id):
    if isinstance(entry_id, str):
        return ObjectId(entry_id)
    elif isinstance(entry_id, ObjectId):
        return entry_id

def has_connection(host='localhost'):
    import pymongo
    try:
        maxSevSelDelay = 2
        client = pymongo.MongoClient(host, serverSelectionTimeoutMS=maxSevSelDelay)
        client.server_info()  # force connection on a request as the
        # connect=True parameter of MongoClient seems
        # to be useless here
        return True
    except pymongo.errors.ServerSelectionTimeoutError as err:
        # do whatever you need
        #print(err)
        return False

if __name__ == "__main__":
   import os
   import sys
   #create_database('test','?','?','?','?',host=host)
   mvd=MatvirdDB('test',user=MONGO_USER,passwd=MONGO_PASSWORD,host=MONGO_HOST,port=MONGO_PORT)
   print(mvd.db.list_collection_names())
   print(mvd.db)
   mvd.db.abc.insert_one({'a':1})
   #mvd.set_collection('abc')
   #mvd.insert_one({'name':'ergouzi'})
