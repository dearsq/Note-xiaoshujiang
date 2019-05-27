title: [Ubuntu18.04] 系统环境搭建看这一篇就够了
date: 2019-5-27 21:00:00
tags: Linux

---

## 一、系统

### VIM Bug 上下左右键变成 ABCD
这么多个版本了，为什么这个问题还没解决呢。
```bash
sudo apt-get remove vim-common
sudo apt-get install vim
```
### 分辨率为 640x480
Ubuntu18.04 安装后分辨率只有一个选项，使用xrandr命令出现错误 `xrandr: Failed to get size of gamma for output default`
打开：/etc/default/grub
搜索：#GRUB_GFXMODE=640x480
编辑：640x480改成你想要的分辨率，并取消前面的#
例如：GRUB_GFXMODE=1920x1080
更新：sudo update-grub
### 分辨率不支持
```bash
gtf 1920 1080 60
# 1920x1080 @ 60.00 Hz (GTF) hsync: 67.08 kHz; pclk: 172.80 MHz
Modeline "1920x1080_60.00"  172.80  1920 2040 2248 2576  1080 1081 1084 1118  -HSync +Vsync
```

## 二、第三方软件

### sogou 输入法
https://blog.csdn.net/fx_yzjy101/article/details/80243710
先安装 fictx 框架，然后下载搜狗后双击 deb 包即可

### Chrome 浏览器
https://jingyan.baidu.com/article/148a1921e1910a4d71c3b1d9.html
```bash
sudo wget http://www.linuxidc.com/files/repo/google-chrome.list -P /etc/apt/sources.list.d/
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub  | sudo apt-key add -
sudo apt update
sudo apt-get install google-chrome-stable
genpac --pac-proxy "SOCKS5 127.0.0.1:1080" --gfwlist-proxy="SOCKS5 127.0.0.1:1080" --gfwlist-url=https://raw.githubusercontent.com/gfwlist/gfwlist/master/gfwlist.txt --output="autoproxy.pac"
```
### VMware

下载 <https://my.vmware.com/cn/web/vmware/info/slug/desktop_end_user_computing/vmware_workstation_pro/15_0#product_downloads>
安装
```
chmod +x VMware-Workstation-Full-15.0.4-12990004.x86_64.bundle 
sudo ./VMware-Workstation-Full-15.0.4-12990004.x86_64.bundle 
```
密钥参考：https://blog.csdn.net/IKQMKSQM/article/details/82912028

### Tmux + Zsh + Oh-My-Zsh
```zsh
sudo apt install tmux zsh
$ sh -c "$(curl -fsSL https://raw.github.com/robbyrussell/oh-my-zsh/master/tools/install.sh)"
```
使用 chsh 切换 Ubuntu 默认的 dash 为 zsh 没有成功，是因为 chsh 修改的是 root 用户的
在 ~/.bashrc 中添加
```bash
# Launch Zsh
if [ -t 1 ]; then
  exec zsh
fi
```
参考： https://www.jianshu.com/p/300827734b69

卸载：
执行
```
sudo sh -c "$(curl -fsSL https://raw.github.com/robbyrussell/oh-my-zsh/master/tools/uninstall.sh)"
```
再把`/etc/passwd`中的 zsh 改回为 bash

### autojump 自动跳转
```
sudo apt install autojump
vi ~/.zshrc
# 在最后一行加入，注意点后面是一个空格
. /usr/share/autojump/autojump.sh
```

### zsh 语法高亮
```
git clone https://github.com/zsh-users/zsh-syntax-highlighting.git
echo "source ${(q-)PWD}/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh" >> ${ZDOTDIR:-$HOME}/.zshrc
```
### zsh 语法历史记录
```
git clone git://github.com/zsh-users/zsh-autosuggestions $ZSH_CUSTOM/plugins/zsh-autosuggestions
echo "source ${(q-)PWD}/zsh-autosuggestions/zsh-autosuggestions.zsh" >> ${ZDOTDIR:-$HOME}/.zshrc
```

## 三、开发环境
### great wall ss-qt5
<https://github.com/shadowsocks/shadowsocks-qt5/releases>
1. 下载 Shadowsocks-Qt5-3.0.1-x86_64.AppImage
2. chmod a+x Shadowsocks-Qt5-3.0.0-x86_64.AppImage
3. ./Shadowsocks-Qt5-3.0.0-x86_64.AppImage
4. 连接到自己的服务器，并设置开机自启动自连接
5. 系统设置-网络-Network Proxy - Manual - SocksHost 一栏填写 127.0.0.1 1080 保存即可
6. 试一下应该可以Google了，重启也会自动连接，完美

接下来再设置 PAC 模式（绕过国内）：**安装genpac、下载gfwlist文件**
参考 https://blog.csdn.net/qq_24406903/article/details/85011090 的第二步

```bash
# 安装genpac
sudo pip install genpac
pip install --upgrade genpac
# 下载gfwlist文件
genpac --pac-proxy "SOCKS5 127.0.0.1:1080" --gfwlist-proxy="SOCKS5 127.0.0.1:1080" --gfwlist-url=https://raw.githubusercontent.com/gfwlist/gfwlist/master/gfwlist.txt --output="autoproxy.pac"
# 会在当前路径生成 autoproxy.pac 文件
# 进入系统设置-网络-Network Proxy - Automatic - URL输入刚才 autoproxy.pac的绝对路径
# 比如我的是 /home/xx/Tools/Config_GenPac/autoproxy.pac
```

另外，SS-QT5客户端也可以按照如下方式获取（2.9版本）

<https://www.bossky8023.com/content.do?id=admin1631120608d&op=visit>

```bash
sudo add-apt-repository ppa:hzwhuang/ss-qt5
vi /etc/apt/sources.list.d/hzwhuang-ubuntu-ss-qt5-bionic.list
# 如果你是 16.04的话，将bionic (18.04版本代号)改成xenial（16.04版本代号）
sudo apt-get update
sudo apt-get install shadowsocks-qt5 
```

### gcc
安装多版本gcc、g++可切换
```bash
sudo apt-get install gcc-4.8 gcc-4.8-multilib
sudo apt-get install g++-4.8 g++-4.8-multilib
sudo apt-get install gcc-5 gcc-5-multilib
sudo apt-get install g++-5 g++-5-multilib
sudo apt-get install gcc-6 gcc-6-multilib
sudo apt-get install g++-6 g++-6-multilib
sudo apt-get install gcc-7 gcc-7-multilib
sudo apt-get install g++-7 g++-7-multilib
sudo update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-4.8 48
sudo update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-5 50
sudo update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-6 60
sudo update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-7 70
sudo update-alternatives --install /usr/bin/g++ g++ /usr/bin/g++-4.8 48
sudo update-alternatives --install /usr/bin/g++ g++ /usr/bin/g++-5 50
sudo update-alternatives --install /usr/bin/g++ g++ /usr/bin/g++-6 60
sudo update-alternatives --install /usr/bin/g++ g++ /usr/bin/g++-7 70
```
### ssh
#### ssh: connect to host localhost port 22: Connection refused

1.sshd 未安装
2.sshd 未启动
3.防火墙
4.需重新启动ssh 服务

```bash
$ sudo apt-get install openssh-server  
$ sudo net start sshd  
$ sudo ufw disable   
$ ssh localhost  
```

## 四、Android 开发环境

```bash
# Google 官方文档 https://source.android.com/source/initializing.html
```

~~~bash
```
sudo apt install git-core gnupg flex bison gperf build-essential zip curl zlib1g-dev gcc-multilib g++-multilib libc6-dev-i386 lib32ncurses5-dev x11proto-core-dev libx11-dev lib32z-dev ccache libgl1-mesa-dev libxml2-utils xsltproc unzip

sudo apt install android-tools-adb minicom 

~~~

