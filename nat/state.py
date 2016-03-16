#!/usr/env/bin python
''' Import Modules '''
import urllib
import urllib2

''' Set all required Variables '''
url1 = 'http://www.google.co.uk'
url2 = 'http://www.pool.ntp.org'
url3 = 'http://www.github.com'

def check_url(url):
    request = urllib2.urlopen(url)
    return request.code

if (check_url(url1) == 200) or (check_url(url2) == 200) or (check_url(url3) == 200):
    f = open('/var/www/html/index.html', 'w')
    f.write("OK")
    f.close()