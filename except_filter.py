__author__ = 'tinyms'

class ExceptFilter():

    def __init__(self):
        pass

    def check(self,matchs):
        match_arr = []
        for match in matchs:
            if self.look_down_3_or_0(match):
                match_arr.append(match)
            elif self.top_draw(match):
                match_arr.append(match)
            elif self.wl_lb_odds_mode_diff(match):
                match_arr.append(match)
        return match_arr

    def look_down_3_or_0(self,match):
        if match["result"] == "3" or match["result"] == "0":
            #get odds mode
            arr = match["Odds_WL"].split(" ")
            if len(arr) != 3:
                return False
            try:
                arr = [float(f) for f in arr]
                mode = [int(f) for f in arr]
                mode = list(set(mode))
                if len(mode) == 2 and mode.count(2)==1 and mode.count(3) == 1:
                    return True
            except ValueError:
                print(match["Odds_WL"])
        return False

    def top_draw(self,match):
        if not match["Odds_WL"]:
            return False
        arr = match["Odds_WL"].split(" ")
        arr = [float(f) for f in arr]
        if len(arr) != 3:
            return False
        draw = arr[1]
        dot_part = draw - int(draw)
        if dot_part >= 0.4 and (arr[0]<arr[2]) and match["result"].find("3")!=-1:
            return True
        elif dot_part >= 0.4 and (arr[0]>arr[2]) and match["result"].find("0")!=-1:
            return True
        return False

    def wl_lb_odds_mode_diff(self,match):
        if not match["Odds_WL"] or not match["Odds_WL"]:
            return False
        wl = match["Odds_WL"].split(" ")
        lb = match["Odds_LB"].split(" ")
        if len(wl)!=3 or len(lb)!=3:
            return False
        wl_arr = [float(f) for f in wl]
        lb_arr = [float(f) for f in lb]
        if wl_arr[0] < wl_arr[2]:
            if int(wl_arr[0]) != int(lb_arr[0]):
                return True
        else:
            if int(wl_arr[2]) != int(lb_arr[2]):
                return True
        return False