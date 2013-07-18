__author__ = 'tinyms'

import postgresql

def pg_open():
    db = postgresql.open("pq://postgres:1@localhost/postgres")
    p = db.prepare("select * from matchs")
    with db.xact():
        for row in p():
            print(row)
    pass

def history_cache(dataset):
    sql = """
        INSERT INTO matchs(score,actual_result,detect_result,balls_diff,vs_team_names,last_10,last_6,last_4,last_battle,
        odds_wl,odds_lb,odds_am,odds_beta,odds_ysb,odds_wl_c,odds_lb_c,odds_am_c,odds_beta_c,odds_ysb_c,wl_lb_flag,wl_lb_diff,
        evt_name,url_key,vs_date)VALUES($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13,$14,$15,$16,$17,$18,$19,$20,$21,$22,$23,$24)
    """
    db = pg_open()
    create_matchs = db.prepare(sql)
    with db.xact():
        for row in dataset:
            create_matchs(row)
    pass