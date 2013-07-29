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

def analysis(limit = 32):
    import random,os
    ds = parse()
    print(ds)
    for item in ds:
        nums = []
        percent = item[1]
        first = int(limit*percent)
        nums.append(first)
        second = limit - first
        #print(second)
        if len(item[0]) == 3:
            three = int(second/2)
            second -= three
            nums.append(second)
            nums.append(three)
        else:
            nums.append(second)

        item.append(nums)
    print(ds)
    results = []
    for item in ds:
        tmp = item[0][0]*item[2][0] + item[0][1]*item[2][1]
        if len(item[0]) == 3:
            tmp = item[0][0]*item[2][0] + item[0][1]*item[2][1] + item[0][2]*item[2][2]
        tmp = [s for s in tmp]
        for i in range(2):
            random.shuffle(tmp)
        results.append(tmp)
        print(tmp)
    #convert
    final_result = [[r[col] for r in results] for col in range(len(results[0]))]
    results_text = []
    for fr in final_result:
        results_text.append("".join(fr))
        print("".join(fr))

    f_name = "results.txt"
    if os.path.exists(f_name):
        os.remove(f_name)
    f = open(f_name,"w+")
    for line in results_text:
        f.write(line+",\n")
    f.close()
analysis()

