import requests
import base64
import urllib.parse
import webbrowser
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

def EbayRefesh():

    url = 'https://auth.ebay.com/oauth2/authorize'

    clientid = "myclientid"
    clientsecret = "myclientsecret"
    uri = 'myuri'
    key1 = "myUserName"
    key2 = "myPassword"
    
    scope = 'https://api.ebay.com/oauth/api_scope/sell.fulfillment'

    payload = {'client_id':clientid, 'redirect_uri':uri, 'response_type':'code', 'scope':scope}
    
    r = requests.get(url, params=payload)
    driver = webdriver.Safari()
    driver.get(r.url)

    time.sleep(5)

  
    actions = ActionChains(driver)
    actions.send_keys(key1)
    actions.send_keys(Keys.TAB)
    actions.send_keys(key2)
    actions.send_keys(Keys.ENTER)
    actions.perform()

    time.sleep(8)

    code = driver.current_url

    code = urllib.parse.unquote(code)
    code = before, sep, after = code.rpartition("code=")
    code = code[2]
    code = before, sep, after = code.rpartition("&expires")
    code = code[0]

    # EbaAPI URL
    url = "https://api.ebay.com/identity/v1/oauth2/token"

    # Encode to base 64
    B64 = clientid + ":" + clientsecret
    B64e = base64.urlsafe_b64encode(bytes(B64, "utf-8"))
    B64e = B64e.decode('ascii')

    # Variables for headers
    contentType = "application/x-www-form-urlencoded"
    auth = "Basic " + B64e

    # make the request
    headers = {'Content-Type':contentType,'Authorization':auth}
    data = {'grant_type':'authorization_code','code':code, 'redirect_uri':uri}
    r = requests.post(url, headers=headers, data=data)

    token = r.text

    print(token)

EbayRefesh()
