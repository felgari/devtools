#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2016 Felipe Gallego. All rights reserved.
#
# This is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""List the global variables of a python source file not used in the python
files of a directory.
""" 

import sys
import os
import keyword 
import re
import glob

from ctes import *

def process_comments(block_comment, line):
    """Process the line to ignore the text related to comments.
    """
    
    pos_blck_com = line.find(BLOCK_COMMENT)
    pos_line_com = line.find(LINE_COMMENT)
    
    if block_comment and pos_blck_com < 0:
        line = ''
    else:
        if pos_blck_com >= 0 and pos_line_com >= 0:
            
            if pos_blck_com > pos_line_com:
                pos_line_com = -1
            else:
                pos_blck_com = -1
                
        if pos_blck_com >= 0:
            
            if not block_comment:
                line = line[:pos_blck_com]
            else:
                line = line[pos_blck_com + 1:]
                
            block_comment = not block_comment
            
        if pos_line_com >= 0:
            line = line[:pos_line_com]
        
    return line, block_comment

def read_ctes_from_file(ctes_file_name):
    """Create a list with the constants found in the file received.
    """
    
    block_comment = False
    ctes_set = set()
    
    try:
        with open(ctes_file_name, 'r') as f:
            for line in f:
                
                line, block_comment = process_comments(block_comment, line)
                
                eq_pos = line.find(EQUAL_CHR)
                
                if eq_pos > 0:
                    line_part = line[:eq_pos].rstrip()                  
                    
                    if re.match("[_a-zA-Z][_a-zA-Z0-9]*$", line_part) and \
                        not keyword.iskeyword(line_part):
                        ctes_set.add(line_part)
                
    except IOError:
        print "ERROR: Reading file '%s'" % ctes_file_name 
        
    return ctes_set

def check_file_for_ctes_use(file_name, ctes_list, used_ctes):
    """Check the use of the constant in the file received.
    """
    
    block_comment = False    
    
    try:
        with open(file_name, 'r') as f:
            for line in f:
                
                line, block_comment = process_comments(block_comment, line)
                
                line_elts = filter(None, re.split("[ (),:\t\n]+", line))
                
                for c in ctes_list:
                    if c in line_elts:
                        used_ctes.add(c)
                                
    except IOError:
        print "ERROR: Reading file '%s'" % file_name         

def check_ctes_use(ctes_set, ctes_file_name):
    """Check if the list of constants received are used 
    in the python files found from current directory.
    """
    
    used_ctes = set()
    
    # Get the list of files.
    files = glob.glob(os.path.join(SRC_DIR, WILDCARD_PY_FILE))
    
    for fd in files:
        _, f = os.path.split(fd)
        if f != ctes_file_name:
            check_file_for_ctes_use(f, ctes_set, used_ctes)
        
    return list(ctes_set - used_ctes)
        
def main(ctes_file_name):
    """Read the constants from the file indicated and search if these
    constants are used in the python files found from current directory.
    """
    
    ctes_set = read_ctes_from_file(ctes_file_name)
    
    if len(ctes_set):
        print "%d constants found." % len(ctes_set)
        
        ctes_list_not_used = check_ctes_use(ctes_set, ctes_file_name)
        
        if len(ctes_list_not_used):
            print "There are constants not used: %s" % \
                ', '.join(ctes_list_not_used)
        else:
            print "All the constants found are in use."
    else:
        print "Not constants found in the file: %s" % ctes_file_name

if __name__ == "__main__":
    
    if len(sys.argv) == NUM_ARGS:
        main(sys.argv[1])
    else:
        print "Use: %s ctes_file_name" % sys.argv[0]