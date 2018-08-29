import hashlib
import json


def hash_string_sha256( inputv ):
      return hashlib.sha256( inputv ).hexdigest()


def hash_block( block ):
     # disabling the normal hashing and performing sha256 hashing below
     #return '-'.join( [ str( block[key]) for key in block ] )
     inputv =  json.dumps( block, sort_keys=True ).encode()
     return hash_string_sha256(inputv)