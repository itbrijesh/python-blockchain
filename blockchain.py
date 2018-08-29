import functools
import hashlib
import json
import pickle
from block import Block
from hash_util import hash_block
from hash_util import hash_string_sha256
from collections import OrderedDict


open_transactions = []
owner = 'Brijesh'
blockchain = []
participants = { owner }
MINING_REWARDS = 10


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
                                                            ('reciepient', tx['reciepient']), 
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
                                                ('reciepient', tx['reciepient']), 
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



def load_data():
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
                        
                        input_transactions = [ OrderedDict( [ ('sender', tx['sender']), 
                                                      ('reciepient', tx['reciepient']), 
                                                      ('amount', tx['amount']) ] ) for tx in block['transactions'] ]

                        updated_block = Block(  block['index'], 
                                                block['previous_hash'], 
                                                input_transactions, 
                                                block['proof'], 
                                                block['timestamp'] )
                         
                        updated_blockchain.append( updated_block )
                  
                  blockchain = updated_blockchain

                  # Here we have to initialize the open transactions with OrderDict which is what we used in this program to avoid 
                  # decrytion hash error.
                  
                  open_transactions = json.loads( file_content[1] )
                  updated_transaction = []

                  for tx in open_transactions:
                        updated_transaction.append(
                              OrderedDict( [ ('sender', tx['sender']), 
                                          ('reciepient', tx['reciepient']), 
                                          ('amount', tx['amount']) ] )
                        )

                  open_transactions = updated_transaction

      except IOError:
            print('ERROR:: File not found, initializing the data manually...')
            genesis_block = Block( 0, '', [], 100, 0 )
            blockchain = [ genesis_block ]
            
      finally:
            print( 'This block will be executed all the times...' )

# Load the file data during the start of program to start from where we left
load_data()

def save_data():
      with open( 'blockchain.txt' , mode='w' ) as f:
            f.write( json.dumps( blockchain ) )
            f.write( '\n' )
            f.write( json.dumps( open_transactions ) )
            

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


def add_value( trans_amount ):
      blockchain.append( [ get_last_transaction(), trans_amount ] )
      print( blockchain )


def get_user_input():
      return input('Enter transaction amount : ')


def print_blockchain():
      # Print the blockchain data
      for block in blockchain:
            print('Block chain value : ' , block )
      else:
            print('-' * 30)


def print_blockchain2():
      for index in range( len( blockchain ) ):
            print( blockchain[index] )

def get_last_transaction():
      """ Return the last transaction from blockchain """
      if len( blockchain ) < 1:
            return None
      else:
            return blockchain[-1]

#This function will verify the transaction if sender has enough money to send.
#It will pull the sender from the transaction and will check her balance
def verify_transaction( transaction ):
      balance = get_balance( transaction['sender'] )

      print( 'In Verify transaction, balance = ', balance , ' New Transaction amount = ', transaction['amount'] )
      return balance >= transaction['amount']

def add_transaction(reciepient, sender=owner, amount=1.0):
      
      #transaction = { 'sender':sender, 'reciepient': reciepient, 'amount':amount }

      transaction = OrderedDict( [ ('sender', sender), ('reciepient', reciepient), ('amount', amount) ] )

      print( 'Transaction in add_transaction >> ', transaction )

      if verify_transaction( transaction) :
            open_transactions.append( transaction )
            participants.add( sender )
            participants.add( reciepent )
            # Saving the data in a file.
            save_data()
            return True
      return False

      
def get_transaction_details():
      tx_reciepent = input('Enter Reciepent Name : ')
      tx_amount = input('Enter Transaction Amount : ')
      return ( tx_reciepent, float(tx_amount) )


def verify_blockchain():
      """ Verify current blockchain and return True otherwise False """

      for( index, block ) in enumerate(blockchain):
            if( index == 0 ):
                  continue
            # Verify if the previous hash is equal to manually cancluated previous value hash
            if( block[ 'previous_hash' ] != hash_block( blockchain[index-1] ) ):
                  return False
            
            # Verify valid proof of work, also make sure you pass the tranasctions without reward transaction, 
            # as we have not added the same while mining blocks, that is why -1 in below code.
            if not valid_proof( block['transactions'][:-1], block['previous_hash'], block['proof'] ):
                  print( '------------- Proof of work is Invalid --------------' )
                  return False
      return True


def valid_proof( transactions, last_hash, proof ):
      guess = ( str(transactions) + str(last_hash) + str(proof) ).encode()
      guess_hash = hash_string_sha256( guess )
      
      return guess_hash[0:2] == '00'


def proof_of_work():
      last_block = blockchain[-1]
      last_block_hash = hash_block( last_block )
      proof = 0

      while not valid_proof( open_transactions, last_block_hash, proof ):
            proof = proof + 1

      return proof


def mine_block():
      last_block = blockchain[-1]
      hashed_block = hash_block( last_block )
      print( 'Hashed block is ' , hash_block )
      #for key in last_block:
      #      value = last_block[ key ]
      #      hashed_block = hashed_block + str( value )

      print( 'Hashed Key ::: ' , hashed_block )

      #reward_transaction =  { 'sender':'MINNER', 'reciepient': owner, 'amount':MINING_REWARDS }

      reward_transaction = OrderedDict( [ ('sender','MINNER'), ('reciepient', owner), ('amount',MINING_REWARDS) ] )

      # Calculate proof of work/nonce before you add reward tranasction
      proof = proof_of_work()

      copied_transactions = open_transactions[:]
      #open_transactions.append( reward_transaction )
      copied_transactions.append( reward_transaction )

      block = {
            'previous_hash' : hashed_block,
            'index' : len(blockchain),
            'transactions' : copied_transactions,
            'proof': proof
      }
      blockchain.append( block )
      print( 'Blockchain after mining : ' , blockchain )

      return True


def get_balance( participant ):
      print( 'Getting balance for ' , participant )

      sender_data = [ [ tx['amount'] for tx in block['transactions'] if tx['sender'] == participant ] for block in blockchain ]
      print( 'Sender amount : ', sender_data )
      # We need to check for the amount spent in open tranasctions too
      open_sender_data = [ opendata['amount'] for opendata in open_transactions if opendata['sender'] == participant ]
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


      reciever_data = [ [ tx['amount'] for tx in block['transactions'] if tx['reciepient'] == participant ] for block in blockchain ]

      amount_received = 0
      amount_received = functools.reduce( lambda tx_sum, tx_amt: tx_sum + sum(tx_amt) if len(tx_amt) > 0 else tx_sum + 0 , reciever_data, 0 )

      #for ramount in reciever_data:
      #      if( len(ramount) > 0 ):
      #            amount_received = amount_received + ramount[0]

      print('Amount send : ' , amount_tobe_sent , ' Amount recieved : ' , amount_received )
      return amount_received - amount_tobe_sent

#add_value( get_user_input() )

def verify_transactions():
      return all( verify_transaction(tx) for tx in open_transactions )

waiting_for_input = True

while waiting_for_input:
      print('1. Add new transaction.')
      print('2. Mine block.')
      print('3. Display blockchain data.')
      print('4. Modify value.')
      print('5  Print Participants.' )
      print('6. Print Open Transactions.')
      print('7. Verify all Transactions.')
      print('q. Quit')

      choice = input('Enter your choice : ')

      if( choice == '1' ):
            tx_details = get_transaction_details()
            print('Transaction details with sender/reciever :: ' , tx_details )
            reciepent, amount = tx_details

            if add_transaction( reciepent, amount=amount ) :
                  print('Transaction has been added successfully !!!')
            else:
                  print('!!!!!!!!!!!!!!!!!!!!!!!!!! Transaction failed !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
            
      elif( choice == '2' ):
            if( mine_block() ):
                  open_transactions = []
                  save_data()

      elif( choice == '3' ):
             print_blockchain2()
            #print( open_transactions )

      elif( choice == '4' ):
            if( len(blockchain) >= 1 ):
                  blockchain[0] = [
                  {     
                        'previous_hash' : 'Hacked',
                        'index' : 20,
                        'transactions' : [{'sender':'abc', 'reciepient': 'def', 'amount':249}]
                  }]
                  
      elif( choice == '5' ):
            print( participants )

      elif( choice == '6' ):
            print(open_transactions)

      elif( choice == '7' ):
            if verify_transactions():
                  print('All transactions are valid....')
            else:
                  print('---------- Few of the transactions are not valid --------------')

      elif( choice == 'q' ):
            waiting_for_input = False
      else:
            print('Enter valid choice.')
      
      if not verify_blockchain():
            print( 'Invalid blockchain' )
            print(blockchain)
            break

      print('-' * 100 )
      print('Calculation balance....' )
      print('Balance of {} is {:6.2f} : '.format( owner, get_balance( owner) ) )
      print('-' * 100 )
else:
      print('User left!')


      

