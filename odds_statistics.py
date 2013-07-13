__author__ = 'TinyMS'

class Odds_Statistics():
    def __init__(self):
        pass

    def single_company(self,start_odds,end_odds):
        changes = dict()
        changes["odds_diff"] = ""
        changes["model_diff"] = ""
        if not start_odds:
            return changes
        start_float_arr = [float(d) for d in start_odds.split(" ")];
        if end_odds:
            end_float_arr = [float(d) for d in end_odds.split(" ")];

            win_diff = end_float_arr[0] - start_float_arr[0]
            if win_diff>0:
                win = "<font color='red'>+%.2f</font>" % win_diff
            elif win_diff<0:
                win = "<font color='green'>%.2f</font>" % win_diff
            else:
                win = "<font color='#000000'>0.00</font>"

            draw_diff = end_float_arr[1] - start_float_arr[1]
            if draw_diff>0:
                draw = "<font color='red'>+%.2f</font>" % draw_diff
            elif draw_diff<0:
                draw = "<font color='green'>%.2f</font>" % draw_diff
            else:
                draw = "<font color='#000000'>0.00</font>"

            lost_diff = end_float_arr[2] - start_float_arr[2]
            if lost_diff>0:
                lost = "<font color='red'>+%.2f</font>" % lost_diff
            elif lost_diff<0:
                lost = "<font color='green'>%.2f</font>" % lost_diff
            else:
                lost = "<font color='#000000'>0.00</font>"

            changes["odds_diff"] = "%s %s %s" % (win,draw,lost)

            #Model
            start_int_arr = [str(int(d)) for d in start_float_arr];
            end_int_arr = [str(int(d)) for d in end_float_arr];
            odds_start_model = "".join(start_int_arr)
            odds_end_model = "".join(end_int_arr)
            if odds_start_model!=odds_end_model:
                changes["model_diff"] = "模式改变(%s to %s)" % (odds_start_model,odds_end_model)

        return changes