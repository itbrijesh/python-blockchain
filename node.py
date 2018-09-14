from flask import Flask, jsonify, request
from flask_cors import CORS
 

from wallet import Wallet
from blockchain import Blockchain
from error import Error


app = Flask( __name__ )
wallet = Wallet()
blockchain = Blockchain( wallet.public_key )
CORS( app )

@app.route( '/test', methods=['GET'] )
def get_ui():
      print('Get_ui called !!')
      return 'Jai Swaminarayan !'


@app.route( '/chain', methods=['GET'] )
def get_chain():
      print( 'Fetching blockchain data...' )
      
      global blockchain
      blockchain = Blockchain( wallet.public_key )
      
      dict_chain = [ block.__dict__.copy() for block in blockchain.get_chain() ]

      for block in dict_chain:
            block['transactions'] = [ tx.__dict__.copy() for tx in block['transactions'] ]

      print( dict_chain )

      # Convert to json and send the tuple object with second value as status code of 200 for success
      return jsonify( dict_chain ), 200


@app.route( '/mine', methods=['POST'])
def mine_block():
      blockchain = Blockchain( wallet.public_key )
      output = blockchain.mine_block()
      print( 'In mine block output is ' , output )
      print( 'Is error ?? ' , (isinstance(output, Error)) )

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
            blockchain = Blockchain( wallet.public_key )

            response ={
                  'public_key' : wallet.public_key,
                  'private_key': wallet.private_key,
                  'funds' : blockchain.get_balance()
            }

            return jsonify( response ), 201


@app.route( '/wallet', methods=['GET'])
def load_keys():
      output = wallet.load_keys()

      if isinstance( output, Error ):
            return jsonify( output ), 500

      else:
            global blockchain
            blockchain = Blockchain( wallet.public_key )

            response ={
                  'public_key' : wallet.public_key,
                  'private_key': wallet.private_key,
                  'funds' : blockchain.get_balance()
            }

            return jsonify( response ), 201

@app.route( '/balance', methods=['GET'])
def get_balance():
      
      output = blockchain.get_balance()

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
                  return jsonify( error ), 500
            
            response = {
                  'message' : 'Transaction added succesfully !',
                  'sender' : wallet.public_key,
                  'recipient' : recipient ,
                  'amount' : amount,
                  'signature' : signature
            }

            return jsonify( response ), 200
      

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


# Setting up the server
if __name__ == '__main__':
      app.run( host='127.0.0.1', port=2000 )



