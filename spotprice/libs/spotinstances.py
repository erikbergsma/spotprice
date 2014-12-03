#!/usr/bin/env python

import logging
import ec2
import spotinstance

from zookeeper import Zookeeper

logging.basicConfig()

class Spotinstances():
    
    def __init__(self):
        #super(Instances, self).__init__()
        self.zookeeper = Zookeeper()
        self.ec2 = ec2.Ec2()

    #this function goes trough zookeeper anyway, so no need for "extended fetch"
    def get_all_running(self):
        return_array = []
        
        #get all instances from ec2, this excludes stopped instances
        spot_instances = self.ec2.connection.get_all_spot_instance_requests()                
        for instance in spot_instances:
            #check if it is an spot instance, use the instance internal method
            if instance.status.code == "fulfilled":

                #return it eventually
                return_array.append(self.create_from_instance_id(instance.instance_id)) 
                    
        return return_array
    
    #this function goes trough zookeeper anyway, so no need for "extended fetch"
    def get_all_defined(self):
        return_array = []
        
        all_instance_ids = self.zookeeper.connection.get_children("/instances")
        for instance_id in all_instance_ids:
            for attribute in self.zookeeper.connection.get_children("/instances/%s" % instance_id):
                if attribute == "spotinstance":
                    return_array.append(self.create_from_instance_id(instance_id)) 
                    
        return return_array
    
    def create_from_instance_id(self, instance_id):
        spot_details = self.get_details_for_id(instance_id)
        
        return spotinstance.Spotinstance(spot_details.get("price"),
                                            spot_details.get("role"),
                                            spot_details.get("name"),
                                            spot_details.get("instancetype"),
                                            spot_details.get("ami"),
                                            spot_details.get("keyname"),
                                            spot_details.get("securitygroups"),
                                            spot_details.get("zone"),
                                            elb_name=spot_details.get("elb"),
                                            instance_id=instance_id)
    
    #this functions is typically called when the ec2 instance is killed, therefore it hacks around the id part
    def get_details_for_id(self, instance_id):
        return_dict = {}
        attributes_to_fetch = ["price", "role", "name", "instancetype", "ami", "keyname", "securitygroups", "elb", "zone"]
        
        for attribute in self.zookeeper.connection.get_children("/instances/%s" % instance_id):
            if attribute in attributes_to_fetch:
                value = self.zookeeper.fetch_node("/instances/%s/%s" % (instance_id, attribute))
                return_dict[attribute] = value.split(",") if attribute == "securitygroups" else value
                
        return return_dict
