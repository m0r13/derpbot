from derpbot import plugin, configuration
import logging

def pluginprefix(plugin):
    if plugin != "":
        return "[%s] " % plugin
    return plugin

class Bot:
    def __init__(self, configfile):
        self._config = configuration.ConfigFile(configfile)
        
        logging.basicConfig(format="%(asctime)s [%(levelname)s] %(plugin)s%(message)s")
        self._log = logging.getLogger("chatbot")
        self._log.setLevel(logging.INFO)
        
        self.plugins = plugin.PluginManager(self)
        
    def get_plugin_config(self, name):
        return self._config.get_plugin_config(name)
        
    def start(self):
        self.plugins.set_plugins_avail(self._config.plugins)
        self.plugins.load_plugins()
        
    def stop(self):
        self.plugins.unload_plugins()
        
    def reload(self):
        self._config.reload()
        self.plugins.set_plugins_avail(self._config.plugins)
        self.plugins.reload_plugins()
        
    def handle_message(self, chat, username, message):
        self.plugins.handle_message(chat, username, message)
            
    def handle_command(self, chat, username, message, args):
        self.plugins.handle_command(chat, username, message, args)
        
    def is_admin(self, username):
        return username in self._config.admins
    
    def log_info(self, message, plugin=""):
        self._log.info(message, extra=dict(plugin=pluginprefix(plugin)))
    def log_warning(self, message, plugin=""):
        self._log.warning(message, extra=dict(plugin=pluginprefix(plugin)))
    def log_error(self, message, plugin=""):
        self._log.error(message, extra=dict(plugin=pluginprefix(plugin)))
    def log_critical(self, message, plugin=""):
        self._log.critical(message, extra=dict(plugin=pluginprefix(plugin)))
    def log_exception(self, message, plugin=""):
        self._log.exception(message, extra=dict(plugin=pluginprefix(plugin)))
    
    def log_plugin_error(self, message, plugin=""):
        self.log_exception(message, plugin)
        
        if plugin:
            message = plugin + " gone wild: " + message
        for channel in self.plugins.channels:
            channel.send("halp! " + message)
    