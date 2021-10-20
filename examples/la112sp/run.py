#!/usr/bin/env python
import subprocess
import sys

def run():
    cmds=["spaghetti --spin sep --save la112_ex_sep", 
          "spaghetti --spin join --save la112_ex_join"]
    for cmd in cmds:
        info = subprocess.call(cmd, shell=True)
        if info != 0:
            print("This example has failed!")
            sys.exit(-1)
    print("This example was executed successfully!")


if __name__ == "__main__":
    run()
    



