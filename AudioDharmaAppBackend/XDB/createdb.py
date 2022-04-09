#!/usr/bin/python
import sys
import cgi
import MySQLdb as mdb

#sudo apt-get install mysql-server
#sudo apt-get install python-pip python-dev libmysqlclient-dev
#sudo apt install python-pip
#sudo apt-get install mysql-server
#pip install MySQL-python

#CREATE0 = "drop database ad"
#CREATE1 = "create database ad"
#CREATE2 = "use ad"
#CREATE3 = "create table track (id INT NOT NULL AUTO_INCREMENT PRIMARY KEY, deviceID varchar(64), operation varchar(16), sharetype varchar(16), filename varchar(128), date varchar(16), time varchar(16), city varchar(32), state varchar(32), country varchar(32), zip varchar(16), altitude varchar(64), latitude varchar(64), longitude varchar(64), created TIMESTAMP DEFAULT NOW())"
CREATE3 = "create table track (id INT NOT NULL AUTO_INCREMENT PRIMARY KEY, deviceID varchar(64), operation varchar(16), sharetype varchar(16), filename varchar(128), date varchar(16), time varchar(16), city varchar(32), state varchar(32), country varchar(32), zip varchar(16), altitude varchar(64), latitude varchar(64), longitude varchar(64), created TIMESTAMP DEFAULT NOW())"
#USER1 = "CREATE USER 'cminson'@'localhost' IDENTIFIED BY 'ireland';"

USER2 = "GRANT ALL ON ad.* TO 'cminson'@'localhost';"


"""
try:
    con = mdb.connect('localhost', 'cminson', 'ireland', 'ad');
    cur = con.cursor()

    command = CREATE0
    cur.execute(command)
    con.commit()

    command = CREATE1
    cur.execute(command)
    con.commit()

    command = CREATE2
    cur.execute(command)
    con.commit()

    command = CREATE3
    cur.execute(command)
    con.commit()

except mdb.Error, e:
    error = "Error %d: %s" % (e.args[0],e.args[1])
    print(error)
    sys.exit(1)

finally:
    print("done")
"""


