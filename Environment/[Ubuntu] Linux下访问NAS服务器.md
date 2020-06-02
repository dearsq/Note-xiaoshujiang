---
title: [Ubuntu] Linux下访问NAS服务器.md
grammar_cjkRuby: true
---

NAS 一定搭建了 SAMBA 服务（CIFS）。
```
sudo mount -t cifs //服务器IP/服务器文件夹 -o username=你的帐号,password=你的密码 /home/挂载点
```

如果 NAS 开启了 NFS ，-t 也可以指定 NFS。