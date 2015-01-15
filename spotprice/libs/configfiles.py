#!/usr/bin/env python

import logging as log
import os
import sys
import os.path

from ConfigParser import SafeConfigParser
from ConfigParser import NoSectionError
from os.path import expanduser

"""
search in these folders, in this order:
- current user' homedir
- current working dir
- /tmp
"""
FOLDERS = [expanduser("~"), os.getcwd(), "/tmp"]

#gets the value for a key in a specific section
def get_value(configfile_name, section_name, key):
    parser = SafeConfigParser()
    
    for folder in FOLDERS:
        config_file_path = folder + "/" + configfile_name
        if os.path.exists(config_file_path):
            try:
                parser.read(config_file_path)
                value = parser.get(section_name, key)
                
                log.debug(value)
                
                if "," in value:
                    return value.split(",")

                return value
            
            except NoSectionError:
                continue
        
    log.error("cannot find a value for: \"%s\" in a configfile called: \"%s\" in folders: %s" % (key, configfile_name, FOLDERS))

    sys.exit(2)
    
#gets an entire section from a configfile
def get_section(configfile_name, section_name):
    parser = SafeConfigParser()
    dictionary = {}
    
    for folder in FOLDERS:
        config_file_path = folder + "/" + configfile_name
        log.debug(config_file_path)
        
        if os.path.exists(config_file_path):
            parser.read(config_file_path)
            
            try:
                for key in parser.options(section_name):
                    value = parser.get(section_name, key)
                    
                    if "," in value:
                        value = value.split(",")
                    
                    dictionary[key] = value
            
            except NoSectionError:
                continue
    
        log.debug(dictionary)        
        return dictionary
