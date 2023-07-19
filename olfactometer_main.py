import olfactometer
import argparse

def parse():
    parser = argparse.ArgumentParser()
    parser.add_argument('-e',"--experiment",help="name of the experiment to run")
    parser.add_argument('-p',"--port",help="Name of port where the instrument is connected (default=com3)",default="com3")

    args = parser.parse_args()
    return args

if __name__=="__main__":
    args=parse()
    expt=getattr(olfactometer,args.experiment) # gets the module in the olfactometer folder
    expt(args.port)