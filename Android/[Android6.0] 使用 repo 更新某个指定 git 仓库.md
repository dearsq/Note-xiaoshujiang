---
title: [Android6.0] 使用 repo 更新某个指定 git 仓库
tags: android,repo,git
grammar_cjkRuby: true
---

[TOC]

## repo 同步整个项目
```
repo sync
```


## repo 同步单个项目


同步单个文件的方式就是
```
repo sync <project>
```
**\<project>** 即为 manifest 中的 name 或者 path。

我们打开 .repo/manifest.xml ，有类似如下代码
```
<?xml version="1.0" encoding="UTF-8"?>
<manifest>
  <remote fetch="." name="aosp" review="https://10.10.10.29"/>
  <remote fetch="." name="rk" review="https://10.10.10.29"/>
  
  <default remote="aosp" revision="refs/tags/android-6.0.1_r63" sync-j="4"/>
  
  <project name="android/RKDocs" path="RKDocs" remote="rk" revision="rk3399/box/android-6.0"/>
  <project name="android/RKTools" path="RKTools" remote="rk" revision="ce0d44915d3b13cc556ff607dde745f71965ccc3" upstream="rk3399/box/android-6.0"/>
  <project name="rk/RKNanoC" path="RKNanoC" remote="rk" revision="master"/>
  <project groups="pdk-cw-fs,pdk-fs" name="android/device/common" path="device/common" remote="rk" revision="6482b0e4219edbbb3da2c6e77ce7c2ba22e55ba9" upstream="rk32/mid/6.0/develop"/>
  <project groups="pdk" name="android/device/generic/arm64" path="device/generic/arm64" revision="39249053f37b7f9633eb406af3dbedfea7bf8b3e" upstream="refs/tags/android-6.0.1_r63"/>
```


比如只要同步 RKDocs 仓库中的内容：
```
repo sync RKDocs
```
或者 
```
repo sync android/RKDocs
```
