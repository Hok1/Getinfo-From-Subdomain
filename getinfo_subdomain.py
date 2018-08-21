from html.parser import HTMLParser
import requests
import queue
import threading
import socket
import getopt
import sys

def usage():
    print("|  Usage:python3 getinfo_subdomain.py -o file [-选项 参数]")
    print("|  -o --output                 -将结果输出到file")
    print("|  -t --thread                 -设置运行线程")
    print("|  -i --input                  -输入存有子域名列表的文件")
    sys.exit(0)


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

# 解析HTML返回data
def getdata(subdomain):
    datalist = []
    # 此处两次requests提高准确性
    for i in range(2):
        try:
            # 为requests请求添加http://
            subdo = "http://" + subdomain
            r = requests.get(subdo,timeout = 3)
            status = r.status_code
            content = r.content
            r.close()

            if status == 200:
                # 可以成功进入的情况
                # 传入class解析html返回描述
                parser = subinfoParser()
                parser.feed(content.decode("utf8"))
                #print("准备打印:" + parser.description)
                data = parser.description
                datalist.append(data)
            else:
                # 返回码不为200时
                if content.decode("utf8") != "":
                    # 返回码不为200时如果有错误信息则收集
                    parser = subinfoParser()
                    parser.feed(content.decode("utf8"))
                    data = parser.description
                    datalist.append(data)
                else:
                    # 不为200时无任何信息时
                    data = str(status)
                    datalist.append(data)

        except UnicodeDecodeError as UDE:
            parser = subinfoParser()
            parser.feed(content.decode("gbk"))
            data = parser.description
            datalist.append(data)
        except requests.exceptions.ConnectTimeout as e:
            #print(e)
            data = "unreachable"
            datalist.append(data)
        except Exception as error:
            #print(error)
            data = "unreachable"
            datalist.append(data)

    for d in datalist:
        #print(d)
        if d != "unreachable":
            return d.strip()
        
    return "unreachable"


# 写入文件
def printinfo(sublist,filename):
    while not sublist.empty():
        subdomain = sublist.get().rstrip()
        
        data = getdata(subdomain)

        ip = socket.gethostbyname(subdomain)
        #print(subdomain + "\t\t" + ip + "\t\t" + data)

        # 此处每次打开文件会影响执行速度，暂时没想好如何改进
        outfile = open(filename,"a")
        outfile.write(subdomain + "\t\t" + ip + "\t\t" + data + "\n")
        outfile.close()


def main():
    threads = 15
    inputfilename = "subdomain.txt"
    if not len(sys.argv[1:]):
        usage()

    try:
        opts,args = getopt.getopt(sys.argv[1:],"o:t:i:",["output","thread","input"])
    except Exception as e:
        print(e)
        usage()

    for o,a in opts:
        if o in ("-o","--output"):
            outfilename = a
        elif o in ("-t","--thread"):
            threads = int(a)
        elif o in ("-i","--input"):
            inputfilename = a
        else:
            assert False,"无法处理的参数"
    

    sublist,count = getsublist(inputfilename)
    for i in range(threads):
        t = threading.Thread(target=printinfo,args=(sublist,outfilename))
        t.start()
    print("正在记录{}个子域名以及相关信息到{}，请稍等...".format(count,outfilename))


if __name__ == "__main__":    
    main()
