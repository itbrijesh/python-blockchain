import functools
import hashlib
import json
import pickle
from utility.verification import Verification
from block import Block
from transaction import Transaction
from utility.hash_util import hash_block
from utility.hash_util import hash_string_sha256
from collections import OrderedDict


open_transactions = []
owner = 'Brijesh'
participants = { owner }
MINING_REWARDS = 10


class Blockchain:

      # Constructor method
      def __init__( self, hosting_node_id ):

            genesis_block = Block( 0, '', [], 100, 0 )
            self.__chain = [ genesis_block ]
            self.__open_transactions = []

            # Load the file data during the start of program to start from where we left
            self.load_data()
            self.hosting_node_id = hosting_node_id


      def get_chain( self ):
            return self.__chain[:]


      def get_open_transactions( self ):
            return self.__open_transactions[:]


      def load_data( self ):
            
            try:
                  with open( 'blockchain.txt', mode ='r' ) as f:
                        file_content = f.readlines()
                        
                        # Here we have to initialize the blockchain with OrderDict which is what we used in this program to avoid 
                        # decrytion hash error.
                        blockchain = json.loads( file_content[0][:-1] ) # -1 because we want to avoid last new line character
                        
                        updated_blockchain = []

                        # Here block is directory object but not the Block object because we are reading from file.  :)
                        for block in blockchain:
                              
                              input_transactions = [ Transaction( tx['sender'], tx['recipient'], tx['amount'] )  for tx in block['transactions'] ]

                              updated_block = Block(  block['index'], 
                                                      block['previous_hash'], 
                                                      input_transactions, 
                                                      block['proof'], 
                                                      block['timestamp'] )
                              
                              updated_blockchain.append( updated_block )
                        
                        self.__chain = updated_blockchain

                        # Here we have to initialize the open transactions with OrderDict which is what we used in this program to avoid 
                        # decrytion hash error.
                        
                        self.__open_transactions = json.loads( file_content[1] )
                        
                        updated_transaction = []

                        for tx in self.__open_transactions:
                              updated_transaction.append(
                                    Transaction( tx['sender'], tx['recipient'], tx['amount'] )
                              )

                        self.__open_transactions = updated_transaction

            except (IOError, IndexError):
                  print('ERROR:: File not found, initializing the data manually...')

            finally:
                  print( 'This block will be executed all the times...' )


      def save_data( self ):

            with open( 'blockchain.txt' , mode='w' ) as f:
                  # JSON cannot serialize object, so convert the same into directory
                  # We have to convert each sub object ( i.e transactions ) into directory/str.
                  # So first we did block for block in blockchain   and then,
                  # [ Block(...) for obj in blockchain ]

                  saveable_chain = [block.__dict__ for block in [Block(block_el.index, block_el.previous_hash, [tx.__dict__ for tx in block_el.transactions], block_el.proof, block_el.timestamp) for block_el in self.__chain]]
                  f.write(json.dumps(saveable_chain))
                  f.write('\n')
                  
                  saveable_tx = [tx.__dict__ for tx in self.__open_transactions]
                  f.write(json.dumps(saveable_tx))

                  print('Open transactions has been stored in a file blockchain.txt...')

      def add_value( self, trans_amount ):
            self.__chain.append( [ self.get_last_transaction(), trans_amount ] )
             

      def get_last_transaction( self ):
            """ Return the last transaction from blockchain """
            if len( self.__chain ) < 1:
                  return None
            else:
                  return self.__chain[-1]

      
      def add_transaction( self, recipient, sender, amount=1.0 ):
      
            if sender == None:
                  print( 'Sender is invalid, Did you generated Wallet?' )
                  return False

            #transaction = { 'sender':sender, 'recipient': recipient, 'amount':amount }
            transaction = Transaction( sender, recipient, amount )
            
            if Verification.verify_transaction( transaction, self.get_balance ) :
                  self.__open_transactions.append( transaction )
                  # Saving the data in a file.
                  self.save_data()
                  return True

            return False

      
      def proof_of_work( self ):
            last_block = self.__chain[-1]
            last_block_hash = hash_block( last_block )
            
            proof = 0
            
            while not Verification.valid_proof( self.__open_transactions, last_block_hash, proof ):
                  proof = proof + 1

            return proof


      def mine_block( self ):
      
            if self.hosting_node_id == None:
                  print( 'Cannot mine the block for invalid sender, Did you generated Wallet? ' )
                  return False


            last_block = self.__chain[-1]
            hashed_block = hash_block( last_block )

            # Calculate proof of work/nonce before you add reward tranasction
            proof = self.proof_of_work()

            copied_transactions = self.__open_transactions[:]

            reward_transaction = Transaction( 'MINNER', self.hosting_node_id, MINING_REWARDS )
            copied_transactions.append( reward_transaction )

            block = Block( len( self.__chain ), hashed_block, copied_transactions, proof )
            
            self.__chain.append( block )
            
            # Clear all the open transactions as we mined the block
            #open_transactions = []
            # Save the data into file for further use
            #save_data()

            Verification.valid_proof( self.__open_transactions, hashed_block, proof )

            self.__open_transactions = []
            # Save data in a file.
            self.save_data()

            return True


      def get_balance( self ):

            participant = self.hosting_node_id
            print( 'Getting balance for ' , participant )

            sender_data = [ [ tx.amount for tx in block.transactions if tx.sender == participant ] for block in self.__chain ]
            print( 'Sender amount : ', sender_data )

            # We need to check for the amount spent in open tranasctions too
            open_sender_data = [ opendata.amount for opendata in self.__open_transactions if opendata.sender == participant ]
            print( 'Open sender amount : ', open_sender_data )
            
            # Combine with sender data amount 
            sender_data.append( open_sender_data )
            print( 'Sender amount (combine with open amount) : ', sender_data )

            amount_tobe_sent = 0         

            amount_tobe_sent = functools.reduce( lambda tx_sum, tx_amt: tx_sum + sum(tx_amt) if len(tx_amt) > 0 else tx_sum + 0, sender_data, 0 )

            # for amount in sender_data:
            #       print( 'for loop -- ' , amount )
            #       if(len(amount) > 0):
            #             print('amount_tobe_sent (before) = ', amount_tobe_sent )
            #             print('amount : ' , amount[0] )
            #             for amt in amount:
            #                   amount_tobe_sent = amount_tobe_sent + amt
            #                   print('amount_tobe_sent (after) = ', amount_tobe_sent )


            reciever_data = [ [ tx.amount for tx in block.transactions if tx.recipient == participant ] for block in self.__chain ]

            amount_received = 0
            amount_received = functools.reduce( lambda tx_sum, tx_amt: tx_sum + sum(tx_amt) if len(tx_amt) > 0 else tx_sum + 0 , reciever_data, 0 )

            #for ramount in reciever_data:
            #      if( len(ramount) > 0 ):
            #            amount_received = amount_received + ramount[0]

            print('Amount send : ' , amount_tobe_sent , ' Amount recieved : ' , amount_received )
            return amount_received - amount_tobe_sent









def save_data_using_pickel():
      with open( 'blockchain.p', mode='wb' ) as f:
            file_data = {
                  'chain' : blockchain,
                  'ot' : open_transactions
            }
            f.write( pickle.dumps( file_data) )


def save_data_using_json():
      with open( 'blockchain.txt', mode='w' ) as f:
            f.write( json.dumps( blockchain ) )
            f.write( '\n' )
            f.write( json.dumps( open_transactions ) )












      











#add_value( get_user_input() )





def load_data_using_json():
     
      global blockchain
      global open_transactions

      try:
                  with open( 'blockchain.txt', mode ='r' ) as f:
                        file_content = f.readlines()
                        
                        # Here we have to initialize the blockchain with OrderDict which is what we used in this program to avoid 
                        # decrytion hash error.
                        blockchain = json.loads( file_content[0][:-1] )
                        updated_blockchain = []

                        for block in blockchain:
                              updated_block = {
                                    'previous_hash' : block['previous_hash'],
                                    'index' : block['index'],
                                    'proof': block['proof'],
                                    'transactions' : [
                                          OrderedDict( [ ('sender', tx['sender']), 
                                                            ('recipient', tx['recipient']), 
                                                            ('amount', tx['amount']) ] ) for tx in block['transactions']
                                    ]
                              }
                              updated_blockchain.append( updated_block )
                        
                        blockchain = updated_blockchain

                        # Here we have to initialize the open transactions with OrderDict which is what we used in this program to avoid 
                        # decrytion hash error.
                        
                        open_transactions = json.loads( file_content[1] )
                        updated_transaction = []

                        for tx in open_transactions:
                              updated_transaction.append(
                                    OrderedDict( [ ('sender', tx['sender']), 
                                                ('recipient', tx['recipient']), 
                                                ('amount', tx['amount']) ] )
                              )

                        open_transactions = updated_transaction
      
      except IOError:
            print('ERROR:: File not found, initializing the data manually...')
            genesis_block = {
                  'previous_hash' : '',
                  'index' : 0,
                  'transactions' : [],
                  'proof': 100
            }
            blockchain = [ genesis_block ]
      finally:
            print( 'This block will be executed all the times...' )


def load_data_using_pickel():

      global blockchain
      global open_transactions

      try:
            with open( 'blockchain.p', mode='rb' ) as f:
                  file_content = pickle.loads( f.read() )
                  
                  blockchain = file_content['chain'] 
                  open_transactions = file_content['ot']

      except IOError:
            print( 'ERROR::File Not Found, Initialize the data manually using code....' )
            genesis_block = {
                  'previous_hash' : '',
                  'index' : 0,
                  'transactions' : [],
                  'proof': 100
            }
            blockchain = [ genesis_block ]

      except ValueError:
            print( 'Some value error !!! ' )

      finally:
            print( 'Always executed !!!' )




      

