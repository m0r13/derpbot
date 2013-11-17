from derpbot import plugin

class AdminPlugin(plugin.Plugin):
    def __init__(self, bot, config):
        super(AdminPlugin, self).__init__(bot, config)
        
    def enable(self):
        pass
    
    def disable(self):
        pass
    
    @plugin.command("reload",
                    name="reload", 
                    usage="reload",
                    desc="Reloads all plugins.",
                    require_admin=True)
    def reload(self, channel, nick, match, message, args):
        if not self.bot.is_admin(nick):
            channel.sendto(nick, "You don't have permission to use this command!")
        channel.sendto(nick, "Reloading.")
        self.bot.reload()
        
    @plugin.command("plugins",
                    name="plugins",
                    usage="plugins",
                    require_admin=True)
    def plugins(self, channel, nick, match, message, args):
        plugin_mgr = self.bot.plugins
        
        enabled = plugin_mgr._plugin_instances.keys()
        channel.sendpriv(nick, "Enabled plugins: " + ", ".join(enabled))
        
        not_enabled = []
        for name in plugin_mgr._plugins_avail.values():
            if name not in enabled:
                not_enabled.append(name)
        channel.sendpriv(nick, "Not enabled plugins: " + ", ".join(not_enabled))
            
    @plugin.command("say (.*)", 
                    name="say", 
                    usage="say <text>", 
                    require_admin=True)
    def say(self, channel, nick, match, message, args):
        for c in self.bot.plugins.channels:
            c.send(match.group(1))
