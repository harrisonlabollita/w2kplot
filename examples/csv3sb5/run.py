#!/usr/bin/env python
import subprocess
import sys

def run():
    cmds=["spaghetti --save csv3sb5_ex", 
          "spaghetti --switch fatbands --save csv3sb5_fat"]
    for cmd in cmds:
        info = subprocess.call(cmd, shell=True)
        if info != 0:
            print("This example has failed!")
            sys.exit(-1)
    print("This example was executed successfully!")


if __name__ == "__main__":
    run()
    



