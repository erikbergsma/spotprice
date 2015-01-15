#!/usr/bin/env python
import requests
import logging as log
import configfiles

from datetime import datetime, timedelta
from ec2 import Ec2

ON_DEMAND_PRICES_URL = configfiles.get_value("spotprice.cfg", "spotprice", "ondemand_price_url")

def get_ondemand_price_for_instancetype(instancetypeArg):
    response = requests.get(ON_DEMAND_PRICES_URL)
    prices = response.json()
    
    my_region = configfiles.get_value("spotprice.cfg", "spotprice", "region")
    
    for region in prices["config"]["regions"]:
        if region["region"] == my_region:
            for instancegroup in region["instanceTypes"]:
                for instancetype in instancegroup["sizes"]:
                    if instancetype["size"] == instancetypeArg:
                        return instancetype["valueColumns"][0]["prices"]["USD"]

def get_current_spot_price_for_instancetype(instancetype, availability_zone, ec2, relaunch=False):
    now = datetime.today() 
    start_time = now.isoformat()
    end_time = (now - timedelta(seconds = 1)).isoformat()
    
    result = ec2.connection.get_spot_price_history(start_time=start_time, end_time=end_time, instance_type=instancetype, 
                                          product_description="Linux/UNIX", availability_zone=availability_zone)

    return result[0].price

def get_spotprice_bid(current_spot_price, percentage=1):
    price = round(current_spot_price * (1 + (float(percentage) / 100)), 6)
    
    return price
