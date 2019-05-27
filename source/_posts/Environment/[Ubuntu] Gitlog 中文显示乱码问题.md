title: [Ubuntu] Gitlog 中文显示乱码问题
date: 2019-5-27 21:00:00
tags: Linux

---


## 问题
```
commit 9e358c91c711c0613b39fc531c4a229a7ba6848f
Author: zhangy <zhangy@qxsamrtcity.com>
Date:   Sun May 5 14:39:13 2019 +0800

    [Function] <D2><C6>ֲ 4G USB <CD><F8><BF><A8> EC20
    1. <B8><FC><BB><BB> ril bin <B0><FC><C0><A8> chat ip-down ip-up
    2. <B8><FC><BB><BB> ril <B5><C4> so <BF><E2>
    3. <B4>򿪿<D8><D6><C6> telphony framework <B2><E3><D7><E9><BC><FE><B1><E0><D2><EB><B5>Ŀ<AA><B9>
<D8>
    4. <CC><ED><BC>Ӷ<D4> messaging App <B5><C4>֧<B3><D6>
    5. <CC><ED><BC>Ӷ<D4> /dev/ttyUSB* <B5><C8> <CE>ļ<FE><BD>ڵ<E3><B5>ķ<C3><CE><CA>Ȩ<CF><DE>
    
    [Attention!!][ע<D2><E2>] kernel <D6>е<C4> USB Audio Driver <B4><CB>ʱ<C8><D4>Ȼ<B4>򿪣<AC><CB><F9>
<D2>Դ<CB>ʱ<CE>޷<A8><D5>������<C5>&<B2>ɼ<AF><C9><F9><D2><F4><A1><A3>
```

## 原因
git commit 的编码是 utf-8，日志输出却为 gbk。

## 解决方法
```
# 设置 git commit 格式为 utf-8
git config --global i18n.commitencoding utf-8
# 设置 git log 输出格式为 utf-8
git config --global i18n.logoutputencoding utf-8
# 设置 Less 命令输出格式为 utf-8
export LESSCHARSET=utf-8
```