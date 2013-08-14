import re
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
		
		self._plugin_modules = []
		
		self._plugin_classes = {}
		self._plugin_instances = {}
		
		self._channels = {}
		
	def set_plugins(self, modules):
		self._plugin_modules = modules
		
	def _load_plugin_module(self, name):
		try:
			module = __import__(name)
			for name in name.split(".")[1:]:
				module = getattr(module, name)
			reload(module)
		except Exception, e:
			self._bot.log_exception("Unable to load plugin module '%s'!" % name)
			return
		
		check = lambda cls: cls != Plugin and isinstance(cls, type) and issubclass(cls, Plugin)
		for attr in dir(module):
			value = getattr(module, attr)
			if check(value):
				self._plugin_classes[classname(value)] = value
		
	def _reload_classes(self):
		self._plugin_classes = {}
		for name in self._plugin_modules:
			self._load_plugin_module(name)
			
	def _load_plugin(self, name, force=False):
		try:
			if name not in self._plugin_classes:
				return False
				
			if force and name in self._plugin_instances:
				self._unload_plugin(name)
			elif name in self._plugin_instances:
				return False
			cls = self._plugin_classes[name]
			plugin = cls(self._bot, self._bot.get_plugin_config(name))
			plugin.enable()
			self._plugin_instances[name] = plugin
			self._channels[name] = []
		except Exception, e:
			self._bot.log_exception("Unable to load plugin %s: %s" % (name, e))
			return False
		return True
			
	def _unload_plugin(self, name):
		try:
			if name not in self._plugin_classes or name not in self._plugin_instances:
				return
				
			plugin = self._plugin_instances[name]
			plugin.disable()
			del self._plugin_instances[name]
			del self._channels[name]
		except Exception, e:
			self._bot.log_exception("Unable to unload plugin %s: %s" % (name, e))
			return False
		return True
		
	def load_plugins(self):
		self._reload_classes()
		for name, cls in self._plugin_classes.items():
			if self._load_plugin(name):
				self._bot.log_info("Enabled plugin %s." % name)
		
	def unload_plugins(self, irc=False):
		for name, cls in self._plugin_classes.items():
			if cls.__module__ == "derpbot.plugins.irc_bot" and irc:
				self._bot.log_info("Skipping irc.")
				continue
			self._unload_plugin(name)
			self._bot.log_info("Disabled plugin %s." % name)
			
	def reload_plugins(self):
		self.unload_plugins(True)
		self.load_plugins()
		
	def handle_message(self, chat, username, message):
		for plugin in self._plugin_instances.values():
			try:
				if plugin.handle_message(chat, username, message):
					return
			except Exception, e:
				chat.sendto(username, "An error happened while handling your message: %s" % e)
				self._bot.log_exception("An error happened while handling a message of %s: %s" % (username, message))
			
	def handle_command(self, chat, username, message, args):
		for plugin in self._plugin_instances.values():
			try:
				if plugin.handle_commands(chat, username, message, args):
					return
			except Exception, e:
				chat.sendto(username, "An error happened while handling your command: %s" % e)
				self._bot.log_exception("An error happened while handling a command of %s: %s" % (username, message))
			
	@property
	def commands(self):
		commands = []
		for plugin in self._plugin_instances.values():
			for command in plugin.commands:
				commands.append(command)
		return commands
	
	def register_channel(self, plugin, channel):
		name = classname(plugin.__class__)
		if name not in self._channels:
			raise Exception("Invalid plugin!")
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
	
	if name == "":
		name = regex
	
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
		
	def handle_message(self, chat, username, message):
		pass
	
	def handle_commands(self, chat, username, message, args):
		for command in self.commands:
			command["func"](chat, username, message, args)
			
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
				"plugin" : classname(self.__class__),
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