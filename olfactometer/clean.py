import serial
import time
import argparse

"""
Flush the olfactometer tubes with clean air for the specified
amount of time in seconds
"""
def parse():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p',"--port",help="Name of port where the instrument is connected (default=com3)",default="com3")

    args = parser.parse_args()
    return args
def clean(port):
    ser = serial.Serial(port) #defines the port that will be used (how do we know that?)
    ser.boudrate = 9600 #sets the speed at which data will be transferred to ARDUINO (default?)
    ser.flush()
    ser.write(b'setchannel 0\r') #set to channel 0 (clean air)
    ser.write(b'setvalve 1\r') # set valve to 1 (open)
    time.sleep(10) # wait
    ser.write(b'setvalve 0\r') # set valve to 0 (closed)
    ser.close()
 
if __name__=="__main__":
    print("Executing script clean.py on its own.")
    args=parse()
    port=args.port
else:
    print("Importing script clean.py as "+__name__)
clean(port)
