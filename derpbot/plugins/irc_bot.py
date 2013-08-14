from derpbot import plugin
import irc.client, irc.buffer
import threading

class MyBuffer(irc.client.DecodingLineBuffer):
	errors = "ignore"
irc.client.ServerConnection.buffer_class = MyBuffer

class IRCThread(threading.Thread):
	def __init__(self, plugin):
		super(IRCThread, self).__init__()
		
		self._plugin = plugin
		self._running = False

	def run(self):
		self._running = True
		while self._running:
			self._plugin.ircobj.process_once(0.2)
	
	def stop(self):
		self._running = False

class IRCChannel(plugin.Channel):
	def __init__(self, ircconn, channel):
		self._ircconn = ircconn
		self._channel = channel
		
		self.name = channel
	
	def send(self, message):
		self._ircconn.privmsg(self._channel, message)
		
	def sendpriv(self, nick, message):
		self._ircconn.notice(nick, message)

class IRCPrivateChannel(plugin.Channel):
	private = True
	
	def __init__(self, ircconn, nick):
		self._ircconn = ircconn
		self._nick = nick
		
		self.name = nick

	def send(self, message):
		self._ircconn.notice(self._nick, message)
		
	def sendto(self, nick, message):
		if nick != self._nick:
			raise Exception("Invalid nick!")
		self.send(message)
		
	def sendpriv(self, nick, message):
		self.sendto(nick, message)

class IRCPlugin(plugin.Plugin, irc.client.SimpleIRCClient):
	
	@plugin.config(
		("host", str),
		("port", int, 6667),
		("channel", str),
		("nick", str),
	)
	def __init__(self, bot, config):
		super(IRCPlugin, self).__init__(bot, config)
		
		irc.client.SimpleIRCClient.__init__(self)
	
	def enable(self):
		config = self.config
		host, port = config["host"], config["port"]
		channel, nick = config["channel"], config["nick"]
		self.log_info("Connecting to %s:%d in %s as %s." % (host, port, channel, nick))
		try:
			self.connect(host, port, nick)
		except irc.client.ServerConnectionError, x:
			self.log_exception("Unable to connect to the IRC server!")
		
		self._thread = IRCThread(self)
		self._thread.start()
		
	def disable(self):
		self.connection.disconnect("Bye!")
	
		self._thread.stop()
		self._thread.join()

	def on_nicknameinuse(self, c, e):
		nick = c.get_nickname() + "_"
		self.log_warning("Can't get nickname %s, trying %s." % (c.get_nickname(), nick))
		c.nick(nick)

	def on_welcome(self, c, e):
		c.join(self.config["channel"])
		
		self._channel = IRCChannel(self.connection, self.config["channel"])
		self.bot.plugins.register_channel(self, self._channel)

	def on_privmsg(self, c, e):
		username = e.source.nick
		message = e.arguments[0].strip()
		
		channel = IRCPrivateChannel(c, username)
		self.bot.handle_message(channel, username, message)

	def on_pubmsg(self, c, e):
		username = e.source.nick
		message = e.arguments[0].strip()
		
		self.bot.handle_message(self._channel, username, message)

#	def on_dccmsg(self, c, e):
#		pass
#		c.privmsg("You said: " + e.arguments[0])
#
#	def on_dccchat(self, c, e):
#		pass
#		if len(e.arguments) != 2:
#			return
#		args = e.arguments[1].split()
#		if len(args) == 4:
#			try:
#				address = ip_numstr_to_quad(args[2])
#				port = int(args[3])
#			except ValueError:
#				return
#			self.dcc_connect(address, port)
#
#	def do_command(self, e, cmd):
#		nick = e.source.nick
#		c = self.connection
#
#		if cmd == "disconnect":
#			self.disconnect()
#		elif cmd == "die":
#			self.die()
#		elif cmd == "stats":
#			for chname, chobj in self.channels.items():
#				c.notice(nick, "--- Channel statistics ---")
#				c.notice(nick, "Channel: " + chname)
#				users = chobj.users()
#				users.sort()
#				c.notice(nick, "Users: " + ", ".join(users))
#				opers = chobj.opers()
#				opers.sort()
#				c.notice(nick, "Opers: " + ", ".join(opers))
#				voiced = chobj.voiced()
#				voiced.sort()
#				c.notice(nick, "Voiced: " + ", ".join(voiced))
#		elif cmd == "dcc":
#			dcc = self.dcc_listen()
#			c.ctcp("DCC", nick, "CHAT chat %s %d" % (
#				ip_quad_to_numstr(dcc.localaddress),
#				dcc.localport))
#		else:
#			c.notice(nick, "Not understood: " + cmd)
