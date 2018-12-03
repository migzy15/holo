from logging import debug, info, error, exception
import praw

# Initialization

_r = None
_config = None

def init_reddit(config):
	global _config
	_config = config

def _connect_reddit():
	if _config is None:
		error("Can't connect to reddit without a config")
		return None
	
	return praw.Reddit(client_id=_config.r_oauth_key, client_secret=_config.r_oauth_secret,
					username=_config.r_username, password=_config.r_password,
					user_agent=_config.useragent,
					check_for_updates=False)

def _ensure_connection():
	global _r
	if _r is None:
		_r = _connect_reddit()
	return _r is not None

# Thing doing

def submit_text_post(subreddit, title, body):
	_ensure_connection()
	try:
		info("Submitting post to {}".format(subreddit))
		new_post = _r.subreddit(subreddit).submit(title, selftext=body, send_replies=False)
                advertise_with_sticky(new_post, body)
		return new_post
	except:
		exception("Failed to submit text post")
		return None

#NOTE: PRAW3 stuff
#def send_modmail(subreddit, title, body):
#	_ensure_connection()
#	_r.send_message("/r/"+subreddit, title, body)
#
#def send_pm(user, title, body, from_sr=None):
#	_ensure_connection()
#	_r.send_message(user, title, body, from_sr=from_sr)
#
#def reply_to(thing, body, distinguish=False):
#	_ensure_connection()
#	
#	reply = thing.reply(body)
#	
#	if distinguish and reply is not None:
#		response = reply.distinguish()
#		if len(response) > 0 and len(response["errors"]) > 0:
#			error("Failed to distinguish: {}".format(response["errors"]))

# Utilities

def get_shortlink_from_id(id):
	return "http://redd.it/{}".format(id)

def advertise_with_sticky(post, body):
    poll_ptrn = r"https://youpoll.me/\d+"
    poll_link = re.search(poll_ptrn, body).group()

    c = configparser.ConfigParser()
    c.read('mod_config.ini')
    mod_acc = praw.Reddit(**c['Auth'])
    reply_to = mod_acc.submission(id=post.id)

    reply_text = """
Hello /r/anime ! Did you know all episode discussion posts include a rating poll ? Just open the post above, you'll see the link plain as day. Go there and give us your opinion on this episode !

... feeling lazy ? Just this once, I'll give you the link here as well. [Click here to go to the poll.]({poll_link}) I hope you enjoyed the episode !
"""

    reply = reply_to.reply(reply_text)
    reply.mod.distinguish(sticky=True)
