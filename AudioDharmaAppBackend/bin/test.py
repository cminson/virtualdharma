#!/usr/bin/python
# 
# sophia.py
#
# implements all APIs to access system
# runs as http server on port SOPHIA_SERVER_PORT
#

DEBUG = 0
DEBUG = 1

import os
import datetime
import time
import cgi
import sys
import socket
import json
import random
import re
import hashlib
import numpy as np
import http.server
import socketserver
from common import is_port_available, HOST, SOPHIA_SERVER_PORT
from openai import OpenAI

from common import  LOG, configureOpenAIKey,  getTalkNameSimilarPath, getSpeakerSimilarPath,  textToInteger, remove_prefix_from_text, getIndexPath



OPENAI_API_KEY = configureOpenAIKey()


client = OpenAI(api_key=OPENAI_API_KEY)

resp = client.responses.create(
    model="gpt-4.1",
    instructions="You are a helpful assistant.",
    input="explain quantum entanglement simply? like I'm a dog",
    max_output_tokens=200
)
print(resp.output_text)

"""
resp = client.responses.create(
    #model="gpt-4.1",
    model="gpt-5",
    input=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello! explain quantum entanglement simply? like I'm a dog"}
    ],
    #max_completion_tokens=50,  
    max_output_tokens=50,
)

print(resp.output_text)
"""

