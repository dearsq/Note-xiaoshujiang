---
title: [Linux][RK3399] 以太网调试 — 利用 ping 和 pathping 工具
tags: ethernet,rockchip
grammar_cjkRuby: true
---

## 网络配置
Redhat 的配置在 /etc/sysconfig/network-scripts/ifcfg-eth0
Debian 的配置在 /etc/network/interfaces
差异有点大，我的板子是采用的 Debian 
这里以 Debian 为例

网络配置有三个方法
1. DHCP 动态
2. static 静态
3. 图形界面配置

因为我们板子和主机连的是同一个网关。
先**在主机** `ifconfig` 看一下自己主机所在的网络的相关信息
```
enp2s0    Link encap:以太网  硬件地址 1c:1b:0d:b3:64:d5  
          inet 地址:192.168.1.130  广播:192.168.1.255  掩码:255.255.255.0
          inet6 地址: fe80::1bbe:be89:15eb:3083/64 Scope:Link
          UP BROADCAST RUNNING MULTICAST  MTU:1500  跃点数:1
          接收数据包:1164966 错误:0 丢弃:0 过载:0 帧数:0
          发送数据包:557220 错误:0 丢弃:0 过载:0 载波:0
          碰撞:0 发送队列长度:1000 
          接收字节:1400257775 (1.4 GB)  发送字节:60841335 (60.8 MB)
```
提取出来的信息有
Host ip address 192.168.1.130
Gatway address 192.168.1.1
Broadcast address 192.168.1.255
Netmask 255.255.255.0
可以按照主机上的信息来配置板子。

### DHCP 
修改配置文件 /etc/network/interfaces
```
auto eth0 
iface eth0 inet dhcp 
```
重启开发板，或者 如下 重启网络服务
```
sudo /etc/init.d/networking restart 
```

### Static IP Address
修改配置文件  /etc/network/interfaces
```
auto eth0
iface eth0 inet static
address 192.168.1.66
network 192.168.1.0
netmask 255.255.255.0
broadcast 192.168.1.255
gateway 192.168.1.1

```
重启开发板，或者 如下 重启网络服务
```
sudo /etc/init.d/networking restart 
```

### 图形界面

![](http://ww1.sinaimg.cn/large/ba061518gy1fjc8lyapzaj20zk0qoq6y.jpg)

图形界面用到的情况不多，就不赘述了。

## 调试步骤

参考 https://technet.microsoft.com/en-us/library/cc940095.aspx

利用 Ping 和 PingPath 来测试网络连接。
Ping 用来验证 IP-level 的连通性。
PathPing 用来检测 multiple-hop trips 时包是否有 loss。

故障排除后，ping 命令用来发送一个 ICMP 回应请求到目标 host name 或是 IP Address。
用 Ping 命令来验证 主机能否正常向目标机发包，也可以用它来区分网络硬件问题和不兼容配置问题。

如果使用了 `ipconfig /all` 并且接收到了响应，没有必要再 ping 回环地址 和 自己的 IP 地址 —— `ipconfig` 为了产生报告已经这么去做了。

要使用 Ping 命令可以按照如下步骤：

### ping 回环地址 loopback address
ping 127.0.0.1 
如果环回步失败，则IP堆栈不响应。这可能是因为TCP驱动程序损坏，网络适配器可能无法正常工作，或其他服务与IP冲突。

### ping 本地计算机的 IP 地址 local ip address
验证它是否已经正确地添加到网络中。如果路由表是正确的，这只是将数据包转发到 127.0.0.1 回环地址。
```
# ping <IP address of local host>
ping 192.168.1.88
```

### ping 默认网关 IP 地址 
验证默认网关是否运行，本地是否能与本地网络上的其他主机进行通信。
```
# ping <Gateway address>
ping 192.168.1.1
```

### ping 远程主机 IP 地址
验证可以通过路由器进行通信
```
# ping <Remote IP address>
```

### ping 远程主机名
验证可以正确解析远程主机名
```
# ping <Remote Host Name>
ping www.baidu.com
```

### pathping 远程主机 IP
验证到远程主机所经过的 中间路由器是否运行正常。
```
# pathping <Remote IP address>

```

## 错误归纳 

### 本地地址返回 0.0.0.0 
微软MediaSense软件启动，因为网络适配器检测到它没有连接到网络。要解决此问题，通过确保网络适配器和网络电缆连接到集线器关闭MediaSense。如果连接是否牢固，重新安装网卡的驱动程序或新的网络适配器。


### ping 远程主机 ip 成功，名称失败
问题在 解析，而不是网络连接。