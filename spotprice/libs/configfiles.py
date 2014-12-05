#!/usr/bin/env python

import logging as log
import os
import sys

from ConfigParser import SafeConfigParser
from ConfigParser import NoSectionError

"""
search in these folders:
- /root
- current working dir
- /tmp
"""
FOLDERS = ["/root", os.getcwd(), "/tmp"]

def get_value(configfile_name, section_name, value):    
    parser = SafeConfigParser()
    
    for folder in FOLDERS:
        try:
            config_file_path = folder + "/" + configfile_name
            parser.read(config_file_path)
            value = parser.get(section_name, value)
            
            log.debug(value)
            
            if "," in value:
                return value.split(",")

            return value
        
        except NoSectionError:
            continue
        
    log.error("cannot find a value for: \"%s\" in a configfile called: \"%s\" in folders: %s" % (value, configfile_name, FOLDERS))

    sys.exit(2)
    
def get_section(configfile_name, section_name):
    parser = SafeConfigParser()
    dictionary = {}
    
    for folder in FOLDERS:
        config_file_path = folder + "/" + configfile_name
        
        log.debug(config_file_path)
        
        parser.read(config_file_path)
        
        try:
            for option in parser.options(section_name):
                dictionary[option] = parser.get(section_name, option)
        except NoSectionError:
            continue
    
    log.debug(dictionary)        
    return dictionary
        
def get_all(configfile_name):
    parser = SafeConfigParser()
    dictionary = {}
    
    for folder in FOLDERS:
        config_file_path = folder + "/" + configfile_name
        parser.read(config_file_path)
        
        for section in parser.sections():
            dictionary[section] = {}
            for option in parser.options(section):
                dictionary[section][option] = parser.get(section, option)
    
    log.debug(dictionary)
    return dictionary
