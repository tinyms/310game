'''
Created on 2013-3-9
@author: tinyms
'''

import threading,re,os
import concurrent.futures
from datetime import datetime, timedelta
from utils import mkdirs
from utils import soup,asian_rq
from utils import get_zero_div
from utils import get_int_numbers
from utils import get_float_numbers
from utils import DownloadWebPageTask
from utils import send_msg,create_history_db
from utils import get_number,write_file
from utils import web_page_download
from utils import get_cache_web_file_name
from utils import trim_all
from formula import Formula
    
class HtmlParseThread(threading.Thread):
    targetUrl = ""
    RQ = True
    dataset = []
    def __init__(self):
        threading.Thread.__init__(self)
        self.season_data_last_id = ""
        self.season_data_prev_id = ""
        self.season_data_last_map = dict()
        self.season_data_prev_map = dict()
    def run(self):
        mkdirs("cache_web_pages/html")
        send_msg("开始分析基本面..")
        matchs = self.extract_matchs(str(self.targetUrl))
        self.batch_download_data_pages(matchs)
        for match in matchs:
            msg = "获取初赔 %s" % match["odds_url"]
            send_msg(msg)
            self.parse_odds(match, get_cache_web_file_name(match["odds_url"]))
            msg = "分析基本面 %s" % match["base_face_url"]
            send_msg(msg)
            self.parse_baseface(match, get_cache_web_file_name(match["base_face_url"]))
        self.dataset = matchs
        send_msg("refresh_match_grid");
        send_msg("完成.")

    def parse_team_battle_balls_io_nums(self,div_id,parser,is_main=True):
        r = dict()
        r["310"] = list()
        scores = list()
        history_battle_data_panel = parser.find("div", id=div_id)
        if history_battle_data_panel:
            imgs = history_battle_data_panel.find_all("img")
            for img in imgs:
                r["310"].append(self.get_status_num_style(img["src"]))
            aList = history_battle_data_panel.find_all("a")
            results = self.parse_history_battle_links(aList,10)
            for score in results:
                if len(score)==2:
                    s = dict()
                    if is_main:
                        s["win"] = score[0]
                        s["lost"] = score[1]
                    else:
                        s["win"] = score[1]
                        s["lost"] = score[0]
                    scores.append(s)
                    pass
                pass
        r["scores"] = scores
        return r

    def count_team_battle_balls_io(self,div_id,parser):
        r = dict()
        is_main_team = True
        if div_id == "team_zhanji2_0":
            is_main_team = False
        #主/客场最近10场对战数据
        total_10_balls_io = self.parse_team_battle_balls_io_nums(div_id,parser,is_main_team)
        r["status"] = "".join(total_10_balls_io["310"][0:6])
        #主/客平均进球数
        win_avg = get_zero_div(sum([balls["win"] for balls in total_10_balls_io["scores"]]),10)
        #主/客平均丢球数
        lost_avg = get_zero_div(sum([balls["lost"] for balls in total_10_balls_io["scores"]]),10)

        r["last_10"] = self.count_team_avgballs_section(total_10_balls_io["scores"],win_avg,lost_avg)
        r["last_6"] = self.count_team_avgballs_section(total_10_balls_io["scores"][0:6],win_avg,lost_avg)
        r["last_4"] = self.count_team_avgballs_section(total_10_balls_io["scores"][0:4],win_avg,lost_avg)

        #掐头去尾
        copy = total_10_balls_io["scores"][:]
        mid_win = [w["win"] for w in copy]
        mid_lost = [w["lost"] for w in copy]
        mid_win.sort()
        mid_lost.sort()
        avg = {"win":0.0,"lost":0.0,"percentage":0.0}
        if len(mid_win)>3:
            avg["win"] = sum(mid_win[1:-1])/(len(mid_win)-2)
        if len(mid_lost)>3:
            avg["lost"] = sum(mid_lost[1:-1])/(len(mid_lost)-2)
        avg["percentage"] = get_zero_div(avg["win"],avg["lost"])
        r["last_mid"] = avg
        return r

    #分段计算平均进球数
    def count_team_avgballs_section(self,balls_arr,win_avg,lost_avg):
        avg = dict()
        size = len(balls_arr)
        win = 0.0
        lost = 0.0
        for b in balls_arr:
            w = b["win"]
            l = b["lost"]

            if l==0 and w > 0:
                lost -= 0.5
            if w==l and w > 0:
                win += 0.5
                lost -= 1

            if get_zero_div(w,win_avg) >= 1.5:
                win += win_avg * 1.5
            else:
                win += w
            if get_zero_div(l,lost_avg) >= 1.5:
                lost += lost_avg * 1.5
            else:
                lost += l

        if lost <= 0:
            lost = 0.1

        if size != 0:
            win /= size
            lost /= size

        avg["win"] = round(win,1) #平均进球数
        avg["lost"] = round(lost,1) #平均丢球数
        avg["percentage"] = round(get_zero_div(win,lost),1) #进失球比率
        return avg

    def parse_baseface(self, row, f_name):
        row["last_mix_total_10"] = ""
        row["last_10_text_style"] = ""
        row["last_6_text_style"] = ""
        row["last_4_text_style"] = ""
        row["last_4_status_text_style"] = ""

        #预测赛果之用
        row["formula_total"] = Formula(Formula.TYPE_TOTAL)
        row["formula_last10"] = Formula(Formula.TYPE_LAST10)
        row["formula_last6"] = Formula(Formula.TYPE_LAST6)
        row["formula_last4"] = Formula(Formula.TYPE_LAST4)
        row["formula_last_mid"] = Formula(Formula.TYPE_LAST_MID)

        parser = soup(f_name)
        if not parser:
            return
        row["match_date"] = self.parse_match_date(parser)
        row["asian"] = self.parse_asian_odds(parser)

        ########################进球数比较引擎数据构造块#######################

        #球队主客混合平均进球数
        avg_balls = self.parse_balls_io_total_10(parser)
        if len(avg_balls)==4:
            defence_main=get_zero_div(avg_balls[0],avg_balls[1])
            defence_client=get_zero_div(avg_balls[2],avg_balls[3])

            #本赛季
            row["formula_total"].main_force = avg_balls[0]
            row["formula_total"].client_force = avg_balls[2]
            row["formula_total"].main_defence = defence_main
            row["formula_total"].client_defence = defence_client

            win = "%.1f,%.1f" % (avg_balls[0],defence_main)
            lost = "%.1f,%.1f" % (avg_balls[2],defence_client)
            row["last_mix_total_10"] = "(%s)/(%s)" % (win,lost)

        #分主客区段平均进球数
        main_data = self.count_team_battle_balls_io("team_zhanji2_1",parser)
        client_data = self.count_team_battle_balls_io("team_zhanji2_0",parser)

        #视图数据
        row["last_4_status_text_style"] = "(%s)/(%s)" % ("".join(main_data["status"]),"".join(client_data["status"]))
        row["last_10_text_style"] = "(%.1f,%.1f)/(%.1f,%.1f)" % (main_data["last_10"]["win"],main_data["last_10"]["percentage"],client_data["last_10"]["win"],client_data["last_10"]["percentage"])
        row["last_6_text_style"] = "(%.1f,%.1f)/(%.1f,%.1f)" % (main_data["last_6"]["win"],main_data["last_6"]["percentage"],client_data["last_6"]["win"],client_data["last_6"]["percentage"])
        row["last_4_text_style"] = "(%.1f,%.1f)/(%.1f,%.1f)" % (main_data["last_4"]["win"],main_data["last_4"]["percentage"],client_data["last_4"]["win"],client_data["last_4"]["percentage"])

        #区段比较数据
        for last_n in [10,6,4]:
            formula_key = "formula_last%i" % last_n
            data_key = "last_%i" % last_n
            row[formula_key].main_force = main_data[data_key]["win"]
            row[formula_key].main_defence = main_data[data_key]["percentage"]
            row[formula_key].client_force = client_data[data_key]["win"]
            row[formula_key].client_defence = client_data[data_key]["percentage"]
            pass
        #掐头去尾中间比较数据
        row["formula_last_mid"].main_force = main_data["last_mid"]["win"]
        row["formula_last_mid"].main_defence = main_data["last_mid"]["percentage"]
        row["formula_last_mid"].client_force = client_data["last_mid"]["win"]
        row["formula_last_mid"].client_defence = client_data["last_mid"]["percentage"]
        ########################结束##########################################

    def parse_odds(self, row, f_name):
        row["Odds_WL"] = ""#新增
        row["Odds_AM"] = ""#新增
        row["Odds_LB"] = ""#新增
        row["Odds_365"] = ""#新增
        row["Odds_YSB"] = ""#新增

        row["Odds_WL_Change"] = ""#新增
        row["Odds_AM_Change"] = ""#新增
        row["Odds_LB_Change"] = ""#新增
        row["Odds_365_Change"] = ""#新增
        row["Odds_YSB_Change"] = ""#新增

        parser = soup(f_name)
        if not parser:
            return

        #获取各大菠菜公司的初盘
        tr_ids = ["293","5","2","3","9"]
        odds_open = []
        for tr_id in tr_ids:
            wl_tr = parser.find("tr",id="tr_"+tr_id)
            if wl_tr:
                nums = get_float_numbers(wl_tr.get_text())
                if len(nums) > 3:
                    if tr_id == "293":
                        item = dict()
                        item["com_id"]="293"
                        item["odds_end_datetime"]=wl_tr["data-time"]
                        odds_open.append(item)
                        row["Odds_WL"] = " ".join(nums[0:3])
                    elif tr_id == "5":
                        item = dict()
                        item["com_id"]="5"
                        item["odds_end_datetime"]=wl_tr["data-time"]
                        odds_open.append(item)
                        row["Odds_AM"] = " ".join(nums[0:3])
                    elif tr_id == "2":
                        item = dict()
                        item["com_id"]="2"
                        item["odds_end_datetime"]=wl_tr["data-time"]
                        odds_open.append(item)
                        row["Odds_LB"] = " ".join(nums[0:3])
                    elif tr_id == "3":
                        item = dict()
                        item["com_id"]="3"
                        item["odds_end_datetime"]=wl_tr["data-time"]
                        odds_open.append(item)
                        row["Odds_365"] = " ".join(nums[0:3])
                    elif tr_id == "9":
                        item = dict()
                        item["com_id"]="9"
                        item["odds_end_datetime"]=wl_tr["data-time"]
                        odds_open.append(item)
                        row["Odds_YSB"] = " ".join(nums[0:3])

            wl_tr = parser.find("tr",id="tr2_"+tr_id)
            if wl_tr:
                nums = get_float_numbers(wl_tr.get_text())
                if len(nums) > 3:
                    if tr_id == "293":
                        row["Odds_WL_Change"] = " ".join(nums[0:3])
                    elif tr_id == "5":
                        row["Odds_AM_Change"] = " ".join(nums[0:3])
                    elif tr_id == "2":
                        row["Odds_LB_Change"] = " ".join(nums[0:3])
                    elif tr_id == "3":
                        row["Odds_365_Change"] = " ".join(nums[0:3])
                    elif tr_id == "9":
                        row["Odds_YSB_Change"] = " ".join(nums[0:3])

        row["odds"] = row["Odds_WL"]

    def format_odds_mode(self, win, draw, lost):
        i_w = "%d" % int(win)
        i_d = "%d" % int(draw)
        i_l = "%d" % int(lost)
        return i_w + i_d + i_l

    def parse_balls_io_total_10(self,parser):
        if not parser:
            return []
        div = parser.find("div",id="team_zhanji_1")
        io_balls = []
        if div:
            txt = div.get_text()
            io_balls = self.parse_balls_io(txt)
        div = parser.find("div",id="team_zhanji_0")
        if div:
            txt = div.get_text()
            io_balls += self.parse_balls_io(txt)
        return [(i/10) for i in io_balls]

    def parse_balls_io(self,text):
        p = re.compile("进\\d+球失\\d+球",re.M)
        items = p.findall(text)
        if len(items)>0:
            item = items[0]
            nums = get_int_numbers(item)
            return [int(i) for i in nums]
        return []

    #解析根据Limit数限定的历史战绩比分集合(N:M,..)
    def parse_history_battle_links(self,links,limit=10):
        items = []
        count = 0;
        for a in links:
            if a["href"].find("shuju-") != -1:
                if count == limit:
                    break
                nums = self.parse_history_score(a.get_text())
                items.append(nums)
                count += 1
        return items

    #解析单个历史战绩比分 N:M
    def parse_history_score(self,text):
        p = re.compile("\\d{1,2}:\\d{1,2}",re.M)
        items = p.findall(text)
        if len(items)>0:
            r = items[0]
            nums = get_int_numbers(r)
            return [int(i) for i in nums]
        return list()

    def get_status_num_style(self, src):
        if src.find("h_red.png") != -1:
            return "3"
        elif src.find("m_green.png") != -1:
            return "1"
        elif src.find("l_blue.png") != -1:
            return "0"
        return ""
    
    def parse_match_date(self, parser):
        div = parser.find("div", class_="against_m")
        if div:
            txt = div.get_text();
            p1 = "\\d{4}-\\d{2}-\\d{2}"
            p2 = "\\d{2}:\\d{2}"
            r1 = re.compile(p1)
            r2 = re.compile(p2)
            items = r1.findall(txt) + r2.findall(txt)
            return " ".join(items)
        return ""
    def parse_asian_odds(self,parser):
        div = parser.find("div", class_="against_m")
        if div:
            txt = div.get_text();
            p = "亚盘：.*大小："
            r = re.compile(p,re.M)
            txts = r.findall(txt)
            if len(txts)>0:
                text = txts[0]
                if text:
                    text = trim_all(text.replace("亚盘：","").replace("大小：",""))
                    return asian_rq(text)
            pass
        return ""

    def batch_download_data_pages(self, matchs):
        targetUrls = ["odds_url","base_face_url"]
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            for item in matchs:
                for key in targetUrls:
                    url = item[key]
                    f = get_cache_web_file_name(url)
                    if os.path.exists(f):
                        continue
                    executor.submit(DownloadWebPageTask,url)
            executor.shutdown()
       
    def extract_matchs(self, url):
        urls = []
        soup = web_page_download(url)
        if not soup:
            print("Soup None.")
            return urls
        trNodes = soup.find_all("tr")
        for tr in trNodes:
            match = dict()
            match["match_id"] = ""
            match["result"] = ""
            match["season_url"] = ""
            match["season_name"] = ""
            match["team_names"] = []
            match["base_face_url"] = ""
            match["odds_url"] = ""
            match["actual_result"] = -1
            match["match_date"] = ""
            match["model"] = ""
            match["team_a_ids"]=[]
            match["odds"] = ""
            match["score"] = ""
            match["db_actual_result"] = -1
            match["rq"] = ""
            match["odds_direction"]=""
            match["asian"] = ""
            match["db_asian"] = 0
            tr_text = tr.get_text()
            rq_p = re.compile("[\\+-]\\d", re.M)
            rq_arr = rq_p.findall(tr_text)
            if len(rq_arr)>1 or len(rq_arr)==0:
                rq_arr=["0"]
            match["db_asian"] = int(rq_arr[0])
            rq_style = "".join(rq_arr)
            if rq_style:
                match["rq"] = "(%s)" % rq_style

            if match["rq"] and HtmlParseThread.RQ:
                continue

            linkNodes = tr.find_all("a")
            alive_result = []
            for link in linkNodes:
                hrefAttr = link["href"]
                if hrefAttr.find("seasonindex") != -1:
                    match["season_url"] = hrefAttr
                    match["season_name"] = trim_all(link.string)
                elif hrefAttr.find("teamid") != -1:
                    match["team_a_ids"].append(get_int_numbers(hrefAttr)[1])
                    match["team_names"].append(trim_all(link.get_text()))
                elif hrefAttr.find("500.com/fenxi/shuju") != -1:
                    nums = get_int_numbers(hrefAttr)
                    match["match_id"] = nums[1]
                    match["base_face_url"] = "http://odds.500.com/fenxi/shuju-%s" % nums[1]
                    match["odds_url"] = "http://odds.500.com/fenxi/ouzhi-%s" % nums[1]
                    map_ = self.get_actual_result(link.get_text())
                    match["db_actual_result"] = map_["result"]
                    match["score"] = "[%s]" % map_["exp"]
                    match["actual_result"] = "%i" % map_["result"]
                elif hrefAttr.find("detail.php?fid=") != -1 and link.string:
                    num = get_number(link.get_text())
                    if num != "":
                        alive_result.append(int(num))
            if len(alive_result) == 2:
                r = alive_result[0] - alive_result[1]
                if r > 0:
                    result = 3
                elif r == 0:
                    result = 1
                else:
                    result = 0
                match["db_actual_result"] = result
                match["score"] = "[%i:%i]" % (alive_result[0],alive_result[1])
                match["actual_result"] = "%i" % result

            if match["season_url"] != "" and match["base_face_url"] != "" and match["odds_url"] != "" and len(match["team_names"]) == 2:
                urls.append(match)
        return urls
    
    def get_actual_result(self, text):
        map_ = {"exp":"","result":-1}
        int_list = []
        exp = re.compile("\\d+:\\d+")
        items = exp.findall(text)
        if len(items) > 0:
            map_["exp"] = items[0]
            exp = re.compile("\\d+")
            nums = exp.findall(items[0])
            for num in nums:
                int_list.append(int(num))
        if len(int_list) == 2:
            result = int_list[0] - int_list[1]
            if result > 0:
                map_["result"] = 3
            elif result < 0:
                map_["result"] = 0
            elif result == 0:
                map_["result"] = 1
        return map_
    
class DownloadHistoryMatch(HtmlParseThread):
    START_DATE = ""
    def __init__(self):
        HtmlParseThread.__init__(self);
        pass
    def run(self):
        if DownloadHistoryMatch.START_DATE=="":
            self.backup_data()
            create_history_db()
        mkdirs("cache_web_pages/html")
        send_msg("分析比赛..")
        urls = self.last_days()
        for url in urls:
            #write_file("cache_history_data_startdate.log",day_format)
            self.targetUrl = url#"http://live.500.com/wanchang.php?e=" + day_format
            send_msg("获取赛事链接 " + self.targetUrl)
            matchs = self.extract_matchs(self.targetUrl)
            self.batch_download_data_pages(matchs)
            for match in matchs:
                msg = "分析赔率 %s" % match["odds_url"]
                send_msg(msg)
                self.parse_odds(match, get_cache_web_file_name(match["odds_url"]))
                msg = "分析基本面 %s" % match["base_face_url"]
                send_msg(msg)
                self.parse_baseface(match, get_cache_web_file_name(match["base_face_url"]))
            self.dataset = matchs
            send_msg("cache_history_data");
        send_msg("completed")
        send_msg("完成.")
        
    def last_days(self):
        url = "http://trade.500.com/bjdc/"
        net_soup = web_page_download(url,False)
        urls = set()
        if net_soup:
            html_select_tag = net_soup.find("select",id="expect_select")
            option_tags = html_select_tag.find_all("option")
            for opt in option_tags:
                opt_text = trim_all(opt.get_text())
                if opt_text and opt_text.find("当前期")!=-1:
                    continue
                urls.add("http://trade.500.com/bjdc/?expect=%s" % opt_text)
                pass
            pass
        return urls
    
    def backup_data(self):
        if os.path.exists("_cache"):
            os.rename("_cache", "_cache." + datetime.now().strftime("%Y_%m_%d_%H_%M_%S"))
        pass
# t = DownloadHistoryMatch()
# #print t.last_7_weeks()
# t.backup_data()
