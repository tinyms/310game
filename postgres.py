__author__ = 'tinyms'

import re
import psycopg2
import psycopg2.extras

def pg_open():
    return psycopg2.connect(database="postgres",user="postgres",password="1")

def to_floats(odds_text):
    if not odds_text:
        return list()
    return [round(float(f),2) for f in odds_text.split(" ")]

def wl_lb_match_history_cache(matchs):
    rows = []
    for row in matchs:
        if row["db_actual_result"] == -1:
            continue
        if not row["Odds_WL"] or not row["Odds_LB"]:
            continue
        detect_result(row)
        arr = list()
        arr.append(row["score"])
        arr.append(row["db_actual_result"])
        arr.append(row["result"])
        arr.append(round(float(row["asia_avg_balls"]),2))
        arr.append(" VS ".join(row["team_names"]))
        arr.append(row["last_10_text_style"])
        arr.append(row["last_6_text_style"])
        arr.append(row["last_4_text_style"])
        arr.append(row["last_4_status_text_style"])
        arr.append(to_floats(row["Odds_WL"]))
        arr.append(to_floats(row["Odds_LB"]))
        arr.append(to_floats(row["Odds_AM"]))
        arr.append(to_floats(row["Odds_365"]))
        arr.append(to_floats(row["Odds_YSB"]))
        arr.append(to_floats(row["Odds_WL_Change"]))
        arr.append(to_floats(row["Odds_LB_Change"]))
        arr.append(to_floats(row["Odds_AM_Change"]))
        arr.append(to_floats(row["Odds_365_Change"]))
        arr.append(to_floats(row["Odds_YSB_Change"]))
        wl_lb = diff_wl_lb_first_odds(row["Odds_WL"], row["Odds_LB"])
        arr.append(wl_lb["flag"])
        arr.append(wl_lb["diff"])
        arr.append(row["season_name"])
        arr.append(row["match_id"])
        arr.append(row["match_date"])
        rows.append(arr)


    sql = """
            INSERT INTO matchs(score,actual_result,detect_result,balls_diff,vs_team_names,last_10,last_6,last_4,last_battle,
            odds_wl,odds_lb,odds_am,odds_beta,odds_ysb,odds_wl_c,odds_lb_c,odds_am_c,odds_beta_c,odds_ysb_c,wl_lb_flag,wl_lb_diff,
            evt_name,url_key,vs_date)VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """

    cnn = pg_open()
    cur = cnn.cursor()
    try:
        cur.executemany(sql,rows)
        cnn.commit()
        pass
    finally:
        cnn.close()

def query_history_matchs(d_result,flag,match_result,odds_direction,odds_int_num):

    #odds_direction
    where_extra = ""
    if match_result != "310":
        where_extra += " AND actual_result = %s " % match_result

    if odds_direction != "-1":
        int_space = get_number(odds_int_num,0)
        if odds_direction == "3":
            where_extra += " AND odds_wl[1] < odds_wl[3] "
            if int_space >= 1:
                where_extra += " AND (odds_wl[1]>=%.2f AND odds_wl[1]<=%i)" % (int_space,int(int_space+1))
        elif odds_direction == "0":
            where_extra += " AND odds_wl[1] > odds_wl[3] "
            if int_space >= 1:
                where_extra += " AND (odds_wl[3]>=%.2f AND odds_wl[3]<=%i)" % (int_space,int(int_space+1))
        elif odds_direction == "1":
            where_extra += " AND odds_wl[1] = odds_wl[3] "

    count_sql = "SELECT COUNT(1) FROM matchs WHERE detect_result = %s AND wl_lb_flag = %s "+where_extra
    sql = "SELECT * FROM matchs WHERE detect_result = %s AND wl_lb_flag = %s "+where_extra+" ORDER BY random() LIMIT 25";
    print(sql)
    result = dict()
    matchs = list()
    try:
        cnn = pg_open()
        cur = cnn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute(count_sql,(d_result,flag))
        total = cur.fetchone()
        print(total)
        cur.execute(sql,(d_result,flag))
        rows = cur.fetchall()
        for row in rows:
            match = dict()
            match["id"] = row["id"]
            match["score"] = row["score"]
            match["actual_result"] = row["actual_result"]
            match["detect_result"] = row["detect_result"]
            match["balls_diff"] = round(float(row["balls_diff"]),2)
            match["vs_team_names"] = row["vs_team_names"]
            match["last_10"] = row["last_10"]
            match["last_6"] = row["last_6"]
            match["last_4"] = row["last_4"]
            match["last_battle"] = row["last_battle"]
            match["odds_wl"] = decimals_to_floats(row["odds_wl"])
            match["odds_lb"] = decimals_to_floats(row["odds_lb"])
            match["odds_am"] = decimals_to_floats(row["odds_am"])
            match["odds_beta"] = decimals_to_floats(row["odds_beta"])
            match["odds_ysb"] = decimals_to_floats(row["odds_ysb"])
            match["odds_wl_c"] = decimals_to_floats(row["odds_wl_c"])
            match["odds_lb_c"] = decimals_to_floats(row["odds_lb_c"])
            match["odds_am_c"] = decimals_to_floats(row["odds_am_c"])
            match["odds_beta_c"] = decimals_to_floats(row["odds_beta_c"])
            match["odds_ysb_c"] = decimals_to_floats(row["odds_ysb_c"])
            match["wl_lb_flag"] = row["wl_lb_flag"]
            match["wl_lb_diff"] = decimals_to_floats(row["wl_lb_diff"])
            match["evt_name"] = row["evt_name"]
            match["url_key"] = row["url_key"]
            match["vs_date"] = row["vs_date"]
            matchs.append(match)
    finally:
        cnn.close()
    result["items"] = matchs
    result["total"] = total
    return result

def get_number(text,default_ = 0):
    if not text:
        return default_
    p = re.compile("\\d+[\\.]?\\d+")
    nums = p.findall(text)
    if len(nums)>0:
        return float(nums[0])
    return default_

def decimals_to_floats(arr):
    return [round(float(d),2) for d in arr]

def diff_wl_lb_first_odds(wl, lb):
    rt = {"flag": "", "diff": ""}
    if not wl or not lb:
        return rt
    wl_nums = [round(float(i), 2) for i in wl.split(" ")]
    lb_nums = [round(float(i), 2) for i in lb.split(" ")]
    #N,H,L => NoChange,High,Low
    if lb_nums[0] - wl_nums[0] > 0:
        rt["flag"] = "H"
    elif lb_nums[0] - wl_nums[0] < 0:
        rt["flag"] = "L"
    elif lb_nums[0] - wl_nums[0] == 0:
        rt["flag"] = "N"

    if lb_nums[1] - wl_nums[1] > 0:
        rt["flag"] += "H"
    elif lb_nums[1] - wl_nums[1] < 0:
        rt["flag"] += "L"
    elif lb_nums[1] - wl_nums[1] == 0:
        rt["flag"] += "N"

    if lb_nums[2] - wl_nums[2] > 0:
        rt["flag"] += "H"
    elif lb_nums[2] - wl_nums[2] < 0:
        rt["flag"] += "L"
    elif lb_nums[2] - wl_nums[2] == 0:
        rt["flag"] += "N"

    items = list()
    items.append(round(lb_nums[0] - wl_nums[0],2))
    items.append(round(lb_nums[1] - wl_nums[1],2))
    items.append(round(lb_nums[2] - wl_nums[2],2))

    rt["diff"] = items

    return rt

def detect_result(match):
    scores = []
    scores += match["formula_last10"].to_results()
    scores += match["formula_last6"].to_results()
    scores += match["formula_last4"].to_results()
    avg_balls = (match["formula_last10"].avg_balls + match["formula_last6"].avg_balls + match[
        "formula_last4"].avg_balls) / 3
    num = round(avg_balls, 2)
    match["asia_avg_balls"] = "%.2f" % num
    diff = abs(num)
    if diff >= 0 and diff <= 0.25:
        match["result"] = "1"
    elif diff > 0.25 and diff < 0.75:
        if num > 0:
            match["result"] = "31"
        else:
            match["result"] = "10"
    elif diff >= 0.75:
        if num > 0:
            match["result"] = "3"
        else:
            match["result"] = "0"