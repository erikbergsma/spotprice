#!/usr/bin/env python

import sys
import logging as log

import boto.ec2
import boto.ec2.elb

class Ec2:
    """ a class to create a ec2 (elb) connection, and some shortcuts """
     
    def __init__(self, ec2_region=None, ec2_key=None, ec2_secret=None, connection=None):
        if not connection:
            if not ec2_region or not ec2_key or not ec2_secret:
                log.fatal("you must supply a region AND a key AND a secret")
                sys.exit(2)
            
            self.EC2_REGION = ec2_region
            self.EC2_KEY = ec2_key
            self.EC2_SECRET = ec2_secret

            self.connection = self.create_ec2_connection()
        
        else:
            self.connection = connection
        
    def create_ec2_connection(self):
        return boto.ec2.connect_to_region(self.EC2_REGION,
                                            aws_access_key_id=self.EC2_KEY,
                                            aws_secret_access_key=self.EC2_SECRET)

    def create_elb_connection(self, region_object=None):
        if not region_object:
            region_object = self.get_region_object()
        
        self.elb_connection = boto.ec2.elb.ELBConnection(aws_access_key_id=self.EC2_KEY, 
                                                    aws_secret_access_key=self.EC2_SECRET, 
                                                    region=region_object)
        return self.elb_connection
    
    def get_region_object(self, region_name=None):
        if not region_name:
            region_name = self.EC2_REGION
        
        for region in boto.ec2.elb.regions():
            if region.name == region_name:
                return region
