from derpbot import plugin

class HelpPlugin(plugin.Plugin):
    def __init__(self, bot, config):
        super(HelpPlugin, self).__init__(bot, config)
        
    def enable(self):
        pass
    
    def disable(self):
        pass
    
    @plugin.command("help( .+)?",
                    name="help",
                    usage="help [command]",
                    desc="Shows help about available commands.")
    def help(self, channel, nick, match, message, args):
        plugins = self.bot.plugins
        if len(args) == 1:
            commands = map(lambda command: command["name"], plugins.commands)
            commands = filter(lambda name: name, commands)
            commands.sort()
            
            channel.sendpriv(nick, "Commands: %s" % ", ".join(commands))
        else:
            search = args[1]
            for command in plugins.commands:
                if command["name"] != search:
                    continue
                channel.sendpriv(nick, "*** Command Help: %s ***" % search)
                if len(command["usage"]) != 0:
                    channel.sendpriv(nick, "Usage: %s" % command["usage"])
                if len(command["desc"]) != 0:
                    channel.sendpriv(nick, "Description: %s" % command["desc"])
                channel.sendpriv(nick, "Plugin: %s" % command["plugin"])
                return
            channel.sendpriv(nick, "Can't find command '%s'!" % search)
