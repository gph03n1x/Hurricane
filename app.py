__author__ = 'John'
import os.path
import tornado.ioloop
import tornado.web
from pprint import pprint


class SearchHandler(tornado.web.RequestHandler):
    def get(self, arguments):
        self.render("log.html", logs=reversed(results))
    def post(self):
        pass

class CrawlHandler(tornado.web.RequestHandler):
    def get(self, arguments):
        self.render("log.html", logs=reversed(results))
    def post(self):
        pass


application = tornado.web.Application(
    [
    (r"/", SearchHandler),
    (r"/crawl", SearchHandler),
    (r"/crawl/(.+)", SearchHandler)
    ],
    template_path=os.path.join(os.path.dirname(__file__), "templates"),
    static_path=os.path.join(os.path.dirname(__file__), "static"),
    )

if __name__ == "__main__":
    application.listen(8000)
    tornado.ioloop.IOLoop.instance().start()