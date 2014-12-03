#!/usr/bin/env python

import logging
import ec2
import spot_instance

from zookeeper import Zookeeper

log = logging.basicConfig()

class SpotInstances():
    """ class to interact (get/create/list) spot instances """
    
    ATTRIBUTES = ["price", "role", "name", "instancetype", "ami",
                  "keyname", "securitygroups", "elb", "zone"]
    
    def __init__(self):
        self.zookeeper = Zookeeper()
        self.ec2 = ec2.Ec2()

    def get_all_running(self):
        """queries ec2 for "fullfilled" spot instances, returns them in an list"""
        
        return_list = []
        
        #get all instances from ec2, this excludes stopped instances
        spot_instances = self.ec2.connection.get_all_spot_instance_requests()                
        log.debug("found these spot instance requests: %s" % spot_instances)
        
        for instance in spot_instances:    
            #check if it is an spot instance, use the instance internal method
            if instance.status.code == "fulfilled":

                #return it eventually
                log.debug("this spot instance requests was fullfilled: %s" % instance)
                return_list.append(self.create_from_instance_id(instance.instance_id)) 
                    
        return return_list
    
    def get_all_defined(self):
        """ 
        queries zookeeper for all spot instances that are defined,
        looks for the child zknode called: spotinstance to determine if that instance is a spotinstance or not
        instance id is the unique identifier, because all instances are stored as zknodes under /instances/ in zookeeper
        """
    
        return_list = []    
        all_instance_ids = self.zookeeper.connection.get_children("/instances")
        
        for instance_id in all_instance_ids:
            for attribute in self.zookeeper.connection.get_children("/instances/%s" % instance_id):
                if attribute == "spotinstance":
                    log.debug("found a spot instance with this id in zookeeper: %s" % instance_id)
                    return_list.append(self.create_from_instance_id(instance_id)) 
                    
        return return_list
    
    def create_from_instance_id(self, instance_id):
        """ 
        fetch all the other values for spotinstance with id: X
        then convert all this information into a "spotinstance" object
        """
        
        spot_details = self.get_details_for_id(instance_id)
        
        return spot_instance.SpotInstance(spot_details.get("price"),
                                            spot_details.get("role"),
                                            spot_details.get("name"),
                                            spot_details.get("instancetype"),
                                            spot_details.get("ami"),
                                            spot_details.get("keyname"),
                                            spot_details.get("securitygroups"),
                                            spot_details.get("zone"),
                                            elb_name=spot_details.get("elb"),
                                            instance_id=instance_id)
    
    def get_details_for_id(self, instance_id):
        """
        get all attributes (zk nodes) for an certain spot instance from zookeeper
        """
        return_dict = {}
        
        for attribute in self.zookeeper.connection.get_children("/instances/%s" % instance_id):
            if attribute in self.ATTRIBUTES:
                value = self.zookeeper.fetch_node("/instances/%s/%s" % (instance_id, attribute))
                
                log.debug("spotinstance with id: %s has this value: %s for this attribute: %s" % instance_id, value, attribute)
                
                #security groups are stored as group1,group2,groupn
                return_dict[attribute] = value.split(",") if attribute == "securitygroups" else value
                
        return return_dict

