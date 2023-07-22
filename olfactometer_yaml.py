import serial
import argparse
import yaml
import sys

def parse():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i',"--input",help="Name of the yaml file with the experiment",default=None)
    args = parser.parse_args()
    return args

def set_parameters(yml):
    print(yml)
    if list(yml.keys())[0]!="parameters": # In python 3, dict_keys object is not subscriptable
       print ("First key in input file is not parameters. Exiting.")
       sys.exit()
    else:
       port=yml["parameters"]["port"]
       total_flow=yml["parameters"]["total_flow"]
       constant_flow_id=yml["parameters"]["constant_flow_channel_id"]
       clean_air_id=yml["parameters"]["clean_air_channel_id"]
       print("Olfactometer will be runing from port ", port)
       print("Total flow set to ", total_flow, " SPLM")
       print("Constant flow will come from channel ", constant_flow_id)
       print("Clean air will come from channel ", clean_air_id)
       return port, total_flow, constant_flow_id, clean_air_id

    
def check_expts(yml): 
    for key in list(yml.keys())[1:]: # first key is ALWAYS the parameters   
       print("Checking step: ",key)
       if len(yml[key]["channel_id"])==len(yml[key]["flow"]):
          print("... Step ", key, " OK")
       else:
          print("... Step ", key, " malformatted. Check that channel_id, flow and time have the same number of values")
          sys.exit()
    return

def run_expt(yml,ser, total_flow, constant_flow_id, clean_air_id):
    for key in list(yml.keys())[1:]: # first key is ALWAYS the parameters
       flow_sum=0
       flow_str="setflow "
       time=yml[key]["time"]
       constant_flow_rate=total_flow
       for i in range(0,len(yml[key]["channel_id"])):
           channel_id=yml[key]["channel_id"][i]
           flow_i=yml[key]["flow"][i]
           flow_sum=flow_sum+flow_i
           print("channel ", channel_id, " will be open at ", flow_i, " SPLM for ", time, " seconds")
           
           #setting the flow of each channel
           flow_str=flow_str+str(channel_id)+":"+str(flow_i)+";"
           constant_flow_rate=constant_flow_rate-flow_i           
           
       if flow_sum>total_flow:
          print("Total flow will be set to ", flow_sum, "SPLM which is larger than indicated on the parameters.")
          print("constant flow rate will be set to 0 SPLM")
          print("this happens when the sum of the odorant flows is larger than the specified total flow")
       z=input("press enter to continue or ctrl+c to kill the execution")

       #calculate the new rate of the constant flow and calibrate the channel flows
       constant_flow_rate=total_flow-flow_sum
       if constant_flow_rate>0:
          flow_str=flow_str+str(constant_flow_id)+":"+str(constant_flow_rate)+";\r"
          #ser.write(bytes(flow_str))

       # Open the constant flow (not timed)
       if constant_flow_rate>0:
          cmd_str="setchannel "+str(constant_flow_id)+"\r"
          #ser.write(bytes(cmd_str))
          cmd_str="setvalve 1\r"
          #ser.write(bytes(cmd_str))
       
       # Open the odorant channels (timed)
       for i in range(0,len(yml[key]["channel_id"])):
           channel_id=yml[key]["channel_id"][i]
           flow_i=yml[key]["flow"][i]
           cmd_str="setchannel "+str(channel_id)+"\r"
           #ser.write(bytes(cmd_str))
           cmd_str="openvalvetimed "+str(time)+"\r"
           #ser.write(bytes(cmd_str))          
       
       #close the constant flow
       cmd_str="setchannel "+str(constant_flow_id)+"\r"
       #ser.write(bytes(cmd_str))
       cmd_str="setvalve 1\r"
       #ser.write(bytes(cmd_str))        
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
           port, total_flow, constant_flow_id, clean_air_id=set_parameters(yml)
           #ser = serial.Serial(port)
           ser=None
           check_expts(yml)
           run_expt(yml,ser, total_flow, constant_flow_id, clean_air_id)
           

    