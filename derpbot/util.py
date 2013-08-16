from xml.etree import ElementTree as ET
from datetime import datetime
import calendar
from derpbot.short_url import short_url

def xml_readlist(node, tagname):
    if not isinstance(node, ET.Element):
        raise ValueError("The given node must be instance of Element!")
    data = []
    for child in node:
        if child.tag == tagname:
            data.append(child.text)
    return data

def xml_readdict(node):
    data = {}
    for child in node:
        if len(child) == 0:
            data[child.tag] = child.text
        else:
            data[child.tag] = child
    return data

class XMLList(object):
    def __init__(self, tagname):
        self._tagname = tagname
        
    def __call__(self, node):
        return xml_readlist(node, self._tagname)
    
def utc_to_timestamp(utcstr):
    return calendar.timegm(datetime.strptime(utcstr, "%Y-%m-%dT%H:%M:%SZ").utctimetuple())