---
title: [Git] 如何修改之前的某次commit 
tags: git
grammar_cjkRuby: true
---


### 需求背景

将 A 功能从 branchA 合入到主分支 master 后过了很多个提交后，发现 A 功能某个地方有 bug，那最好的方法就是跳回到写 A 功能的时候进行修改。

这分为两个部分
1. 修改之前某次的 commit 信息
2. 修改之前每次的 commit 内容

### 实现方法

比如我现在的 git log 如下：
```
4fd65115db FUNCTION Mipi Camera Camera IC: OV13850 Interface: RX1
97a8ad0f7f FUNCTION 移植 8寸 Mipi LCD Driver IC: RM72014
9633cf0919 FUNCTION 移植 TP 8inch Driver IC:GT911
```

我现在发现当时移植 TP 的时候有 bug，我需要回到 `9633cf0919` 对进行 TP 进行移植的时候来修复这个 Bug。

我只需要这样做：
1. 在当前分支开始修改 TP 功能的 Bug，完成修改后 
```
git stash
```
2. 将 HEAD 移动到需要修改的 commit 上
```
git rebase 9633cf0919^ --interactive
```
3. 找到需要修改的 commit ，将首行的 pick 改成 edit
4. 合入 bug 解决的代码
```
git stash pop
```
5. git add 将改动文件添加到暂存
6. git commit --amend 追加改动到提交
7. git rebase --continue 移动 HEAD 回最新的 commit
