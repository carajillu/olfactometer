import serial
import time
ser = serial.Serial('com4') #defines the port that will be used (how do we know that?)
ser.boudrate = 9600 #sets the speed at which data will be transferred to ARDUINO (default?)
ser.flush() # flushes the port buffer 
input("Press any key to start\n") #wait
print("Now we are going to generate an odour on channel 1")
print('The odour "duration" of 200ms is controlled by Sniff-0 ')
input("Press any key to generate the odour\n")
ser.write(b'setchannel 1\r')
ser.write(b'openvalvetimed 200\r')
print("Now the clean air channel is going to be opened")
print("Clean air will be delivered for 1000ms")
input("Press any key to open clean air\n")
ser.write(b'setchannel 0\r')
ser.write(b'setvalve 1\r')
time.sleep(1)
ser.write(b'setvalve 0\r')
print("End")
ser.close()