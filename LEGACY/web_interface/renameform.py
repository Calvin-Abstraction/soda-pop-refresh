#!/usr/bin/python2
#
# Form to enter machine refills.
#

import cgi
import cgitb
import time
import hashlib
import MySQLdb
from mysqlconnect import *

print "Content-type: text/html"
print ""

# Debugging
import cgitb
cgitb.enable()


def generatePopsForm():
    conn = mysqlconnect()
    c = conn.cursor()

    c.execute("SELECT product_id, product FROM products");

    print "<table>"

    for row in c:
        print "<tr><td>" 
        print "Slot "
        print str(row[0])
        print ":"
        print "</td><td><input type='text' name='name_" + str(row[0]) + "' "
        print 'value="' + cgi.escape(row[1]) + '" />'
        print "</td></tr>"

    conn.close()
    print "</table>"
    return

def displayForm():
    print "<html><head></head><body>"

    print "<h1>Rename pop machine products</h1>"
    print "<form method='post'>"
    print "Enter the secret word:"
    print "<input type='text' name='secret'>"
    generatePopsForm()
    print "<input type='Submit' name='submitted' value='Submit' />"
    print "</form>"

    print "</body></html>"
    return

def commitForm():
    global form

    # The secret word isn't too secret... but I don't want
    #  everyone meddling with my database.
    secret = form.getfirst("secret", "")
    hash_secret = hashlib.sha256(secret).hexdigest()
    if hash_secret != "8548d75fcb3a2a275a1ba868a36f6a26e528f16b07aa7d8006616ad090a9b349":
        print "Wrong secret!"
        exit()

    conn = mysqlconnect()
    c = conn.cursor()

    c.execute("SELECT product_id FROM products")
    for row in c:
        new_name = form.getfirst("name_" + str(row[0]), "")

        if new_name == "":
            continue

        d = conn.cursor()
        d.execute("UPDATE products SET product=%s WHERE product_id=%s",
                  [ new_name, row[0] ] )

    conn.commit()
    print "New names duly noted."

    conn.close()
    return

form = cgi.FieldStorage()
someText = form.getfirst("submitted", "")
if someText:
    commitForm()
else:
    displayForm()
