from xml.etree import ElementTree as ET
import json
import urllib2

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

def short_url(url):
    if not url:
        return None
    
    apiurl = "https://www.googleapis.com/urlshortener/v1/url"
    data = json.dumps({"longUrl" : url})
    headers = {"Content-Type" : "application/json"}
    r = urllib2.Request(apiurl, data, headers)
    
    try:
        retdata = urllib2.urlopen(r).read()
        retdata = json.loads(retdata)
        return retdata.get("id", url)
    except urllib2.URLError:
        return url
    except ValueError:
        return url