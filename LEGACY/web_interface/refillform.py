#!/usr/bin/python2
#
# Form to enter machine refills.
#

import cgi
import cgitb
import time
import hashlib
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
    print "<tr><th>Pop</th>"
    print "<th><b>Total</b> number of bottles in machine</th></tr>"

    for row in c:
        print "<tr><td>" 
        print cgi.escape(row[1])
        print "</td><td><input type='text' name='refill_" + str(row[0]) + "' />"
        print "</td></tr>"

    conn.close()
    print "</table>"
    return

def displayForm():
    print "<html><head></head><body>"

    print "<h1>Update pop stocks</h1>"
    print "The number you need to enter is the total number of the kind of pop in the machine,"
    print "<i>excluding</i> the ones below the metal barrier in the bottom of the slot. "
    print "The machine always keeps one pop there, even when it says 'sold out' so if we count it, "
    print "nothing will ever be marked 'sold out'."
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
    secret = form.getfirst("secret", None)
    hash_secret = hashlib.sha256(secret).hexdigest()
    if hash_secret != "8548d75fcb3a2a275a1ba868a36f6a26e528f16b07aa7d8006616ad090a9b349":
        print "Wrong secret!"
        exit()

    conn = mysqlconnect()
    c = conn.cursor()

    c.execute("SELECT product_id FROM products")
    for row in c:
        number = form.getfirst("refill_" + str(row[0]), None)

        if number is None:
            continue

        d = conn.cursor()
        d.execute("INSERT INTO refills VALUES (%s, %s, %s )",
                  [ time.time(), row[0], number ] )

    conn.commit()
    print "Refill duly noted."

    conn.close()
    return

form = cgi.FieldStorage()
someText = form.getfirst("submitted", "")
if someText:
    commitForm()
else:
    displayForm()
