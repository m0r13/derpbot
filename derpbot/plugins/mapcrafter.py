import urllib2
from derpbot import plugin

class MapcrafterPlugin(plugin.Plugin):
    def __init__(self, *args, **kwargs):
        super(MapcrafterPlugin, self).__init__(*args, **kwargs)
        
    def enable(self):
        pass
    
    def disable(self):
        pass
    
    @plugin.command("mapcrafter downloads")
    def mapcrafter_downloads(self, channel, nick, match, message, args):
        data = urllib2.urlopen("http://mapcrafter.org/deb_downloads.txt").read()
        lines = data.strip().split("\n")
        
        for i in xrange(2):
            downloads, name = lines[i].split(" ")
            channel.send("%s: %s downloads" % (name, downloads))
