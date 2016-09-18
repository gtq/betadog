import datetime
import mechanize
import cookielib
import html2text
import csv
import ConfigParser
import string
import sys
import logging
import sqlite3
from BeautifulSoup import BeautifulSoup

#set currentdate
now = datetime.datetime.now()
currdate = now.strftime("%Y%m%d")

#load config file
config = ConfigParser.RawConfigParser()
config.read('phedgemarket.cfg')

#load run specific config
fnamepattern = config.get('RunSettings','fnamepattern')
ignoredate = config.getboolean('RunSettings','ignoredate')

#load site specific config
detailurl = config.get('SiteSettings','detailurl')
datafile = config.get('SiteSettings','datafile')
tablename = config.get('SiteSettings','tablename')
idcol = config.get('SiteSettings','idcol')
col1 = config.get('SiteSettings','col1')
col2 = config.get('SiteSettings','col2')
col3 = config.get('SiteSettings','col3')
col4 = config.get('SiteSettings','col4')
col5 = config.get('SiteSettings','col5')
col6 = config.get('SiteSettings','col6')

#TODO:Fix logging
logger = logging.getLogger("mechanize")
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel(logging.DEBUG)

# Browser
br = mechanize.Browser()

# Cookie Jar
cj = cookielib.LWPCookieJar()
br.set_cookiejar(cj)

# Browser options
br.set_handle_equiv(True)
br.set_handle_gzip(True)
br.set_handle_redirect(True)
br.set_handle_referer(True)
br.set_handle_robots(False)
#br.set_debug_http(True)
#br.set_debug_responses(True)
#br.set_debug_redirects(True)

# Follows refresh 0 but not hangs on refresh > 0
br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)

# User-Agent (this is cheating, ok?)
br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]

print currdate
#legacy code line
urlstring=detailurl
fnamestring=fnamepattern % (currdate)
print fnamestring

try:
 br.open(urlstring)
except:
 print "Failed to open market data summary"
 #no access to datasource, should just exit
 quit()
html = br.response().read()
soup = BeautifulSoup(html)
marketdata = soup.find("div", {"id": "market"})
details = marketdata.findAll("tr")
marketdate = marketdata.find("th","alignR").string[8:20].strip()
marketnow=datetime.datetime.strptime(marketdate, "%b %d, %Y").date()
if ignoredate:
 currdate=marketnow.strftime("%Y%m%d")
 fnamestring=fnamepattern % (currdate)
else:
 if (marketnow.day!=now.day or marketnow.month!=now.month or marketnow.year!=now.year):
  print marketnow
  quit()

configmain = ConfigParser.RawConfigParser()
configmain.read('../phstockmain.cfg')
configmain.set('RunSettings','offset',0)
configmain.set('RunSettings','currdate',currdate)
with open('../phstockmain.cfg', 'wb') as configfile:
 configmain.write(configfile)
configmain = ConfigParser.RawConfigParser()
configmain.read('phedgemain.cfg')
configmain.set('RunSettings','offset',0)
configmain.set('RunSettings','currdate',currdate)
with open('phedgemain.cfg', 'wb') as configfile:
 configmain.write(configfile)


marketdatarows=[]
for row in details:
 rowcols = row.findAll("td")
 if (len(rowcols)>0):
  marketdatarows.append([rowcols[0].string.strip(),rowcols[1].string.strip()])
marketdatatrows=zip(*marketdatarows)
print marketdatatrows
try:
 conn = sqlite3.connect(datafile)
 c = conn.cursor()
except:
 print "Failed to open datafile"
 pass

try:
 with open(fnamestring, 'wb') as csvfile:
  tswriter = csv.writer(csvfile, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_MINIMAL)
  for row in marketdatatrows:
   if len(row)>1:
    tswriter.writerow(row)
#left column label, right column data
    if 'Total Volume' not in row:
     querystring = "INSERT OR IGNORE INTO {tn} ({idf}, {cn1},{cn2},{cn3},{cn4},{cn5},{cn6}) VALUES (%s,%s)" % (currdate,','.join([x.encode('ascii','ignore').replace(',','') for x in row]))
     querystring = querystring .\
     format(tn=tablename, idf=idcol, cn1=col1,cn2=col2,cn3=col3,cn4=col4,cn5=col5,cn6=col6)
     c.execute(querystring)
except:
 print "Failed to write output data"
 pass

conn.commit()
conn.close()

