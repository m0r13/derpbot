from derpbot import plugin, util
from xml.etree import ElementTree
import urllib, urllib2

# from hesperus
# see github.com/aheadley/hesperus

alpha_api_url = "http://api.wolframalpha.com/v2/query"
alpha_web_url = "http://www.wolframalpha.com/input/"

def alpha(s, alpha_app_id):
    args = {}
    args["appid"] = alpha_app_id
    args["input"] = s
    args["format"] = "plaintext"
    args["podindex"] = "1,2"
    
    url = alpha_api_url + "?" + urllib.urlencode(args)
    web_url = alpha_web_url + "?" + urllib.urlencode({"i" : s})
    data = ElementTree.parse(urllib2.urlopen(url)).getroot()
    
    if data.get("error", "true").lower() == "true" or data.get("success", "false").lower() == "false":
        return {"success" : False, "web" : web_url, "input" : None, "output" : None}
    
    simple_data = []
    input_data = []
    
    for el in data.findall("pod"):
        name = el.get("id")
        for subel in el.findall("subpod"):
            textel = subel.find("plaintext")
            if textel is None or textel.text is None:
                continue
            if name == "Input":
                input_data.append(textel.text)
            else:
                simple_data.append(textel.text)
        if name != "Input":
            break
    
    ret = {}
    ret["success"] = True
    ret["web"] = web_url
    ret["input"] = "\n".join(input_data)
    ret["output"] = "\n".join(simple_data)
    
    if ret["output"] == "":
        ret["output"] = ret["input"]
    
    return ret

class WolframAlphaPlugin(plugin.Plugin):
    
    @plugin.config(("app-id", str, None))
    def __init__(self, bot, config):
        super(WolframAlphaPlugin, self).__init__(bot, config)
        
        self.app_id = self.config["app-id"]
        
    def enable(self):
        pass
    
    def disable(self):
        pass
    
    @plugin.command("(=|wolframalpha|wa|alpha) (.*)", 
                   name="wolframalpha", 
                   usage="(=|wolframalpha|wa|alpha) <query>", 
                   desc="Queries Wolfram Alpha.")
    def wolframalpha(self, channel, nick, match, message, args):
        if self.app_id is None:
            channel.sendto(nick, "Sorry, I do not have an API Key :(")
            return
        
        ret = alpha(match.group(2), self.app_id)
        if not ret["success"]:
            channel.sendto(nick, "Wolfram Alpha is confused: %s" % util.short_url(ret["web"]))
        else:
            s = ret["output"].splitlines()
            web = util.short_url(ret["web"])
            if len(s) == 1:
                channel.sendto(nick, "%s (%s)" % (s[0], web))
            else:
                for part in s:
                    channel.sendto(nick, part)
                channel.sendto(nick, ("(%s)" % web))
