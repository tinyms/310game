__author__ = 'tinyms'

import concurrent.futures


def generate(guess_results, similar_rate=[0.8], limit=32):
    if len(similar_rate) == 0:
        similar_rate = [0.8]
    items = [s.strip(" ") for s in guess_results.split(",")]
    import itertools, random
    from difflib import SequenceMatcher

    a = list(itertools.product(*items))

    first = "".join(a[0])
    unorder_results = dict()
    for r in a:
        target = "".join(r)
        diff = SequenceMatcher(None, first, target)
        ratio = round(diff.ratio(), 1)
        if not unorder_results.get(ratio):
            unorder_results[ratio] = [r]
        else:
            unorder_results[ratio].append(r)

    summary = dict()
    for k in unorder_results.keys():
        summary[k] = len(unorder_results[k])

    end = list()
    for rate in similar_rate:
        order_val = unorder_results.get(rate)
        if order_val:
            end += order_val

    random.shuffle(end)
    end.insert(0,a[0])
    #z = random.sample(end, 32)

    #_analysis(end, z, items)

    result = dict()
    result["summary"] = summary
    if limit == 0:
        limit = 32
    normal = end[:limit]
    result["result"] = normal
    result["balance"] = _random_results_balance(normal)
    print(result["balance"])
    end_text_style = []
    for end_text in normal:
        end_text_style.append("".join(end_text))
    result["result_text_style"] = end_text_style

    return result

def _random_results_balance(normal_result_arr):
    rcv = [[r[col] for r in normal_result_arr] for col in range(len(normal_result_arr[0]))]
    items = []
    for r in rcv:
        items.append("".join(r))
    counters = []
    for item in items:
        counter = {}
        for c in item:
            if c in counter:
                counter[c] += 1
            else:
                counter[c] = 1
        fmt = "('%s',%i)"
        tmp = sorted([(v,k) for v,k in counter.items()],reverse=True)
        tmp_texts = ""
        for t in tmp:
            tmp_texts += "('%s',%i)" % (t[0],t[1])
        counters.append(tmp_texts)
    return counters

#samples=>随机抓取的组合数组,results=>人选择的可能赛果数组
def _analysis(all, samples, results):
    import os
    path  = "e:/results.txt"
    if os.path.exists(path):
        os.remove(path)
    import random

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        thread_stop = list()
        for c in range(100000):
            #行列转换,准备校验
            if len(thread_stop) > 0:
                break
            z = random.sample(all, 32)
            first = "".join(z[0])
            chg_a = [[r[col] for r in z] for col in range(len(z[0]))]
            executor.submit(_valid, results, chg_a, z, thread_stop, first)
        print("Wait for download completed.")
        executor.shutdown()


def _valid(results, samples, samples_normal, thread_stop, first):
    if len(thread_stop) > 0:
        return
    rows = len(samples)
    diff = int(rows / 4)
    valid_b = list()
    for p in range(rows):
        c_arr = [s for s in results[p]]
        if len(c_arr) >= 2:
            c_arr_tmp = c_arr[:2]
            b = _count(samples[p], c_arr_tmp, diff)
            valid_b.append(b)
            pass
        pass

    if valid_b.count(False) <= 2:
        import os
        path = "e:/results.txt"
        if not os.path.exists(path):
            #write
            f = open(path, "a+")
            f.write(first+"\n")
            for normal in samples_normal:
                line = "".join(normal)+"\n"
                f.write(line)
            f.close()
            thread_stop.append(True)
        return True
    return False

# [3,3,3,3,4,4,4] [3,4]
def _count(rows, c_strs, diff):
    limit = int(len(rows)/3)+1
    nums = list()
    for c in c_strs:
        a = rows.count(c);
        if a >= limit:
            nums.append(True)
    if nums.count(True) == 2:
        return True
    return False


# from tkinter import *
#
#
# class App(Frame):
#     def __init__(self, master=None):
#         Frame.__init__(self, master)
#         self.pack()


# # create the application
# myapp = App()
#
# #
# # here are method calls to the window manager class
# #
# myapp.master.title("My Do-Nothing Application")
# myapp.master.maxsize(600, 450)
#
# # start the program
#
# arr = list()
# arr.append('31')
# arr.append('30')
# arr.append('31')
# arr.append('13')
# arr.append('31')
# arr.append('31')
# arr.append('01')
# arr.append('10')
# arr.append('31')
# arr.append('31')
# arr.append('10')
# arr.append('13')
# arr.append('3')
# arr.append('13')
#
# generate(",".join(arr))
#
# myapp.mainloop()