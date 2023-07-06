import olfactometer
import argparse

def parse():
    parser = argparse.ArgumentParser()
    parser.add_argument('-e',"--experiment",help="name of the experiment to run")

    args = parser.parse_args()
    return args

if __name__=="__main__":
    args=parse()
    expt=getattr(olfactometer,args.experiment) # gets the module in the olfactometer folder
    expt()