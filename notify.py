
import httplib, urllib

def notify(message, importance, thetype):
    c = httplib.HTTPSConnection("wifi-me-niet.jerryhopper.com:443")
    headers = { "content-type": "", "pragma": "no-cache" , "cache-control": "no-cache" , "accept": "application/json, */*;q=0.1" ,  "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.72 Safari/537.36" }
    params = urllib.urlencode({'mac-wifi': message})
    c.request("POST", "/api/notme",params, headers)
    response = c.getresponse()
    print response.status, response.reason
    data = response.read()
    c.close()
    
