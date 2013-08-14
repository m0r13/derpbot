from derpbot import plugin

class FunPlugin(plugin.Plugin):
    def __init__(self, bot, config):
        super(FunPlugin, self).__init__(bot, config)
        
    def enable(self):
        pass
    
    def disable(self):
        pass
    
    @plugin.command("slap .*",
                    name="slap",
                    usage="slap <username>",
                    desc="Slaps another user.")
    def hello(self, channel, nick, match, message, args):
        if len(args) > 1:
            channel.send("%s slaps %s." % (nick, "".join(args[1:])))

    @plugin.command("kree .*",
                    name="kree",
                    usage="kree <username>",
                    desc="Jaffa Kree!")
    def kree(self, channel, nick, match, message, args):
        if not self.bot.is_admin(nick) or len(args) < 2:
            return
        channel.sendto(args[1], "Jaffa Kree!")
