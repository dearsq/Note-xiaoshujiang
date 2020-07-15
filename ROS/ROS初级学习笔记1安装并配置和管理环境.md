title: ROS初级学习笔记1安装并配置和管理环境
date: 2020-7-14 21:00:00
tags: ROS

---
本文是记录阅读  ROS Wiki 过程中
碰到的问题和解决方案
标题是和 wiki 中的一一对应的。如果由于 wiki 更新了，而导致本文信息过时，请评论哟。
[TOC]

## 1. 安装
本部分是记录阅读`http://wiki.ros.org/kinetic/Installation/Ubuntu` 过程中碰到的问题和解决方案。
### 1.2+1.3+1.4 更新 Ubuntu 源+设置密钥+安装
```
sudo sh -c 'echo "deb http://packages.ros.org/ros/ubuntu $(lsb_release -sc) main" > /etc/apt/sources.list.d/ros-latest.list'
```
```
sudo apt-key adv --keyserver 'hkp://keyserver.ubuntu.com:80' --recv-key C1CF6E31E6BADE8868B172B4F42ED6FBAB17C654
```

或者使用清华源
```
sudo sh -c '. /etc/lsb-release && echo "deb http://mirrors.tuna.tsinghua.edu.cn/ros/ubuntu/ $DISTRIB_CODENAME main" > /etc/apt/sources.list.d/ros-latest.list'
```
```
sudo apt-key adv --keyserver 'hkp://keyserver.ubuntu.com:80' --recv-key C1CF6E31E6BADE8868B172B4F42ED6FBAB17C654
```

桌面完整版安装
```
sudo apt-get install ros-kinetic-desktop-full
```

### 1.5 开发环境搭建
根据你自己的终端是 bash 还是 zsh 有点差别
我是 zsh，所以使用：
```
echo "source /opt/ros/kinetic/setup.zsh" >> ~/.zshrc
source ~/.zshrc
```
如果你是 bash，那么使用如下应该没有问题：
```
echo "source /opt/ros/kinetic/setup.bash" >> ~/.bashrc
source ~/.bashrc
```

### 1.6 依赖问题
构建工厂依赖
为了创建和管理自己的 ROS 工作区，有各种各样的工具和需求分别分布。例如：rosinstall 是一个经常使用的命令行工具，它使你能够轻松地从一个命令下载许多 ROS 包的源树。

要安装这个工具和其他构建ROS包的依赖项，请运行:
```
sudo apt-get install python-rosinstall python-rosinstall-generator python-wstool build-essential
```
#### 1.6.1 初始化 rosdep
```
$ sudo rosdep init                                      
[sudo] password for younix: 
ERROR: cannot download default sources list from:
https://raw.githubusercontent.com/ros/rosdistro/master/rosdep/sources.list.d/20-default.list
Website may be down.
```
### 错误解决方法
手动`mkdir /etc/ros/rosdep/sources.list.d/20-default.list`并写入内容。
### 正确解决方法
```
#打开hosts文件
sudo gedit /etc/hosts
#在文件末尾添加
151.101.84.133  raw.githubusercontent.com
#保存后退出再尝试
```
由于之前手动创建过`/etc/ros/rosdep/sources.list.d/20-default.list`所以有如下报错：
```
$ sudo rosdep init     
ERROR: default sources list file already exists:
        /etc/ros/rosdep/sources.list.d/20-default.list
Please delete if you wish to re-initialize
```
rm 即可
```
sudo rm /etc/ros/rosdep/sources.list.d/20-default.list
```

成功后打印如下信息
```
$ sudo rosdep init                                                                          
Wrote /etc/ros/rosdep/sources.list.d/20-default.list
Recommended: please run

        rosdep update
```

按照要求
```
rosdep update
# 成功打印如下信息
$ rosdep update
reading in sources list data from /etc/ros/rosdep/sources.list.d
Hit https://raw.githubusercontent.com/ros/rosdistro/master/rosdep/osx-homebrew.yaml
Hit https://raw.githubusercontent.com/ros/rosdistro/master/rosdep/base.yaml
Hit https://raw.githubusercontent.com/ros/rosdistro/master/rosdep/python.yaml
Hit https://raw.githubusercontent.com/ros/rosdistro/master/rosdep/ruby.yaml
Hit https://raw.githubusercontent.com/ros/rosdistro/master/releases/fuerte.yaml
Query rosdistro index https://raw.githubusercontent.com/ros/rosdistro/master/index-v4.yaml
Skip end-of-life distro "ardent"
Skip end-of-life distro "bouncy"
Skip end-of-life distro "crystal"
Add distro "dashing"
Add distro "eloquent"
Add distro "foxy"
Skip end-of-life distro "groovy"
Skip end-of-life distro "hydro"
Skip end-of-life distro "indigo"
Skip end-of-life distro "jade"
Add distro "kinetic"
Skip end-of-life distro "lunar"
Add distro "melodic"
Add distro "noetic"
Add distro "rolling"
updated cache in /home/younix/.ros/rosdep/sources.cache
```
### 成功运行
ROS 成功运行：
```
$ roscore 
... logging to /home/younix/.ros/log/e27c0a52-c5ab-11ea-8524-88d7f67db4f5/roslaunch-Yo-PC-14248.log
Checking log directory for disk usage. This may take awhile.
Press Ctrl-C to interrupt
Done checking log file disk usage. Usage is <1GB.

started roslaunch server http://Yo-PC:46349/
ros_comm version 1.12.14


SUMMARY
========

PARAMETERS
 * /rosdistro: kinetic
 * /rosversion: 1.12.14

NODES

auto-starting new master
process[master]: started with pid [14259]
ROS_MASTER_URI=http://Yo-PC:11311/

setting /run_id to e27c0a52-c5ab-11ea-8524-88d7f67db4f5
process[rosout-1]: started with pid [14273]
started core service [/rosout]

```

## 2. 管理环境
本部分是记录阅读`http://wiki.ros.org/cn/ROS/Tutorials/InstallingandConfiguringROSEnvironment` 过程中碰到的问题和解决方案。

这里主要是跟自己的环境有关。
我是 Ubuntu16.04 + ROS kinetic。并且使用的是 zsh。那么正确的声明环境变量的命令为：
```
$ source /opt/ros/kinetic/setup.zsh
```

## 3. 创建 ROS 工作空间
本部分是记录阅读`http://wiki.ros.org/cn/ROS/Tutorials/InstallingandConfiguringROSEnvironment` 过程中碰到的问题和解决方案。

```
$ mkdir -p ~/catkin_ws/src
$ cd ~/catkin_ws/
$ catkin_make                                     
Base path: /home/younix/ros/07.Code/catkin_ws
Source space: /home/younix/ros/07.Code/catkin_ws/src
Build space: /home/younix/ros/07.Code/catkin_ws/build
Devel space: /home/younix/ros/07.Code/catkin_ws/devel
Install space: /home/younix/ros/07.Code/catkin_ws/install
Creating symlink "/home/younix/ros/07.Code/catkin_ws/src/CMakeLists.txt" pointing to "/opt/ros/kinetic/share/catkin/cmake/toplevel.cmake"
####
#### Running command: "cmake /home/younix/ros/07.Code/catkin_ws/src -DCATKIN_DEVEL_PREFIX=/home/younix/ros/07.Code/catkin_ws/devel -DCMAKE_INSTALL_
PREFIX=/home/younix/ros/07.Code/catkin_ws/install -G Unix Makefiles" in "/home/younix/ros/07.Code/catkin_ws/build"
####
-- The C compiler identification is GNU 5.4.0
-- The CXX compiler identification is GNU 5.4.0
-- Check for working C compiler: /usr/bin/cc
-- Check for working C compiler: /usr/bin/cc -- works
-- Detecting C compiler ABI info
-- Detecting C compiler ABI info - done
-- Detecting C compile features
-- Detecting C compile features - done
-- Check for working CXX compiler: /usr/bin/c++
-- Check for working CXX compiler: /usr/bin/c++ -- works
-- Detecting CXX compiler ABI info
-- Detecting CXX compiler ABI info - done
-- Detecting CXX compile features
-- Detecting CXX compile features - done
-- Using CATKIN_DEVEL_PREFIX: /home/younix/ros/07.Code/catkin_ws/devel
-- Using CMAKE_PREFIX_PATH: /opt/ros/kinetic
-- This workspace overlays: /opt/ros/kinetic
-- Found PythonInterp: /usr/bin/python2 (found suitable version "2.7.12", minimum required is "2") 
-- Using PYTHON_EXECUTABLE: /usr/bin/python2
-- Using Debian Python package layout
-- Using empy: /usr/bin/empy
-- Using CATKIN_ENABLE_TESTING: ON
-- Call enable_testing()
-- Using CATKIN_TEST_RESULTS_DIR: /home/younix/WorkSpace/01.Project/Pi_ROS/07.Code/catkin_ws/build/test_results
-- Found gtest sources under '/usr/src/gmock': gtests will be built
-- Found gmock sources under '/usr/src/gmock': gmock will be built
-- Found PythonInterp: /usr/bin/python2 (found version "2.7.12") 
-- Looking for pthread.h
-- Looking for pthread.h - found
-- Looking for pthread_create
-- Looking for pthread_create - not found
-- Looking for pthread_create in pthreads
-- Looking for pthread_create in pthreads - not found
-- Looking for pthread_create in pthread
-- Looking for pthread_create in pthread - found
-- Found Threads: TRUE  
-- Using Python nosetests: /usr/bin/nosetests-2.7
-- catkin 0.7.20
-- BUILD_SHARED_LIBS is on
-- BUILD_SHARED_LIBS is on
-- Configuring done
-- Generating done
-- Build files have been written to: /home/younix/WorkSpace/01.Project/Pi_ROS/07.Code/catkin_ws/build
####
#### Running command: "make -j4 -l4" in "/home/younix/ros/07.Code/catkin_ws/build"
####
```
然后在 catkin_ws 目录下就能看到 build 和 devel 两个文件夹。
devel 下是环境变量的脚本。
```
$ source develsetup.zsh
```
查看环境变量是否正确：
```
$ echo $ROS_PACKAGE_PATH
/home/younix/ros/07.Code/catkin_ws/src:/opt/ros/kinetic/share
```