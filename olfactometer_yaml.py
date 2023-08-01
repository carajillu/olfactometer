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
       clean_air_id=yml["parameters"]["clean_air_channel_id"]
       print("Olfactometer will be runing from port ", port)
       print("Constant flow will come from channel ", constant_flow_id)
       print("Constant flow will be set at ", constant_flow_rate," SPLM")
       print("Clean air will come from channel ", clean_air_id)
       return port, constant_flow_rate, constant_flow_id, clean_air_id
   
def check_expts(yml): 
    for key in list(yml.keys())[1:]: # first key is ALWAYS the parameters   
       print("Checking step: ",key)
       if len(yml[key]["channel_id"])==len(yml[key]["flow"]):
          print("... Step ", key, " OK")
       else:
          print("... Step ", key, " malformatted. Check that channel_id, flow and time have the same number of values")
          sys.exit()
    return

def run_expt(yml,ser, constant_flow_rate, constant_flow_id, clean_air_id):
    # 1) Open the constant flow channel
    cmd_str="setflow "+str(constant_flow_id)+":"+str(constant_flow_rate)+";"
    ser_exec(ser,cmd_str)

    cmd_str="setchannel "+str(constant_flow_id)
    ser_exec(ser,cmd_str)

    cmd_str="setvalve 1"
    ser_exec(ser,cmd_str)

    # 2) Run experiments 
    for key in list(yml.keys())[1:]: # first key is ALWAYS the parameters
       
       timeopenvalve=yml[key]["time"] #This is the time this experiment will run for

       # 2.1) Calibrate flows of odorant channels (incl clean air)
       cmd_str="setflow "
       for i in range(0,len(yml[key]["channel_id"])):
           channel_id=yml[key]["channel_id"][i]
           flow_i=yml[key]["flow"][i]
           print("channel ", channel_id, " will be open at ", flow_i, " SPLM for ", timeopenvalve, " seconds")
           #setting the flow of each channel
           cmd_str=cmd_str+str(channel_id)+":"+str(flow_i)+";"          
       ser_exec(ser,cmd_str)
       
       # 2.2) Open the odorant channels (timed)
       time_ms=timeopenvalve*1000
       for i in range(0,len(yml[key]["channel_id"])):
           channel_id=yml[key]["channel_id"][i]

           cmd_str="setchannel "+str(channel_id)
           ser_exec(ser,cmd_str)

           cmd_str="openvalvetimed "+str(time_ms)
           ser_exec(ser,cmd_str)

           pause=int(yml[key]["pause"])
           time.sleep(pause)
       
    # 3) Close the constant flow
    cmd_str="setchannel "+str(constant_flow_id)
    ser_exec(ser,cmd_str)

    cmd_str="setvalve 0"
    ser_exec(ser,cmd_str)
    return

def ser_exec(ser,cmd_str):
    print("WRITING TO SERIAL: ", cmd_str)
    if ser is not None:
       cmd_bytes=(cmd_str+"\r").encode()
       ser.write(cmd_bytes)
    return

if __name__=="__main__":
    args=parse()
    with open(args.input, 'r') as file:
        try:
          yml = yaml.safe_load(file)
        except Exception as error:
          print("The input file has formatting errors.")
          print(error)
          sys.exit()
        else:
           port, constant_flow_rate, constant_flow_id, clean_air_id=set_parameters(yml)
           try:
              ser = serial.Serial(port)
           except:
              print("Serial Port ", port, " cannot be reached.")
              print("Running in emulator mode.")
              print("Press enter to continue or CTRL+C to break execution.") 
              ser=None
              z=input()
           check_expts(yml)
           run_expt(yml,ser, constant_flow_rate, constant_flow_id, clean_air_id)
           

    