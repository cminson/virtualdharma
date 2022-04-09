#!/usr/bin/python
import string
from subprocess import call

base = "https://www.audiodharma.org/talks?page=X"
i = 2
cmd = base.replace("X", str(i))
#call(["wget", "-ahtml", cmd])
#call(["ls", "-l"])

"""
for i in range(0, 371):
    cmd = base.replace("X", str(i))
    print(cmd)
    call(["wget", "-ahtml", cmd])
"""

cmd = "https://www.audiodharma.org/series/14356"
call(["wget", "-atest", cmd])

