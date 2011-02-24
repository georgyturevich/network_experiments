from twisted.web import resource, server, static
from twisted.application import internet, service


class ClientManager(object):
    clients = []
    def registerClient(self, client):
        self.clients.append(client)

    def broadcastMessage(self, message):
        for client in self.clients:
            client.write(message)
            client.notifyFinish()
        self.clients = []

clientManager = ClientManager()

class LongPollServer(resource.Resource):
    isLeaf = False
    def __init__(self):
        resource.Resource.__init__(self)
        self.registerChildren()

    def registerChildren(self):
        self.putChild('subscribe', Subscribe() )
        self.putChild('publish', Publish() )

        # @todo How to avoid abspath?
        jsFile = static.File('/var/www/http_chat/python/twisted/public/')
        self.putChild('', jsFile)

    def getChild( self, path, req ):
        if path == '':
            return self
        else:
            return resource.Resource.getChild( self, path, req )

class Subscribe(resource.Resource):
    isLeaf = True
    def render_GET(self, req):
        clientManager.registerClient(req)
        return server.NOT_DONE_YET

class Publish(resource.Resource):
    isLeaf = True
    def render_POST(self, req):
        clientManager.broadcastMessage(req.args['message'][0])
        return "ok"

application = service.Application("App")
service = internet.TCPServer(8002, server.Site(LongPollServer()))
service.setServiceParent(application)
