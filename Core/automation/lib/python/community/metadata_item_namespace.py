'''

Class to simplify reading and writing item metadata

Instantiate with item name and the metadata namespace to work with

'''

from org.eclipse.smarthome.core.items import Metadata
from org.eclipse.smarthome.core.items import MetadataKey
from core import osgi

MetadataRegistry = osgi.get_service("org.eclipse.smarthome.core.items.MetadataRegistry")

class Metadata_Item_Namespace(object):
    def __init__(self,item_name,namespace):
        self.item_name = item_name
        self.namespace = namespace

    def __str__(self):
        return 'Item: {}, Namespace = {}, Value {}, Configuration {}'.format(self.item_name,self.namespace,self.get_value(),self.get_configuration())

    def exists(self): # returns true if the namespace for this item exists 
        if self.read_raw() is not None:
            return True
        else:
            return False

    def read_raw(self): # reads the value and configuration for the namespace, generally not called outside of class
        return MetadataRegistry.get(MetadataKey(self.namespace,self.item_name)) # returns None if namespace does not exist
    
    def read(self): # reads the value and configuration for the namespace
        value = self.get_value()
        configuration = self.get_configuration()
        return value,configuration

    def write(self,value = '',configuration = {}): #writes the value and conifuration for the namespace
        MetadataRegistry.add(Metadata(MetadataKey(self.namespace,self.item_name),str(value),configuration))
    
    def remove(self): #removes the namespace 
        MetadataRegistry.remove(MetadataKey(self.namespace,self.item_name))

    def get_value(self): #gets the value of the namespace
        metadata = self.read_raw()
        return metadata and str(metadata.value) or None

    def has_configuration(self): # returns true if the namespace has configuration set
        metadata=self.read_raw() 
        if hasattr(metadata, 'configuration'):
            return True
        else:
            return False

    def get_configuration(self): #gets the configuration of the namespace, returning key/value pairs in a dictionary
        metadata=self.read_raw() 
        md_configuration = hasattr(metadata, 'configuration') and metadata.configuration or {}

        configuration = {} # process any configuration values here
        for key,value in md_configuration.iteritems():
            configuration [str(key)] = str(value)

        return configuration

    def has_configuration_key(self,key): # returns true if the configuration key exists
        if self.get_configuration().haskey(key):
            return True
        else:
            return False

    def get_value_for_configuration_key(self,key): # returns the value for the configuration key
        configuration = self.get_configuration()
        return configuration.has_key(key) and configuration [key] or None 

