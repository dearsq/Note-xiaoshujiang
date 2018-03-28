---
title: 【MTK6737_Android6.0】版本控制和开发流程说明
tags: 
grammar_cjkRuby: true
---

[TOC]


# 本地编译

## 注册 gitlab

1. 桂成在服务器 10.0.0.3:9000 上搭建了 Gitlab，需要先进行注册 http://10.0.0.3:9000/users/sign_in
2. 桂成将开发者赋予 Developer 或者 Master 权限，并拉进 Group MTK6737_Android6.0

## 添加 Gitlab 对本地机器的认证 via SSH_Keys
1. 参照如下命令生成 私钥和公钥对（YounixPC 和 YounixPC.pub）。
```bash
$ cd ~/.ssh/
$ ssh-keygen -t rsa -C "zhang.yang@aiiage.com"
Generating public/private rsa key pair.
Enter file in which to save the key (/home/younix/.ssh/id_rsa): YounixPC
Enter passphrase (empty for no passphrase): 
Enter same passphrase again: 
Your identification has been saved in YounixPC.
Your public key has been saved in YounixPC.pub.
The key fingerprint is:
SHA256:u1BNH8tBqdTx49cEGtCESAMfhvSahhmdXhhCVVXIC7M zhang.yang@aiiage.com
The key's randomart image is:
+---[RSA 2048]----+
|   .oo==*+oO*o.  |
|     o.B+o=.++ . |
|    . + +=.o+ o .|
|     = +Eooo = o.|
|    o = S . + . o|
|     . . .     . |
|      . .        |
|       . .       |
|        .        |
+----[SHA256]-----+
```

2. 点击 Gitlab 网站 http://10.0.0.3:9000/ 右上角头像下的子菜单中的 Setting 选项
3. 在左侧菜单中找到 SSH_Keys 标签并点击之
4. 将公钥 YounixPC.pub 中的内容复制到 Key 一栏中

提交后即添加认证完成。

## 同步代码
MTK6737 Android6.0 的代码已经采用 repo 进行管理。http:10.0.0.3:9000/MTK6737_Android6.0
```
$ cd ~/SDK/MTK/MTK6737_Android6.0
$ repo init -u http://10.0.0.3:9000/MTK6737_Android6.0/repo.git --repo-url=https://github.com/dearsq/repo -b master
$ repo sync
```
期间需要输入若干次 Gitlab 的帐号和密码。 //TODO: 添加自动认证

## 开发流程
SDK 被划分为 28 个子 git 仓库，使用 repo 管理。
1. 各模块开发遵循 git 规范。
2. 开发完后本地编译烧录验证，验证通过后即可 git push ，无需提交 PR。所以请保证代码规范 / 无 Bug。

# 服务器编译
服务器中，SDK 的目录为 `/home/aiiage/WorkSpace/02.SDK/alps`。