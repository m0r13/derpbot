from derpbot import plugin, util
import urllib2
import json

# from hesperus chat bot, see https://github.com/agrif/hesperus
# pretty string trunc function
# <http://kelvinwong.ca/2007/06/22/a-nicer-python-string-truncation-function/>
# from Kelvin Wong, under the license at http://www.python.org/psf/license/
def trunc(s, min_pos=0, max_pos=75, ellipsis=True):
    # Sentinel value -1 returned by String function rfind
    NOT_FOUND = -1
    # Error message for max smaller than min positional error
    ERR_MAXMIN = "Minimum position cannot be greater than maximum position"
    
    # If the minimum position value is greater than max, throw an exception
    if max_pos < min_pos:
        raise ValueError(ERR_MAXMIN)
    # Change the ellipsis characters here if you want a true ellipsis
    if ellipsis:
        suffix = '...'
    else:
        suffix = ''
    # Case 1: Return string if it is shorter (or equal to) than the limit
    length = len(s)
    if length <= max_pos:
        return s + suffix
    else:
        # Case 2: Return it to nearest period if possible
        try:
            end = s.rindex('.',min_pos,max_pos)
        except ValueError:
            # Case 3: Return string to nearest space
            end = s.rfind(' ',min_pos,max_pos)
            if end == NOT_FOUND:
                end = max_pos
        return s[0:end] + suffix

def format_ref(ref):
    if ref.startswith("refs/heads/master"):
        return ref.replace("refs/heads/", "")
    return ref

class GitHubPlugin(plugin.PollPlugin):
    interval = 60
    interval_auth = 30
    
    @plugin.config(
        ("client-id", str, ""),
        ("client-secret", str, ""),
        ("feeds", util.XMLList("feed"), []),
    )
    def __init__(self, *args, **kwargs):
        super(GitHubPlugin, self).__init__(*args, **kwargs)
        
        self.auth = ""
        if self.config["client-id"]:
            self.auth = "?client_id=%s&client_secret=%s" % (self.config["client-id"], self.config["client-secret"])
            self.set_interval(self.interval_auth)
    
    def format_event(self, event):
        if "payload" not in event:
            return None
        payload = event["payload"]
        
        msg = None
        args = dict()
        if event["type"] == "PushEvent":
            extra = json.load(urllib2.urlopen(urllib2.Request(payload["commits"][-1]["url"] + self.auth, None, {"User-Agent" : "derpbot"})))
            msg = "{user} pushed {count} commit{plural} to {ref} on {repo}"
            args = dict(
                user=event["actor"]["login"],
                count=len(payload["commits"]),
                plural="s",
                ref=format_ref(payload["ref"]),
                repo=event["repo"]["name"],
                message=trunc(payload["commits"][-1]["message"], 0, 50),
                url=util.short_url(extra["html_url"], provider="git.io")
            )
            if len(payload["commits"]) == 1:
                msg += ": \"{message}\""
                args.update(plural="")
            msg += ". ({url})"
        elif event["type"] == "IssuesEvent":
            msg = "{user} {action} issue #{number} \"{title}\" on {repo}. ({url})"
            args = dict(
                user=event["actor"]["login"],
                action=payload["action"],
                number=payload["issue"]["number"],
                title=payload["issue"]["title"],
                repo=event["repo"]["name"],
                url=util.short_url(payload["issue"]["url"], provider="git.io"),
            )
        elif event["type"] == "IssueCommentEvent":
            msg = "{user} commented on issue #{number} \"{title}\" on {repo}: \"{message}\". ({url})"
            args = dict(
                user=event["actor"]["login"],
                number=payload["issue"]["number"],
                title=payload["issue"]["title"],
                repo=event["repo"]["name"],
                message=trunc(payload["comment"]["body"], 0, 50),
                url=util.short_url(payload["comment"]["html_url"], provider="git.io"),
            )
        if msg is not None:
            return msg.format(**args)
        return None
        
    def poll(self):
        for feed in self.config["feeds"]:
            try:
                req = urllib2.Request(feed + self.auth, None, {"User-Agent" : "derpbot"})
                data = json.load(urllib2.urlopen(req))
            except urllib2.HTTPError:
                self.log_exception("HTTP Error")
                continue
            
            if "message" in data and "API rate limit exceeded" in data["message"]:
                self.log_critical("GitHub api rate limit exceeded!")
                return
            
            for event in data:
                created = util.utc_to_timestamp(event["created_at"])
                if created < self.lastpoll:
                    continue
                msg = self.format_event(event)
                if msg is not None:
                    for channel in self.bot.plugins.channels:
                        channel.send(msg)
