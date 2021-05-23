
#import httplib, urllib
import http.client, urllib
import json
from urllib.parse import urlparse


def donotify(message,SETTINGS_NOTIFYURL):
    # create headers.
    headers = { "content-type": "application/json", "pragma": "no-cache" , "cache-control": "no-cache" , "accept": "application/json, */*;q=0.1" ,  "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.72 Safari/537.36" }
    o = urlparse(SETTINGS_NOTIFYURL)
    # create the appropreate connection
    if o.scheme.lower() == "https":
        c = http.client.HTTPSConnection(o.netloc)
    else:
        c = http.client.HTTPConnection(o.netloc)
    # post data
    c.request("POST", o.path,json.dumps(message), headers)

    # get the result.
    response = c.getresponse()
    print (response.status, response.reason)
    data = response.read()
    c.close()
    #exit()
    return data

