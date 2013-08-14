from derpbot import plugin
import urllib
import urllib2
import json

def get_imdb_info(title):
    url = "http://imdbapi.com/?" + urllib.urlencode(dict(t=title))
    data = urllib2.urlopen(url).read()
    data = json.loads(data)
    return data

class IMDBPlugin(plugin.Plugin):
    def __init__(self, bot, config):
        super(IMDBPlugin, self).__init__(bot, config)
        
    def enable(self):
        pass
    
    def disable(self):
        pass
    
    @plugin.command("imdb (.*)",
                    name="imdb",
                    usage="imdb [title]",
                    desc="Shows some informations about a movie or tv series from IMDB.")
    def imdb(self, channel, nick, match, message, args):
        title = " ".join(args[1:])
        data = get_imdb_info(title)
        if data["Response"] == "False":
            if "Error" in data:
                channel.sendto(nick, "Error: %s" % data["Error"])
            else:
                channel.sendto(nick, "An unknown error happened.")
                self.log_warning("Got an unknown error from IMDB searching '%s': %s" % (title, repr(data)))
        else:
            type = data["Type"]
            format = (type.upper(),  data["Title"], data["Year"], 
                      data["imdbRating"], data["Genre"],
                      "http://imdb.com/title/%s" % data["imdbID"])
            message = ("[%s] Title: %s | Year: %s | Rating: %s" + \
                        " | Genre: %s | IMDB Link: %s") % format
            channel.send(message)
