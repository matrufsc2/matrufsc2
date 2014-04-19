from bottle import run, default_app, debug, request, response, route, static_file 
import os

IN_DEV = "dev" in os.environ.get("SERVER_SOFTWARE", "").lower() or os.environ.has_key("DEV")
application = default_app()

@route('/ping.cgi', method='POST')
def ping():
	content_disposition = 'attachment; filename=' + request.GET['q']
	data = request.forms['ping']
	response.set_header('Content-Type', 'application/octet-stream')
	response.set_header('Content-Disposition', content_disposition)
	return data

@route('/css/<path:re:.*>')
def css(path):
	return static_file(path, root='./static/css')

@route('/js/<path:re:.*>')
def js(path):
	return static_file(path, root='./static/js')

@route('/<path:re:.*>.json')
def dados(path):
	return static_file(str(path)+'.json', root='./static/dados')

@route('<:re:.*>')
def index():
	return static_file('index.html', root='./static')

# Enables development if running on dev app server
debug(IN_DEV)
if __name__ == '__main__':
	run(port=8181, host='localhost', reloader=IN_DEV)