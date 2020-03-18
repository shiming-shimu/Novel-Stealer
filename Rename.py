import os

digit = {'一': 1, '二': 2, '两' : 2 , '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9}

def _trans(s):
    num = 0
    if s:
        idx_q, idx_b, idx_s = s.find('千'), s.find('百'), s.find('十')
        if idx_q != -1:
            num += digit[s[idx_q - 1:idx_q]] * 1000
        if idx_b != -1:
            num += digit[s[idx_b - 1:idx_b]] * 100
        if idx_s != -1:
            # 十前忽略一的处理
            num += digit.get(s[idx_s - 1:idx_s], 1) * 10
        if s[-1] in digit:
            num += digit[s[-1]]
    return num

def trans(chn):
    chn = chn.replace('零', '')
    idx_y, idx_w = chn.rfind('亿'), chn.rfind('万')
    if idx_w < idx_y:
        idx_w = -1
    num_y, num_w = 100000000, 10000
    if idx_y != -1 and idx_w != -1:
        return trans(chn[:idx_y]) * num_y + _trans(chn[idx_y + 1:idx_w]) * num_w + _trans(chn[idx_w + 1:])
    elif idx_y != -1:
        return trans(chn[:idx_y]) * num_y + _trans(chn[idx_y + 1:])
    elif idx_w != -1:
        return _trans(chn[:idx_w]) * num_w + _trans(chn[idx_w + 1:])
    return _trans(chn)

def name(oldname):
    a = oldname.find('第')
    b = oldname.find('章')
    if b == -1:
        b = oldname.find('级')
    newname = oldname[:a+1] + str(trans(oldname[a+1:b])) +'章'
    return newname

def main():
    dirlist = os.listdir('./text')
    namelist = []
    for i in dirlist:
        namelist.append(i)
        os.rename('./text/'+i,name(i))
