#!/usr/bin/env python

import os
import sys

from ConfigParser import SafeConfigParser
from ConfigParser import NoSectionError

def get_value_from_configfile(configfile_name, section_name, value, extrafolders=None):
    """
    search in these folders:
    - /root
    - current working dir
    - /tmp
    """
    folders = ["/root", os.getcwd() ]
    
    if extrafolders:
        folders.extend(extrafolders)
    
    parser = SafeConfigParser()
    
    for folder in folders:
        try:
            config_file_path = folder + "/" + configfile_name
            parser.read(config_file_path)
            return parser.get(section_name, value)
        
        except NoSectionError:
            continue
        
    print("cannot find a value for: \"%s\" in a configfile called: \"%s\" in folders: %s" % (value, configfile_name, folders))
    sys.exit(2)
