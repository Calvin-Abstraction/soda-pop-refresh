#!/usr/bin/python
# createdb.py - create the tables in the database that parsexml.py uses.
#
# Author: John Kloosterman
# Date: Feb. 25, 2011

import sqlite3
from settings import *

# Connect to database
conn = sqlite3.connect(databaseFile)

# Create tables
conn.execute("create table product (unix_time FLOAT, product_id INTEGER, item_price FLOAT, num_vended INTEGER)")
conn.execute("create table temperature (unix_time FLOAT, temp FLOAT, unit CHAR)")
conn.execute("create table names (product_id INTEGER, name VARCHAR)")
conn.execute("CREATE TABLE refills (product_id INTEGER, number INTEGER, unix_time FLOAT)");

# Add names for our specific pop machine.
names = {1:"Coke", 3:"Diet Coke", 5:"Mountain Dew", 7:"Caffeine-free Diet Coke", 8:"A&W Root Beer", 9:"Vernor's"}

for prod, name in names.iteritems():
	conn.execute("insert into names values (?, ?)", [prod, name])

# Finalize
conn.commit()
conn.close()

print "Created database tables in", databaseFile
print "Added specific names for our machine."
