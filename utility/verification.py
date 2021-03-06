
from utility.hash_util import hash_block, hash_string_sha256
from wallet import Wallet

class Verification:

      # We need to verify each transaction for any security thret and signature will help us here a lot.
      @classmethod
      def verify_transactions( cls, open_transactions, get_balance ):
            return all( [ cls.verify_transaction( tx, get_balance, False ) for tx in open_transactions] )

      #This function will verify the transaction if sender has enough money to send.
      #It will pull the sender from the transaction and will check her balance
      @classmethod
      def verify_transaction( cls, transaction, get_balance, funds_check=True ):
      
            balance = get_balance( transaction.sender )

            print( 'In Verify transaction, balance = ', balance , ' New Transaction amount = ', transaction.amount )
            
            if funds_check:
                  return balance >= transaction.amount and Wallet.verify_signature( transaction )
            else:
                  return Wallet.verify_signature( transaction )


      @classmethod
      def verify_blockchain( cls, blockchain ):
            """ Verify current blockchain and return True otherwise False """

            print( '+' * 100 )
            for( index, block ) in enumerate(blockchain):
                  if( index == 0 ):
                        continue
                  # Verify if the previous hash is equal to manually cancluated previous value hash
                  
                  if( block.previous_hash != hash_block( blockchain[index-1] ) ):
                        return False
                  
                  # Verify valid proof of work, also make sure you pass the tranasctions without reward transaction, 
                  # as we have not added the same while mining blocks, that is why -1 in below code.
                  if not cls.valid_proof( block.transactions[:-1], block.previous_hash, block.proof ):
                        print( '>>>>>>>>>>>>>>>>>>>>...------------- Proof of work is Invalid --------------...<<<<<<<<<<<<<<<<<<<<<<<<<<<<<' )
                        return False
            return True

      
      @staticmethod
      def valid_proof( transactions, last_hash, proof ):
            """Validate a proof of work number and see if it solves the puzzle algorithm (two leading 0s)

            Arguments:
                  :transactions: The transactions of the block for which the proof is created.
                  :last_hash: The previous block's hash which will be stored in the current block.
                  :proof: The proof number we're testing.
            """
            # Create a string with all the hash inputs
            guess = (str([tx.to_ordered_dict() for tx in transactions]) + str(last_hash) + str(proof)).encode()
            # Hash the string
            # IMPORTANT: This is NOT the same hash as will be stored in the previous_hash. It's a not a block's hash. It's only used for the proof-of-work algorithm.
            guess_hash = hash_string_sha256( guess )
            # Only a hash (which is based on the above inputs) which starts with two 0s is treated as valid
            # This condition is of course defined by you. You could also require 10 leading 0s - this would take significantly longer (and this allows you to control the speed at which new blocks can be added)
            return guess_hash[0:2] == '00'