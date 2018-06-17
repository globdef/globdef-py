from rdflib.namespace import Namespace

GSM = Namespace('https://globdef.github.io/ontology/globdef-meta.owl#')

class DataBundle(object):
    """ Path to data and metadata files """

    def __init__(self, filePath, ontoPath):
        self.filePath = filePath
        self.ontoPath = ontoPath

    def __repr__(self):
        return str(self.__dict__)

