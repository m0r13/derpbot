from derpbot import plugin, util

class CommandPlugin(plugin.Plugin):
    @plugin.config(
        ("botname", str),
        ("commandprefixes", util.XMLList("prefix"), ["!", "{name}: ", "{name}! ", "{name}, "])
    )
    def __init__(self, bot, config):
        super(CommandPlugin, self).__init__(bot, config)
        
        self._prefixes = []
        for prefix in config["commandprefixes"]:
            self._prefixes.append(prefix.format(name=config["botname"]))
        
    def enable(self):
        pass
    
    def disable(self):
        pass
    
    def handle_message(self, channel, username, message):
        if channel.private:
            self.bot.handle_command(channel, username, message, message.split(" "))
            return
        
        for prefix in self._prefixes:
            if message.startswith(prefix):
                message = message[len(prefix):]
                self.bot.handle_command(channel, username, message, message.split(" "))
                break