#!/usr/bin/python3
import json
import sys

len = len(sys.argv)
if len != 2:
    print("usage: validate.py filename")
    json_file = "/var/www/virtualdharma/httpdocs/AudioDharmaAppBackend/Config/CONFIG00.JSON"
    #json_file = "/var/www/virtualdharma/httpdocs/AudioDharmaAppBackend/crons/DEV.JSON"
else:
    json_file = sys.argv[1]

try:
    print(json_file)
    with open(json_file,'r') as myfile:
        data  = json.load(myfile)
        #print(data)
        print("{}: JSON Valid".format(json_file))
except ValueError as e:
    print(e)
    print("{}: Bad JSON!".format(json_file))
    exit(0)
except:
    e = sys.exc_info()[0]
    print(e)
    print("{}: Bad JSON!".format(json_file))
    exit(0)
