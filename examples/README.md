# About
This folder contains examples and information on how to run them. Subfolders may include sample excerpts from external datasets for illustrative purposes.

# sample-mixed-data
The folder contains data from
 - the Mini MASC dataset - http://www.anc.org/data/masc/downloads/data-download/
https://storage.googleapis.com/openimages/web/index.html
 - the standard test images dataset collected by ImageProcessingPlace - http://www.imageprocessingplace.com/root_files_V3/image_databases.htm

To run GLOBDEF on this folder, ensure you have a running STANBOL instance on localhost:8080 than cd to the repository root and execute the following:

    activate globdef-py
    python main.py --dataLocation examples\sample-mixed-data\

Observe how the different data types received different enhancements.