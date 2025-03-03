import requests
    
url = "https://reg-prod.ec.udmercy.edu/StudentRegistrationSsb/ssb/searchResults/getSectionPrerequisites"

session = requests.Session()  # Maintain session
response = session.get(url)

cookies = session.cookies.get_dict()  # Extract cookies
print(cookies)
