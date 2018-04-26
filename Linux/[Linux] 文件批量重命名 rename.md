---
title: [Linux] 文件批量重命名 rename
tags: 
grammar_cjkRuby: true
---

OS : Ubuntu16.04

## 需求场景 
修改 bootanimation 的时候美工发过来的文件太多了 , 需要批量重命名

## 方法
Linux 下的 ` rename ` 命令
格式是
```
rename 's/修改前的内容/修改后的内容/' 要修改的文件
```

### 批量添加后缀 txt
```
rename 's/$/\.txt/' *
```
`$` 表示结束符, 
`\.txt` 表示修改为 .txt 

### 批量修改后缀
```
rename 's/\.txt/\.bat/'
```
将 .txt 改为 .bat

### 将 10_01_001.png 改名为 001.png
```
rename 's/10_01_//'
```

### man rename

更多的参看 man rename 