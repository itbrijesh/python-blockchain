
class Error:
      
      def __init__( self, message='', code='' ):
            self.__message = message
            self.__code = code

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
