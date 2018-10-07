from flask import Flask, jsonify, request
from flask_cors import CORS
 

from wallet import Wallet
from blockchain import Blockchain
from error import Error


app = Flask( __name__ )
blockchain = None
CORS( app )

@app.route( '/test', methods=['GET'] )
def get_ui():
      print('Get_ui called !!')
      return 'Jai Swaminarayan !'


@app.route( '/chain', methods=['GET'] )
def get_chain():
      print( 'Fetching blockchain data...' )
      
      dict_chain = [ block.__dict__.copy() for block in blockchain.get_chain() ]

      for block in dict_chain:
            block['transactions'] = [ tx.__dict__.copy() for tx in block['transactions'] ]

      print( dict_chain )

      # Convert to json and send the tuple object with second value as status code of 200 for success
      return jsonify( dict_chain ), 200


@app.route( '/mine', methods=['POST'])
def mine_block():

      print( 'REST API - mine >>>>> Consflicts ? (before) ' , blockchain.resolve_conflicts )
      output = blockchain.mine_block()
      print( 'Is error ?? ' , (isinstance(output, Error)) )
      print( 'REST API - mine >>>>> Consflicts ? (after) ' , blockchain.resolve_conflicts )

      if isinstance( output, Error ):
            return jsonify( output.__dict__ ), 500
      else:
            dict_block = output.__dict__.copy()
            dict_block['transactions'] = [ tx.__dict__.copy() for tx in dict_block['transactions'] ]
            
            return jsonify( dict_block ), 201


@app.route( '/wallet', methods=['POST'] )
def create_keys():
      wallet.create_keys()
      output = wallet.save_keys()

      if isinstance( output, Error ):
            return jsonify( output.__dict__ ), 500

      else:
            global blockchain
            blockchain = Blockchain( wallet.public_key, port )

            response ={
                  'public_key' : wallet.public_key,
                  'private_key': wallet.private_key,
                  'funds' : blockchain.get_balance( wallet.public_key )
            }

            return jsonify( response ), 201


@app.route( '/wallet', methods=['GET'])
def load_keys():
      output = wallet.load_keys()

      if isinstance( output, Error ):
            return jsonify( output ), 500

      else:
            global blockchain
            blockchain = Blockchain( wallet.public_key, port )

            response ={
                  'public_key' : wallet.public_key,
                  'private_key': wallet.private_key,
                  'funds' : blockchain.get_balance( wallet.public_key )
            }

            return jsonify( response ), 201

@app.route( '/balance', methods=['GET'])
def get_balance():
      
      output = blockchain.get_balance( wallet.public_key )

      if isinstance( output, Error ):
            return jsonify( output.__dict__ ), 500
      
      else:
            response = {
                  'funds' : output,
                  'message' : 'Funds/Balance fetched successfully',
                  'public_key': wallet.public_key
            }
            return jsonify( response ), 200


@app.route( '/trans', methods=['POST'])
def add_transaction():

      values = request.get_json()

      if not values:
            error = Error()
            error.code = 400
            error.message = 'No Data found for adding transaction. Please provide 1. Amount 2. Recipient !'
            return jsonify( error.__dict__ ), 400
      
      else:
            # First check and verify mandatory fields are suppiled in request.
            required_fields = ['recipient', 'amount']

            if not all( field in values for field in required_fields ):
                  error = Error()
                  error.code = 400
                  error.message = 'Required fields --> recipient & amount are missing !'
                  
                  return jsonify( error.__dict__ ), 400

            recipient = values['recipient']
            amount = float(values['amount'])
            signature = wallet.sign_transaction( wallet.public_key, recipient, amount )

            success = blockchain.add_transaction( recipient, wallet.public_key, amount, signature )

            if isinstance( success, Error ):
                  return jsonify( error.__dict__ ), 500
            
            response = {
                  'message' : 'Transaction added succesfully !',
                  'sender' : wallet.public_key,
                  'recipient' : recipient ,
                  'amount' : amount,
                  'signature' : signature
            }

            return jsonify( response ), 200
      

@app.route( '/broadcast_transaction', methods=['POST'] )
def broadcast_transaction():
      values = request.get_json()

      if not values:
            return jsonify( Error.get_no_data_found_error().__dict__ ), 400

      required = [ 'sender', 'recipient', 'amount', 'signature' ]

      if not all( key in values for key in required ):
            return jsonify ( Error.get_error_object( 400, 'Missing required/mandatory attributes !' ).__dict__ ), 400

      success = blockchain.add_transaction( values['recipient'], values['sender'], values['amount'], values['signature'], is_receiving=True )

      if isinstance( success, Error ):
            return jsonify( Error.get_error_object(500, 'Transaction has not been verified/added !').__dict__  ), 500
              
      response = {
            'message' : 'Transaction added succesfully !',
            'sender' : values['sender'],
            'recipient' : values['recipient'] ,
            'amount' : values['amount'],
            'signature' : values['signature']
      }

      return jsonify( response ), 200


@app.route( '/broadcast_block', methods=['POST'])
def boradcast_block():
      print('-'*100)
      print('Inside broadcasting block,...')
      values = request.get_json()

      print( 'DATA ==>> ' , values )

      if not values:
            return jsonify( Error.get_no_data_found_error().__dict__ ), 400

      if 'block' not in values:
            return jsonify ( Error.get_error_object( 400, 'Missing required/mandatory attributes !' ).__dict__ ), 400
     
      block = values['block']

      print( 'New block index = ' , block['index'] , ' , Existing block index = ', blockchain.get_chain()[-1].index )
      # New block index is 7 and current block index is 6, so we have to add that block
      if block['index'] == blockchain.get_chain()[-1].index + 1:
            print( 'We need to add a new block.' )
            success = blockchain.add_block( block )
            # We got some erro
            if isinstance( success, Error ):
                  return jsonify( success ), 500
            # We got False value due to hash or proof invalid
            if not success:
                  return jsonify( { 'error': 'Hash or Proof is invalid while adding new block.' } ), 500
            # We got True value and block added successfully
            response = {
                  'message' : 'New mined block added successfully !'
            }
            print( blockchain.get_chain() )
            return jsonify( response ), 201
            
      elif block['index'] > blockchain.get_chain()[-1].index + 1:
            print( 'My block is smaller than coming block, that means issue from my side and i have to resolve. You are good.' )
            response = {
                  'message' : 'My block is smaller than coming block, that means issue from my side and i have to resolve. You are good.',
                  'code' : 200
            }
            return jsonify ( response ), 200
      else:
            print( 'Need to resolve the conflict... Looks like earlier we had 200 response as coming chain was valid, ',
            'but not got a chance correct myself so now while i am mining i have to resolve this...' )
            return jsonify( Error.get_error_object( 409, 'My block is smaller than coming block!' ).__dict__ ), 409




@app.route( '/trans', methods=['GET'] )
def get_open_transactions():

      print('In open transactions REST api,...')

      transactions = blockchain.get_open_transactions()

      if len( transactions ) == 0 :
            error = Error()
            error.code = 400
            error.message = 'No Opens Transactions to return.'

            return jsonify( error.__dict__ ), 400

      transactions_dict = [ tx.__dict__ for tx in transactions ]
      return jsonify( transactions_dict ), 200


@app.route( '/node', methods=['POST'] )
def add_peer_node():
      values = request.get_json()

      if not values:
            error = Error()
            error.code = 400
            error.message = 'No data to retrive from request !'
            return jsonify( error.__dict__ )

      if 'node' not in values:
            error = Error()
            error.code = 400
            error.message = 'Data found but mandatory attribute node has not supplied !'
            return jsonify( error.__dict__ )

      blockchain.add_peer_node( values['node'] )

      response = {
            'message' : 'Node added successfully',
            'nodes' : blockchain.get_peer_nodes()
      }

      return jsonify( response ), 200


@app.route( '/nodes', methods=['GET'] )
def get_peer_nodes():

      nodes = blockchain.get_peer_nodes()

      if not nodes :
            return jsonify( Error.get_error_object(400, 'No Data Found !').__dict__ ), 400

      response = {
            'message' : 'Peer nodes fetched successfully.',
            'nodes' : blockchain.get_peer_nodes()
      }

      return jsonify( response ), 200


@app.route( '/node/<node_id>', methods=['DELETE'] )
def delete_peer_node(node_id):
      print( 'Node going to be delete is ', node_id )
      blockchain.remove_peer_node( node_id )

      response = {
            'nodes' : blockchain.get_peer_nodes()
      }
      return jsonify( response ), 200


@app.route( '/resolve', methods=['POST'] )
def resolve():

      success = blockchain.resolve()

      if success:
            response = {
                  'message' : 'Chain has been replaced successfully.'
            }
            return jsonify( response ), 200

      response = {
            'message' : 'Chain has not been replaced.'
      }

      return jsonify( response ), 200


# Setting up the server
if __name__ == '__main__':

      from argparse import ArgumentParser
      parser = ArgumentParser()
      parser.add_argument( '-p', '--port' , type=int, default=2000) # Register input arguments
      
      args = parser.parse_args()
      port = args.port

      wallet = Wallet( port )
      blockchain = Blockchain( wallet.public_key, port )

      app.run( host='127.0.0.1', port=port )



