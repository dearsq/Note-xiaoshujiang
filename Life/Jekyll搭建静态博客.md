title: Jekyll搭建静态博客
date: 2021-11-9 21:00:00
tags: Jekyll

---


官方文档（英文）：https://jekyllrb.com/docs/

## 搭建步骤
### 1. 环境准备
需要安装如下三个工具
> Ruby version 2.5.0 or higher
> RubyGems
> GCC and Make

#### 1.1 安装 Ruby
##### 1.1.1 Ubuntu20.04 安装 Ruby
```bash
$ sudo apt install ruby-full
```
确保安装成功：
```
$ ruby --version
ruby 2.5.1p57 (2018-03-29 revision 63029) [x86_64-linux-gnu]
```
更多安装方法参考：https://zhuanlan.zhihu.com/p/143980490

##### 1.1.2 Win10 安装 Ruby
访问 https://rubyinstaller.org/downloads/
下载对应的安装包即可，比如 Ruby+Devkit 3.0.2-1 (x64) 
无脑安装

#### 1.2 安装 RubyGems
##### 1.2.1 Ubuntu20.04 安装 RubyGems
```bash
$ sudo apt install rubygems
```
确保安装成功：
```
$ which gem 
/usr/bin/gem
```

##### 1.2.2 Win10 安装 RubyGems
如果 Ruby 版本是 2.5 以上，默认是自带 gem 的。
可以看一下 Ruby30-x64\bin\ 目录下，是否有 gem 的可执行文件。
如果没有，则按照如下步骤安装：
官方下载地址：https://rubygems.org/pages/download
下载 zip 包：rubygems-3.2.31.zip 并解压

#### 1.3 安装 Jekyll
##### 1.3.1 Ubuntu20.04 安装 Jekyll
```bash
$ sudo gem install jeykll
```
输出信息如下表示成功安装：
```
$ jekyll -v
jekyll 4.2.1
```

##### 1.3.2 Win10 安装 Jekyll
打开 cmd ，注意不可以用 wsl 或者 git bash
D:\Ruby30-x64\bin
```cmd
gem install jekyll
```
输出信息如下表示成功安装:
```
$ jekyll -v
jekyll 4.2.1
```

#### 1.4 本地运行博客
```
jekyll new restlessManBlog   #新建博客 
cd restlessManBlog           #切换目录 
jekyll server                #启动项目
```