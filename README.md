![Soda-Pop-Logo](assets/soda-poplogo.svg)

# Soda-Pop-Refresh

Soda-Pop-Refresh is a webserver stack running on a Raspberry Pi 3 that pulls data from a vending 
machine on Calvin College's campus (SB 382) and generates a webpage for the use of students and 
faculty.

## A Brief Overview of the Data Flow

### From Machine to Database
The vending machine, a Vendo 540 model, has a simple microcontroller that keeps track of various 
data-points such as sales, temperature, money in the machine, and other diagnostic data. This device 
can then offload the data over a serial interface using the [DEX protocol][DEX-WP]. This data is 
normally managed by specially designed devices used by a vending technician whenever they refill or 
service the machine.

By creating a 1/4" TRS to RS-232 (9-Pin D-Sub) cable, we can pass the DEX data into our Raspberry Pi.
This is handled by the C code in dex_communicator; which drops the DEX data into a temporary file.
Our glue code, written in Python, then passes this DEX data to dex_parser, which converts the DEX to 
XML. This XML is then parsed and added to an sqlite database.

[DEX-WP]: https://en.wikipedia.org/wiki/DEX_(protocol)
### Making it Accessable
We chose to host the web server on the Pi itself. Because of this, the server had to be small in size
and fast. As we want to build a webpage populated with information from our sqlite DB, we also wanted
to use CGI (Common Gateway Interface) to allow our scripts dynamic generation ability.

Given these constraints, we chose [Lighttpd][lighttpd-home] as it is light and small
(unlike apache), *and* it supports CGI out-of-the box (unlike nginx).

Our lighttpd server is barebones. Currently we configured it just enough to pass through to our python
scripts that we put in /var/www/cgi-bin/.

[lighttpd-home]: https://lighttpd.net/

## Moving Forward
The progress we made from a very outdated server running on a different architecture and a full
dedicated machine, to an up-to-date stack acheiving the same responsiveness while being *contained
entirely on a credit-card sized ARM SoC*, is a great start. However, this project is not done as of
today. 

Calvin's C.S. Club, [Abstraction][abs], has adopted this project and intends to add the following by the
end of the semester:

1. Responsive Website Design
1. Social Media Integration (Tweet whenever it sells a soda, for example)
1. Internal Management Tools and Statistics   
    * To Elaborate on this a little, we would like to use the sales data with a statistical model to
give the soda-pop refillers (student volunteers!) an estimate of how much of each beverage we should
get. Once we have 365 days of data, we could even pre-emptively purchase more stock during seasonal
highs (e.g. finals) and reduce refill frequency during lows (e.g. summer).

[abs]: https://abs.calvin.edu/
