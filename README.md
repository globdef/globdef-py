# About globdef-py
This is a python implementation of the GlobDEF framework.

Mind it that this project is more an experimental work in progress than a finished product

## Working with the conda environment

**Note**: The current conda environment only works on Windows. Linux support is on the roadmap but not a high priority.

 - Install conda (both miniconda and anaconda are fine) and open the commandline.
 - To create the necessary environment on a new machine run `conda env create -f environment.yml`
 - To activate it run `activate globig-data`
 - To install new things
    - just use `pip install` within the activated environmant,
    - export the environment with `conda env export -f environment.yml`
    - check remove the `prefix` line at the end of `environment.yml`
    - commit it for others to use the environment
 - To update a local environment with changes from `environment.yml` run `conda env update -f environment.yml`

## First run
 - Run `python main.py --help` to see the options
 - Download some data (files) in a folder (say `/a/b/c`)
 - Run `python main.py -d /a/b/c` to enhance it with default enhancers

## Resources for development and experiments
 - run `python pyconsole.py` for interactive python console in the current folder<br>
   This console has auto-completiong and can be used to experiment with modules in the project during development. For example one can `import dataModel` then experiment with the types defined there.

### Online resources
 - http://rdflib.readthedocs.io/en/stable/rdf_terms.html - terms and concepts in rdflib
 - http://rdflib.readthedocs.io/en/stable/intro_to_creating_rdf.html - working with rdflib

### Sideways tools for experimentation
  - DBPedia Spotlight - takes 2-3 GB storage and needs 8GB RAM, which also implies a x64 Java version
    - See how to download and run here - https://github.com/dbpedia-spotlight/dbpedia-spotlight/wiki/Run-from-a-JAR
    - Run with at least 8GB for the English model: `java -Xmx8g -XX:-UseGCOverheadLimit -jar dbpedia-spotlight-1.0.0.jar en_2+2 http://localhost:2222/rest`
    - Use pyspotlight for simple python experiments - https://github.com/ubergrape/pyspotlight
  - Apache STANBOL - requires maven and takes time to build
    - Download and extract the latest release from here - https://stanbol.apache.org/downloads/releases.html
    - See how to build here - https://stanbol.apache.org/docs/trunk/tutorial.html
      - If working on Windows on C:, give Full permissions to Everyone for the extracted folder
      - Running maven with `-DskipTests=true` speeds it up

## Simple roadmap

### POC checkpoints
  - [done] Create an easy-to-setup development environment
  - [done] Model of the data bundle.
  - [done] Working forward-chaining pipeline.
  - [done] Experiment with external enhancement engines.
  - [done] Implement enhancers based on external engines.
  - [done] Document a case of dynamic choice of enhancer based on the data.
  - [todo] Summarize experimentation results and publish on globdef.github.io
  
### What's next...
These are loosely formulated goals. Each may take more time and effort than anticipated.

 - Replace the goals with more generic matching in the metamodel.
 - Define mechanism for error reporting and propagation from the enhancers.
 - Add a unit-test framework.
 - Make the enhancers dynamically plugable (process py files from a folder).
 - Abstract communication with enhancers so that it can scale (out-of-process).
 - Integrate PROV-O (see W3C PROV) for provenance.
 - De-duplication of annotations in meta models.
 - Conflict resolution in forward chaining.
 - Goal-driven backward chaining.
 - Implement some naive overall confidence algorithm.
 - Add equivalent conda support for Linux (check out meta packages)