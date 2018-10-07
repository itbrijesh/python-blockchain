
class Error:
      
      def __init__( self, message='', code='' ):
            self.__message = message
            self.__code = code
            self.NO_DATA_FOUND = 'NO_DATA_FOUND'
            self.NO_DATA_FOUND_MSG = 'No data found !'

      @property
      def message( self ):
            return self.__message 

      @message.setter
      def message( self, value ):
            self.__message = value


      @property
      def code( self ):
            return self.__code

      
      @code.setter
      def code( self, value ):
            self.__code = value


      @staticmethod
      def get_error_object( code, message ):
            error = Error()
            error.code = code
            error.message = message
            return error

      @staticmethod
      def get_no_data_found_error():
            error = Error()
            error.code = 'NO_DATA_FOUND'
            error.message = 'No data found !'
            return error