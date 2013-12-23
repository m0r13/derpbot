import time
import threading
import re
from collections import OrderedDict
from derpbot import util, configuration

class Channel(object):
    name = None
    private = False
    
    def send(self, message):
        pass
    
    def sendto(self, nick, message):
        self.send("%s: %s" % (nick, message))
    
    def sendpriv(self, nick, message):
        pass
        
def classname(cls):
    if cls.__module__ != "":
        return cls.__module__ + "." + cls.__name__
    return cls.__name__
    
class PluginManager(object):
    def __init__(self, bot):
        self._bot = bot
        
        self._plugins_avail = OrderedDict()
        
        self._plugin_classes = OrderedDict()
        self._plugin_instances = OrderedDict()
        
        self._channels = OrderedDict()
        
    def set_plugins_avail(self, plugins):
        self._plugins_avail.clear()
        for path in plugins:
            name = path.split(".")[-1]
            self._plugins_avail[path] = name
    
    def load_plugin(self, name, force=False):
        try:
            if name not in self._plugin_classes:
                return False
                
            if force and name in self._plugin_instances:
                self.unload_plugin(name)
            elif name in self._plugin_instances:
                return False
            self._channels[name] = []
            cls = self._plugin_classes[name]
            plugin = cls(self._bot, self._bot.get_plugin_config(name))
            plugin.enable()
            self._plugin_instances[name] = plugin
        except Exception, e:
            self._bot.log_plugin_error("Unable to load plugin %s: %s" % (name, util.format_exception(e)))
            #self._bot.log_exception("Unable to load plugin %s: %s" % (name, e))
            return False
        return True
    
    def load_plugins(self):
        self._reload_classes()
        for name in self._plugins_avail.values():
            if self.load_plugin(name):
                self._bot.log_info("Enabled plugin %s." % name)
    
    def unload_plugin(self, name):
        if name not in self._plugin_classes or name not in self._plugin_instances:
            return False
        plugin = self._plugin_instances[name]
        try:
            plugin.disable()
        except Exception, e:
            self._bot.log_plugin_error("An error happened while unloading plugin %s, plugin was force-unloaded: %s" % (name, util.format_exception(e)))
            #self._bot.log_exception("Unable to unload plugin %s: %s" % (name, e))
        del self._plugin_instances[name]
        del self._channels[name]
        return True
    
    def unload_plugins(self, irc=False):
        for name in self._plugin_classes.keys():
            if name == "IRCPlugin" and irc:
                self._bot.log_info("Skipping irc.")
                continue
            self.unload_plugin(name)
            self._bot.log_info("Disabled plugin %s." % name)
            
    def reload_plugins(self):
        self.unload_plugins(True)
        self.load_plugins()
        
    def _load_plugin_class(self, path):
        modulename = ".".join(path.split(".")[:-1])
        clsname = path.split(".")[-1]
        try:
            module = __import__(modulename)
            for m in modulename.split(".")[1:]:
                module = getattr(module, m)
            reload(module)
        except Exception, e:
            self._bot.log_plugin_error("Unable to load plugin module '%s': %s" % (modulename, util.format_exception(e)))
            #self._bot.log_exception("Unable to load plugin module '%s'!" % modulename)
            return
        
        cls = getattr(module, clsname)
        if cls != Plugin and isinstance(cls, type) and issubclass(cls, Plugin):
            return cls
        else:
            self._bot.log_plugin_error("Invalid plugin class '%s'!" % path)
            #self._bot.log_error("Invalid plugin class '%s'!" % path)
    
    def _reload_classes(self):
        self._plugin_classes.clear()
        for path, name in self._plugins_avail.items():
            cls = self._load_plugin_class(path)
            if cls != None:
                self._plugin_classes[name] = cls
        
    def handle_message(self, chat, username, message):
        for name, plugin in self._plugin_instances.items():
            try:
                if plugin.handle_message(chat, username, message):
                    return
            except Exception, e:
                chat.sendto(username, "An error happened while handling your message.")
                self._bot.log_plugin_error(util.format_exception(e), name)
                #self._bot.log_exception("An error happened while handling a message of %s: %s" % (username, message))
            
    def handle_command(self, chat, username, message, args):
        for name, plugin in self._plugin_instances.items():
            try:
                if plugin.handle_commands(chat, username, message, args):
                    return
            except Exception, e:
                chat.sendto(username, "An error happened while handling your command.")
                self._bot.log_plugin_error(util.format_exception(e), name)
                #self._bot.log_exception("An error happened while handling a command of %s: %s" % (username, message))
            
    @property
    def commands(self):
        commands = []
        for plugin in self._plugin_instances.values():
            for command in plugin.commands:
                commands.append(command)
        return commands
    
    def register_channel(self, plugin, channel):
        name = plugin.__class__.__name__
        if name not in self._channels:
            raise Exception("Invalid plugin %s!" % name)
        self._channels[name].append(channel)
    
    @property
    def channels(self):
        for channels in self._channels.values():
            for channel in channels:
                yield channel

def config(*attributes):
    def sub_generator(func):
        def sub_function(self, bot, config):
            node = config
            if config is None:
                node = configuration.ET.Element("")
            func(self, bot, configuration.convert_plugin_config(node, attributes))
        return sub_function
    return sub_generator

def command(regex, regexflags=0, 
            name="", usage="", desc="", require_admin=False):
    if not regex.endswith("$"):
        regex += "$"
    cregex = re.compile(regex, regexflags)
    
    def sub_generator(func):
        def sub_function(self, channel, nick, message, args):
            match = cregex.match(message)
            if not match:
                return False
            if require_admin and not self.bot.is_admin(nick):
                channel.sendto(nick, "You don't have permission to use this command!")
                return
            func(self, channel, nick, match, message, args)
            return True
        sub_function._is_command = 42
        sub_function._command_regex = regex
        sub_function._command_name = name
        sub_function._command_usage = usage
        sub_function._command_desc = desc
        return sub_function
    return sub_generator

EVENT_USERJOIN = 1
EVENT_USERLEAVE = 2

def event(event):
    def sub_generator(func):
        def sub_function(self, *args, **kwargs):
            func(self, *args, **kwargs)
        sub_function._is_event_handler = 42
        sub_function._event = event
        return sub_function
    return sub_generator
    
class Plugin(object):
    def __init__(self, bot, config):
        self.bot = bot
        self.config = config
        
    def enable(self):
        pass
        
    def disable(self):
        pass
        
    def handle_message(self, channel, username, message):
        pass
    
    def handle_commands(self, channel, username, message, args):
        for command in self.commands:
            command["func"](channel, username, message, args)
            
    @property
    def commands(self):
        for func in dir(self):
            func = getattr(self, func)
            if not "_is_command" in dir(func) or func._is_command != 42:
                continue
            
            yield {
                "regex" : func._command_regex,
                "name" : func._command_name,
                "usage" : func._command_usage,
                "desc" : func._command_desc,
                "func" : func,
                "plugin" : self.__class__.__name__,
            }
            
    def log_info(self, message):
        self.bot.log_info(message, self.__class__.__name__)
    def log_warning(self, message):
        self.bot.log_warning(message, self.__class__.__name__)
    def log_error(self, message):
        self.bot.log_error(message, self.__class__.__name__)
    def log_critical(self, message):
        self.bot.log_critical(message, self.__class__.__name__)
    def log_exception(self, message):
        self.bot.log_exception(message, self.__class__.__name__)

class PollWorker(threading.Thread):
    def __init__(self, interval, errhandler=lambda e: None):
        threading.Thread.__init__(self)
        
        self.interval = interval
        self.lastpoll = 0
        self.running = True
        
        self._errhandler = errhandler
        
    def set_interval(self, interval):
        self.interval = interval
    
    def stop(self):
        self.running = False
        self.join()
    
    def run(self):
        self.lastpoll = time.time()
        while self.running:
            if time.time() - self.lastpoll >= self.interval:
                start = time.time()
                try:
                    self.poll()
                except Exception, e:
                    self._errhandler(e)
                self.lastpoll = start
            else:
                time.sleep(0.5)
    
    def poll(self):
        # implement this
        pass
    
class PollPlugin(Plugin, PollWorker):
    interval = 30
    
    def __init__(self, bot, config):
        Plugin.__init__(self, bot, config)
        PollWorker.__init__(self, self.interval, self._handle_exception)
        
        self._bot = bot
        
    def enable(self):
        super(PollPlugin, self).enable()
        
        self.start()
        
    def disable(self):
        super(PollPlugin, self).disable()
        
        self.stop()
    
    def _handle_exception(self, exception):
        self._bot.log_plugin_error(util.format_exception(exception), self.__class__.__name__)
