---
title: [RK3399] 基于 Firefly RK3399 Board 制作 Ubuntu Base 版本
tags: rockchip,ubuntu
grammar_cjkRuby: true
---

# OrangePi_RK3399_制作UbuntuBase过程

Platform: RK3399
OS: Android 6.0 
Kernel: 4.4 
Version: v2017.04

[TOC]

## 编译 u-boot
```
cd u-boot
make rk3399_defconfig
make ARCHV=aarch64 -j8
```
制作出来的文件包括 
uboot.img
trust.img
RK3399MiniLoaderAll_V1.05.bin

## 编译 kernel
```
cd kernel
make ARCH=arm64 firefly_linux_defconfig
make ARCH=arm64 rk3399-firefly-mini-linux.img -j8
```
制作出来的文件包括 
kernel.img
resource.img
arch/arm64/boot/Image

## 整合内存盘 打包成 boot.img
### 创建内存盘 Ramdisk
```
git clone -b for-kernel_4.4 https://github.com/TeeFirefly/initrd.git
make -C initrd
```
会生成 initrd.img
### 打包内核和内存盘
```
mkbootimg --kernel arch/arm64/boot/Image --ramdisk initrd.img --second resource.img -o boot.img
```
会生成 boot.img

## 修改 parameter.txt 文件
```
CMDLINE: console=tty0 console=ttyFIQ0 root=/dev/mmcblk1p5 rw rootwait rootfstype=ext4 init=/sbin/init mtdparts=rk29xxnand:0x00002000@0x00002000(uboot),0x00002000@0x00004000(trust),0x00010000@0x00006000(boot),0x00002000@0x00016000(backup),-@0x00018000(rootfs)
```
## 制作根文件系统
```
dd if=/dev/zero of=rootfs.img bs=1M count=1024
mkfs.ext4 rootfs.img
mkdir -pv rootfs_mnt
mount rootfs.img rootfs_mnt
```

### 采用 qemu-debootstrap 进行根文件系统的制作
```
sudo apt-get install debootstrap
# 使用规则 sudo debootstrap --arch [平台] [发行版本代号] [目录]
# 当前支持的发行版代号可以在此查找 /usr/share/debootstrap/scripts
# 另外，如果是在 PC 上制作 arm 版本的话，需要改成 qemu-debootstrap
sudo qemu-debootstrap --arch arm64 xenial ./rootfs_mnt
# 如果需要增加一些第三方的库，可以适用 --include 选项，比如
sudo qemu-debootstrap --arch arm64 --include locales,dbus xenial ./rootfs_mnt
```
**遇到 问题1**

### 安装系统软件
```
# 配置网络相关，目的是为了将 nameserver 192.168.1.1 添加到 resolv.conf
sudo cp -b /etc/resolv.conf rootfs_mnt/etc/resolv.conf
sudo vi rootfs_mnt/etc/hostname # 添加自己的主机名 orangepi
sudo vi rootfs_mnt/etc/hosts # 配置主机名对应的 ip 127.0.0.1 orangepi
# 检查 apt 源
sudo vi rootfs_mnt/etc/apt/sources.list
# 发现只有一行 deb http://ports.ubuntu.com/ubuntu-ports xenial main
# 可以将自己的电脑的 apt 源 替换之（我的是清华大学的源）
cp /etc/apt/sources.list ./rootfs_mnt/etc/apt/
# 使用 chroot 进入 ./rootfs_mnt 中的系统
sudo chroot ./rootfs_mnt /bin/bash
# 添加用户和管理员组
root@YounixPC:/# useradd -s '/bin/bash' -m -G adm,sudo orangepi
root@YounixPC:/# passwd orangepi
root@YounixPC:/# passwd root
```
### 生成系统镜像
```
sudo umount -R rootfs_mnt
e2fsck -p -f rootfs.img
resize2fs -M rootfs.img
```

## 问题汇总
### 问题1
W: Failure trying to run: chroot RockChip_SDK/RK3399/rootfs_mnt mount -t proc proc /proc
解决方法，如果在 PC 端进行 rootfs 的制作。应该是采用 qemu-debootstrap ，我采用的却是 debootstrap。
