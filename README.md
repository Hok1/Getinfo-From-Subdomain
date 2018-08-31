## 工具为原创，转载请标明出处
# 用途：

> 用于收集子域名后的信息收集。收集信息后输出到文档。不加-i参数默认由subdomain.txt读取子域名列表，不加-t参数默认15线程

# 用法：
```
python3 getinfo_subdomain.py -o 输出文件名
```


# eg:
```
python3 getinfo_subdomain.py -o result.txt
```

# more details:
```
python3 getinfo_subdomain.py
```

# version
> v1.1----</br> 
> v1.2---- </br>
> 解决了有关编码错误导致无法获取信息的问题</br> 
> v1.3---- </br>
> 增加了参数，使输入输出更灵活,无参数输入则显示用法</br> 
> v1.4---- </br> 
> 在网络通畅的情况下增加了准确度</br>
> v1.5---- </br> 
> 解决了一些编码问题</br>
> v1.6---- </br> 
> 修改了一些逻辑使结果更加精确</br>
> v1.7---- </br>
> 对于html细节处理改用了BeautifulSoup处理使信息更准确，以及一些小修改</br>


# 输入效果
![pic](https://wx1.sinaimg.cn/mw690/86146a5fly1fu9v2hf61kj205r064a9y.jpg)

# 输出效果
![pic](http://wx4.sinaimg.cn/mw690/86146a5fly1fu9v0tz9ftj20jg05hq3p.jpg)
