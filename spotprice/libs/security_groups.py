#!/usr/bin/env python

import logging
from ec2 import Ec2

log = logging.basicConfig()

def get_id_for_groupname(groupname, ec2=None):
    used_group=False
    
    if not ec2:
        ec2 = Ec2()
    
    #check if security group name is set in ec2
    available_security_groups = ec2.connection.get_all_security_groups()
    
    for group in available_security_groups:
        if group.name == groupname:
            used_group = group
            
    if not used_group:
        log.error("security group with name: %s not found" % groupname)
    
    return used_group
