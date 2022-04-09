#!/usr/bin/python
import json
from pprint import pprint
import sys

JSON_FILE = "./json"
JSON_FILE= "/var/www/virtualdharma/httpdocs/AlexaADBackend/Code/ALEXATALKS00.JSON"
JSON_FILE= "/var/www/virtualdharma/httpdocs/AlexaADBackend/Config/RECOMMENDED00.JSON"
JSON_FILE= "/var/www/virtualdharma/httpdocs/AlexaADBackend/TMP/ALEXATALKS00.JSON"
try:
    with open(JSON_FILE,'r') as myfile:
        content = myfile.read()
        print(content)
        d = eval(content)
        print json.dumps(d, indent=4, sort_keys=True)
except ValueError as e:
    print("VALIDATION ERROR")
    print(e)
    exit(0)
except:
    e = sys.exc_info()[0]
    print("VALIDATION ERROR: %s" % e)
    exit(0)
