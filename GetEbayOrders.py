import requests
import json
import csv
import base64
import urllib.parse
import webbrowser
import pandas as pd
import lxml.html as lh
from boto3.session import Session
import boto3
import os
import fileinput
import sys
from shutil import copyfile
import unicodedata

# Part of a larger file: not all imports may be needed

def EbayAPI():

    rt = "my refresh token"
  
    # Get the token
    url = 'https://api.ebay.com/identity/v1/oauth2/token'
     
    # Developer ID's
    clientid = "my client id"
    clientsecret = "my client secret"
    scope = 'https://api.ebay.com/oauth/api_scope/sell.fulfillment'

    # Encode to base 64
    B64 = clientid + ":" + clientsecret
    B64e = base64.urlsafe_b64encode(bytes(B64, "utf-8"))
    B64e = B64e.decode('ascii')

    contentType = "application/x-www-form-urlencoded"
    auth = "Basic " + B64e

    # make the first request to mint the token
    headers = {'Content-Type':contentType,'Authorization':auth}
    data = {'grant_type':'refresh_token','refresh_token':rt, 'scope':scope}
    r = requests.post(url, headers=headers, data=data)

    # Token is minted
    token = r.text

    # Parse the token
    token = token.rpartition('{"access_token":"')
    token = token[2]
    token = token.rpartition('","expires_in"')
    token = token[0]
    
    # make an API call to get the order ID's
    url = "https://api.ebay.com/sell/fulfillment/v1/order?"
    accToken = token
    auth = "Bearer " + accToken
    orders = "orderfulfillmentstatus:{NOT_STARTED|IN_PROGRESS}"

    headers = {'Authorization':auth}
    payload = {'filter':orders}

    r = requests.get(url, headers=headers, params=payload)
    data = r.text

    path = 'data.json'

    with open(path, 'w') as outfile:
        json.dump(data, outfile)
    
    json_file='data.json'
    with open(json_file, 'r') as json_data:
        x = json.load(json_data)
    
    # convert JSON file into Python compatible
    new = x.replace("\\", "")
    
    path = 'data.txt'
    
    
    try:
        text_file = open(path, 'w')
        text_file.write(new)
        text_file.close()
    except:
        new = new.encode('ascii', 'ignore').decode('ascii')
        text_file = open(path, 'w')
        text_file.write(new)
        text_file.close()

    
    #make an empty list to store all data for every matching order
    data2 = []
    
    #load the data from previous API request that has stored unfufilled orders
    json_file='data.txt'
    with open(json_file, 'r') as json_data:
        x = json.load(json_data)
    
    # Get the order ID for each order
    for key in x["orders"]:
        
         # make the API call to get all information for each order
        thisorderid = str(key['orderId'])
        url = 'https://api.ebay.com/sell/fulfillment/v1/order/' + thisorderid
        
        accToken = token
        auth = "Bearer " + accToken

        headers = {'Authorization':auth}
        
        r = requests.get(url, headers=headers)
        data = r.text
        data2.append(data)
    
    # Make an empty list to store the orders in a CSV file later
    allOrders = []

    #Optional gives a brief readout for Flask
    Overview = []
    
    # save and load JSON data for each order
    for i in data2:
        
        path = 'data2.txt'

        with open(path, 'w') as outfile:
            json.dump(i, outfile)
        
        json_file='data2.txt'
        with open(json_file, 'r') as json_data:
            x = json.load(json_data)
        
        # make the JSON data compatible with Python
        new = x.replace("\\", "")
    
        path = 'data2.txt'
        
        try:
            text_file = open(path, 'w')
            text_file.write(new)
            text_file.close()
        except:
            new = new.encode('ascii', 'ignore').decode('ascii')
            text_file = open(path, 'w')
            text_file.write(new)
            text_file.close()
        
        # load the JSON data
        json_file='data2.txt'
        with open(json_file, 'r') as json_data:
            x = json.load(json_data)
        
        orderID = str(x["orderId"])
        legacyID = str(x['legacyOrderId'])
        date1 = str(x['creationDate'])
        date2 = str(x['lastModifiedDate'])
        orderStatus = str(x['orderFulfillmentStatus'])
        PaymentStatus = str(x['orderPaymentStatus'])
        sellerId = str(x['sellerId'])
        username = str(x['buyer']['username'])
        value = str(x['pricingSummary']['priceSubtotal']['convertedFromValue'])
        currency = str(x['pricingSummary']['priceSubtotal']['convertedFromCurrency'])
        cancel = str(x["cancelStatus"]["cancelState"])
        name = str(x["fulfillmentStartInstructions"][0]["shippingStep"]["shipTo"]["fullName"])
        line1 = str(x["fulfillmentStartInstructions"][0]["shippingStep"]["shipTo"]["contactAddress"]["addressLine1"])
        try:
            line2 = str(x["fulfillmentStartInstructions"][0]["shippingStep"]["shipTo"]["contactAddress"]["addressLine2"])
        except:
            line2 = ""

        city = str(x["fulfillmentStartInstructions"][0]["shippingStep"]["shipTo"]["contactAddress"]["city"])

        try:
            state = str(x["fulfillmentStartInstructions"][0]["shippingStep"]["shipTo"]["contactAddress"]["stateOrProvince"])
        except:
            state = ""
            
        postcode = str(x["fulfillmentStartInstructions"][0]["shippingStep"]["shipTo"]["contactAddress"]["postalCode"])
        countryCode = str(x["fulfillmentStartInstructions"][0]["shippingStep"]["shipTo"]["contactAddress"]["countryCode"])
        phone = str(x["fulfillmentStartInstructions"][0]["shippingStep"]["shipTo"]["primaryPhone"]["phoneNumber"])
        
        #Not all orders have the email supplied
        try:
            email = str(x["fulfillmentStartInstructions"][0]["shippingStep"]["shipTo"]["email"])
        except: 
            email = ""
        shippingService = str(x["fulfillmentStartInstructions"][0]["shippingStep"]["shippingServiceCode"])
        
        productDetails2 = []
        
        for key in x['lineItems']:
            try:
                sku = (str(key["sku"]))
            except:
                sku = ""
            lineID = (str(key["lineItemId"]))
            title = (str(key["title"]))
            cost = (str(key["lineItemCost"]["convertedFromValue"]))
            qty = (str(key["quantity"]))
            shipping = (str(key["deliveryCost"]["shippingCost"]["convertedFromValue"]))
            productDetails = [sku, lineID, title, cost, qty, shipping]
            productDetails2.append(productDetails)
        
        # repeat rows for multiple item orders
        j = 0
        if len(productDetails2) == 1:
            productDetails2 = productDetails2[0]
            order = [orderID, legacyID, date1, date2, orderStatus, PaymentStatus, sellerId, username, value, currency, cancel, name, line1, line2, city, state, postcode, countryCode, phone, email, shippingService, productDetails2[0], productDetails2[1], productDetails2[2], productDetails2[3], productDetails2[4], productDetails2[5]]
            if orderStatus == "NOT_STARTED" and PaymentStatus != "FULLY_REFUNDED":
                allOrders.append(order)
                
        # For multiple orders by the same customer       
        else:
            for X2 in productDetails2:
                order = [orderID, legacyID, date1, date2, orderStatus, PaymentStatus, sellerId, username, value, currency, cancel, name, line1, line2, city, state, postcode, countryCode, phone, email, shippingService, X2[0], X2[1], X2[2], X2[3], X2[4], X2[5]]
                if orderStatus == "NOT_STARTED" and PaymentStatus != "FULLY_REFUNDED":
                    allOrders.append(order)
                    j += 1
 
    file = "myEbayfile.csv"
    Header = ('orderID', 'leagcyID', 'date1', 'data2', 'Order Status', 'Payment Status', 'Seller', 'Username', 'Total Value', 'Curency', 'Cancelled', 'Name', 'Line1', 'Line2', 'City', 'State', 'PostCode', 'Country', 'Phone', 'Email', 'Shipping Service', 'SKU', 'Line ID', 'Title', 'Cost', 'QTY', 'Shipping')

    with open(file, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(Header)
        writer.writerows(allOrders)
        
    #Write to AmazonS3
    s3 = boto3.client('s3', aws_access_key_id='myAWSid' , aws_secret_access_key='myS3Secret')
    s3.upload_file(file, 'my-bucket-name', 'my_folder/' + file)
    
    EbayAPI()
