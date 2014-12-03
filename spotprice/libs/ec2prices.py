#!/usr/bin/env python
import requests
import json
from datetime import datetime, timedelta

from ec2 import Ec2

INSTANCE_PRICES_URL="http://aws.amazon.com/ec2/pricing/pricing-on-demand-instances.json"

def get_ondemand_price_for_instancetype(instancetypeArg):
    response = requests.get(INSTANCE_PRICES_URL)
    prices = json.loads(response.text)
    
    for region in prices["config"]["regions"]:
        if region["region"] == "eu-ireland":
            for instancegroup in region["instanceTypes"]:
                for instancetype in instancegroup["sizes"]:
                    if instancetype["size"] == instancetypeArg:
                        return instancetype["valueColumns"][0]["prices"]["USD"]

def get_current_spot_price_for_instancetype(instancetype, availability_zone, relaunch=False):
    ec2 = Ec2()
    
    now = datetime.today() 
    start_time = now.isoformat()
    end_time = (now - timedelta(seconds = 1)).isoformat()
    
    result = ec2.connection.get_spot_price_history(start_time=start_time, end_time=end_time, instance_type=instancetype, 
                                          product_description="Linux/UNIX", availability_zone=availability_zone)

    return result[0].price

def get_spotprice_bid(current_spot_price, percentage=1):
    price = round(current_spot_price * (1 + (float(percentage) / 100)), 6)
    
    return price
