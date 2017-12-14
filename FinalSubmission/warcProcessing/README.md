This folder contains the code used to process WARC files in a parallelized manner using the multiprocessing Python module.
Communication is done via pipes, which can be read from and written to. For pipes, a read call is a blocking call - if there is nothing in the pipe, the process will wait there and make read calls until there is something in the pipe. Most cleaning functions have a process that is specific to it. The subprocesses are killed useing a -1 as a kill signal. More information can be found in section 7.4 in the final report. 


The config file is used to specify the name of the tsv file that is being written, the warc file that is to be read from, and the collection names and id's for that event (lines 1- 16). This configuration file also contains a flag for if the file to be processed is a warc file or not. This is a leftover from previous iterations of the code before PySpark was successfully used to parallelize cleaning for webpage data. For the purposes of this code, the flag should always be set to 1. 


The generateWarc file script is meant to be placed in the main directory of the Event Focused Crawler. It accepts the file name of what file was used as input for the EFC. This is done since the EFC create a directory for output based on the input file's name. 
