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
from wallet import Wallet
from error import Error
import requests

open_transactions = []
owner = 'Brijesh'
participants = { owner }
MINING_REWARDS = 10


class Blockchain:

      # Constructor method
      def __init__( self, hosting_node_id, port ):

            genesis_block = Block( 0, '', [], 100, 0 )
            self.__port = port
            self.__chain = [ genesis_block ]
            self.__open_transactions = []
            self.__peer_nodes = set()
            self.resolve_conflicts = False

            # Load the file data during the start of program to start from where we left
            self.load_data()
            self.hosting_node_id = hosting_node_id


      def get_chain( self ):
            return self.__chain[:]


      def get_open_transactions( self ):
            return self.__open_transactions[:]


      def load_data( self ):
            
            try:
                  with open( 'blockchain-{}.txt'.format( self.__port ), mode ='r' ) as f:
                        file_content = f.readlines()
                        
                        # Here we have to initialize the blockchain with OrderDict which is what we used in this program to avoid 
                        # decrytion hash error.
                        blockchain = json.loads( file_content[0][:-1] ) # -1 because we want to avoid last new line character
                        
                        updated_blockchain = []

                        # Here block is directory object but not the Block object because we are reading from file.  :)
                        for block in blockchain:
                              
                              input_transactions = [ Transaction( tx['sender'], tx['recipient'], tx['amount'], tx['signature'] )  for tx in block['transactions'] ]

                              updated_block = Block(  block['index'], 
                                                      block['previous_hash'], 
                                                      input_transactions, 
                                                      block['proof'], 
                                                      block['timestamp'] )
                              
                              updated_blockchain.append( updated_block )
                        
                        self.__chain = updated_blockchain

                        # Here we have to initialize the open transactions with OrderDict which is what we used in this program to avoid 
                        # decrytion hash error.
                        
                        self.__open_transactions = json.loads( file_content[1][:-1] ) # -1 because we want to avoid last new line character
                        
                        updated_transaction = []

                        for tx in self.__open_transactions:
                              updated_transaction.append(
                                    Transaction( tx['sender'], tx['recipient'], tx['amount'], tx['signature'] )
                              )

                        self.__open_transactions = updated_transaction

                        # Populating peer nodes from blockchain.txt file
                        
                        self.__peer_nodes = set(json.loads( file_content[2] )) # convert back to set object

            except (IOError, IndexError):
                  print('ERROR:: File not found, initializing the data manually...')

            finally:
                  print( 'This block will be executed all the times...' )


      def save_data( self ):

            with open( 'blockchain-{}.txt'.format( self.__port ) , mode='w' ) as f:
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

                  f.write( '\n' )
                  f.write( json.dumps( list(self.__peer_nodes) ) )

      def add_value( self, trans_amount ):
            self.__chain.append( [ self.get_last_transaction(), trans_amount ] )
             

      def get_last_transaction( self ):
            """ Return the last transaction from blockchain """
            if len( self.__chain ) < 1:
                  return None
            else:
                  return self.__chain[-1]

      
      # This method will keep saving new/ope transactions in a file so that can be retrived later if there is no mining done yet.
      def add_transaction( self, recipient, sender, amount, signature, is_receiving=False ):
      
            if sender == None:
                  print( 'Sender is invalid, Did you generated Wallet?' )
                  error = Error()
                  error.code = 400
                  error.message =  'Sender is invalid, Did you generated Wallet?'
                  return error

            #transaction = { 'sender':sender, 'recipient': recipient, 'amount':amount }
            transaction = Transaction( sender, recipient, amount, signature )
            
            if Verification.verify_transaction( transaction, self.get_balance ) :
                  
                  # We have to broadcast this transction to other nodes so they can get update their own version of blockchain
                  if not is_receiving:
                        for node in self.__peer_nodes:
                              url = 'http://{}/broadcast_transaction'.format(node)
                              print( 'Broadcasting transaction on ==> ', url )

                              try:
                                    response = requests.post( url, json={ 'sender': sender, 'recipient' : recipient, 'amount' : amount, 'signature' : signature  } )

                                    if response.status_code == 400 or response.status_code == 500:
                                          print( 'Broadcasting transaction declined ! Need to resolve...')
                                          return Error.get_error_object( '500', 'Broadcasting transaction declined ! Need to resolve...' )

                              except requests.exceptions.ConnectionError:
                                    print( 'ERROR:::Connections issue while broading transction for the node ', node )
                                    continue

                  self.__open_transactions.append( transaction )
                  # Saving the data in a file.
                  self.save_data()
                  
                  print( 'New/Open Transaction added successfully...' )
                  return True
            else:
                  error = Error()
                  error.code = 500
                  error.message = 'Transaction verification failed !'
                  return error

            return False

      
      def proof_of_work( self ):
            last_block = self.__chain[-1]
            last_block_hash = hash_block( last_block )
            
            proof = 0
            
            while not Verification.valid_proof( self.__open_transactions, last_block_hash, proof ):
                  proof = proof + 1

            return proof


      def resolve( self ):

            winner_chain = self.__chain
            replaced = False

            for node in self.__peer_nodes:
                  
                  try:
                        url = 'http://{}/chain'.format( node )

                        response = requests.get( url )

                        node_chain = response.json()

                        node_chain = [ Block( block['index'], block['previous_hash'], 
                                          [ Transaction( tx['sender'], tx['recipient'], tx['amount'], tx['signature']) for 
                                                      tx in block['transactions'] ],
                                          block[ 'proof' ],
                                          block['timestamp']
                                          ) for block in node_chain ]
                        
                        if len( node_chain ) > len( winner_chain ) and Verification.verify_blockchain( node_chain ):
                              winner_chain = node_chain
                              replaced = True
                  except ConnectionError:
                        print('Connection error occured while connection chain REST api from resolve()...')

            self.__chain = winner_chain
            self.resolve_conflicts = False

            if replaced:
                  self.__open_transactions = []
                  print( 'Chain has been replaced !') 

            self.save_data()
            return replaced 
                  

      def mine_block( self ):
      
            print('In mine block, Resolve Conflicts =====>>> ' , self.resolve_conflicts )
            if self.resolve_conflicts:
                  return Error.get_error_object( '409', 'Resolved conflict before you mine a new Block !')

            if self.hosting_node_id == None:
                  print( 'Cannot mine the block for invalid sender, Did you generated Wallet? ' )

                  error = Error()
                  error.message= 'Cannot mine the block for invalid sender, Did you generated Wallet?'
                  error.code= 'MINE_MISSING_WALLET'
                  return error


            last_block = self.__chain[-1]
            hashed_block = hash_block( last_block )

            # Calculate proof of work/nonce before you add reward tranasction
            proof = self.proof_of_work()

            copied_transactions = self.__open_transactions[:]

            # Verify for the signature mismatch before you mine the block.
            for tx in copied_transactions:
                  if not Wallet.verify_signature( tx ):
                        print( 'ERRPR:::Cannot mine the block as Signature is not matching...!!!' )
                        
                        error = Error()
                        error.message= 'Cannot mine the block as Signature is not matching...!!!'
                        error.code= 'MINE_MISSING_SIGNATURE'
                        return error


            reward_transaction = Transaction( 'MINNER', self.hosting_node_id, MINING_REWARDS, '' )
            copied_transactions.append( reward_transaction )

            block = Block( len( self.__chain ), hashed_block, copied_transactions, proof )
            
            self.__chain.append( block )
            self.__open_transactions = []
            # Save data in a file.
            self.save_data()

            print('In mine block data has been saved successfully, Starting broadcast now !!! ')

            # Let's inform other nodes for this mining using broadcasting a block
            for node in self.__peer_nodes:
                  try:
                        url = 'http://{}/broadcast_block'.format( node )
                        converted_block = block.__dict__.copy()
                        converted_block['transactions'] = [ tx.__dict__ for tx in converted_block['transactions'] ]
                        
                        print('Bradcasting mined block on ===>>> ' , url )
                        input = {
                              'block' : converted_block
                        }
                        response = requests.post( url, json={'block': converted_block} )

                        if response.status_code == 400 or response.status_code == 500:
                              print( 'Error:::Error in mine block for borading casting is ', response )
                        if response.status_code == 201:
                              print( '*** Mined Block broadcasted successfully ***' )  
                        
                        if response.status_code == 409:
                              print( '*** We need to resolve config which might caused due to earlier node network block missmatch...' )
                              self.resolve_conflicts = True


                  except ConnectionError:
                        print('Error connection a node server ', node )

            print('Mine Block Broadcasting completed....')

            return block


      # Here you will get new block from rest api will be in directory form so you have convert into object form
      def add_block( self, block ):

            print('Adding new block received from broadcasting,...')

            if not block:
                  return Error.get_error_object( 400, 'Cannot add empty block!') 

            transactions = [ Transaction( tx['sender'], tx['recipient'], tx['amount'], tx['signature'] ) for tx in block['transactions'] ]
            
            print( 'Previous Hash == ' , block['previous_hash'] )
            print( 'Proof == ' , block['proof'] )

            # We need to exclude last transaction of minner that we are not using while generating proof 
            is_valid_proof = Verification.valid_proof( transactions[:-1], block['previous_hash'], block['proof'] )
            print( 'Is Proof Valid ?? ', is_valid_proof )

            is_hash_valid = block['previous_hash'] == hash_block( self.get_chain()[-1] )
            print( 'Is Hash valid ?? ' , is_hash_valid )

            if not is_hash_valid or not is_valid_proof:
                  return False

            # Convert directory block received from rest api into Block object
            new_block = Block( block['index'], 
                               block['previous_hash'], 
                               transactions, 
                               block['proof'], 
                               block['timestamp'] )
            print( 'Appending new block == ' , new_block )
            self.__chain.append( new_block )
            
            # We are adding new broadcasted block but when it was mine by original sender open transactions were cleared out.
            # Same way here also we have to cleared out the open transactions if any before we add this new mined block.
            
            stored_trans = self.__open_transactions[:]

            for o_tx in transactions:
                  for s_tx in stored_trans:
                        if o_tx.sender == s_tx.sender and o_tx.recipient == s_tx.recipient and o_tx.amount == s_tx.amount and o_tx.signature == s_tx.signature:
                              try:
                                    self.__open_transactions.remove( s_tx )
                              except:
                                    print('Item/Transction was already removed!')

            self.save_data()

            print( 'New block added and saved successfully...' )
            return True
      

      def get_balance( self, sender ):

            #if self.hosting_node_id == None:
            if sender == None:
                  error = Error()
                  error.message = 'Invalid public_key (sender)'
                  error.code = 'INVALID_SENDER'
                  return error

            #participant = self.hosting_node_id
            participant = sender
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


      def add_peer_node( self, node ):

            self.__peer_nodes.add( node )
            self.save_data()


      def remove_peer_node( self, node ):

            self.__peer_nodes.discard( node )
            self.save_data()


      def get_peer_nodes( self ):

            return list( self.__peer_nodes )







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




      

