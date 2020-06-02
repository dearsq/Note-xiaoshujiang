---
title: [Ubuntu] Linux 下使用 mount_afp 访问 AFP 服务器.md
tags: 
---

## 需求
公司共享磁盘更换为 Apple 的 afp 形式的了。

## 步骤
Ubuntu下挂载步骤如下：

```
sudo apt-get install libfuse-dev libreadline-dev

git clone https://github.com/simonvetter/afpfs-ng
cd afpfs-ng
./configure
make
sudo make install
sudo ldcondig
```

试一下：
```
mount_afp                                                               
Usage:
     mount_afp [-o volpass=password] <afp url> <mountpoint>
```
**成功～**


最后挂载的用法见：`https://linux.die.net/man/1/mount_afp`
```
mount_afp afp://username：password@server.company.com/volumename/ /Volumes/mntpnt
```
对于我而言是：
```
mount_afp afp://younix:bugaosuni@6.6.6.6/技术研发中心/ /home/younix/AFP_SERVER
Mounting 技术研发中心 from 6.6.6.6 on /home/younix/AFP_SERVER
Mounting of volume 技术研发中心 from server MYCOMPANY succeeded.
```
**成功～**

## 问题
如果出现：
```
mount_afp
mount_afp: error while loading shared libraries: libafpclient.so.0: cannot open shared object file: No such file or directory
```
是由于 libpthread.so.0 链接的不对
```
find . -name libafpclient.so.0
./lib/.libs/libafpclient.so.0

cp lib/.libs/libafpclient.so.0 /lib/x86_64-linux-gnu/
```


参考文章：
`https://stackoverflow.org/wiki/Mount_an_AFP_share_from_Linux`
`https://askubuntu.com/questions/886656/how-can-i-mount-an-afp-share`
`https://linux.die.net/man/1/mount_afp`



另一篇：
Linux下访问NAS服务器