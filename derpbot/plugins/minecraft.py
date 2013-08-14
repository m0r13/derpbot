from derpbot import plugin
import subprocess

class MCRCPlugin(plugin.Plugin):
    @plugin.config(("script", str, ""))
    def __init__(self, bot, config):
        super(MCRCPlugin, self).__init__(bot, config)
        
    def enable(self):
        pass
    
    def disable(self):
        pass
    
    @plugin.command("mcrc (start|stop|restart|status|cmd .*|say .*)",
                    name="mcrc", 
                    usage="mcrc start|stop|restart|status|cmd [command]|say [message", 
                    desc="Controls the Minecraft Server script.", 
                    require_admin=True)
    def mcrc(self, channel, nick, match, message, args):
        if self.config["script"] == "":
            channel.sendto(nick, "Can I haz script?")
            return
        
        pargs = [self.config["script"]]
        group = match.group(1)
        if group in ("start", "stop", "restart", "status"):
            pargs.append(group)
        else:
            split = group.split(" ")
            action = split[0]
            message = " ".join(split[1:])
            pargs.append(action)
            pargs.append(message)
        
        out = subprocess.check_output(pargs).strip()
        if out == "":
            return
        
        for line in out.split("\n"):
            channel.send(line)
