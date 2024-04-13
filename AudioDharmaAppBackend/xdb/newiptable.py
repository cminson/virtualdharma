#!/usr/bin/python
import sys
import cgi
import MySQLdb as mdb

#sudo apt-get install mysql-server
#sudo apt-get install python-pip python-dev libmysqlclient-dev
#sudo apt install python-pip
#sudo apt-get install mysql-server
#pip install MySQL-python

"""
CREATE0 = "use ad"
#CREATE1 = "create table ops (id INT NOT NULL AUTO_INCREMENT PRIMARY KEY, ip varchar(20), deviceID varchar(64), operation varchar(16), devicetype varchar(10), sharetype varchar(16), filename varchar(128), date varchar(16), seconds varchar(16), city varchar(32), state varchar(32), country varchar(4), zip varchar(16), latitude varchar(64), longitude varchar(64), attr1 varchar(8), attr2 varchar(8), attr3 varchar(8), created TIMESTAMP DEFAULT NOW())"
CREATE1 = "create table ipmap (id INT NOT NULL AUTO_INCREMENT PRIMARY KEY, ip varchar(20), city varchar(32), country varchar(2), created TIMESTAMP DEFAULT NOW())"
#USER1 = "CREATE USER 'cminson'@'localhost' IDENTIFIED BY 'ireland';"
#USER2 = "GRANT ALL ON ad.* TO 'cminson'@'localhost';"


try:
    con = mdb.connect('localhost', 'cminson', 'ireland', 'ad');
    cur = con.cursor()

    command = CREATE0
    cur.execute(command)
    con.commit()

    command = CREATE1
    cur.execute(command)
    con.commit()

except mdb.Error, e:
    error = "Error %d: %s" % (e.args[0],e.args[1])
    print(error)
    sys.exit(1)

finally:
    print("done")

"""


