from Crypto.PublicKey import RSA
import Crypto.Random 
import binascii

class Wallet:

      def __init__( self ):
            self.private_key = None
            self.public_key = None
            
            
      def create_keys( self ):
            private_key, public_key = self.generate_keys()
            self.private_key = private_key
            self.public_key = public_key


      def save_keys( self ):

            if self.private_key != None and self.public_key != None:
                  try:
                        with open( 'wallet.txt', 'w') as f:
                              f.write( self.public_key )
                              f.write( '\n' )
                              f.write( self.private_key ) 
                  except(IOError, IndexError):
                        print('ERROR:::Error saving a wallet file...')


      def load_keys( self ):

            try:
                  with open( 'wallet.txt', 'r' ) as f:
                        keys = f.readlines()
                        self.public_key = keys[0][:-1]
                        self.private_key = keys[1]

            except( IOError, IndexError ):
                  print( 'ERROR:::Error reading wallet file !!!' )
            

      def generate_keys( self ):
            private_key = RSA.generate( 1024, Crypto.Random.new().read )
            public_key = private_key.publickey()
            return (
                        binascii.hexlify( private_key.exportKey(format='DER')).decode('ascii'),
                        binascii.hexlify( public_key.exportKey(format='DER')).decode('ascii')
                   ) 