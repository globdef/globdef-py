import Queue
import logging
import magic
import requests

from rdflib import Graph, URIRef, Literal, BNode
from rdflib.namespace import Namespace, RDF, RDFS, OWL

from dataModel import DataBundle, GSM

FOAF = Namespace('http://xmlns.com/foaf/0.1/')
DCTERMS = Namespace('http://purl.org/dc/terms/')
FISE = Namespace('http://fise.iks-project.eu/ontology/')

def getMimeType(filePath):
    return magic.Magic(mime=True).from_file(filePath)

class Enhancer(object):
    
    def __init__(self):
        self._bundleQueue = Queue.Queue()
    
    def matchModel(self, ontoGraph):
        raise NotImplementedError("Goal matching is implemented in children")

    def doProcess(self, dataBundle, goalInstance, metaModel):
        raise NotImplementedError("Bundle processing is implemented in children")

    def name(self):
        return self.__class__.__name__

    def enqueBundle(self, dataBundle):
        self._bundleQueue.put(dataBundle)

    def pendingCount(self):
        return self._bundleQueue.qsize()

    def processNext(self):
        """ Returns None if nothing to process"""
        next = self._bundleQueue.get_nowait()
        return None if not next else self.doProcess(next)
        

class DataTypeEnhancer(Enhancer):
    def find_matching_goal(self, metaModel):
        goalBaseTypes = [GSM.InitialGoal]
        
        # Determine all possible classes for the base types
        goalTypes = []
        while len(goalBaseTypes) > 0:
            g = goalBaseTypes.pop()
            goalBaseTypes += [gs[0] for gs in metaModel.triples((None, RDFS.subClassOf, g))]
            goalTypes.append(g)

        logging.debug("Found candidate goal classes: %s", goalTypes)

        # Now find all instances that don't have an enhancement result yet
        for gt in goalTypes:
            for i in metaModel.triples((None, RDF.type, gt)):
                logging.debug("Traversing %s", i)
                existingResult = next(metaModel.triples((i[0], GSM.hasResult, None)), None)
                if not existingResult:
                    return i[0]
                else:
                    logging.debug("Skipping goal %s of type %s as it is already satisfied", i[0], gt)
        return None

    def matchModel(self, metaModel):
        # TODO wtf is goalClasses
        matching_goal = self.find_matching_goal(metaModel)
        logging.info("Matching goal is %s", repr(matching_goal))
        return matching_goal

    def doProcess(self, dataBundle, goalInstance, metaModel):
        g = metaModel
        # g.parse(source=dataBundle.ontoPath) # see issue #1

        # Create instance to represent the current enhancer
        thisEnhancer = BNode()
        g.add((thisEnhancer, RDF.type, GSM.Enhancer))
        
        # Create instance for the enhancement result
        enhancementResult = BNode()
        g.add((enhancementResult, RDF.type, GSM.GoalResult))
        g.add((goalInstance, GSM.hasResult, enhancementResult))

        # Mark the goal as enhanced by the current enhancer
        g.add((enhancementResult, GSM.isCreatedBy, thisEnhancer))

        # Create enhancement instance from external ontology
        enhancementInstance = BNode()
        g.add((enhancementInstance, RDF.type, FOAF.Document))
        g.add((enhancementInstance, DCTERMS['format'], Literal(getMimeType(dataBundle.filePath))))

        # Link the goal result to the enhancement annotation
        g.add((enhancementResult, GSM.hasEnhancement, enhancementInstance))

        # Add new goals for subsequent enhancers that work on typed data
        g.add((BNode(), RDF.type, GSM.KnownTypeGoal))

        g.serialize(destination=dataBundle.ontoPath, format='pretty-xml')
        g.close()

class STANBOLBasedEnhancer(Enhancer):

    def __init__(self, endpoint):
        self._endpoint = endpoint

    def find_datatype_goal(self, metaModel):
        for i in metaModel.triples((None, RDF.type, GSM.KnownTypeGoal)):
            logging.debug("Traversing %s", i)
            existingResult = next(metaModel.triples((i[0], GSM.hasResult, None)), None)
            if not existingResult:
                formatTriplet = next(metaModel.triples((None, DCTERMS['format'], None)), None)
                if not formatTriplet:
                    continue
                knownFormat = str(formatTriplet[2])
                if knownFormat.split('/')[0] != 'text':
                    logging.debug("Skipping format %s as not supported by STANBOL based enhancer", knownFormat)
                else:
                    return i[0]
            else:
                logging.debug("Skipping goal %s of type %s as it is already satisfied", i[0], GSM.KnownTypeGoal)
        return None

    def matchModel(self, metaModel):
        matching_goal = self.find_datatype_goal(metaModel)
        logging.info("STANBOLBasedEnhancer matches goal %s", repr(matching_goal))
        return matching_goal
        
    def doProcess(self, dataBundle, goalInstance, metaModel):
        g = metaModel

        # We know that the format is in the metaModel since we matched it
        knownFormat = str(next(g.triples((None, DCTERMS['format'], None)), None)[2])

        params = {'dbpedia-dereference:enhancer.engines.dereference.languages': 'en'}
        headers = {'Content-type': knownFormat, 'Accept': 'application/rdf+xml'}
        with open(dataBundle.filePath, 'r') as dataFile:
            data = dataFile.read()
        
        logging.debug("Posting to stanbol endpoint %s with headers %s, params %s and data with size %d", self._endpoint, headers, params, len(data))
        resp = requests.post(self._endpoint, data=data, headers=headers, params=params)
        assert(resp.status_code == 200)

        # Create instance to represent the current enhancer
        thisEnhancer = BNode()
        g.add((thisEnhancer, RDF.type, GSM.Enhancer))
        
        # Create instance for the enhancement result
        enhancementResult = BNode()
        g.add((enhancementResult, RDF.type, GSM.GoalResult))
        g.add((goalInstance, GSM.hasResult, enhancementResult))

        # Mark the goal as enhanced by the current enhancer
        g.add((enhancementResult, GSM.isCreatedBy, thisEnhancer))

        # Add the response to the metamodel
        g.parse(data=resp.content)

        # Link all instances in resp with enhancementResult
        for i in metaModel.triples((None, RDF.type, FISE.Enhancement)):
            g.add((enhancementResult, GSM.hasEnhancement, i[0]))

        g.serialize(destination=dataBundle.ontoPath, format='pretty-xml')
        g.close()
