#!/usr/bin/env python
import logging
import argparse
import sys

from libs import configfiles
from libs.zookeeper import Zookeeper
from libs.ec2 import Ec2
from libs import ec2_prices
from libs.spot_instances import SpotInstances

def setup_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--loglevel", "-l", default="INFO")

    return parser.parse_args()

def setup_logging(logname, loglevel="INFO"):
    logger = logging.getLogger(logname)
    logger.setLevel(loglevel)

    handler = logging.StreamHandler()
    handler.setLevel(loglevel)
    handler.setFormatter(logging.Formatter('%(levelname)s %(message)s'))
    
    logger.addHandler(handler)

    return logger

def main():
    log.debug("getting definded spot instances:")
    all_defined_spot_instances = spot_instances.get_all_defined()
    
    log.debug("getting alive spot instances:")
    all_running_spot_instances = spot_instances.get_all_running()    
    
    #get the ones that are defined, but not running
    for defined_spot_instance in all_defined_spot_instances:
        for running_instance in all_running_spot_instances:
            if defined_spot_instance.id == running_instance.id:
                all_defined_spot_instances.pop(all_defined_spot_instances.index(defined_spot_instance))
    
    #these are the ones that are defined, but not running    
    for spot_instance in all_defined_spot_instances:
        log.info("this instance id is defined, but is not running anymore: %s, respawning" % spot_instance.id)
        current_spot_price = ec2_prices.get_current_spot_price_for_instancetype(spot_instance.instancetype,
                                                                                spot_instance.zone, ec2=ec2)
        log.info("current_spot_price: %s" % current_spot_price)
        price = ec2_prices.get_spotprice_bid(current_spot_price)
        
        log.info("going to bid: %s" % price)
        
        log.info("going to spawn an instance with the following details:")
        print "name: %s role: %s " % (spot_instance.name, spot_instance.role) 
        
        spot_instance.price = price
        spot_instance.spawn(respawn=True)

if __name__ == '__main__':
    args = setup_parser()
    log = setup_logging("check_running_instances.py", loglevel=args.loglevel)
    
    #get the zookeeper host, and create the zookeeper object
    zookeeper_url = configfiles.get_value("spotprice.cfg", "zookeeper", "url")
    zookeeper = Zookeeper(zookeeperhost=zookeeper_url)
    
    #get the ec2 credentials, and create the ec2 object
    ec2_region = configfiles.get_value("spotprice.cfg", "ec2", "EC2_REGION")
    ec2_key = configfiles.get_value("spotprice.cfg", "ec2", "EC2_KEY")
    ec2_secret = configfiles.get_value("spotprice.cfg", "ec2", "EC2_SECRET")
    ec2 = Ec2(ec2_region=ec2_region, ec2_key=ec2_key, ec2_secret=ec2_secret)
    
    spot_instances = SpotInstances(zookeeperObj=zookeeper, ec2Obj=ec2)
    
    sys.exit(main())
