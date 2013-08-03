__author__ = 'tinyms'

from tornado.ioloop import IOLoop
from tornado.web import RequestHandler,Application
import webbrowser,os,json,sys,re
from postgres import query_history_matchs
from lottery import combination

def get_number(text):
    p = re.compile("\\d+")
    nums = p.findall(text)
    if len(nums)>0:
        return int(nums[0])
    return 0

class DefaultHandler(RequestHandler):
    def get(self):
        self.redirect("/static/index.html")

class MatchHistoryHandler(RequestHandler):
    def get(self):
        dataset = dict()
        event_name = self.get_argument("event_name")
        d_result = self.get_argument("d_result")
        flag = self.get_argument("flag")
        odds_direction = self.get_argument("odds_direction")
        odds_int_num = self.get_argument("odds_int_num")
        match_result = self.get_argument("match_result")
        callback = self.get_argument("callback")
        dataset["matchs"] = query_history_matchs(d_result,flag,match_result,odds_direction,odds_int_num,event_name)
        self.set_header("Content-Type","text/javascript")
        self.write(callback+"("+json.dumps(dataset)+")")

class SingleBetting(RequestHandler):
    def get(self):
        guess_match_results = self.get_argument("guess_match_results")
        callback = self.get_argument("callback")
        rates = self.get_argument("rates")
        limit = get_number(self.get_argument("Orders_Number"))
        rates_float = [round(float(s),1) for s in json.loads(rates)]
        print(rates_float)
        self.set_header("Content-Type","text/javascript;charset=utf-8")
        dataset = dict()
        if guess_match_results:
            if len(rates_float) == 0:
                data = combination.generate(guess_match_results,rates_float,limit)
            else:
                data = combination.generate(guess_match_results,rates_float,limit)
            dataset["result"] = data
        self.write(callback+"("+json.dumps(dataset)+")")

settings = {
    "static_path" : os.path.join(os.getcwd(), "static")
}

app = Application([
    (r"/",DefaultHandler),
    (r"/match/history",MatchHistoryHandler),
    (r"/betting/single",SingleBetting),
],**settings)

if __name__ == "__main__":
    port = 8888
    webbrowser.open_new_tab("http://localhost:%i" % port)
    try:
        app.listen(port)
        IOLoop.instance().start()
    except:
        sys.exit(1)
