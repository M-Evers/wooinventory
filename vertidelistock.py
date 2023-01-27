import requests
from typing import OrderedDict
import time
from requests.structures import CaseInsensitiveDict
from flask import jsonify
from flask import Flask, render_template
import json

headers = CaseInsensitiveDict()
headers["Accept"] = "application/json"
headers["Content-Type"] = "application/json"
endpoint = "http://api.vertideli.com/wp-json/wc/v3/products"



app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['EXPLAIN_TEMPLATE_LOADING'] = True
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.static_folder = 'static'

now = time.time()

def gettoken():
    username = "someone@vertideli.com"
    password = "xxx"

    ## Get Bearer token from webshop
    url = 'https://api.vertideli.com/wp-json/jwt-auth/v1/token'
    payload={"username":  username ,"password": password }
    resp = requests.post(url,data=payload)
    d = resp.json()
    print('Retrieved new API token')
    try:
        headers["Authorization"] = "Bearer "+d['token']
        return True
    except:
        print('App:No TOKEN from WP')
        print('App:Restarting in 5 seconds')
        time.sleep(5)
        return False



@app.before_first_request
def declarestuff():
    tokened = False
    while not(tokened):
        now = time.time()
        tokened = gettoken()
        time.sleep(5)
    
        
  

@app.route("/")
def index():
    if (time.time() - now) > 86400:
        tokened = False
        while not(tokened):
            tokened = gettoken()
            time.sleep(5)
    per_page = 100
    page = 1

    thelist = []

    while True:
        params = {
            "per_page": per_page,
            "page": page
        }
        response = requests.get(endpoint, headers=headers, params=params)
        products = response.json()
        for product in products:
            #print (product)
            mysku = product['sku']
            myname = product['name']
            myquantity = product['stock_quantity']
            
            myatumlocations = product['atum_locations']
            for myatumlocation in myatumlocations:
                mylocation = myatumlocation['name']

            myitem = {"sku":mysku,"name":myname,"quantity":myquantity,"location":mylocation}
            thelist.append(myitem)

            #print(product['sku'])
        page += 1
        if len(products) == 0:
            break

    json_str = json.dumps(thelist)
    thelist = json.loads(json_str)

    # sort the list by the 'sku' field
    sorted_list = sorted(thelist, key=lambda x: x['sku'])
    return render_template("index.html", products=sorted_list)

app.run(debug=True,host="0.0.0.0")


