#!/usr/bin/env python2

import sys
import os
sys.path.append(os.path.dirname(__file__))

from derpbot import bot

if __name__ == "__main__":
	
	bot = bot.Bot("config.xml")
	
	bot.start()
	raw_input("")
	bot.stop()
