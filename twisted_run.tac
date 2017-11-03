from twisted.web.wsgi import WSGIResource
from twisted.internet import reactor
from twisted.web import server
from system_trading.wsgi import application as application

resource = WSGIResource(reactor, reactor.getThreadPool(), application)
site = server.Site(resource)
reactor.listenTCP(9032, site)
reactor.run()


