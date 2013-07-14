from odds_statistics import Odds_Statistics
import re
class Result(object):
    def __init__(self,scores,odds):
        super(Result, self).__init__()
        self._scores = scores
        self.odds_ = odds

    def detect_odds(self):
        if self.odds_:
            o310 = self.odds_.split(" ");
            o310 = [float(f) for f in o310 ]
            if len(o310) == 3:
                r = dict()
                r[o310[0]] = "3"
                r[o310[1]] = "1"
                r[o310[2]] = "0"
                return r[min(o310)]
                pass
            pass
        return ""

    def detect(self,last4):
        r = list()
        com_odds_result = self.detect_odds()
        #r.add(com_odds_result)
        num_3 = self._scores.count(3)
        num_1 = self._scores.count(1)
        num_0 = self._scores.count(0)

        total_3 = num_3 + num_1
        total_0 = num_0 + num_1
        total_3_0 = num_3 + num_0

        if total_3 > total_0:
            r.append("3")
        elif total_3 < total_0:
            r.append("0")
        if num_1 > total_3_0:
            r.clear()
            r.append("1")

        # if r.count("1")==0:
        #     if com_odds_result == "3":
        #         if last4.client_defence>=0.8:
        #             r.append("1")
        #     elif com_odds_result == "0":
        #         if last4.main_defence >= 0.8:
        #             r.append("1")

        # if r.count("3")==0:
        #     if (last4.main_force >= last4.client_force) and (last4.main_defence > last4.client_defence) :
        #         r.append("3")
        #
        # if r.count("0")==0:
        #     if (last4.main_force <= last4.client_force) and (last4.main_defence < last4.client_defence):
        #         r.append("0")

        program_result = "".join(r)
        # if program_result.find(com_odds_result)==-1:
        #     program_result = com_odds_result+program_result
        return program_result
    
class Formula(object):
    TYPE_TOTAL = "total"
    TYPE_LAST10 = "last10"
    TYPE_LAST6 = "last6"
    TYPE_LAST4 = "last4"
    TYPE_LAST_MID = "last_mid"
    def __init__(self, type_=TYPE_TOTAL):
        super(Formula, self).__init__()
        self._type = type_
        self._results = []
        self.main_force = 0.0 #攻击
        self.main_defence = 0.0 #防御
        self.client_force = 0.0
        self.client_defence = 0.0
    def type_(self):
        return self._type
    def to_results(self):
        self.count_force(self.main_force,self.client_force)
        #self.count_defence(self.main_defence,self.client_defence)
        return self._results

    def count_force(self,main,client,fact=0.75):
        diff = main-client
        if diff >= fact and main > 1:
            self._results.append(3)
        elif diff <= -1*fact and client > 1:
            self._results.append(0)
        else:
            self._results.append(1)

    def count_defence(self,main,client,fact=0.5):
        if main > 1 and client > 1:
            self._results.append(1)
            return
        diff = main-client
        if diff >= fact:
            self._results.append(3)
        elif diff <= -1*fact:
            self._results.append(0)
        else:
            self._results.append(1)

def get_float_numbers_(text):
    p = re.compile("\\d+\\.\\d+",re.M)
    return p.findall(text)

def get_int_numbers_(text):
    p = re.compile("\\d+",re.M)
    strs = p.findall(text)
    return [int(i) for i in strs]

def odds_detect_exclude_one_result(row):
    results = [s for s in row["result"]]
    detect_result = results
    statis = Odds_Statistics()

    wl = row["Odds_WL"]
    wl_c = row["Odds_WL_Change"]
    wl_diff = statis.single_company(wl,wl_c)

    am = row["Odds_AM"]
    am_c = row["Odds_AM_Change"]
    am_diff = statis.single_company(am,am_c)

    lb = row["Odds_LB"]
    lb_c = row["Odds_LB_Change"]
    lb_diff = statis.single_company(lb,lb_c)

    ysb = row["Odds_YSB"]
    ysb_c = row["Odds_YSB_Change"]
    ysb_diff = statis.single_company(ysb,ysb_c)

    o365 = row["Odds_365"]
    o365_c = row["Odds_365_Change"]
    o365_diff = statis.single_company(o365,o365_c)

    start_odds = list()
    end_odds = list()
    diff_odds = list()
    diff_mode = list()

    start_modes = set()
    #end_modes = set();

    if wl:
        arr = [float(i) for i in wl.split(" ")]
        mode_int = [int(f) for f in arr]
        start_odds.append(arr)
        start_modes.add("%i%i%i" % (mode_int[0],mode_int[1],mode_int[2]))
    if am:
        arr = [float(i) for i in am.split(" ")]
        mode_int = [int(f) for f in arr]
        start_odds.append(arr)
        start_modes.add("%i%i%i" % (mode_int[0],mode_int[1],mode_int[2]))
    if lb:
        arr = [float(i) for i in lb.split(" ")]
        mode_int = [int(f) for f in arr]
        start_odds.append(arr)
        start_modes.add("%i%i%i" % (mode_int[0],mode_int[1],mode_int[2]))
    if ysb:
        arr = [float(i) for i in ysb.split(" ")]
        mode_int = [int(f) for f in arr]
        start_odds.append(arr)
        start_modes.add("%i%i%i" % (mode_int[0],mode_int[1],mode_int[2]))
    if o365:
        arr = [float(i) for i in o365.split(" ")]
        mode_int = [int(f) for f in arr]
        start_odds.append(arr)
        start_modes.add("%i%i%i" % (mode_int[0],mode_int[1],mode_int[2]))

    print(start_modes)

    if wl_c:
        end_odds.append([float(i) for i in wl_c.split(" ")])
    if am_c:
        end_odds.append([float(i) for i in am_c.split(" ")])
    if lb_c:
        end_odds.append([float(i) for i in lb_c.split(" ")])
    if ysb_c:
        end_odds.append([float(i) for i in ysb_c.split(" ")])
    if o365_c:
        end_odds.append([float(i) for i in o365_c.split(" ")])

    if wl_diff:
        diff_odds.append([float(i) for i in get_float_numbers_(wl_diff["odds_diff"])])
    if am_diff:
        diff_odds.append([float(i) for i in get_float_numbers_(am_diff["odds_diff"])])
    if lb_diff:
        diff_odds.append([float(i) for i in get_float_numbers_(lb_diff["odds_diff"])])
    if ysb_diff:
        diff_odds.append([float(i) for i in get_float_numbers_(ysb_diff["odds_diff"])])
    if o365_diff:
        diff_odds.append([float(i) for i in get_float_numbers_(o365_diff["odds_diff"])])

    #模式变化
    if wl_diff["model_diff"].find("to")!=-1:
        wl_mode_change = get_int_numbers_(wl_diff["model_diff"])
        if len(wl_mode_change)==2:
            diff_mode.append((wl_mode_change[0]-wl_mode_change[1])>0)
    if am_diff["model_diff"].find("to")!=-1:
        am_mode_change = get_int_numbers_(am_diff["model_diff"])
        if len(am_mode_change)==2:
            diff_mode.append((am_mode_change[0]-am_mode_change[1])>0)
    if lb_diff["model_diff"].find("to")!=-1:
        lb_mode_change = get_int_numbers_(lb_diff["model_diff"])
        if len(lb_mode_change)==2:
            diff_mode.append((lb_mode_change[0]-lb_mode_change[1])>0)
    if ysb_diff["model_diff"].find("to")!=-1:
        ysb_mode_change = get_int_numbers_(ysb_diff["model_diff"])
        if len(ysb_mode_change)==2:
            diff_mode.append((ysb_mode_change[0]-ysb_mode_change[1])>0)
    if o365_diff["model_diff"].find("to")!=-1:
        o365_mode_change = get_int_numbers_(o365_diff["model_diff"])
        if len(o365_mode_change)==2:
            diff_mode.append((o365_mode_change[0]-o365_mode_change[1])>0)

    odds_model_change_com_nums = len(diff_mode)
    if odds_model_change_com_nums>=2:
        if diff_mode.count(False)==odds_model_change_com_nums:
            if detect_result.count("0")==1:
                detect_result.remove("0")
        elif diff_mode.count(True)==odds_model_change_com_nums:
            if detect_result.count("3")==1:
                detect_result.remove("3")

        print(diff_mode)
        pass

    #初赔平赔差异
    start_draws = [i[1] for i in start_odds]
    start_draw_max = max(start_draws)
    start_draw_min = min(start_draws)
    if len(start_draws)>0 and (round(start_draw_max - start_draw_min,2))>=0.29:
        if detect_result.count("1")==1:
            detect_result.remove("1")
        pass

    #变赔平赔差异
    # end_draws = [i[1] for i in end_odds]
    # end_draw_max = max(end_draws)
    # end_draw_min = min(end_draws)
    # if len(end_draws)>0 and (round(end_draw_max - end_draw_min,2))>=0.29:
    #     if detect_result.count("1")==1:
    #         detect_result.remove("1")
    #     pass

    #初盘庄家的看法
    if len(start_modes)>=3 and detect_result.count("1")==0:
        detect_result.append("1")

    #合并探测结果
    r_tmp = " (%s)" % ("".join(detect_result))
    #row["result"] += r_tmp
    pass