
class Printable:

      # String re-presentation of your class object.
      def __repr__( self ):
            return str( self.__dict__ )
