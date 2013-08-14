from derpbot import plugin

class TestPlugin(plugin.Plugin):
    def __init__(self, bot, config):
        super(TestPlugin, self).__init__(bot, config)
        
    def enable(self):
        pass
    
    def disable(self):
        pass
    
    @plugin.command("hello",
                    name="hello")
    def hello(self, channel, nick, match, message, args):
        channel.sendto(nick, "Hello %s!" % nick)
        channel.sendpriv(nick, "Psssst! Don't worry, this is private. Wanna start socialist revolution?")

    @plugin.command("error",
                    name="error")
    def error(self, channel, nick, match, message, args):
        raise Exception("This is an exception")