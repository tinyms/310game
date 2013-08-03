__author__ = 'tinyms'

#format: 01 0.7
def parse():

    f = open("guess.txt")
    all = f.readlines()
    f.close()

    ds = list()
    if not all:
        return ds

    for line in all:
        row = list()
        s1 = line.split(" ")
        if len(s1) >= 2:
            s2 = [s for s in s1[0]]
            s3 = round(float(s1[1]),1)
            row.append(s2)
            row.append(s3)
        if len(row) > 0:
            ds.append(row)
    return ds

def compare_two(a,b):
    size = len(a)
    if size != len(b):
        return -1
    a_arr = [s for s in a]
    b_arr = [s for s in b]
    count = 0
    for i in range(size):
        if a_arr[i] != b_arr[i]:
            count += 1
    return count

def analysis(limit = 32):
    import random,os
    from difflib import SequenceMatcher
    ds = parse()
    for item in ds:
        nums = []
        percent = item[1]
        first = int(limit*percent)
        nums.append(first)
        second = limit - first
        if len(item[0]) == 3:
            three = int(second/2)
            second -= three
            nums.append(second)
            nums.append(three)
        else:
            nums.append(second)

        item.append(nums)

    #first select
    first = []
    for item in ds:
        first.append(item[0][0])
    first = "".join(first)
    print(first)

    results = []
    for item in ds:
        tmp = item[0][0]*item[2][0]
        if len(item[0]) == 2:
            tmp = item[0][0]*item[2][0] + item[0][1]*item[2][1]
        if len(item[0]) == 3:
            tmp = item[0][0]*item[2][0] + item[0][1]*item[2][1] + item[0][2]*item[2][2]
        tmp = [s for s in tmp]
        for i in range(1):
            random.shuffle(tmp)
        results.append(tmp)

    #row and col reversion
    final_result = [[r[col] for r in results] for col in range(len(results[0]))]
    results_text = []
    for fr in final_result:
        results_text.append("".join(fr))

    #check match rate
    match_rate = dict()
    for r in results_text:
        diff = SequenceMatcher(None, first, r)
        ratio = round(diff.ratio(), 2)
        if not match_rate.get(ratio):
            match_rate[ratio] = [r]
        else:
            match_rate[ratio].append(r)

    for k in match_rate.keys():
        print("----------------------------------------")
        print("阀值: %.2f:" % k)
        print("组合:",match_rate[k])
        diff_nums = list()
        for match in match_rate[k]:
            num = compare_two(first,match)
            diff_nums.append(num)
        print("差异:",diff_nums)
        print("----------------------------------------")
    #write to file.
    results_text.insert(0,first)
    f_name = "results.txt"
    if os.path.exists(f_name):
        os.remove(f_name)
    f = open(f_name,"w+")
    for line in results_text:
        f.write(line+",\n")
    f.close()

analysis(limit=16)

