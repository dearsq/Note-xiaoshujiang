---
title: [Ubuntu] 服务器添加硬盘方法
tags: Ubuntu
grammar_cjkRuby: true
---
[TOC]

服务器容量 10 T 竟然只剩 50G 不到了～ 
于是公司加了 500 G 的普通硬盘用于存放不常用的源码。

**环境：**
Linux ubuntu 3.11.0-15-generic #25~precise1-Ubuntu SMP Thu Jan 30 17:39:31 UTC 2014 x86_64 x86_64 x86_64 GNU/Linux

以下是步骤：

## 查看当前硬盘状况
```
$ df -h     
$ ls -l /dev/sd*  
```
![](https://ws1.sinaimg.cn/large/ba061518gw1f9cmz2twfgj20ez085djs.jpg)
可以看到 sdb 是我们的第二块硬盘

```
$ fdisk -l
```
![](https://ws1.sinaimg.cn/large/ba061518gw1f9cn3864ysj20ve0e2doj.jpg)
可以看到
**Disk /dev/sdb doesn't contain a valid partition table**
我们看到 sdb 还未挂载。



## 添加分区
```
$ sudo fdisk sdb
```
按 m 帮助可以看到用法
![](https://ws2.sinaimg.cn/large/ba061518gw1f9cn6oi05gj20nb0f9gu3.jpg)

依次输入
n //添加分区
p //主要分区 //p表示主要 e表示拓展
1 //起始分区号
1 //起始扇区 //我这里填的是 2048
+500 //最后的扇区
W //确认
![](https://ws2.sinaimg.cn/large/ba061518gw1f9cn8medecj20nq09eq7e.jpg)

之后我们就可以在 /dev 下看到 **sdb1** 的存在了

## 分区格式化
将分区设置为 ext4 格式
```
$ mkfs -t ext4 /dev/sdb1
```
执行完这条命令需要等待一下，格式化分区
![](https://ws1.sinaimg.cn/large/ba061518gw1f9cncnepnoj20mw0f0gtr.jpg)


## 挂载分区到用户目录
比如我们需要挂载这个 sdb1 分区到 用户 atu 的 atusoftware 目录下：
在 root 用户下执行
```
# mkdir /home/atu/atusoftware
# mount /dev/sdb1 /home/atu/atusoftware
```

## 执行服务器开机自动挂载
修改 /etc/fstab 文件
```
$sudo vi /etc/fstab
```
添加如下内容
```
/dev/sdb1       /home/atu/softwaredata  ext4   defaults   0  0
```
该行内容表达的意思是
 < file system>  什么文件系统
 < mount point>   挂载点在哪
 < type>  文件系统的类型呢
 < options> 选项，一般填默认 defaults
 < dump>  是否要备份文件系统，1 备份 0 不备份
 < pass>  以什么顺序检查文件系统，0 不检查

点击这里有一篇 [/etc/fstab 详解](http://diamonder.blog.51cto.com/159220/282542)

![](https://ws4.sinaimg.cn/large/ba061518gw1f9cnjdrufuj20rt09xq97.jpg)

至此，**重新登录** ssh atu@[IP]  可以正常访问下面的 atusoftware 目录。
**scp** 也可以正常上传下载东西。

完。


