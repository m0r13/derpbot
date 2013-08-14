from derpbot import plugin
import urllib2
import json

def get_user_info(username):
    data = urllib2.urlopen("http://reddit.com/user/%s/about.json" % username).read()
    data = json.loads(data)
    return data

class RedditPlugin(plugin.Plugin):
    def __init__(self, bot, config):
        super(RedditPlugin, self).__init__(bot, config)
        
    def enable(self):
        pass
    
    def disable(self):
        pass
    
    @plugin.command("redditor (.*)",
                    name="redditor",
                    usage="redditor [username]",
                    desc="Shows informations about a redditor.")
    def redditor(self, channel, nick, match, message, args):
        try:
            info = get_user_info(args[1])
        except urllib2.HTTPError:
            channel.send("[REDDITOR] Redditor does not exist!")
            return
        except urllib2.URLError:
            channel.send("[REDDITOR] Unable to connect to reddit!")
            self.log_exception("Unable to connect to reddit to check redditor '%s'" % args[1])
            return
        
        info = info["data"]
        
        message = "[REDDITOR] Name: %s | Link Karma: %s | Comment Karma: %s" % (info["name"], info["link_karma"], info["comment_karma"])
        if info["is_mod"]:
            message += " | Mod"
        if info["is_gold"]:
            message += " | Reddit Gold"
        message += " | Link: http://reddit.com/u/%s" % info["name"]
        channel.send(message)
