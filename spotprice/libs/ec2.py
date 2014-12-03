#!/usr/bin/env python

import boto.ec2
import boto.ec2.elb

import configfiles

class Ec2:
    def __init__(self, connection=None):
        self.EC2_REGION = configfiles.get_value_from_configfile("ec2.cfg", "ec2", "EC2_REGION")
        self.EC2_KEY = configfiles.get_value_from_configfile("ec2.cfg", "ec2", "EC2_KEY")
        self.EC2_SECRET = configfiles.get_value_from_configfile("ec2.cfg", "ec2", "EC2_SECRET")
        
        if not connection:
            self.create_ec2_connection()
        else:
            self.connection = connection
        
    def create_ec2_connection(self):
        self.connection = boto.ec2.connect_to_region(self.EC2_REGION,
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
