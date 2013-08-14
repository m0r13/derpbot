#!/usr/bin/env python2

import sys
import os
sys.path.append(os.path.dirname(__file__))

from derpbot import bot

if __name__ == "__main__":
	if len(sys.argv) < 2:
		print "You have to specify a configuration file!"
		sys.exit(1)
	
	bot = bot.Bot(sys.argv[1])
	try:
		bot.start()
		raw_input("")
	finally:
		bot.stop()
