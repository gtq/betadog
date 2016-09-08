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
from phstocksymbol import symbols

#load config file
config = ConfigParser.RawConfigParser()
config.read('../phstockmain.cfg')

#load run specific config
currdate = config.get('RunSettings','currdate')
offset = config.getint('RunSettings','offset')
fnamepattern = config.get('RunSettings','fnamepattern')

#load site specific config
frmusername = config.get('SiteSettings','frmusername')
frmpasswd = config.get('SiteSettings','frmpasswd')
username = config.get('SiteSettings','username')
passwd = config.get('SiteSettings','passwd')
enablelogin = config.getboolean('SiteSettings','enablelogin')
loginurl = config.get('SiteSettings','loginurl')
logouturl = config.get('SiteSettings','logouturl')
detailurl = config.get('SiteSettings','detailurl')
headerlist = ['Time','Price','Volume','Buyer','Seller']

datafile = config.get('SiteSettings','datafile')
tablename = config.get('SiteSettings','tablename')
idcol1 = config.get('SiteSettings','idcol1')
idcol2 = config.get('SiteSettings','idcol2')
col1 = config.get('SiteSettings','col1')
col2 = config.get('SiteSettings','col2')
col3 = config.get('SiteSettings','col3')
col4 = config.get('SiteSettings','col4')
col5 = config.get('SiteSettings','col5')
col6 = config.get('SiteSettings','col6')


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

# The site we will navigate into, handling it's session
if enablelogin:
 try:
  br.open(loginurl)
 except:
  print "Error during login"
  quit()
 #print br.response().read()
 # Select the first (index zero) form
 br.select_form(nr=0)

 #User credentials
 br.form[frmusername]=username
 br.form[frmpasswd]=passwd

 # Login
 br.submit()
#print br.response().read()
# Filter all links to mail messages in the inbox
#all_msg_links = [l for l in br.links(url_regex='\?v=c&th=')]
# Select the first 3 messages
#for msg_link in all_msg_links[0:3]:
#    print msg_link
    # Open each message
#    br.follow_link(msg_link)
try:
 conn = sqlite3.connect(datafile)
 c = conn.cursor()
except:
 print "Failed to open datafile"
 pass

cnt=offset
for secsym in symbols[cnt:]:
 urlstring=detailurl % (secsym)
 fnamestring=fnamepattern % (secsym,currdate)
 cnt=cnt+1
 print cnt
 print secsym
 br.open(urlstring)
 html = br.response().read()
 soup = BeautifulSoup(html)
 transactions = soup.findAll("tr")
#trnrows = transactionsam.findAll("tr")
#print trnrows
 with open(fnamestring, 'wb') as csvfile:
  tswriter = csv.writer(csvfile, delimiter=' ',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
  for row in transactions:
   rowwrite=[]
   rowcols = row.findAll("span")
   for col in rowcols:
    if ((col.string != None) and (row.find("span","trnTime")!=None) and
       (col.string not in headerlist)):
        rowwrite.append(col.string.strip())
#      if (col.string not in ['Time','Price','Volume','Buyer','Seller']):
    else:
     if (row.find("span","trnItemBUp") != None):
      rowwrite.append("BUp")
     elif (row.find("span","trnItemSDown")!=None):
      rowwrite.append("SDown")
     elif ((row.find("span","trnTime")!=None) and (row.find("span","trnTime").string!="Time")):
      #row has no change
      rowwrite.append("NC")
     else:
      print "header"

   if len(rowwrite)>1:
    tswriter.writerow(rowwrite)
    print rowwrite
    querystring = "INSERT OR IGNORE INTO {tn} ({idf1}, {idf2}, {cn1},{cn2},{cn3},{cn4},{cn5},{cn6}) VALUES (%s,'%s',%s)" % (currdate,secsym,','.join(["'%s'" % x.encode('ascii','ignore').replace(',','') for x in rowwrite]))
    print querystring
    querystring = querystring .\
    format(tn=tablename, idf1=idcol2, idf2=idcol2, cn1=col1,cn2=col2,cn3=col3,cn4=col4,cn5=col5,cn6=col6)
    c.execute(querystring)

#left column buyer, right column seller

conn.commit()
conn.close()

# Logout
if enablelogin:
 br.open(logouturl)
