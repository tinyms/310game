__author__ = 'tinyms'

from tornado.ioloop import IOLoop
from tornado.web import RequestHandler,Application
import webbrowser,os

class DefaultHandler(RequestHandler):
    def get(self):
        self.redirect("/static/index.html")

settings = {
    "static_path" : os.path.join(os.path.dirname(__file__), "static")
}

app = Application([
    (r"/",DefaultHandler),
],**settings)

if __name__ == "__main__":
    webbrowser.open_new_tab("http://localhost:8080")
    app.listen(8080)
    IOLoop.instance().start()
