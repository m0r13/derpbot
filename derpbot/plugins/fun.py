from derpbot import plugin
import random

class FunPlugin(plugin.Plugin):
    def __init__(self, *args, **kwargs):
        super(FunPlugin, self).__init__(*args, **kwargs)
        
    def enable(self):
        pass
    
    def disable(self):
        pass
    
    def handle_message(self, channel, username, message):
        if username == "Thor" and message.lower().startswith("derp"):
            if random.randint(0, 10) < 2:
                channel.send("Thor is a derp, indeed")
            else:
                channel.send("indeed")
    
    @plugin.command("slap (.*)",
                    name="slap",
                    usage="slap <username>",
                    desc="Slaps another user.")
    def hello(self, channel, nick, match, message, args):
        channel.send("%s slaps %s." % (nick, match.group(1)))

    @plugin.command("kree (.*)",
                    name="kree",
                    usage="kree <username>",
                    desc="Jaffa Kree!")
    def kree(self, channel, nick, match, message, args):
        if not self.bot.is_admin(nick):
            channel.sendto(nick, "Sorry, I can't find any Naquadah in your blood.")
        else:
            channel.sendto(match.group(1), "Jaffa Kree!")
