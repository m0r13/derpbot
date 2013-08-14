import xml.etree.ElementTree as ET
from derpbot import util

class ConfigException(Exception):
    pass

def convert_plugin_config(config, attributes):
    avail = util.xml_readdict(config)
    config = {}
    
    for attribute in attributes:
        name = attribute[0]
        convert = attribute[1]
        has_default = len(attribute) > 2
        
        if name not in avail and has_default:
            config[name] = attribute[2]
            continue
        elif name not in avail:
            raise ConfigException("Config attribute '%s' not found!" % name)
        
        try:
            value = convert(avail[name])
            config[name] = value
        except ValueError, e:
            raise ConfigException("Unable to convert value '%s' of attribute '%s'!" % (value, name))
        
    return config

class ConfigFile(object):
    def __init__(self, filename):
        self._filename = filename
        self._plugin_configs = {}
        
        self.plugins = []
        self.admins = []
        
        self.reload()
        
    def reload(self):
        tree = ET.parse(self._filename).getroot()
        bot_config = tree.find("bot")
        
        self.plugins = util.xml_readlist(bot_config.find("plugins"), "plugin")
        self.admins = util.xml_readlist(bot_config.find("admins"), "admin")
        
        self._plugin_configs = {}
        for config in tree.findall("config"):
            self._plugin_configs[config.attrib["plugin"]] = config
        
    def get_plugin_config(self, plugin):
        return self._plugin_configs.get(plugin, None)