#!/usr/bin/env python

import os
import sys
import logging as log

from ConfigParser import SafeConfigParser
from ConfigParser import NoSectionError

def get_value_from_configfile(configfile_name, section_name, value, extrafolders=None):
    """
    search in these folders:
    - /root
    - current working dir
    - /tmp
    """
    folders = ["/root", os.getcwd(), "/tmp"]
    
    if extrafolders:
        folders.extend(extrafolders)
    
    parser = SafeConfigParser()
    
    for folder in folders:
        try:
            config_file_path = folder + "/" + configfile_name
            parser.read(config_file_path)
            value = parser.get(section_name, value)
            
            if "," in value:
                return value.split(",")
            
            return value
        
        except NoSectionError:
            continue
        
    log.error("cannot find a value for: \"%s\" in a configfile called: \"%s\" in folders: %s" % (value, configfile_name, folders))
    sys.exit(2)
