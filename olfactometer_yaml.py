import serial
import argparse
import yaml
import sys
import time

def parse():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i',"--input",help="Name of the yaml file with the experiment",default=None)
    args = parser.parse_args()
    return args

def set_parameters(yml):
    if list(yml.keys())[0]!="parameters": # In python 3, dict_keys object is not subscriptable
       print ("First key in input file is not parameters. Exiting.")
       sys.exit()
    else:
       port=yml["parameters"]["port"]
       constant_flow_rate=yml["parameters"]["constant_flow_rate"]
       constant_flow_id=yml["parameters"]["constant_flow_channel_id"]
       calibration=yml["parameters"]["calibration"]
       print("Olfactometer will be runing from port ", port)
       print("Constant flow will come from channel ", constant_flow_id)
       print("Constant flow will be set at ", constant_flow_rate," SPLM")
       if calibration==True:
         print("Channels will be calibrated before starting each experiment.")
       else:
         print("Calibration will NOT be done for any channels. Make sure it is already done.") 
         z=input("Press enter to continue or ctrl+C to exit.")
       return port, constant_flow_rate, constant_flow_id, calibration
   
def check_expts(yml):
    if yml["parameters"]["calibration"]==False:
      print("Calibration has been done externally. Displayed flow rate values may not be true")
    for key in list(yml.keys())[1:]: # first key is ALWAYS the parameters   
       print("Checking step:",key, "...")
       print("Run time:",yml[key]["seconds"],"seconds")
       for channel in list(yml[key]["channels"].keys()):
         print("Channel",channel,"will run at",yml[key]["channels"][channel],"SPLM")
    return

def run_calibration(ser,channel_id,flow):
   cmd_str="setflow "+str(channel_id)+":"+str(flow)+";"
   outcome=ser_exec(ser,cmd_str)
   return outcome

def run_expt(yml,ser, constant_flow_rate, constant_flow_id, calibration):
    # Set the instrument to verbose so that we can veerify steps went through
    cmd_str="setverbose 2"
    result=ser_exec(ser,cmd_str)

    # 0) Calibrate the constant flow channel if required
    if calibration is True:
       print("calibrating constant flow")
       outcome=run_calibration(ser,constant_flow_id,constant_flow_rate)
       print(constant_flow_id,constant_flow_rate,outcome)
       if outcome is False:
          print("constant flow calibration failed. Exiting.")
          return

    # 1) Open constant flow
    cmd_str="setchannel "+str(constant_flow_id)
    result=ser_exec(ser,cmd_str)

    cmd_str="setvalve 1"
    result=ser_exec(ser,cmd_str)

    # 2) Run experiments 
    for key in list(yml.keys())[1:]: # first key is ALWAYS the parameters
       z=input("Press Enter to start: "+key)
       timeopenvalve=yml[key]["seconds"] #This is the time this experiment will run for

       # 2.1) Calibrate flows of odorant channels if required
       if calibration is True:
          print("calibrating odorant channels")
          for channel in list(yml[key]["channels"].keys()):
              flow=yml[key]["channels"][channel]
              outcome=run_calibration(ser,channel,flow)
              print(channel,flow,outcome)
              if outcome is False:
                 print("Calibration of channel",channel,"failed. Exiting.")
                 return
       
       # 2.2) Open the odorant channels (timed)
       time_ms=timeopenvalve*1000
       cmd_str="openmultivalvetimed "+str(time_ms)+" "+";".join(map(str,list(yml[key]["channels"].keys())))
       result=ser_exec(ser,cmd_str)
      
       # 2.3) Once all commands are submitted, wait for the execution time + 10 seconds to catch up. 
       time.sleep(timeopenvalve+10)
           
       
    # 3) Close the constant flow
    cmd_str="setchannel "+str(constant_flow_id)
    result=ser_exec(ser,cmd_str)

    cmd_str="setvalve 0"
    result=ser_exec(ser,cmd_str)
    return

def ser_exec(ser,cmd_str):
    print("WRITING TO SERIAL: ", cmd_str)
    if ser is None:
       print("Cannot verify command in emulator mode. Assuming it was successful.")
       return True

    cmd_bytes=(cmd_str+"\r").encode()
    ser.write(cmd_bytes)

    result=False   
    readback=ser_listen(ser)
    if readback is None:
       pass
    elif ("Result" in readback):
       print (readback)
       readback=ser_listen(ser)
       if readback is None:
         pass
       elif ("*OK" in readback):
         result=True
    
    if result==False:
       print("COMMAND FAILED. EXITING.")
       sys.exit()
    else:
       return result

def ser_listen(ser):
   readback="\r\n"
   waiting_time=0
   readback = ser.readline().decode('utf-8')
   while(readback is "\r\n"):
      readback = ser.readline().decode('utf-8')
      time.sleep(1)
      waiting_time+=1
      if waiting_time>60:
         print("instrument is taking too long to reply. Aborting.")
         break
   return readback
      
if __name__=="__main__":
    args=parse()
    with open(args.input, 'r') as file:
        try:
          yml = yaml.safe_load(file)
          print(yml)
        except Exception as error:
          print("The input file has formatting errors.")
          print(error)
          sys.exit()
        else:
           port, constant_flow_rate, constant_flow_id, calibration=set_parameters(yml)
           try:
              ser = serial.Serial(port)
              ser.boudrate=9600
              ser.flush()
           except:
              print("Serial Port ", port, " cannot be reached.")
              print("Running in emulator mode.")
              ser=None
              z=input("Press enter to continue or CTRL+C to break execution.")
           check_expts(yml)
           run_expt(yml,ser, constant_flow_rate, constant_flow_id, calibration)
           

    