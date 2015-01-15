#!/usr/bin/env python

import logging as log
import copy
import time
import requests

import security_groups
import configfiles
import ec2 as ec2

from zookeeper import Zookeeper
from boto.exception import EC2ResponseError

class SpotInstance():
    """ the 'model' for a spot instance """
    
    #this is usually the first part of a full node path; e.g. /instances/i-bloebla/role or /backups/ratingredis/success
    INSTANCEPREFIX="/instances/"

    #the end part of the full node path
    ROLEPREFIX="/role"
    ARCHPREFIX="/arch"
    PRICEPREFIX="/price"
    NAMEPREFIX="/name"
    INSTANCETYPE="/instancetype"
    AMIPREFIX="/ami"
    IDPREFIX="/id"
    KEYNAMEPREFIX="/keyname"
    SECURITYGROUPSPREFIX="/securitygroups"
    SPOTINSTANCEPREFIX="/spotinstance"
    ELBPREFIX="/elb"
    ZONEPREFIX="/zone"
    
    def __init__(self, price, role, name, instancetype, ami, keyname, 
                 securitygroups, zone, instance_id=None, elb_name=None,
                 extended_fetch=True, zookeeperObj=None, ec2Obj=None):
        
        self.price = price
        self.role = role
        self.name = name
        self.instancetype = instancetype
        self.ami = ami
        self.keyname = keyname
        self.securitygroups = securitygroups
        self.elb_name = elb_name
        self.zone = zone
        
        #this could be gotten from the spawn/wait for fullfillment function
        self.id = instance_id
        self.zk_path = self.INSTANCEPREFIX + self.id if self.id else False
        
        #connections are sparse, preferable re-use
        if zookeeperObj:
            self.zookeeper = zookeeperObj 
        else:
            zookeeper_url = configfiles.get_value("spotprice.cfg", "zookeeper_url", "spotprice")
            self.zookeeper = Zookeeper(zookeeper_url)
            
        if ec2Obj:
            self.ec2 = ec2Obj
        else:
            ec2_region = configfiles.get_value("spotprice.cfg", "spotprice", "EC2_REGION")
            ec2_key = configfiles.get_value("spotprice.cfg", "spotprice", "EC2_KEY")
            ec2_secret = configfiles.get_value("spotprice.cfg", "spotprice", "EC2_SECRET")
            self.ec2 = ec2.Ec2(ec2_region=ec2_region, ec2_key=ec2_key, ec2_secret=ec2_secret)
                    
    def store_details(self):
        pricepath = self.zk_path + self.PRICEPREFIX
        self.zookeeper.set_node(pricepath, self.price)
        
        rolepath = self.zk_path + self.ROLEPREFIX
        self.zookeeper.set_node(rolepath, self.role)
        
        idpath = self.zk_path + self.IDPREFIX
        self.zookeeper.set_node(idpath, self.id)
        
        namepath = self.zk_path + self.NAMEPREFIX
        self.zookeeper.set_node(namepath, self.name)
        
        instancetypepath = self.zk_path + self.INSTANCETYPE
        self.zookeeper.set_node(instancetypepath, self.instancetype)
        
        amipath = self.zk_path + self.AMIPREFIX
        self.zookeeper.set_node(amipath, self.ami)
        
        keynamepath = self.zk_path + self.KEYNAMEPREFIX
        self.zookeeper.set_node(keynamepath, self.keyname)
        
        securitygroupspath = self.zk_path + self.SECURITYGROUPSPREFIX
        self.zookeeper.set_node(securitygroupspath, ",".join(self.securitygroups))
        
        zonepath = self.zk_path + self.ZONEPREFIX
        self.zookeeper.set_node(zonepath, self.zone)
        
        is_spot_instance_path = self.zk_path + self.SPOTINSTANCEPREFIX
        self.zookeeper.set_node(is_spot_instance_path, True)
        
        if self.elb_name:
            elb_path = self.zk_path + self.ELBPREFIX
            self.zookeeper.set_node(elb_path, self.elb_name)
    
    #this function is expection more than one request_ids, was to lazy to rewrite to single
    def __wait_for_fulfillment(self, request_ids, pending_request_ids, instance_ids=[]):
        """Loop through all pending request ids waiting for them to be fulfilled.
        If a request is fulfilled, remove it from pending_request_ids.
        If there are still pending requests, sleep and check again in 10 seconds.
        Only return when all spot requests have been fulfilled.
        
        thanks to: Lucas Hrabovsky for this
        http://www.imlucas.com/post/55003108849/waiting-for-spot-instances-to-be-fulfilled-with
        """
        try:
            requests = self.ec2.connection.get_all_spot_instance_requests(request_ids=pending_request_ids)
            
            for request in requests:
                if request.status.code == 'fulfilled' and request.instance_id:
                    pending_request_ids.pop(pending_request_ids.index(request.id))
                    instance_ids.append(request.instance_id)
                    log.info("spot request `{}` fulfilled!".format(request.id))
                else:
                    log.debug("waiting on `{}`".format(request.id))
        
        except EC2ResponseError:
            pass
    
        if len(pending_request_ids) == 0:
            log.debug("all spots fulfilled!")
            return instance_ids
        
        else:
            time.sleep(10)
            return self.__wait_for_fulfillment(request_ids, pending_request_ids, instance_ids)
        
    def set_ec2_tags(self, environment="test"):
        self.ec2.connection.create_tags([self.id], {"Name": self.name, "Environment": environment})
        
    def add_to_loadbalancer(self):
        elb = self.ec2.create_elb_connection()
        loadbalancers = elb.get_all_load_balancers(load_balancer_names=[self.elb_name])
        
        if loadbalancers:
            loadbalancers[0].register_instances([self.id])
        else:
            log.warn("could not find ELB with name: %s" % self.elb_name)
            
    def spawn(self, respawn=False, count=1, typearg="one-time"):
        securitygroup_ids=[]
        for security_group in self.securitygroups:
            securitygroup_ids.append(security_groups.get_id_for_groupname(security_group, ec2=self.ec2))
        
        #this function returns an list
        spawned_spotrequests = self.ec2.connection.request_spot_instances(price=self.price, image_id=self.ami, 
                                                                          key_name=self.keyname, instance_type=self.instancetype,
                                                                          security_group_ids=securitygroup_ids, 
                                                                          placement=self.zone, count=count, type=typearg)

        request_ids=[]
        for spotrequest in spawned_spotrequests:
            request_ids.append(spotrequest.id)

        # Wait for our spots to fulfill, and set our id (is only given AFTER the spot instance is succefully spawned
        self.id = self.__wait_for_fulfillment(request_ids, copy.deepcopy(request_ids))[0]
        self.zk_path = self.INSTANCEPREFIX + self.id

        #set the right tags in the ec2 dashboard
        self.set_ec2_tags()

        #add it to an ELB (optionally)
        if self.elb_name:
            self.add_to_loadbalancer()

        if not respawn:
            #store in zookeeper
            self.store_details()
    
    def is_spot_instance(self):
        return True
