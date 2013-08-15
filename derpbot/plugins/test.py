from derpbot import plugin
import time

class TestPlugin(plugin.Plugin):
    def __init__(self, *args, **kwargs):
        super(TestPlugin, self).__init__(*args, **kwargs)
        
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
        
class PollTestPlugin(plugin.PollPlugin):
    interval = 10
    
    def __init__(self, *args, **kwargs):
        super(PollTestPlugin, self).__init__(*args, **kwargs)
        
    def poll(self):
        for channel in self.bot.plugins.channels:
            channel.send("It's %d and the last poll was %d." % (time.time(), self.lastpoll))
