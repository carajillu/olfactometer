# olfactometer
Set of python scripts used to automate olfacotmeter tasks at SWRI.
All experiments will start and end by emitting clean air for 1 second, so that no cross-contamination may occur between experiments

USAGE

DEPENDENCIES
   - pyserial: helps python interact with serial ports. can be installed with "pip install pyserial" on the computer that will use the olfactometer.
   - time: helps add pauses between opening valves when needed. As far as I am aware, this module comes with any default python installation.
SCRIPTS