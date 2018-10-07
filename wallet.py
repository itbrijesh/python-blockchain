from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
from Crypto.Signature import PKCS1_v1_5

import Crypto.Random 
import binascii

from error import Error

class Wallet:

      def __init__( self, port ):
            self.private_key = None
            self.public_key = None
            self.__port = port 
            
            
      def create_keys( self ):
            private_key, public_key = self.generate_keys()
            self.private_key = private_key
            self.public_key = public_key


      def save_keys( self ):

            if self.private_key != None and self.public_key != None:
                  try:
                        with open( 'wallet-{}.txt'.format( self.__port ), 'w') as f:
                              f.write( self.public_key )
                              f.write( '\n' )
                              f.write( self.private_key ) 
                        
                        return True

                  except(IOError, IndexError):
                        print('ERROR:::Error saving a wallet file...')
                        
                        error = Error()
                        error.message = 'Error saving a wallet file.'
                        error.code = 'FILE_SAVE_ERROR'
                        return error


      def load_keys( self ):

            try:
                  with open( 'wallet-{}.txt'.format( self.__port ), 'r' ) as f:
                        keys = f.readlines()
                        self.public_key = keys[0][:-1]
                        self.private_key = keys[1]

                  return True

            except( IOError, IndexError ):
                  print( 'ERROR:::Error reading wallet file !!!' )

                  error = Error()
                  error.message = 'Error loading a wallet file.'
                  error.code = 'FILE_LOAD_ERROR'

                  return error
            

      def generate_keys( self ):
            private_key = RSA.generate( 1024, Crypto.Random.new().read )
            public_key = private_key.publickey()
            return (
                        binascii.hexlify( private_key.exportKey(format='DER')).decode('ascii'),
                        binascii.hexlify( public_key.exportKey(format='DER')).decode('ascii')
                   )


      def sign_transaction( self, sender, recipient, amount ):
            rsaKey = RSA.importKey( binascii.unhexlify( self.private_key ) )
            signer = PKCS1_v1_5.new( rsaKey )
            hash_payload = SHA256.new( ( str(sender) + str( recipient) + str( amount ) ).encode( 'utf8' ) )
            signature = signer.sign( hash_payload )
            
            return binascii.hexlify( signature ).decode( 'ascii' )

      @staticmethod
      def verify_signature( transaction ):
             
            publickey = RSA.importKey( binascii.unhexlify( transaction.sender ) )
            verifier = PKCS1_v1_5.new( publickey )
            hash_payload = SHA256.new( ( str(transaction.sender) + str( transaction.recipient ) + str( transaction.amount ) ).encode( 'utf8' ) )
            return verifier.verify( hash_payload, binascii.unhexlify( transaction.signature ) )