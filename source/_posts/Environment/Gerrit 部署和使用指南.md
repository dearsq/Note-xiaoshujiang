title: Gerrit 部署和使用指南
date: 2019-1-11 21:00:00
tags: Linux,Gerrit

---
https://gerrit-review.googlesource.com/Documentation/index.html
https://blog.csdn.net/HuangLin_Developer/article/details/78732306
## 使用
### Android 插件
### Clone 项目
和正常 Git clone 完全一致. 比如:
```
git clone ssh://gerrithost:29418/RecipeBook.git RecipeBook
Cloning into RecipeBook...
```
### CodeReview 工作流 (重要)
1. 审查每个提交
2. 必须将提交推送到 refs/for/ 定义目标分支的命名空间中的
`ref : refs/for/<target-branch>` 

代码审查:
```
git commit
git push origin HEAD：refs/for/master
```
绕过代码审查
```
git commit
git push origin HEAD：master
```
获取变更:
```
git fetch https：//gerrithost/myProject refs/changes/74/67374/2 && git checkout FETCH_HEAD
```
`refs/changes/XX/YYYY/ZZ`，其中YYYY是数值变更号码，ZZ就是补丁集数，XX是数值变更号码，例如最后两位数字 refs/changes/20/884120/1


## 部署

### 下载
```
wget https://www.gerritcodereview.com/download/gerrit-2.16.2.war
```
### 安装

```
java -jar gerrit*.war init --batch --dev -d ~/WorkTools/gerrit_testsite
```
`--batch` 表示参数默认
`--dev` 表示可以切换开发者身份

正常出现如下 Log
```
[2019-01-11 09:50:13,103] [main] INFO  com.google.gerrit.server.config.GerritServerConfigProvider : No /home/younix/WorkTools/gerrit_testsite/etc/gerrit.config; assuming defaults
Generating SSH host key ... rsa... ed25519... ecdsa 256... ecdsa 384... ecdsa 521... done
Initialized /home/younix/WorkTools/gerrit_testsite
Reindexing projects:    100% (2/2)
Reindexed 2 documents in projects index in 0.0s (52.6/s)
Executing /home/younix/WorkTools/gerrit_testsite/bin/gerrit.sh start
Starting Gerrit Code Review: WARNING: Could not adjust Gerrit's process for the kernel's out-of-memory killer.
         This may be caused by /home/younix/WorkTools/gerrit_testsite/bin/gerrit.sh not being run as root.
         Consider changing the OOM score adjustment manually for Gerrit's PID= with e.g.:
         echo '-1000' | sudo tee /proc//oom_score_adj
OK
```
### 更新监听的 URL
修改为 localhost 以防止外部连接到 Gerrit 实例
```
git config --file ~/WorlTools/gerrit_testsite/etc/gerrit.config httpd.listenUrl 'http://localhost:8080'
```
### 重启
```
 ~/WorkTools/gerrit_testsite/bin/gerrit.sh restart
```
正常 Log 如下:
```
Stopping Gerrit Code Review: OK
Starting Gerrit Code Review: WARNING: Could not adjust Gerrit's process for the kernel's out-of-memory killer.
         This may be caused by /home/younix/WorkTools/gerrit_testsite/bin/gerrit.sh not being run as root.
         Consider changing the OOM score adjustment manually for Gerrit's PID= with e.g.:
         echo '-1000' | sudo tee /proc//oom_score_adj
OK
```
