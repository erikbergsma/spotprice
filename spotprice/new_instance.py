#!/usr/bin/env python
import logging
import argparse
import sys

import libs.ec2
import libs.ec2prices

from libs.spotinstance import Spotinstance

from argparse import RawTextHelpFormatter
from boto.exception import BotoServerError
from boto.exception import EC2ResponseError

SPOT_PRICES_URL="http://spot-price.s3.amazonaws.com/spot.js"
INSTANCEPREFIX="/spotinstances/"
SUPPORTED_INSTANCES=[
"t1.micro", "m1.small", "m1.medium", "m1.large", "m1.xlarge", "m3.medium", "m3.large", "m3.xlarge", "m3.2xlarge", "c1.medium", "c1.xlarge", "m2.xlarge", 
"m2.2xlarge", "m2.4xlarge", "cr1.8xlarge", "hi1.4xlarge", "hs1.8xlarge", "cc1.4xlarge", "cg1.4xlarge", "cc2.8xlarge", "g2.2xlarge", "c3.large", "c3.xlarge",
"c3.2xlarge", "c3.4xlarge", "c3.8xlarge", "i2.xlarge", "i2.2xlarge", "i2.4xlarge", "i2.8xlarge", "t2.micro", "t2.small", "t2.medium"]
SUPPORTED_AMIS=["ami-70dd0f07", "ami-7e439809", "ami-948f55e3", "ami-d28852a5"]

def setup_parser():
    parser = argparse.ArgumentParser(description='usage: new_instance.py name role instancetype zone [[[[[[securitygroup1 securitygroup2] percentage] ami] keyname] elb] loglevel]', 
                                     formatter_class=RawTextHelpFormatter)
    
    parser.add_argument("--name", 
                        required=True,
                        help="REQUIRED: the name of the new instance")
    parser.add_argument("--role", 
                        required=True,
                        help="REQUIRED: the (puppet) role of the new instance")
    parser.add_argument("--instancetype",
                        required=True,
                        help="REQUIRED: the instance type of the new instance")
    parser.add_argument("--zone", 
                        required=True,
                        help="REQUIRED: the ec2 zone in where the instance should be launched")
    parser.add_argument("--securitygroups",
                        default=["General"],
                        nargs='*',
                        help="OPTIONAL: the name(s) of the security groups that should be attached to the instance, multiple arguments accepted\n\
Defaults to: 'General'")
    parser.add_argument("--percentage", default=1, 
                        type=int, 
                        help="OPTIONAL: the percentage we bid above the current bidprice\n\
Defaults to: 1")
    parser.add_argument("--ami",
                        default="ami-d28852a5",
                        help="OPTIONAL: the id of the AMI that we should use as the base of the instance\n\
Defaults to: 'ami-d28852a5'")
    parser.add_argument("--keyname",
                        default="Production",
                        help="OPTIONAL: the name of the SSH key that will be used\n\
Defaults to: 'Production'")
    parser.add_argument("--elb",
                        help="OPTIONAL: the name of the ELB this machine should be attached to (if any)")
    parser.add_argument("--loglevel",
                        "-l",
                        default="INFO",
                        help="OPTIONAL: the verbosity of the logging\n\
Defaults to: 'Info'")

    return parser.parse_args()

def setup_logging(logname, loglevel="INFO"):
    logger = logging.getLogger(logname)
    logger.setLevel(loglevel)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter('%(levelname)s %(message)s'))
    logger.addHandler(handler)

    return logger

def check_arguments():
    #check if the instance type is supported
    
    #supported_instance_types=ec2.connection.get_all_instance_types()
    supported_instance_types = SUPPORTED_INSTANCES
    if args.instancetype not in supported_instance_types:
        log.fatal("i dont support instance type: %s, i support: %s" % (args.instancetype, supported_instance_types))
        sys.exit(2)
    
    #check if we support the keyname
    supported_keynames = ec2.connection.get_all_key_pairs()
    #found_keys = [keyname for keyname in supported_keynames if args.keyname == keyname.name]
    if len(filter(lambda x: x.name == args.keyname, supported_keynames)) == 0:
        log.fatal("i dont support keyname type: %s, i support: %s" % (args.keyname, supported_keynames))
        sys.exit(2)
    
    #check if the ami id is supported
    if args.ami not in SUPPORTED_AMIS:
        log.fatal("i dont support ami_id: %s, i support: %s" % (args.ami, SUPPORTED_AMIS))
        sys.exit(2)
    
    #check if the availability zone is supported
    try:
        ec2.connection.get_all_zones(zones=args.zone)
    except EC2ResponseError:
        log.fatal("i dont support availability zone: %s, i support: %s" % (args.zone, ec2.connection.get_all_zones()))
        sys.exit(2)
    
    #check if the elb name is supported
    if args.elb:
        elb = ec2.create_elb_connection()
        try:
            elb.get_all_load_balancers([args.elb])
        except BotoServerError:
            log.fatal("i cannot find loadbalancer with name: %s, i support: %s" % (args.elb, elb.get_all_load_balancers()))
            sys.exit(2)
            
def main():
    check_arguments()
    
    current_spot_price = libs.ec2prices.get_current_spot_price_for_instancetype(args.instancetype, args.zone)
    print "current spot price: %s" % current_spot_price
    
    current_on_demand_price = libs.ec2prices.get_ondemand_price_for_instancetype(args.instancetype)
    print "current on demand price: %s" % current_on_demand_price
    
    bidprice = libs.ec2prices.get_spotprice_bid(current_spot_price, args.percentage)
    print "wanting to bid: %s" % bidprice
        
    #price sanity check
    if float(bidprice) > float(current_on_demand_price):
        log.error("your bid price (%s) is higher than the on demand price (%s), exiting" % (bidprice, current_on_demand_price))
        sys.exit(1)

    #turn into spot spotinstances
    spotinstance = Spotinstance(bidprice, args.role, args.name, args.instancetype, args.ami, 
                                     args.keyname, args.securitygroups, args.zone, 
                                     elb_name=args.elb, Ec2Connection=ec2.connection)
    
    spotinstance.spawn()
    
    print "succesfully spawned: %s with id: %s" % (spotinstance.name, spotinstance.id)

if __name__ == '__main__':
    args = setup_parser()
    log = setup_logging("new_spot_instance.py", loglevel=args.loglevel)
    logging.getLogger('boto').setLevel(logging.CRITICAL)
    
    ec2 = libs.ec2.Ec2()
    
    sys.exit(main())
