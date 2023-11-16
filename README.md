# olfactometer
Python program to automate olfactometer experiments.

DEPENDENCIES
   - Anaconda: python environment for installing and using scientific software. 
     Installation instructions can be found at www.anaconda.org.

   - pyserial: helps python interact with serial ports. Can be installed with:
     conda install -c anaconda pyserial

     on the computer that will use the olfactometer.

   - time: helps add pauses between opening valves when needed. 
     Generally, this module comes with any default python installation. Otherwise, it can be installed using the following command:
     conda install -c conda-forge time

USAGE
   python olfactometer_yaml.py -i config_file.yml

   where config_file.yml is the configuration file for the selected experiment. Examples can be found in the folder experiments_yaml.

   Example of running an experiment from scratch (SWRI Sensory computer)
   1) Open Anaconda Prompt
   2) enter the following command:
      cd source\repos\olfactometer
   3) enter the following command:
      python olfactometer_yaml.py -i experiments_yaml\expt1.yml
   
CONFIG FILES
   olfactometer_yaml.py uses yml configuration files. When writing those files, their structure needs to be preserved, as per the following template:

   ##############################################################

   parameters: # All the following parameters need to be specified.
     port: "com3" #Name of the port through which the instrument is connected to the computer
     constant_flow_channel_id: 0 #Channel that will give constant flow (typically 0)
     constant_flow_rate: 2 #Constant flow rate in SPLM
     calibration: no #Whether or not olfactometer_yaml.py has to calibrate the channels (yes/no)
     max_flow: 6 #maximum flow that is gonna go through the system, total flow should not exceed that

   step1:
     seconds: 20 #Time in seconds that this step will run for (always +10 to catch up)
     channels: # Nothing after the colon. on the lines below
      1: 1    # CHANNEL_ID: FLOW
      2: 1
      3: 1

   step2:
     seconds: 20 #Time in seconds that this step will run for (always +10 to catch up)
     channels: # Nothing after the colon. on the lines below
      4: 1    # CHANNEL_ID: FLOW
      5: 1
      6: 1
   #################################################################

   Note the indents (spaces) before the different parameters, or seconds, or channels and then the indents before the specified channels. Those need to be preserved too. 

   YAML does NOT allow 2 experiments with the same name, so make sure each of them has a different name. Otherwise, only the last one with the same name will be run and the order in which the experiments are run will probably be wrong.
   

