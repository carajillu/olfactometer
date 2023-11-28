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
       run=yml["parameters"]["run"]
       max_flow=yml["parameters"]["max_flow"]
       pause=yml["parameters"]["pause"]
       print("Olfactometer will be runing from port ", port)
       print("Constant flow will come from channel ", constant_flow_id)
       print("Constant flow will be set at ", constant_flow_rate," SPLM")
       if calibration==True:
         print("Channels will be calibrated before starting each experiment.")
       else:
         print("Calibration will NOT be done for any channels. Make sure it is already done.") 
         z=input("Press enter to continue or ctrl+C to exit.")
       return port, constant_flow_rate, constant_flow_id, calibration, run, max_flow, pause
   
def check_expts(yml):
    if yml["parameters"]["calibration"]==False:
      print("Calibration has been done externally. Displayed flow rate values may not be true")
    for key in list(yml.keys())[1:]: # first key is ALWAYS the parameters   
       print("Checking step:",key, "...")
       print("Run time:",yml[key]["seconds"],"seconds")
       total_flow=yml["parameters"]["constant_flow_rate"]
       for channel in list(yml[key]["channels"].keys()):
         if (yml[key]["channels"][channel]>0):
            print("Channel",channel,"will run at",yml[key]["channels"][channel],"SPLM")
            total_flow=total_flow+yml[key]["channels"][channel]
         else:
            print("Channel ",channel,"'s flow has been set to ",yml[key]["channels"][channel],". This channel will be skipped.")
       if (total_flow>max_flow):
          print("The total flow for experiment",key,"is set to",total_flow,". Max flow is",max_flow,". Press Enter to continue or ctrl+C to abort execution.")
          z=input()
    return

def run_calibration(ser,yml):
   channels=[yml["parameters"]["constant_flow_channel_id"]]
   flows=[yml["parameters"]["constant_flow_rate"]]
   for key in list(yml.keys())[1:]:
      for channel in list(yml[key]["channels"].keys()):
         if channel in channels:
            print("Channel "+str(channel)+" has been specified more than once. Only the first instance will be taken into account")
            print("This is normal if you are using same channels at different steps")
            z=input("Please press enter to confirm.")
            continue
         channels.append(channel)
         flows.append(yml[key]["channels"][channel])
   
   print(channels)
   print(flows)
   
   z=input("Please attach output tubes to calibration ports and press enter")
   print("calibrating odorant channels one by one")
   for i in range(0,len(channels)):
       if (flows[i]==0):
          print("Channel ", channels[i], " has flow set to zero. Skipping.")
          continue
       cmd_str="setflow "+str(channels[i])+":"+str(flows[i])+";"
       ser_exec(ser,cmd_str)
       outcome=check_cmd_success(ser)
       if outcome is False:
          z=input("Calibration of channel",channel,"failed. Do you want to continue? (y/n)").lower()
          while (z!="y" and z!="n" and z!="yes" and z!="no"):
             z=input("please enter y or n")
          if (z[0]=="y"):
             continue
          else:
             return False
   z=input("Calibration complete. Please reattach the output tubes to the nose piece and press enter.")
   return True

def run_step(yml, key):
    z=input("Press Enter to start step \""+key+"\", or type \"skip\" and press enter to skip it\n")
    if (z=="skip"):
       print("skipping step ",key)
       return
    
    timeopenvalve=yml[key]["seconds"] #This is the time this experiment will run for
          
    # 2.1) Open the odorant channels (timed)
    time_ms=timeopenvalve*1000
    channels_lst=[]
    for channel in yml[key]["channels"].keys():
       if (yml[key]["channels"][channel]==0):
          continue
       channels_lst.append(channel)
    cmd_str="openmultivalvetimed "+str(time_ms)+" "+";".join(map(str,channels_lst))
    ser_exec(ser,cmd_str)
   
    # 2.2) Once all commands are submitted, wait for the execution time + 10 seconds to catch up.
    print("Pausing execution for",yml["parameters"]["pause"]," seconds (this is normal).")
    time.sleep(timeopenvalve+yml["parameters"]["pause"]) 
    return

def run_expt(yml,ser,constant_flow_id):

    # 1) Open constant flow
    cmd_str="setchannel "+str(constant_flow_id)
    ser_exec(ser,cmd_str)

    cmd_str="setvalve 1"
    ser_exec(ser,cmd_str)

    # 2) Run experiments 
    for key in list(yml.keys())[1:]: # first key is ALWAYS the parameters
       run_step(yml,key)

    while (key!=""):       
       key=input("Please enter the name of a previous step if you wish to repeat it, or press enter to finish the experiment\n")
       if (key==""):
          continue
       elif key in (list(yml.keys())[1:]):
          run_step(yml,key)
       else:
          print("Invalid step name. Please enter again.")

    # 4) Close the constant flow
    cmd_str="setchannel "+str(constant_flow_id)
    ser_exec(ser,cmd_str)

    cmd_str="setvalve 0"
    ser_exec(ser,cmd_str)
    return

def ser_exec(ser,cmd_str):
    print("WRITING TO SERIAL: ", cmd_str)
    if ser is None:
       return
    cmd_bytes=(cmd_str+"\r").encode()
    ser.write(cmd_bytes)
    
def check_cmd_success(ser):    
    if ser is None:
       print ("Command verification not available in emulator mode. Assuming success.")
       return True
    time.sleep(1) # waiting for the instrument to send output (just 1 sec)  
    readback = ser.readline().decode('utf-8')
    print(readback)
    while (("*OK" not in readback) and ("*NOK" not in readback)):
       readback = ser.readline().decode('utf-8')
       print(readback)
       time.sleep(1)

    if ("*OK" in readback):
       result=True
    elif ("*NOK" in readback):
       result=False
    
    if result==False:
       print("COMMAND FAILED. EXITING.")
       sys.exit()
    else:
       return result
      
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
           port, constant_flow_rate, constant_flow_id, calibration, run, max_flow,pause=set_parameters(yml)
           try:
              ser = serial.Serial(port)
              ser.boudrate=115200
              ser.flush()
              # Set the instrument to verbose so that we can veerify steps went through
           except:
              print("Serial Port ", port, " cannot be reached.")
              print("Running in emulator mode.")
              ser=None
              z=input("Press enter to continue or CTRL+C to break execution.")
           
           check_expts(yml)
           
           cmd_str="setverbose 1"
           ser_exec(ser,cmd_str)
           
           if calibration is True:
              outcome=run_calibration(ser,yml)
              if outcome is False:
                 print ("Calibration falied. Exiting.")
                 sys.exit()
           if run is True:
              run_expt(yml,ser,constant_flow_id)
           

    