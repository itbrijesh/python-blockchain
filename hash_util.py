import hashlib
import json


def hash_string_sha256( inputv ):
      return hashlib.sha256( inputv ).hexdigest()


def hash_block( block ):
     # disabling the normal hashing and performing sha256 hashing below
     #return '-'.join( [ str( block[key]) for key in block ] )
     
     # Json cannot serialize the object, so we have to convert the same into directory object.
     # We are also coping because it is the reference which can be changed in future by other operations.
     # So it is safe to first make a copy before we use.
      
     upd_block = block.__dict__.copy()
     inputv =  json.dumps( upd_block, sort_keys=True ).encode()
     
     return hash_string_sha256(inputv)