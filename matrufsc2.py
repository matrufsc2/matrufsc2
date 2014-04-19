from bottle import run, default_app, debug
import os
application = default_app() # For Google App Engine recognize the request

# We yet does not use this file
# But it will be used when I put cron jobs (which Google App Engine will call) here
# And too when I put an API here =)


# Enables development if running on dev app server
debug("dev" in os.environ.get("SERVER_SOFTWARE", "").lower() or os.environ.has("DEV"))
if __name__ == '__main__':
	run(port=8080, host='localhost')