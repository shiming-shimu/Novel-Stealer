import urllib  
import urllib.request
import urllib.parse
import string
import re
from os import _exit
import os
import tkinter
import time
import tkinter.messagebox
import multiprocessing
import json
from PIL import Image, ImageTk 
import Rename
import ctypes
user32 = ctypes.windll.LoadLibrary('user32.dll')

#-------------------globalVar----------------------------
menu = []
#------------------------head----------------------------
def urlOpen (url) : #打开网站函数
    headers = {'User-Agent':'Mozilla/5.0 (iPhone; CPU iPhone OS 7_1_2 like Mac OS X) App leWebKit/537.51.2 (KHTML, like Gecko) Version/7.0 Mobile/11D257 Safari/9537.53'}
    url = urllib.request.Request(url = url,headers=headers)
    try:
        response = urllib.request.urlopen(url,timeout=15) 
    except:
        print("网址打开失败。。。")
        return None
    try:
        a = response.read().decode("utf-8")
    except:
        try:
            a = response.read().decode("GB18030")
        except:
            a = response.read().decode("GBK")
    return a #返回爬取的网站


def search (reg,web) : #搜索书籍信息
    Findlist = re.findall(str(reg),str(web))
    return Findlist

def readJson () : #读取json来获取源
    global sets,apts
    for js in os.listdir("apt"):
        with open("apt/"+js) as f:
            apts[js[:len(js)-5]] = json.loads(f.read())
    with open("set.json") as f:
        sets = json.loads(f.read())

def downLoad (urllist,name) : #下载书籍
    global pool
    nurllist = []
    num = int(len(urllist)/20)
    other = len(urllist)%20
    for i in range(0,20):
        if i < other:
            nurllist.append(list(urllist[i*(num+1):(num+1)*(i+1)]))
        else:
            nurllist.append(list(urllist[i*num+other:(i+1)*num+other]))
    for work in range(len(nurllist)):
        pool.apply_async(func=page,args=(nurllist[work],work,name,sets))


def page (work,id,name,sets):
    for i in work:
        page1 = urlOpen(apts[aptn]["url"]+i)
        title = re.findall(apts[aptn]["title"],page1)[0]
        file =  "DownLoad/" + name + "/page/" + Rename.name(title) + ".htm"
        if os.path.exists(str(file)) == False:
            try:
                body = re.findall(apts[aptn]["chapter"],page1)
                with open(file,"w",encoding='utf-8') as f:
                    f.write("<head>\n<title>"+title+"</title>\n<style>\np1{font-size:"+str(sets["size"])+"px}h1{font-size:40}\n</style>\n</head>\n<body>\n<h1>\n"+title+"</h1>\n<br /><br />\n<p1 id='p1'>\n<br />"+body[0][0] if type(body[0])==list() or type(body[0])==tuple() else body[0]+"\n</p1>\n</body>")
            except:
                if sets["info"]:
                    user32.MessageBoxA(0, str.encode(file + "出错，已自动跳过").decode('utf8').encode('GBK'), str.encode('提示').decode('utf8').encode('GBK'), 0)
        else:
            if sets["info"]:
                user32.MessageBoxA(0, str.encode("检测到1个章节已存在于" + file +"，已跳过").decode('utf8').encode('GBK'), str.encode('提示').decode('utf8').encode('GBK'), 0)



def load(name) : #加载动画
    page1 = urlOpen(apts[aptn]["surl"]+(urllib.parse.quote(name)))
    booklist = search(apts[aptn]["book"],page1)
    return booklist

#------------------------body----------------------------
def main () : #主界面
    global menu
    for i in menu:
        i.destroy()
    menu = []
    menu.append(tkinter.Button(image=image_search,width=256,height=256,command=searchBook))
    menu[0].place(x=160,y=160,anchor=tkinter.CENTER)

def searchBook () : #搜索书籍界面
    global menu
    for i in menu:
        i.destroy()
    menu = []
    menu.append(tkinter.Entry(width=32,textvariable=tkinter.StringVar(value='请输入书名')))
    menu.append(tkinter.Button(image=image_searchs,width=16,height=16,command=lambda : chooseBook(menu[0].get())))
    menu.append(tkinter.Button(text="取消",command=main))
    menu[0].place(x=150,y=160,anchor=tkinter.CENTER)
    menu[1].place(x=278,y=160,anchor=tkinter.CENTER)
    menu[2].place(x=16,y=300,anchor=tkinter.CENTER)
def chooseBook (name) : #选择书本界面
    global menu
    for i in menu:
        i.destroy()
    menu = []
    tkinter.messagebox.showinfo("提示","正在爬取网页，请稍后")
    booklist = load(name)
    menu.append(tkinter.Button(text="返回",command=searchBook))
    for book in booklist:
        menu.append(tkinter.Button(height=1,width=20,text=book[1],command=lambda name=book[1],url=book[0]: waitDown(name,url)))
    menu[0].place(x=16,y=300,anchor=tkinter.CENTER)
    for B in range(0,len(booklist)):
        if B != 0 and B<=20:
            menu[B].place(x=80 if B%2==1 else 240,y=25*(int(B/2)+B%2),anchor=tkinter.CENTER)
        

def waitDown (name,url) : #等待下载界面
    global menu
    for i in menu:
        i.destroy()
    menu = []
    os.makedirs("DownLoad/"+name) if not os.path.exists("DownLoad/"+name) else None
    os.makedirs("DownLoad/"+name+"/page") if not os.path.exists("DownLoad/"+name+"/page") else None
    pagelist = search(apts[aptn]["pageUrl"],urlOpen(apts[aptn]["url"]+url))
    downLoad(pagelist,name)
    menu.append(tkinter.Message(text="正在努力下载请稍后。。。"))
    menu[0].pack()
    menu.append(tkinter.Button(text="取消",command=pool.terminate))
    menu[1].pack()
    pool.join()
    doneDone(name)

def doneDone (name) : #下载完成界面
    global menu
    for i in menu:
        i.destroy()
    menu = []
    pageName = []
    for i in os.listdir("DownLoad/%s/"%name):
        pageName.append(i[:len(i)-4])
    with open("DownLoad/%s/目录.htm"%name,"w") as f:
        f.write("<!DOCTYPE html>\n<head>\n<style>\ntitle {text-align: center;font-size: large;};\n</style>\n</head>\n<body>\n<title>%s</title>\n"%(name))
        for i in pageName:
            f.write("\n<a href=\"%s\">%s</a>"%(i,"DownLoad/page/"+i+".htm"))
        f.write("\n</body>")
    menu.append(tkinter.Message(text="下载完成。。。"))
    menu.append(tkinter.Message(text="已保存至源文件目录下的DownLoad/%s/page下"%name))
    menu[0].pack()
    menu[1].pack()
#------------------------class----------------------------
class bar () : #操作条
    def __init__(self, w):
        self.bar = tkinter.Menu(w)#主操作条
        self.set = tkinter.Menu(self.bar)#设置
        self.apt = tkinter.Menu(self.bar)#换源
        self.help = tkinter.Menu(self.bar)#帮助
        #设置菜单内容
        self.set.add_command(label="是否显示提示",command=lambda :self.Set("info"))
        self.set.add_command(label="设置字体大小",command=self.setSize)
        #end
        #换源菜单内容
        for apt in apts:
            self.apt.add_command(label=apt,command=lambda : self.chanceApt(apt))
        #end
        #帮助菜单内容
        self.help.add_command(label="怎么爬取小说",command=lambda :tkinter.messagebox.showinfo("提示","按照下方的提示一步一步输入，就可以获得你的小说了"))
        self.help.add_command(label="怎么创建目录及注意事项",command=lambda :tkinter.messagebox.showinfo("提示","在小工具>创建目录，输入你爬取的小说所在的文件夹\nps:目录指的是软件的同目录下的文件夹的名称 \n再ps:有浏览器打开目录文件后可以按Ctrl+F查找章节"))
        self.help.add_command(label="更新计划",command=lambda :tkinter.messagebox.showinfo("提示","目前的小说源只有一个，且缺了很多小说，下一个更新版本将加入另一个小说源"))
        self.help.add_separator()
        self.help.add_command(label="@copyright",command=lambda :tkinter.messagebox.showwarning("警告","不要随意在网络上传播，这只是一个盗版盗版的脚本软件，是违法的。\n若没有大范围传播，就不是违法的。"))
        #end
        #添加进入主操作条
        self.bar.add_cascade(label="设置", menu=self.set)
        self.bar.add_cascade(label="换源", menu=self.apt)
        self.bar.add_cascade(label="帮助", menu=self.help)
    def chanceApt (self,apt) : #换源
        global aptn, sets
        aptn = apt
        sets["apt"] = apt
        with open("set.json","w") as f:
            f.write(json.dumps(sets))
    def Set (self,T) : #设置
        sets[T] = False if sets[T] else True
        tkinter.messagebox.showinfo("提示","已" + ("开启" if sets[T] else "关闭") + T)
        with open("set.json","w") as f:
            f.write(json.dumps(sets))
    def setSize (self) : #设置
        self.v = tkinter.Toplevel()
        self.t = tkinter.Entry(self.v,textvariable=tkinter.StringVar(value="输入字体大小"))
        self.b = tkinter.Button(self.v,text="完成",command=lambda :self.setSize2(self.t.get()))
        self.t.pack()
        self.b.pack()

    def setSize2 (self,s) :
        self.t.destroy()
        self.b.destroy()
        self.v.destroy()
        try:
            s = int(s)
            sets["size"] = s
        except:
            tkinter.messagebox.showerror("错误","请输入正整数")
        with open("set.json","w") as f:
            f.write(json.dumps(sets))



#---------------------------------------------------------

#-------------------------main----------------------------
if __name__ == "__main__":
    sets = multiprocessing.Manager().dict()
    apts = {}
    readJson()#获取源
    aptn = sets["apt"]
    base = tkinter.Tk()#定义窗口
    image_search = tkinter.PhotoImage(file="image/search.png")
    image_searchs = tkinter.PhotoImage(file="image/searchs.png")
    base.geometry("320x320")#窗口大小
    base.title("偷取")#标题
    menuc = bar(base)
    base["menu"] = menuc.bar
    pool = multiprocessing.Pool()
    main()#载入主界面布局
    base.mainloop()#窗口主循环