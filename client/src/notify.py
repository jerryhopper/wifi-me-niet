
#import httplib, urllib
import http.client, urllib
import json


def donotify(message):
    c = http.client.HTTPSConnection("wifi-me-niet.jerryhopper.com:443")
    headers = { "content-type": "application/json", "pragma": "no-cache" , "cache-control": "no-cache" , "accept": "application/json, */*;q=0.1" ,  "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.72 Safari/537.36" }
    c.request("POST", "/api/donotfollowtest",json.dumps(message), headers)
    response = c.getresponse()
    print (response.status, response.reason)
    data = response.read()
    c.close()
    return data

