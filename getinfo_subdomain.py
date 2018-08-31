import html.parser
from bs4 import BeautifulSoup
import requests
import queue
import threading
import socket
import getopt
import sys

def usage():
    print("\033[1;34m")

    print("*" * 60)
    print("|  Usage:python3 getinfo_subdomain.py -o file [-选项 参数]")
    print("|  -o --output                 -将结果输出到file")
    print("|  -t --thread                 -设置运行线程")
    print("|  -i --input                  -输入存有子域名列表的文件")
    print("*" * 60)

    print("\033[0m")
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

# 解析HTML返回data
def getdata(subdomain):
    datalist = []
    # 此处两次requests提高准确性
    for i in range(2):
        try:
            # 为requests请求添加http://
            subdo = "http://" + subdomain
            r = requests.get(subdo,timeout=4)
            status = r.status_code
            content = r.content
            r.close()

            if status == 200:
                # 可以成功进入的情况
                # 解析html返回描述
                soup = BeautifulSoup(content.decode("utf8"),"html.parser")
                if str(soup.title) == "None":
                    data = ""
                else:
                    data = str(soup.title.string)
                datalist.append(data)
            else:
                # 返回码不为200时如果有错误信息则收集
                soup = BeautifulSoup(content.decode("utf8"),"html.parser")

                if str(soup.title) == "None":
                    # 不为200时无任何信息时
                    data = str(status)
                    datalist.append(data)
                else:
                    data = str(soup.title.string)
                    datalist.append(data)

        except UnicodeDecodeError as UDE:
            soup = BeautifulSoup(content.decode("gbk"),"html.parser")
            data = str(soup.title.string)
            datalist.append(data)

        except requests.exceptions.ConnectTimeout as e:
            data = "unreachable"
            datalist.append(data)
        
        except requests.exceptions.ConnectionError as cs:
            data = "unreachable"
            datalist.append(data)
        
        except requests.exceptions.TooManyRedirects as too:
            data = "unreachable"
            datalist.append(data)

        except requests.exceptions.SSLError as ssl:
            data = "证书错误"
            datalist.append(data)

        except Exception as error:
            print("\033[1;34m")
            print(subdo)
            print(error)
            print("\033[0m")

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
    print("\033[1;34m")
    print("正在记录{}个子域名以及相关信息到{}，请稍等...".format(count,outfilename))
    print("\033[0m")

if __name__ == "__main__":    
    main()
