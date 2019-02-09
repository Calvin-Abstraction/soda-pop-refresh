# Spot to put credentials so that all the different forms
#  can get them from a central location.
#
# Don't check this in!

import MySQLdb

def mysqlconnect():
    return MySQLdb.connect( host='localhost',
                            user='popmachine',
                            passwd='2SQV77Hp770I2VXuxbmTPb',
                            db='popmachine' )
