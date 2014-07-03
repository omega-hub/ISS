import urllib2
import json

req = urllib2.Request("http://api.open-notify.org/iss-now.json")
response = urllib2.urlopen(req)

obj = json.loads(response.read())

print obj['timestamp']
print obj['iss_position']['latitude'], obj['iss_position']['longitude']

print obj

# Example prints:
#   1364795862
#   -47.36999493 151.738540034
