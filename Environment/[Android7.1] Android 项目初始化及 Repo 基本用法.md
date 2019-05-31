title: [Android7.1] Android 项目初始化及 Repo 基本用法
date: 2019-5-31 21:00:00
tags: Android7.1,Rockchip

---

参考文档：
repo 使用简单手册： http://source.android.com/source/version-control.html
repo 代码工程地址： https://code.google.com/p/git-repo/

## 安装 repo

参考 https://mirrors.tuna.tsinghua.edu.cn/help/git-repo/
```
curl https://mirrors.tuna.tsinghua.edu.cn/git/git-repo -o repo
chmod +x repo
export REPO_URL='https://mirrors.tuna.tsinghua.edu.cn/git/git-repo/'
```

## 初始化 Android 工程
```
repo init --repo-url=https://mirrors.tuna.tsinghua.edu.cn/git/git-repo -u ssh://qxzn-git@10.10.7.83/repo/platform/manifest.git -b master -m rk3399_android-7.1.xml
```
如果没有 -m 指定 xml， 会使用名为 default 的 xml，
```
repo sync
```

## 开发规范
最好请先通读 repo 基本用法，再了解开发规范
### 个人开发规范
```
# 务必创建分支开发
repo start 

# 在子仓库中进行开发，提交变更
git add 
git commit 
# git push 仓库名 本地分支名:远程分支名
git push origin master:msater
```
### 管理员开发规范
参见 RK《REPO 镜像服务器搭建和管理.pdf》

## repo 基本用法
### 同步更新代码
```
repo sync 
repo sync [project]  # repo sync kernel 
```
本质是 `git fetch --update-head-ok` 作用是更新当前分支，并将你的本地修改 rebase 到最近一次更新。
注意：如果当前分支有本地提交或者与服务器有冲突，或者不是用 repo start 建立

### 解决冲突
sync 有可能出现提示冲突，并提示使用“git rebase --abort”，“git rebase --continue”，“git rebase --skip”等 3 个命令解决冲突。
如果您知道如何解决冲突，使用如下命令：
a) 手工编辑 conflicts（即提示冲突）的文件，并使用
```
vim some_comflict_file
git add some_conflict_file
```
b) 解决所有冲突后，执行
```
git commit
git rebase --continue
```
如果不知道如何解决，请先使用如下命令：
a) 退出 rebase 状态
```
git rebase --abort
```
b) 手工去相应工程用 git 命令合并。

### 创建开发分支
```
# 创建分支
repo start branch_name

# 检查分支是否创建：
repo status

# 查看当前所有工程分支：
repo branch

# git 命令中关于分支的操作：
# 检出新分支
git checkout -b branch_name

# 检出基于远程分支的跟踪分支
git checkout -b branch_name -t repository/remote_branch_name

# 删除分支
git branch -d branch_name
git branch -D branch_name

# 比较分支提交差别，分支名也可以是 HEAD， commitid 等。
git log branch_name1..branch_name2
```

### 查看修改
```
# 查看所有本地工程修改
repo diff

# 查看状态
# “-m”指修改未提交，“--”指不在版本库管理的文件。
repo status

# 查看所有未合并的分支
repo overview
```