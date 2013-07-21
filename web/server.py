__author__ = 'tinyms'

from tornado.ioloop import IOLoop
from tornado.web import RequestHandler,Application
import webbrowser,os,json,sys
from postgres import query_history_matchs

class DefaultHandler(RequestHandler):
    def get(self):
        self.redirect("/static/index.html")

class MatchHistoryHandler(RequestHandler):
    def get(self):
        dataset = dict()
        d_result = self.get_argument("d_result")
        flag = self.get_argument("flag")
        odds_direction = self.get_argument("odds_direction")
        odds_int_num = self.get_argument("odds_int_num")
        match_result = self.get_argument("match_result")
        callback = self.get_argument("callback")
        dataset["matchs"] = query_history_matchs(d_result,flag,match_result,odds_direction,odds_int_num)
        self.set_header("Content-Type","text/javascript")
        self.write(callback+"("+json.dumps(dataset)+")")

settings = {
    "static_path" : os.path.join(os.getcwd(), "static")
}

app = Application([
    (r"/",DefaultHandler),
    (r"/match/history",MatchHistoryHandler),
],**settings)

if __name__ == "__main__":
    port = 8888
    webbrowser.open_new_tab("http://localhost:%i" % port)
    try:
        app.listen(port)
        IOLoop.instance().start()
    except:
        sys.exit(1)
