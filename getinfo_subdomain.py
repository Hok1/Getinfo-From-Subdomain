from html.parser import HTMLParser
import requests
import queue
import threading
import socket

threads = 15
#outfile = open("./result.txt","a")
count = 0

# 读取文件中域名
def getsublist(subfile):
    fd = open(subfile,"r")
    subdomains = fd.readlines()
    fd.close()

    sublist = queue.Queue()
    for sub in subdomains:
        sublist.put(sub.rstrip())
    
    #insize = sublist.qsize()
    #print(insize)
    return sublist,sublist.qsize()


# 解析html
class subinfoParser(HTMLParser):

    description = ""
    flag = 1
    def handle_data(self, data):
        """
        recognize data, html content string
        :param data:
        :return:
        """
        # print(self.lasttag)
        # lasttag 不管结束标签还是开始标签均相同，所以此处设置flag防止多算
        # 前一标签为title时，取出内容
        if self.lasttag == 'title' and self.flag == 1:
            #print("data is :" + data)
            #print("des before is:" + self.description)
            self.description = data
            #print("des after is:" + self.description)
            self.flag += 1
            
# 写入文件
def printinfo(sublist):
    while not sublist.empty():
        subdomain = sublist.get().rstrip()
        try:
            # 为requests请求添加http://
            subdo = "http://" + subdomain
            r = requests.get(subdo,timeout = 2)

            if r.status_code == 200:
                # 可以成功进入的情况
                # 传入class解析html返回描述
                parser = subinfoParser()
                parser.feed(r.content.decode("utf8"))
                #print("准备打印:" + parser.description)
                r.close()
                data = parser.description
            else:
                # 返回码不为200时
                if r.content.decode("utf8") != "":
                    # 返回码不为200时如果有错误信息则收集
                    parser = subinfoParser()
                    parser.feed(r.content.decode("utf8"))
                    r.close()
                    data = parser.description
                else:
                    # 不为200时无任何信息时
                    data = str(r.status_code)
                    r.close()

        except Exception as error:
            #print(error)
            data = "unreachable"

        ip = socket.gethostbyname(subdomain)
        #print(subdomain + "\t\t" + ip + "\t\t" + data)

        # 此处每次打开文件会影响执行速度，暂时没想好如何改进
        outfile = open("./result.xlsx","a")
        outfile.write(subdomain + "\t\t" + ip + "\t\t" + data + "\n")
        outfile.close()


if __name__ == "__main__":
    
    sublist,count = getsublist("subdomain.txt")
    for i in range(threads):
        t = threading.Thread(target=printinfo,args=(sublist,))
        t.start()
    print("正在记录{}个子域名以及相关信息，请稍等...".format(count))    
