import serial
import time
import argparse

"""
Open channel 0 (connstant flow), then open and close channels 1 to 13 (odorants) in succession.
Open channel 0
    Open channel 1 for 10 sec, then close
    Wait 10 sec
    Open channel 2 for 10 sec, then close
    Wait 10 sec
    And so o
Close channel 0
"""
def parse():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p',"--port",help="Name of port where the instrument is connected (default=com3)",default="com3")

    args = parser.parse_args()
    return args
def channeltest(port):
    ser = serial.Serial(port) #defines the port that will be used (how do we know that?)
    ser.boudrate = 9600 #sets the speed at which data will be transferred to ARDUINO (default?)
    ser.flush()
    
    # Open constant flow
    ser.write(b'setchannel 0\r') #set to channel 0 (constant flow)
    ser.write(b'setflow 0:10;\r') # set flow of channel 0 to 10 SPLM (too much?)
    ser.write(b'setvalve 1\r') # set valve to 1 (open)
    flow=0.1 # odorant channel flows will be 0.1 SPLM (needs to be negligible in comparison to constant flow)
    for i in range(1,13): # i is the channel number
        channel_str="setchannel "+str(i)+"\r"
        flow_str="setflow "+str(i)+":"+str(flow)+";\r"
        ser.write(bytes(channel_str)) # set channel
        ser.write(bytes(flow_str)) # set flow
        ser.write(b'setvalve 1\r') # open
        time.sleep(10) # wait
        ser.write(b'setvalve 0\r') # close 
        time.sleep(10) # wait
    
    #close constant flow
    ser.write(b'setchannel 0\r') #set to channel 0 (constant flow)
    ser.write(b'setvalve 0\r') # set valve to 1 (open)
    ser.close()
 
if __name__=="__main__":
    print("Executing script channeltest.py on its own.")
    args=parse()
    port=args.port
else:
    print("Importing script channeltest.py as "+__name__)
channeltest(port)
