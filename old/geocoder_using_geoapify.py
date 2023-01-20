import requests, urllib

def geocode(address): #returns [x, y]
    url="https://api.geoapify.com/v1/geocode/search?text="+ urllib.parse.quote(address)+"&apiKey=dddb306415724bfe99d6882228f04fef"
    resp = requests.get(url).json()
    return resp['features'][0]['geometry']['coordinates']

print(geocode('6 Shakambari Nagar, 1st stage, JP Nagar, Bangalore'))