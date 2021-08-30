import requests
headers = { 'User-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0' }

#For Setting Cookies
URL = 'http://www.thegameschedule.com/mv/index.php'

session = requests.Session()
r = session.get(URL, headers = headers)

LOGIN_URL = 'http://www.thegameschedule.com/mv/ref1.php'
data = {
    'requiredref_num': '19172',
    'requiredpassword':  'VR9vn2',
    'Submit1': 'Go'
}

post_response = session.post(LOGIN_URL, data=data, headers=headers)

print(post_response.content)