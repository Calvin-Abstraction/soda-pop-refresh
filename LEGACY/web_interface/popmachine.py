#!/usr/bin/python
# Combine Twitter feed, graphs, etc. into one page.
#
# Last Updated on February 09, 2018
# By Ben Kastner Isfar Baset, and Quentin Baker

from graphlib import *
from statuslib import *

import cgitb
cgitb.enable()

googleAnalytics = """
<script type="text/javascript">

  var _gaq = _gaq || [];
  _gaq.push(['_setAccount', 'UA-23444084-1']);
  _gaq.push(['_trackPageview']);

  (function() {
    var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;
    ga.src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js';
    var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s);
  })();

</script>
"""

lighttpdlogo = """
<p style='text-align: center'>
<a href="https://www.lighttpd.net/">
<img class=lighttpd-badge src="https://www.lighttpd.net/light_button.png" alt="Lighttpd Server"> 
</a></p>
"""
pythonlogo = """
<p style='text-align: center'>
<a href="https://python.org/">
<img src="https://www.python.org/static/community_logos/python-powered-w-140x56.png" alt="Powered by Python">
</a></p>
"""
raspi = """
<p style='text-align: center'>
<a href="https://raspberrypi.org/">
<img src="https://www.raspberrypi.org/homepage-9df4b/favicon.png" alt="Served on Delicious Pi 3">
</a></p>
"""

html5badge = """
<p style='text-align: center'>
This page is valid HTML5. </p>

<p style='text-align: center'>
<img src="http://www.w3.org/html/logo/badge/html5-badge-h-graphics.png" width="133" height="64" alt="HTML5 Powered with Graphics, 3D &amp; Effects" title="HTML5 Powered with Graphics, 3D &amp; Effects">
"""

logo = """
<p style='text-align: center'> 
<img class=soda-poplogo src="soda-poplogo.svg" alt="Soda can next to the words Soda-Pop.">
</p>
"""

barGraph = """
<div style="position: absolute;right: 160px;top: 535px;"> 
<img src="bargraph.png" width="550" height="500" alt="Bargraph showing sales of Soda-Pop by day.">
</div>
"""

# If we use border-radius, we can't use this.
cssbadge = """<br/>
<br/>
<a href="http://jigsaw.w3.org/css-validator/check/referer">
    <img style="border:0;width:88px;height:31px"
        src="http://jigsaw.w3.org/css-validator/images/vcss-blue"
        alt="Valid CSS!" />
</a>
</p>
"""

# This can't be xhtmlized because of the Twitter widget.
print "Content-type: text/html"
print ""

# By the way, we're HTML5. So there's no head or body tags, and this doctype
# is correct.
print """<!DOCTYPE html>
<meta charset="UTF-8">
"""
"""print "<logo class='soda-poplogo'>"""
"""print logo"""
"""print barGraph"""
print "<title>Calvin CS Pop Machine</title>"
print googleAnalytics
graphHeaders()
print "<link rel='stylesheet' href='popmachine.css' media='screen'/>"
print logo

print """
<h1> Calvin Computer Science Pop Machine </h1>
"""
print "<table class='mainTable'>"
print "<tr><td style='vertical-align: top'>"
infoTable()
"""print barGraph"""
print "<br/><br/>"
print "<h3>Tools Used</h3>"
print lighttpdlogo
print pythonlogo
print raspi
# print html5badge # Currently we don't like the way this looks, so we're omitting.
print "</td>"

print "<td>"
print """
<h3>Information</h3>
<p>I am the Calvin Computer Science department's pop machine. <br/> 
I live in the corner of SB321, the CS lounge. <br/>
You should come visit me some time.</p>"""
graphBody(600,300)

print "</td></tr></table>"
print "<p class='credits'>Maintainer: Quentin Baker &lt;qrb2&gt;</p>"
