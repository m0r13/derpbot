from derpbot import plugin
import random

class RandPlugin(plugin.Plugin):
    def __init__(self, bot, config):
        super(RandPlugin, self).__init__(bot, config)
        
    def enable(self):
        pass
    
    def disable(self):
        pass
    
    @plugin.command("rand .*",
                    name="rand",
                    usage="rand [from] <to>",
                    desc="Generates a random number <from> <to>.")
    def rand(self, channel, nick, match, message, args):
        if len(args) < 2:
            return
        try:
            if len(args) == 2:
                channel.sendto(nick, str(random.randint(1, int(args[1]))))
            else:
                channel.sendto(nick, str(random.randint(int(args[1]), int(args[2]))))
        except ValueError:
            channel.sendto(nick, "I NEED A FUCKING INTEGER!!!")
            
    @plugin.command("randchoice (.*)",
                    name="randchoice",
                    usage="randchoice <choices>",
                    desc="Chooses a random element from a comma-separated list of choices.")
    def randchoice(self, channel, nick, match, message, args):
        if len(args) < 2:
            return
        choices = match.group(1).split(",")
        channel.sendto(nick, random.choice(choices))
