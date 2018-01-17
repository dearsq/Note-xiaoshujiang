---
title: [Ubuntu] 在终端中利用Wget/aria2下载百度云资源
tags: Ubuntu
grammar_cjkRuby: true
---

OS: Ubuntu16.04
Tools: Baiduyun、Wget

## 需求

Linux 下暂时没有好用的 百度云应用。
利用 Chrome 浏览器直接下载百度云大文件不支持断点续传，一旦失败就要重头开始下。
所以考虑采用 Wget 来下载资源。

another way is using BaiduExporter + aria2, Verrrrrrrry Good.

## 步骤

比如我现在下载 windows7 的镜像。

百度云地址是 ：https://pan.baidu.com/s/1jIhvmrc

### 1. 获取链接

点击 下载

![enter description here][1]

Ctrl + J 进入 Chrome 的下载管理器，查看其真实下载地址的链接：

![enter description here][2]

中间的地址就是真实的地址。右键复制。
```
https://d11.baidupcs.com/file/91d7089992e41c2ed7017521e6efca6f?bkt=p3-0000eb279d3adf2c1d1267e23789d078b33d&xcode=ee54de7d24eb85e9b28459f49768aa8ef20ac5b0ff7c90640b2977702d3e6764&fid=2288450327-250528-699849965031568&time=1497174234&sign=FDTAXGERLBHS-DCb740ccc5511e5e8fedcff06b081203-daZ89sIbCMzSqrQr0WMEIvK2owo%3D&to=d11&size=4092624896&sta_dx=4092624896&sta_cs=895&sta_ft=iso&sta_ct=5&sta_mt=5&fm2=MH,Yangquan,Netizen-anywhere,,guangdong,ct&newver=1&newfm=1&secfm=1&flow_ver=3&pkey=0000eb279d3adf2c1d1267e23789d078b33d&sl=76480590&expires=8h&rt=sh&r=896598456&mlogid=3751180020012367572&vuk=28420&vbdid=1640506990&fin=YLMF_GHOST_WIN7_X64_AQWD.iso&fn=YLMF_GHOST_WIN7_X64_AQWD.iso&rtype=1&iv=0&dp-logid=3751180020012367572&dp-callid=0.1.1&hps=1&csl=80&csign=QAYtCvA3moi4oLKno0uhupHAU9A%3D&by=themis

```

### 2. 利用 wget 命令下载

参照如下格式开始下载：

```
wget -c --referer=百度云短链接 -O 文件名 "真实链接"
```

所以我们下载的命令为：

```
wget -c --referer=https://pan.baidu.com/s/1jIhvmrc -O windows7_64.iso "https://d11.baidupcs.com/file/91d7089992e41c2ed7017521e6efca6f?bkt=p3-0000eb279d3adf2c1d1267e23789d078b33d&xcode=ee54de7d24eb85e9b28459f49768aa8ef20ac5b0ff7c90640b2977702d3e6764&fid=2288450327-250528-699849965031568&time=1497174234&sign=FDTAXGERLBHS-DCb740ccc5511e5e8fedcff06b081203-daZ89sIbCMzSqrQr0WMEIvK2owo%3D&to=d11&size=4092624896&sta_dx=4092624896&sta_cs=895&sta_ft=iso&sta_ct=5&sta_mt=5&fm2=MH,Yangquan,Netizen-anywhere,,guangdong,ct&newver=1&newfm=1&secfm=1&flow_ver=3&pkey=0000eb279d3adf2c1d1267e23789d078b33d&sl=76480590&expires=8h&rt=sh&r=896598456&mlogid=3751180020012367572&vuk=28420&vbdid=1640506990&fin=YLMF_GHOST_WIN7_X64_AQWD.iso&fn=YLMF_GHOST_WIN7_X64_AQWD.iso&rtype=1&iv=0&dp-logid=3751180020012367572&dp-callid=0.1.1&hps=1&csl=80&csign=QAYtCvA3moi4oLKno0uhupHAU9A%3D&by=themis"
```

最后开始下载的界面如下：

![正在下载界面][3]


  [1]: http://wx2.sinaimg.cn/large/ba061518ly1fghf06y4nlj20jw03lweu.jpg
  [2]: http://wx1.sinaimg.cn/large/ba061518ly1fghf00bd99j20i204c74d.jpg
  [3]: http://wx2.sinaimg.cn/large/ba061518ly1fghf5m8644j20za0dadod.jpg



## BaiduExporter + aria2
useage: 
https://blog.icehoney.me/posts/2015-01-31-Aria2-download
https://github.com/acgotaku/BaiduExporter