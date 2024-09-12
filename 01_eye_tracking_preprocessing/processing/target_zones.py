#####################################################################
# Copyright (C) 2024 HIDDEN UNIVERSITY
# HIDDEN WEBSITE
# HIDDEN SUBTEXT
# HIDDEN INSTITUTE
# 
# Authors: AUTHORS CURRENTLY HIDDEN DUE TO ONGOING PEER REVIEW PROCESS
# 
# Licensed under the MIT License (the "License");
# you may only use this file in compliance with the License.
# You may obtain a copy of the License at
# 
#         https://mit-license.org/
# 
# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
####################################################################

import os
import xml.etree.ElementTree as ET


def get_target_zone_names():
    tree = ET.parse("target_zone_names.xml")
    root = tree.getroot()
    target_zone_names = {}

    for child in root:
        target_zone = int(child.attrib['id'])
        target_zone_name = child.attrib['name']
        target_zone_right = float(child.attrib['right'])
        target_zone_names.update({target_zone: {'name': target_zone_name, 'right': target_zone_right}})

    return target_zone_names


# Write the target zone names into a .xml file
def write_target_zone_names():
    tree = ET.parse('../../Data/target_zones/gaze_zones.xml')
    root = tree.getroot()
    target_zone_names = {}

    for child in root:
        a = child.find('lowerLeft')
        for little in child:
            print(little)

    target_zone_names = {-1: {'name': 'no_gaze_available', 'right': 50},
                         0: {'name': 'no_target_zone_detected', 'right': 30},
                         1: {'name': 'driver_side_windscreen', 'right': 1000},
                         2: {'name': 'copilot_side_windscreen', 'right': 200},
                         3: {'name': 'left_rear_mirror', 'right': 30},
                         4: {'name': 'right_rear_mirror', 'right': 5},
                         5: {'name': 'left_window', 'right': 130},
                         6: {'name': 'right_window', 'right': 4},
                         7: {'name': 'central_rear_mirror', 'right': 200},
                         8: {'name': 'driver_instruments', 'right': 250},
                         10: {'name': 'navigation_display', 'right': 100},
                         11: {'name': 'middle_instrument_cluster', 'right': 10}}

    root = ET.Element("root")
    for target_zone_id in target_zone_names:
        target_zone = ET.SubElement(root, "target_zone")
        target_zone.set('id', str(target_zone_id))
        target_zone.set('name', target_zone_names[target_zone_id]['name'])
        target_zone.set('right', str(target_zone_names[target_zone_id]['right']))

    tree = ET.ElementTree(root)
    tree.write("../../Data/target_zones/target_zone_names.xml")
