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

# from hesperus chat bot, see https://github.com/agrif/hesperus
# pretty string trunc function
# <http://kelvinwong.ca/2007/06/22/a-nicer-python-string-truncation-function/>
# from Kelvin Wong, under the license at http://www.python.org/psf/license/
def trunc(s, min_pos=0, max_pos=75, ellipsis=True):
    # Sentinel value -1 returned by String function rfind
    NOT_FOUND = -1
    # Error message for max smaller than min positional error
    ERR_MAXMIN = "Minimum position cannot be greater than maximum position"
    
    # If the minimum position value is greater than max, throw an exception
    if max_pos < min_pos:
        raise ValueError(ERR_MAXMIN)
    # Change the ellipsis characters here if you want a true ellipsis
    if ellipsis:
        suffix = '...'
    else:
        suffix = ''
    # Case 1: Return string if it is shorter (or equal to) than the limit
    length = len(s)
    if length <= max_pos:
        return s + suffix
    else:
        # Case 2: Return it to nearest period if possible
        try:
            end = s.rindex('.',min_pos,max_pos)
        except ValueError:
            # Case 3: Return string to nearest space
            end = s.rfind(' ',min_pos,max_pos)
            if end == NOT_FOUND:
                end = max_pos
        return s[0:end] + suffix