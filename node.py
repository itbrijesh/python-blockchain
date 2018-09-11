from uuid import uuid4
from utility.verification import Verification
from blockchain import Blockchain
from wallet import Wallet

class Node:

      def __init__( self ):
            # Unique sender/ID
            #self.node_id = str( uuid4() ) # We used temporarily only when we had no public/private keys
            self.wallet = Wallet()
            #self.blockchain = Blockchain( self.node_id )
            self.blockchain = None


      def get_user_input( self ):
            return input('Enter transaction amount : ')


      def print_blockchain( self ):
            # Print the blockchain data
            print('-' * 100)
            for block in self.blockchain.get_chain():
                  print('Block chain value : ' , block)
            print('-' * 100)


      def print_blockchain2( self ):
            for index in range( len( self.blockchain.get_chain() ) ):
                  print( self.blockchain.get_chain()[index] )

      
      def get_transaction_details( self ):
            tx_reciepent = input('Enter Reciepent Name : ')
            tx_amount = input('Enter Transaction Amount : ')
            return ( tx_reciepent, float(tx_amount) )


      def listening_for_input( self ):
            waiting_for_input = True

            while waiting_for_input:
                  print('1. Add new transaction.')
                  print('2. Mine block.')
                  print('3. Display blockchain data.')
                  print('4. Modify value.')
                  #print('5  Print Participants.' )
                  print('6. Print Open Transactions.')
                  print('7. Verify all Transactions.')
                  print('8. Create Wallet.')
                  print('9. Save keys in Wallet.')
                  print('10. Load Wallet.')
                  print('q. Quit')

                  choice = input('Enter your choice : ')

                  # 1. Add new transaction.
                  if( choice == '1' ):
                        tx_details = self.get_transaction_details()

                        print('Transaction details with sender/reciever :: ' , tx_details )
                        
                        recipient, amount = tx_details

                        # Generate and send the signature along with the transaction
                        # Signature will be generated only for sender, reciever and amount with private key
                        signature = self.wallet.sign_transaction( self.wallet.public_key, recipient, amount )

                        if self.blockchain.add_transaction( recipient, self.wallet.public_key, amount, signature ) :
                              print('!!!!!!!!!!     Transaction has been added successfully      !!!!!!!!!')
                        else:
                              print('!!!!!!!!!!!!!!!!!!!!!!!!!! Transaction failed !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
                        
                  # 2. Mine block.
                  elif( choice == '2' ):
                        self.blockchain.mine_block()
                              

                  # 3. Display blockchain data.
                  elif( choice == '3' ):
                        self.print_blockchain()
                        #print( open_transactions )

                  # 4. Modify value.
                  elif( choice == '4' ):
                        if( len( self.blockchain.get_chain() ) >= 1 ):
                              self.blockchain.get_chain()[0] = [
                              {     
                                    'previous_hash' : 'Hacked',
                                    'index' : 20,
                                    'transactions' : [{'sender':'abc', 'recipient': 'def', 'amount':249}]
                              }]
                              
                  # 5  Print Participants.
                  #elif( choice == '5' ):
                  #      print( participants )

                  # 6. Print Open Transactions.
                  elif( choice == '6' ):
                        print('-' * 100)
                        print('Open Transactions are,')
                        for tx in self.blockchain.get_open_transactions():
                              print( tx )
                        print('-'*100)
                        
                  # 7. Verify all Transactions.
                  elif( choice == '7' ):
                        if Verification.verify_transactions( self.blockchain.get_open_transactions(), self.blockchain.get_balance ):
                              print('All transactions are valid....')
                        else:
                              print('---------- Few of the transactions are not valid --------------')

                  # 8. Create Wallet (public/private keys)
                  elif choice == '8':
                        self.wallet.create_keys()
                        # Reinitiallze the blockchain objects with newly generated keys.
                        self.blockchain = Blockchain( self.wallet.public_key )

                  # 9. Save Wallet in a file.
                  elif choice == '9':
                        self.wallet.save_keys()
                        # Reinitiallze the blockchain objects with newly generated keys.
                        self.blockchain = Blockchain( self.wallet.public_key )

                  # 10. Load public/private keys from file
                  elif choice == '10':
                        self.wallet.load_keys()
                        self.blockchain = Blockchain( self.wallet.public_key )

                  elif( choice == 'q' ):
                        waiting_for_input = False
                  else:
                        print('Enter valid choice.')
                  

                  if not Verification.verify_blockchain( self.blockchain.get_chain() ):
                        print( '!!!!!!!!!!!!!!!!!!!!---:::::::::::::::::     Invalid blockchain       ::::::::::::::::---!!!!!!!!!!!!!!!!' )
                        print( self.print_blockchain() )
                        #break

                  print('-' * 100 )
                  print('Calculation balance....' )
                  print('Balance of {} is {:6.2f} : '.format( self.wallet.public_key, self.blockchain.get_balance() ) )
                  print('-' * 100 )
                  
            else:
                  print('User left!')


if __name__ == '__main__':
      node = Node()
      node.listening_for_input()
      