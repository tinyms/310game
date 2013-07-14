'''
Created on 2013-2-27

@author: tinyms
'''
import sys,hashlib,os,re
import concurrent.futures
import socket,json
import urllib.request
import urllib.parse
#from datetime import date,datetime
from bs4 import BeautifulSoup
from PyQt5 import QtCore,QtGui
from formula import Result,odds_detect_exclude_one_result

import sqlite3

def connect_db():
    cnn = sqlite3.connect("_cache")
    #cnn.text_factory = str
    return cnn

def create_history_db():
    cnn = connect_db()
    cur = cnn.cursor()
    cur.executescript("""
    CREATE TABLE IF NOT EXISTS [Match] (
      [ID] INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
      [Score] NVARCHAR(5),
      [Asia] INT DEFAULT (0),
      [Result] NVARCHAR(5),
      [Actual_Result] INT DEFAULT (-1),
      [Top_Draw] REAL DEFAULT (0.00),
      [TeamNames] NVARCHAR(255),
      [Last10TextStyle] NVARCHAR(30),
      [Last6TextStyle] NVARCHAR(30),
      [Last4TextStyle] NVARCHAR(30),
      [Last4BattleHistoryDesc] NVARCHAR(20),
      [Odds_WL] NVARCHAR(20),
      [Odds_AM] NVARCHAR(20),
      [Odds_LB] NVARCHAR(20),
      [Odds_365] NVARCHAR(20),
      [Odds_YSB] NVARCHAR(20),
      [Odds_WL_Change] NVARCHAR(20),
      [Odds_AM_Change] NVARCHAR(20),
      [Odds_LB_Change] NVARCHAR(20),
      [Odds_365_Change] NVARCHAR(20),
      [Odds_YSB_Change] NVARCHAR(20),
      [EventName] NVARCHAR(20)
      );
    """)
    cnn.commit()
    cur.close()

def batch_save_history_matchs(ds):
    try:
        rows = []
        for row in ds:
            if row["db_actual_result"] == -1:
                continue
            companys = 0
            if row["Odds_WL"]:
                companys += 1
            if row["Odds_AM"]:
                companys += 1
            if row["Odds_LB"]:
                companys += 1
            if row["Odds_365"]:
                companys += 1
            if row["Odds_YSB"]:
                companys += 1
            if companys < 3:
                continue
            detect_result(row)
            #_batch_save_history_matchs_for_score(row)
            tmp = dict()
            tmp["Score"] = row["score"]
            tmp["Asia"] = row["db_asian"]
            tmp["Result"] = row["result"]
            tmp["Actual_Result"] = row["db_actual_result"]
            tmp["TeamNames"] = " VS ".join(row["team_names"])
            tmp["Last10TextStyle"] = row["last_10_text_style"]
            tmp["Last6TextStyle"] = row["last_6_text_style"]
            tmp["Last4TextStyle"] = row["last_4_text_style"]
            tmp["Last4BattleHistoryDesc"] = row["last_4_status_text_style"]

            tmp["Odds_WL"] = row["Odds_WL"]#新增
            tmp["Odds_AM"] = row["Odds_AM"]#新增
            tmp["Odds_LB"] = row["Odds_LB"]#新增
            tmp["Odds_365"] = row["Odds_365"]#新增
            tmp["Odds_YSB"] = row["Odds_YSB"]#新增
            
            tmp["Top_Draw"] = 0.00
            if tmp["Odds_WL"]:
                nums = [float(f) for f in tmp["Odds_WL"].split(" ")]
                draw = nums[1]
                tmp["Top_Draw"] = draw - int(draw)

            tmp["Odds_WL_Change"] = row["Odds_WL_Change"]#新增
            tmp["Odds_AM_Change"] = row["Odds_AM_Change"]#新增
            tmp["Odds_LB_Change"] = row["Odds_LB_Change"]#新增
            tmp["Odds_365_Change"] = row["Odds_365_Change"]#新增
            tmp["Odds_YSB_Change"] = row["Odds_YSB_Change"]#新增

            tmp["EventName"] = row["season_name"]
            rows.append(tmp)
            pass

        cnn = connect_db()
        cur = cnn.cursor()
        sql = """
            INSERT INTO Match(Score,Asia,Result,Actual_Result,Top_Draw,TeamNames,Last10TextStyle,Last6TextStyle,Last4TextStyle,Last4BattleHistoryDesc,
            Odds_WL,Odds_AM,Odds_LB,Odds_365,Odds_YSB,
            Odds_WL_Change,Odds_AM_Change,Odds_LB_Change,Odds_365_Change,Odds_YSB_Change,EventName)
            VALUES(:Score,:Asia,:Result,:Actual_Result,:Top_Draw,:TeamNames,:Last10TextStyle,:Last6TextStyle,:Last4TextStyle,:Last4BattleHistoryDesc,
            :Odds_WL,:Odds_AM,:Odds_LB,:Odds_365,:Odds_YSB,:Odds_WL_Change,:Odds_AM_Change,:Odds_LB_Change,:Odds_365_Change,:Odds_YSB_Change,:EventName)
        """
        cur.executemany(sql,rows)
        cnn.commit()
        cur.close()
    except:
        print("Insert to db failure.")
        info=sys.exc_info()
        print(info[0],":",info[1])

def list_history_matchs(model,event_name):
    cnn = connect_db()
    cnn.row_factory = sqlite3.Row
    cur = cnn.cursor()
    if model == "":
        sql2 = "SELECT * FROM match WHERE Event=:evt_name ORDER BY Model LIMIT 100"
        return cur.execute(sql2,{"evt_name":event_name})
    else:
        sql = "SELECT * FROM match WHERE Model=? AND Event=? LIMIT 100"
        return cur.execute(sql,(model,event_name))
    
def groupby_match_result(model,event_name):
    cnn = connect_db()
    cnn.row_factory = sqlite3.Row
    cur = cnn.cursor()
    if model == "":
        sql2 = "SELECT AR,COUNT(1) as scale FROM match WHERE Event=:evt_name GROUP BY AR LIMIT 100"
        return cur.execute(sql2,{"evt_name":event_name})
    else:
        sql = "SELECT AR,COUNT(1) as scale FROM match WHERE Model=? AND Event=? GROUP BY AR LIMIT 100"
        return cur.execute(sql,(model,event_name))

def cache_last_access_urls(url):
    if url.find("@")!=-1:
        return
    if url == "http://zc.trade.500.com/sfc/index.php":
        return
    if os.path.exists("data/urls-cache"):
        arr = json.loads(read_file("data/urls-cache"))
        if url in arr:
            return
        arr.append(url)
        if len(arr) > 20:
            write_file("data/urls-cache",json.dumps(arr[1:]))
        else:
            write_file("data/urls-cache",json.dumps(arr))
    else:
        arr = [url]
        write_file("data/urls-cache",json.dumps(arr))
        
def get_last_access_urls():
    if os.path.exists("data/urls-cache"):
        arr = json.loads(read_file("data/urls-cache"))
        arr.reverse()
        return arr
    return []

#utils funciton

#求列表排序后的中值
def median_value(numbers):
    return sum(numbers)/10

def median_value1(numbers):
    n = len(numbers)
    copy = numbers[:]
    copy.sort()
    if n & 1:
        print(int(n/2))
        return copy[int(n/2)]
    else:
        return (copy[int(n/2) - 1] + copy[int(n/2)]) / 2

#求列表中频繁出现的数字
def freq_num(numbers):
    results = set()

    freq = {}
    for i in range(len(numbers)):
        try:
            freq[numbers[i]] += 1
        except KeyError:
            freq[numbers[i]] = 1

    max = 0
    first_max_item = None
    print(freq)
    for k in freq:
        v = freq[k]
        if v > max:
            max = v
            first_max_item = k
    results.add(first_max_item)
    #find onter same nums item
    first_max_value = freq[first_max_item]
    for k in freq:
        v = freq[k]
        if first_max_value == v:
            results.add(k)

    return results

def trim_all(text):
    return "".join(text.split())

def md5(s):
    h = hashlib.new('ripemd160')
    h.update(bytearray(s.encode("utf8")))
    return h.hexdigest()

def url_with_params(url):
    r1 = urllib.parse.urlsplit(str(url))
    if r1.query!="":
        return True
    return False

def write_file(file_name,data):
    f = QtCore.QFile(file_name)
    if not f.open(QtCore.QIODevice.WriteOnly):
        return
    stream = QtCore.QTextStream(f)
    stream.setCodec("UTF-8")
    stream << data

def append_file(file_name,data):
    f = QtCore.QFile(file_name)
    if not f.open(QtCore.QIODevice.Append):
        return
    stream = QtCore.QTextStream(f)
    stream.setCodec("UTF-8")
    stream << data
        
def read_file(file_name):
    f = QtCore.QFile(file_name)
    if not f.open(QtCore.QIODevice.ReadOnly):
        return
    stream = QtCore.QTextStream(f)
    stream.setCodec("UTF-8")
    return str(stream.readAll())

def web_page_download(url,cached=True):
    soup = None
    while True:
        try:
            f = get_cache_web_file_name(url)
            if os.path.exists(f):
                html = read_file(f)
                soup = BeautifulSoup(html)
            else:
                web_page = urllib.request.urlopen(url,timeout=15)
                html = web_page.read()
                html = html.decode('gb18030')
                soup = BeautifulSoup(html)
                if url_with_params(url) and cached:
                    local_file = get_cache_web_file_name(url)
                    write_file(local_file,html)
            break
        except urllib.error.URLError as ex:
            info=sys.exc_info()
            #send_msg(info[1])
            print(info[0],":",info[1])
            continue
            #break
    return soup

def soup(local_file):
    if os.path.exists(local_file):
        html = read_file(local_file)
        return BeautifulSoup(html)
    return None

def mkdirs(path):
    isExists=os.path.exists(path)
    if not isExists:
        os.makedirs(path)
        return True
    else:
        return False
    
def get_number(text):
    p = re.compile("\\d+")
    nums = p.findall(text)
    if len(nums)>0:
        return nums[0]
    return ""

def get_date_text(text):
    p = re.compile("\\d{4}-\\d{2}-\\d{2}")
    dates = p.findall(text)
    if len(dates)>0:
        return dates[0]
    return ""

def get_short_time(text):
    p = "\\d{2}-\\d{2}\\s{1}\\d{2}:\\d{2}"
    r = re.compile(p)
    matchs = r.findall(text)
    if len(matchs)>0:
        return matchs[0]
    return ""

def get_int_numbers(text):
    p = re.compile("\\d+",re.M)
    return p.findall(text)

def get_float_numbers(text):
    p = re.compile("\\d+\\.\\d+",re.M)
    return p.findall(text)

def get_map_value(map_,key,defaut_=None):
    if map_.has_key(key):
        return map_[key]
    return defaut_

def get_zero_div(a,b,extra=0.01):
    try:
        r = a/b
    except ZeroDivisionError:
        r = a/(b+extra)
    return round(r,2)

def get_sina_vote_scale_url():
    parse = web_page_download("http://sports.sina.com.cn/iframe/lottery/sfc/iframe_index.html")
    if not parse:
        return ""
    links = parse.find_all("a")
    for link in links:
        text = link.get_text()
        if text == "火线伤停":
            return link["href"]
    return ""

def udp_server(deal_func):
    ip = ('127.0.0.1',MessageService.PORT)
    udp = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    while True:
        try:
            udp.bind(ip)
            break
        except:
            MessageService.PORT += 1
            ip = ('127.0.0.1',MessageService.PORT)
            continue

    while True:
        data,ip = udp.recvfrom(2028)
        if data == "close_message_loop":
            udp.close()
            break
        if data:
            if deal_func:
                deal_func.emit(str(data,encoding="utf8"))
    udp.close()

def send_msg(data):
    ip = ('127.0.0.1',MessageService.PORT)
    udp = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    udp.sendto(data.encode("utf8"),ip)
    udp.close()
    
class MessageService(QtCore.QThread):
    PORT = 8888
    signal_message_arrival = QtCore.pyqtSignal(str)
    def __init__(self):
        QtCore.QThread.__init__(self)
        
    def run(self):
        try:
            udp_server(self.signal_message_arrival)
        except:
            info=sys.exc_info()
            print(info[0],":",info[1]) 
                  
def DownloadWebPageTask(url):
    send_msg("下载 %s" % url)
    while True:
        try:
            web_page = urllib.request.urlopen(url,timeout=15)
            html = web_page.read()
            html = html.decode('gb18030')
            local_file = get_cache_web_file_name(url)
            write_file(local_file,html)
            break
        except urllib.error.URLError as ex:
            info=sys.exc_info()
            send_msg(info[1])
            print(info[0],":",info[1])
            send_msg("重下载 %s" % url)
            continue
    
def get_cache_web_file_name(url):
    return "cache_web_pages/%s/%s" % ("html",md5(url))

def batch_download_web_pages(urls):
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        for url in urls:
            f = get_cache_web_file_name(url)
            if os.path.exists(f):
                continue
            executor.submit(DownloadWebPageTask,url)
        send_msg("等待下载任务完成..")
        executor.shutdown()

def asian_rq(key):
    m = dict()
    m["平手"] = "0"
    m["平手/半球"] = "0.25"
    m["半球"] = "0.5"
    m["半球/一球"] = "0.75"
    m["一球"] = "1"
    m["一球/球半"] = "1.25"
    m["球半"] = "1.5"
    m["球半/两球"] = "1.75"
    m["两球"] = "2"
    m["两球/两球半"] = "2.25"
    m["两球半"] = "2.5"
    m["两球半/三球"] = "2.75"
    m["三球"] = "3"
    m["三球/三球半"] = "3.25"
    m["三球半"] = "3.5"
    m["三球半/四球"] = "3.75"
    m["四球"] = "4"
    sign = "-"
    if key:
        if key.find("受")!=-1:
            sign = "+"
            key = key.replace("受","")
        val = m.get(key)
        if val:
            return sign + val
    return ""

#For Matchs TreeView
class MatchsTreeItem(object):
    def __init__(self, data, parent=None):
        self.parentItem = parent
        self.itemData = data
        self.childItems = []

    def appendChild(self, item):
        self.childItems.append(item)

    def child(self, row):
        return self.childItems[row]

    def childCount(self):
        return len(self.childItems)

    def columnCount(self):
        return len(self.itemData)

    def data(self, column):
        try:
            if column == 0:
                return self.itemData["result"]
            elif column == 1:
                return self.itemData["actual_result"]
            elif column == 2:
                return self.itemData["odds_asian"]
            elif column == 3:
                return self.itemData["odds"]
            elif column == 4:
                return self.itemData["asian_rq_text_style"]
            elif column == 5:
                return self.itemData['team_names']
            elif column == 6:
                return self.itemData["last_10_text_style"]
            elif column == 7:
                return self.itemData["last_6_text_style"]
            elif column == 8:
                return self.itemData["last_4_text_style"]
            elif column == 9:
                return self.itemData["last_4_status_text_style"]
            elif column == 10:
                return self.itemData["season_name"]
            elif column == 11:
                return self.itemData["match_date"]
            return ""
        except IndexError:
            return None

    def parent(self):
        return self.parentItem

    def row(self):
        if self.parentItem:
            return self.parentItem.childItems.index(self)
        return 0

#赛果预测
def detect_result(match):
    scores = []
    #scores += match["formula_total"].to_results()
    scores += match["formula_last10"].to_results()
    scores += match["formula_last6"].to_results()
    scores += match["formula_last4"].to_results()
    #scores += match["formula_last_mid"].to_results()
    r = Result(scores,match["odds"])
    match["result"]=r.detect(match["formula_last4"])

class MatchsTreeModel(QtCore.QAbstractItemModel):
    HIDE_SCORE = False
    def __init__(self, data, parent=None):
        super(MatchsTreeModel, self).__init__(parent)
        titles = dict()
        titles["result"]="实力"
        titles["odds_asian"] = "欧亚"
        titles["asian_rq_text_style"] = "(让球)亚盘(比分)"
        titles["actual_result"]="赛果"
        titles["team_names"]="对阵球队"
        titles["last_6_text_style"]="近6场(主客)"
        titles["last_10_text_style"]="近10场(主客)"
        titles["last_4_text_style"]="近4场(状态)"
        titles["last_4_status_text_style"] = "近6场(热度)"
        titles["odds"]="初盘(威廉)"
        titles["season_name"]="赛事"
        titles["match_date"]="比赛日期"
        self.rootItem = MatchsTreeItem(titles)

        self.setupModelData(data, self.rootItem)

    def columnCount(self, parent):
        if parent.isValid():
            return parent.internalPointer().columnCount()
        else:
            return self.rootItem.columnCount()

    def data(self, index, role):

        if not index.isValid():
            return None

        tip_index = -1
        if role == QtCore.Qt.DisplayRole:
            item = index.internalPointer()
            data = item.data(index.column())
            return data

        if role == QtCore.Qt.TextAlignmentRole:
            if 0==index.column() or 1==index.column() or 8==index.column():
                return QtCore.Qt.AlignCenter

        if role == QtCore.Qt.BackgroundRole:
            item = index.internalPointer()
            data = item.data(index.column())
            if index.column() == 3:
                if data:
                    arr = [float(s) for s in data.split(" ")]
                    draw = arr[1]
                    int_part = int(draw)
                    dot_part = draw - int_part
                    if round(dot_part,1) >= 0.4:
                        tip_index = index.column()
                        return QtGui.QColor("#FF6666")
                pass

            if 4 == index.column():
                return QtGui.QColor("#99CCCC")
            elif 6 == index.column():
                return QtGui.QColor("#FFFFCC")
            elif 7 == index.column():
                return QtGui.QColor("#99CC99")
            elif 8 == index.column():
                return QtGui.QColor("#99CCCC")

            elif 2 == index.column():
                return QtGui.QColor("#FFCC99")

        return None

    def flags(self, index):
        if not index.isValid():
            return QtCore.Qt.NoItemFlags

        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def headerData(self, section, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self.rootItem.data(section)
        return None

    def index(self, row, column, parent):
        if not self.hasIndex(row, column, parent):
            return QtCore.QModelIndex()

        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()

        childItem = parentItem.child(row)
        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QtCore.QModelIndex()

    def parent(self, index):
        if not index.isValid():
            return QtCore.QModelIndex()

        childItem = index.internalPointer()
        parentItem = childItem.parent()

        if not parentItem:
            return QtCore.QModelIndex()

        if parentItem == self.rootItem:
            return QtCore.QModelIndex()

        return self.createIndex(parentItem.row(), 0, parentItem)

    def rowCount(self, parent):
        if parent.column() > 0:
            return 0

        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()

        return parentItem.childCount()

    def convert_odds_to_balls(self,odds):
        if not odds:
            return "0"
        items = odds.split(" ")
        nums = [float(i) for i in items]
        win_rate = round(1/nums[0],2)
        #draw_rate = round(1/nums[1],2)
        lost_rate = round(1/nums[2],2)
        diff = win_rate-lost_rate
        sign = "-"
        if diff < 0:
            sign = "+"
        balls = "%s%.2f" % (sign,round(abs(diff)/0.5,2))
        return balls

    def setupModelData(self, matchs, parent):
        for match in matchs:
            match["asian_rq_text_style"] = "%s%s%s" % (match["rq"],match["asian"],match["score"])
            detect_result(match)
            #odds_detect_exclude_one_result(match)
            match["odds"] = match["odds"];
            match["odds_asian"] = self.convert_odds_to_balls(match["Odds_WL"])
            if match["actual_result"].find("-1")!=-1:
                match["actual_result"]=""

            if match["score"] == "[]":
                match["score"] = ""

            if type(match['team_names']) == list:
                if MatchsTreeModel.HIDE_SCORE:
                    team_names = ' VS '.join(match['team_names'])
                else:
                    team_names = ' VS '.join(match['team_names'])
            else:
                team_names = match['team_names']

            match["team_names"] = team_names
            match["match_date"] = match["match_date"]
            first_child = MatchsTreeItem(match)
            parent.appendChild(first_child)
        pass
    