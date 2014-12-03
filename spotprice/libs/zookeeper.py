#!/usr/bin/env python

import kazoo
import logging

import configfiles

from kazoo.client import KazooClient
from kazoo.handlers.threading import TimeoutError

log = logging.basicConfig()

class Zookeeper(object):
            
    def __init__(self, connection=False, zookeeperhost=None):
        """ possibility to override the zookeeperhost (url:port) 
        otherwise it reads from a configfile """
                
        if not zookeeperhost:
            self.ZOOKEEPERHOST = configfiles.get_value_from_configfile("zookeeper.cfg", "zookeeper", "url")
        
        else:
            self.ZOOKEEPERHOST = zookeeperhost
            
        if connection:
            self.connection = connection
        else:
            self.create_connection(self.ZOOKEEPERHOST)

    def create_connection(self, zookeeperhost):
        try:
            self.connection = KazooClient(hosts=zookeeperhost)
            self.connection.start(timeout=5)
            
        except TimeoutError:
            self.connection = None
    
    def create_node(self, zkpath, value=None):
        log.debug("creating this zkpath: %s and setting it to this value: %s" % (zkpath, value))
        
        try:
            self.connection.ensure_path(zkpath)
            self.connection.create(zkpath, value)
        
        except kazoo.exceptions.NodeExistsError:
            pass
        
    def set_node(self, zkpath, value):
        self.connection.ensure_path(zkpath)
        self.connection.set(zkpath, str(value))
        
    def node_exists(self, zkpath):
        return self.connection.exists(zkpath)
                    
    def fetch_node(self, zknode, return_stat=False):
        rawdata, stat = self.connection.get(zknode)
        
        try:
            data = rawdata.decode("utf-8")
        
        except AttributeError:
            logging.debug("error parsing zk_data as utf-8")
            if return_stat:
                return rawdata, stat
            else:        
                return rawdata
        
        if return_stat:
            return data, stat
        else:
            return data
    
    def stop_connection(self):
        return self.connection.stop()
