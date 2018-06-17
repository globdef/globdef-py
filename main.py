"""Just a place to start writing code into."""
import sys
import rdflib
import pprint
import argparse
import logging
import datetime
import os

from rdflib.namespace import Namespace, RDF, RDFS, OWL
from rdflib import Graph, URIRef, Literal, BNode
from dataModel import DataBundle, GSM
from enhancer import DataTypeEnhancer, STANBOLBasedEnhancer
from collections import deque

def get_data_bundles(path, reset=False):
    """Get the data bundles from a path. If a file has no bundle, create one"""
    # list all the files in the path
    files = [
        fname for fname in os.listdir(path)
        if os.path.isfile(os.path.join(path, fname))
    ]
    bundles = []

    ONTO_FILE_EXTENSION = ".globdef"

    # map files to their globig sidecar
    for fname in files:
        if not fname.endswith(ONTO_FILE_EXTENSION):
            bundles.append(
                DataBundle(
                    os.path.join(path, fname),
                    os.path.join(path, fname + ONTO_FILE_EXTENSION)))

    # create one for them
    for b in bundles:
        ontog = Graph()
        nowLiteral = Literal(datetime.datetime.utcnow())

        if os.path.isfile(b.ontoPath) and not reset:
            ontog.parse(source=b.ontoPath)

        else:
            dataFile = URIRef('dataFile')
            ontoFile = URIRef('ontoFile')

            ontog.add((dataFile, RDF.type, GSM.File))
            ontog.add((dataFile, GSM.hasFileName, Literal(b.filePath)))
            ontog.add((dataFile, GSM.isDescribedBy, ontoFile))
            ontog.add((dataFile, GSM.isCreatedOn,
                       Literal(
                           datetime.datetime.fromtimestamp(
                               os.path.getctime(b.filePath)))))
            ontog.add((dataFile, GSM.isModifiedOn,
                       Literal(
                           datetime.datetime.fromtimestamp(
                               os.path.getmtime(b.filePath)))))

            ontog.add((ontoFile, RDF.type, GSM.SidecarFile))
            ontog.add((ontoFile, GSM.hasFileName, Literal(b.ontoPath)))
            ontog.add((ontoFile, GSM.isCreatedOn, nowLiteral))
            ontog.add((ontoFile, GSM.isModifiedOn, nowLiteral))

        initialGoal = BNode()
        ontog.add((initialGoal, RDF.type, GSM.InitialGoal))
        ontog.add((initialGoal, GSM.isCreatedOn, nowLiteral))

        ontog.serialize(destination=b.ontoPath, format='pretty-xml')
        ontog.close()

    # TODO - create generator over these bundles

    return bundles

def get_matching_enhancer(enhancers, bundle, metaModel):
    for e in enhancers:
        target_goal = e.matchModel(metaModel)
        if target_goal:
            logging.info("Enhancer %s matched %s for goal %s", type(e), bundle.filePath, target_goal)
            return (e, target_goal)
    return None
            
def process_bundles(bundles):
    """Rough processing algorithm:
    Enhancers: [{goalMatcher, waitingQueue, state=idle|processing}]
    ActiveQueue [Bundle{file, ontoFile}] - goals available, waiting for enhancers
    IncompleteQueue [Bundle{file, ontoFile}] - no enhancers for goals
    PassiveQueue [Bundle{file, ontoFile}] - all goals completed

    While allEnhancers not idle and activeQueue not empty 
        - loop through active bundles
        - find enhancer that matches goals
        - if no enhancer => move to passiveQueue
        - pop bundle from active list
        - send bundle to enhancer queue
        - wait for any enhancer to finish

    Note: The current implementation is ad-hoc and only achieves the same end result
    as the outlined algorithm above. We don't use parallellism yet.
    """
    active_queue = deque(bundles)
    passive_queue = deque()
    enhancers = [DataTypeEnhancer(), STANBOLBasedEnhancer('http://localhost:8080/enhancer')]

    logging.info("Start processing of %d bundles with %d enhancers", len(bundles), len(enhancers))
    while len(active_queue) > 0:
        b = active_queue.popleft()
        logging.info("Processing bundle %s ...", b.filePath)

        metaModel = Graph()
        metaModel.parse(source=b.ontoPath)
        e = get_matching_enhancer(enhancers, b, metaModel)
        if e == None:
            logging.info("No more enhancers for bundle %s", b.filePath)
            passive_queue.append(b)
        else:
            logging.info("Enhancing bundle %s with %s, for goal %s", b.filePath, e[0].name(), e[1])
            e[0].doProcess(b, e[1], metaModel)
            # Finally return the bundle to the active queue to be processed by more enhancers
            active_queue.append(b)
        

def main():
    """Entry point for globig-data"""
    logging.basicConfig(level=logging.INFO)


    # - parse arguments: dataLocation
    parser = argparse.ArgumentParser()
    defDataPath = '/dev/globig/data/test'
    parser.add_argument(
        '-d',
        '--dataLocation',
        help="Location of the folder with data to be enhanced.\n'%s' by default."
        % defDataPath,
        default=defDataPath)

    defMetaOntoPath = './ontologies/globdef-meta.owl'
    parser.add_argument(
        '-s',
        '--sideCarOntoLocation',
        help=
        "Location of the ontology that describes the sidecar metadata.\n'%s' by default."
        % defMetaOntoPath,
        default=defMetaOntoPath)

    parser.add_argument(
        '--cleanPreviousMeta',
        help="Whether to clean all meta previously accompanying the data",
        action='store_true')

    parser.add_argument(
        '--processFirstOnly',
        help="Whether to process only one bundle. Useful for testing.",
        action='store_true')

    args = parser.parse_args()

    # - load meta ontology
    metaOnto = Graph()
    metaOnto.parse(source=args.sideCarOntoLocation)

    # - load data bundles (create empty meta if missing - file type)
    bundles = get_data_bundles(args.dataLocation, args.cleanPreviousMeta)
    pprint.pprint(bundles)

    if args.processFirstOnly:
        bundles = bundles[:1]

    process_bundles(bundles)    


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

    sys.exit(main())
    # sys.exit(testme())
