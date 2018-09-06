
from hash_util import hash_block, hash_string_sha256

class Verification:

      def verify_transactions( self, open_transactions, get_balance ):
            return all( [self.verify_transaction(tx, get_balance) for tx in open_transactions] )

      #This function will verify the transaction if sender has enough money to send.
      #It will pull the sender from the transaction and will check her balance
      def verify_transaction( self, transaction, get_balance ):
      
            balance = get_balance( transaction.sender )

            print( 'In Verify transaction, balance = ', balance , ' New Transaction amount = ', transaction.amount )
            return balance >= transaction.amount


      def verify_blockchain( self, blockchain ):
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
                  if not self.valid_proof( block.transactions[:-1], block.previous_hash, block.proof ):
                        print( '>>>>>>>>>>>>>>>>>>>>...------------- Proof of work is Invalid --------------...<<<<<<<<<<<<<<<<<<<<<<<<<<<<<' )
                        return False
            return True

      
      def valid_proof( self, transactions, last_hash, proof ):
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