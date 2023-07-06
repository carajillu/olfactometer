import serial
import time

"""
Flush the olfactometer tubes with clean air for the specified
amount of time in seconds
"""
def clean():
    ser = serial.Serial('com4') #defines the port that will be used (how do we know that?)
    ser.boudrate = 9600 #sets the speed at which data will be transferred to ARDUINO (default?)
    ser.flush()
    ser.write(b'setchannel 0\r') #set to channel 0 (clean air)
    ser.write(b'setvalve 1\r') # set valve to 1 (open)
    time.sleep(1) # wait
    ser.write(b'setvalve 0\r') # set valve to 0 (closed)
    ser.close()
 
if __name__=="__main__":
    print("Executing script clean.py on its own.")
else:
    print("Importing script clean.py as "+__name__)
clean()
