#!/usr/bin/env python
import logging
import argparse
import sys
import libs.spotinstances
import libs.ec2prices

def setup_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--loglevel", "-l", default="INFO")

    return parser.parse_args()

def setup_logging(logname, loglevel="INFO"):
    logger = logging.getLogger(logname)
    logger.setLevel(loglevel)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter('%(levelname)s %(message)s'))
    logger.addHandler(handler)

    return logger

def main():
    log.debug("alive spotinstances:")
    all_running_spot_instances = spotinstances.get_all_running()    
    for instance in all_running_spot_instances:
        log.debug(instance.id)
    
    log.debug("definded spotinstances:")
    all_defined_spot_instances = spotinstances.get_all_defined()
    for defined_spot_instance in all_defined_spot_instances:
        log.debug(defined_spot_instance.id)
    
    #get the ones that are defined, but not running
    for defined_spot_instance in all_defined_spot_instances:
        for running_instance in all_running_spot_instances:
            if defined_spot_instance.id == running_instance.id:
                all_defined_spot_instances.pop(all_defined_spot_instances.index(defined_spot_instance))
        
    for spotinstance in all_defined_spot_instances:
        print "this instance id is defined, but is not running anymore: %s, respawning" % spotinstance.id
                
        current_spot_price = libs.ec2prices.get_current_spot_price_for_instancetype(spotinstance.instancetype, spotinstance.zone)
        print "current_spot_price: %s" % current_spot_price
        
        price = libs.ec2prices.get_spotprice_bid(current_spot_price)
        print "going to bid: %s" % price
        
        print "going to spawn an instance with the following details:"
        print spotinstance
        
        spotinstance.price = price
        spotinstance.spawn()

if __name__ == '__main__':
    args = setup_parser()
    log = setup_logging("new_spot_instance.py", loglevel=args.loglevel)
    
    spotinstances = libs.spotinstances.Spotinstances()
    
    sys.exit(main())
