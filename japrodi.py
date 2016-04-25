#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2013 Felipe Gallego. All rights reserved.
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

"""This module read Java properties files and show the values of
all the properties for each file.
This utility allows an easy comparison of parameters values and the
identification of parameters used in a file and not used in others.
"""

import argparse
import csv

OUT_FILE = 'out.csv'
COMMENT_CHAR = '#'
EQUAL_CHAR = '='

PROP_NAME = 'PROP NAME'
FILE_NAME = 'FILE NAME'
NONE_TEXT = 'THIS_PARAMETER_DOES_NOT_EXIST'

def process_program_arguments():
    """Process the program arguments to retrieve the names of
    the properties files to use.
    """
    
    print "Processing program arguments... "
    
    parser = argparse.ArgumentParser(description='Compare Java property files.')
    
    parser.add_argument('-f', '--files', nargs='+', required=True, \
                        dest='prop_files', help='property files to compare')
    
    parser.add_argument('-o', dest='out_file', default=OUT_FILE, \
                        help='output file')
    
    args = parser.parse_args()
    
    return args

def process_prop_line(line):
    """Process a line of a properties file to retrieve the parameter
    name and value if it exists.
    """    
    
    prop = None
    
    # Look for a comment char.
    comm_pos = line.find(COMMENT_CHAR)
    
    # Get the comment position to discard all the characters behind it.
    if comm_pos != -1:
        line = line[0:comm_pos]

    # Look for an equal character.
    eq_pos = line.find(EQUAL_CHAR)
    
    # If the equal character exists, the string leading string trimmed is
    # taken as the parameter name, and the trailing string trimmed is taken
    # as the parameter value.
    if eq_pos != -1:
        name = line[0:eq_pos].strip()
        value =  line[eq_pos + 1:].strip()
        
        prop = [ name, value ]
        
    return prop

def read_properties_file(prop_file):
    """Process a line of a properties file to retrieve the parameter
    name and value if it exists.
    """ 
        
    # Properties are saved as a dictionary.
    properties = {}
            
    f = open(prop_file)
    
    # Process all the lines of the properties file.
    for line in iter(f):
        prop = process_prop_line(line)
        
        # If a property has been found in current line.
        if not prop is None:
            # Save it in the dictionary using the name as key.
            properties[prop[0]] = prop[1] 
        
    f.close()    
    
    return properties

def write_comparison(header, properties_names, properties_values, out_file):
    """Write to a CSV file all the values found for each parameter
    in all the properties files.
    """     
    
    with open(out_file, 'wb') as f:
        writer = csv.writer(f)
        
        # Write header.
        writer.writerow(header)
        
        # Write all the properties found with the values that takes
        # in each file. 
        for i in range(len(properties_names)): 
            # Add the name of the property.                   
            current_row = [properties_names[i]]
            
            # For each property file, add to the row the parameter value found.
            for pv in properties_values:
                current_row.append(pv[i])
                
            writer.writerow(current_row)
            
    print "Results saved in file: %s" % out_file

def compare_properties(properties_sets, prop_files, out_file):    
    """For all the properties found in any properties file,
    get the value that takes in each file.
    """   
        
    properties_names = []
    properties_values = []
    
    # Create a list that contains only once all the properties
    # found in any file.
    for ps in properties_sets:
        prop_keys = ps.keys()
        for pk in prop_keys:
            try:
                properties_names.index(pk)
            except ValueError:
                properties_names.append(pk)
                
        # For each property set add an empty list.
        properties_values.append([])
    
    # Sort the list of properties's name.
    properties_names.sort()
    
    # Creates a header row for the exit result with a column for the properties
    # name and an additional column for each properties file where the value that
    # takes each parameter in each file is shown.   
    header = [ PROP_NAME ]    
    header.extend(prop_files)
    
    sets_num = len(properties_sets)
    
    # For all the properties.
    for n in range(len(properties_names)):
        name = properties_names[n]
        
        # In each properties file.
        for i in range(sets_num):
            # Get the list for the values of current properties file.
            current_properties_values = properties_values[i]            
            
            try:
                # Try to get the value for current property.
                value = properties_sets[i][name]
    
                current_properties_values.append(value)                
            except KeyError:
                # If there isn't value for this property, use NONE.
                current_properties_values.append(NONE_TEXT)
		
    # Write the values found for all the properties in each file.
    write_comparison(header, properties_names, properties_values, out_file)        

def process_properties_files(prop_files, out_file):
    """Process all the properties files. """
           
    properties_sets = []
    
    print "Processing properties sets files: "
    
    # For each properties file.
    for pf in prop_files:
        print "- %s" % pf
        # Read its properties.
        prop = read_properties_file(pf)
        
        properties_sets.append(prop)
        
    not_empty = True
    
    # Determines if all the files has properties.
    for p in properties_sets:
        if p is None:
            not_empty = False
            break;
        
    if not_empty:
        compare_properties(properties_sets, prop_files, out_file)
    else:
        print "Some file hasn't properties."
    
def main():

    args = process_program_arguments()
    
    if len(args.prop_files) == 2:
        process_properties_files(args.prop_files, args.out_file)
    else:
        print "The number of files should be 2."
    
if __name__ == "__main__":
    main()