---
title: Linux 内核的 sysfs 文件系统
tags: Linux,sysfs
grammar_cjkRuby: true
---
sysfs 是 Linux 内核中一种新的  虚拟的基于内存的 文件系统。
它的作用和 proc 类似，但除了同样具有查看(cat) 和 设定(echo) 内核参数功能之外，也可以用来管理 Linux 统一设备模型。
它使用 sysfs 导出内核数据的方式更为统一。
* sysfs 挂载点 /sys 目录结构
* sysfs 与 Linux 统一设备模型的关系
* 常见属性文件的用法
* 以内核编程方面的具体例子展示如何添加 sysfs 支持

## sysfs 介绍及其挂载点 /sys 下的目录结构
### /sys 
sysfs 文件系统会被挂载在 /sys 上。参考 sysfs-rules.txt
### proc
sysfs 比 proc 相比有很多优点，最重要的就是设计上很清晰。
比如，一个**proc 虚拟文件**有可能有内部格式，/proc/scsi/scsi 它是可读可写的（但是其权限被标记为 0444,这是 bug），并且读写格式不一样，代表不同的操作。即 应用程序 读到了这个文件的内容还需要进行字符串的解析，在写入时还需要先用字符串格式化按指定的格式写入字符串进行操作。
但是，一个 **sysfs 设计原则是 一个属性文件 只做一件事情**，sysfs 属性文件一般只有一个值，直接读取或者写入。

###  /sys 下的目录结构
```bash
root@younixPC:~# ls -F /sys
block/  bus/  class/  dev/  devices/  firmware/  fs/  hypervisor/  kernel/  module/  power/
root@younixPC:~# ls -F /sys/devices/pci0000:00/0000:00:01.0/0000:01:00.0/
broken_parity_status  enable         modalias  resource0     rom               uevent
class                 irq            msi_bus   resource0_wc  subsystem@        vendor
config                local_cpulist  power/    resource1     subsystem_device
device                local_cpus     resource  resource2     subsystem_vendor
```

在 /sys 目录下有 block, bus, class, dev, devices, firmware, fs, kernel, module, power 这些子目录，本文将分别介绍这些目录存在的含义。
第二个 ls 命令展示了在一个 pci 设备目录下的文件， "ls" 命令的 "-F" 命令为所列出的每个文件使用后缀来显示文件的类型，后缀 "/" 表示列出的是目录，后缀 "@" 表示列出的是符号链接文件。可以看到第二个目录下包含有普通文件 (regular file) 和符号链接文件 (symbolic link file) ，后面将介绍这个具体的设备为例说明其中每一个普通文件的用途。

| /sys 下的子目录 | 所包含的内容 |
|--|--|
|/sys/devices|	这是内核对系统中所有设备的分层次表达模型，也是 /sys 文件系统管理设备的最重要的目录结构，下文会对它的内部结构作进一步分析；|
|/sys/dev|	这个目录下维护一个按字符设备和块设备的主次号码(major:minor)链接到真实的设备(/sys/devices下)的符号链接文件，它是在内核 2.6.26 首次引入；|
|/sys/bus|	这是内核设备按总线类型分层放置的目录结构， devices 中的所有设备都是连接于某种总线之下，在这里的每一种具体总线之下可以找到每一个具体设备的符号链接，它也是构成 Linux 统一设备模型的一部分；|
|/sys/class|	这是按照设备功能分类的设备模型，如系统所有输入设备都会出现在 /sys/class/input 之下，而不论它们是以何种总线连接到系统。它也是构成 Linux 统一设备模型的一部分；|
|/sys/block|	这里是系统中当前所有的块设备所在，按照功能来说放置在 /sys/class 之下会更合适，但只是由于历史遗留因素而一直存在于 /sys/block, 但从 2.6.22 开始就已标记为过时，只有在打开了 CONFIG_SYSFS_DEPRECATED 配置下编译才会有这个目录的存在，并且在 2.6.26 内核中已正式移到 /sys/class/block, 旧的接口 /sys/block 为了向后兼容保留存在，但其中的内容已经变为指向它们在 /sys/devices/ 中真实设备的符号链接文件；|
|/sys/firmware|	这里是系统加载固件机制的对用户空间的接口，关于固件有专用于固件加载的一套API，在附录 LDD3 一书中有关于内核支持固件加载机制的更详细的介绍；|
|/sys/fs|	这里按照设计是用于描述系统中所有文件系统，包括文件系统本身和按文件系统分类存放的已挂载点，但目前只有 fuse,gfs2 等少数文件系统支持 sysfs 接口，一些传统的虚拟文件系统(VFS)层次控制参数仍然在 sysctl (/proc/sys/fs) 接口中中；|
|/sys/kernel|	这里是内核所有可调整参数的位置，目前只有 uevent_helper, kexec_loaded, mm, 和新式的 slab 分配器等几项较新的设计在使用它，其它内核可调整参数仍然位于 sysctl (/proc/sys/kernel) 接口中 ;|
|/sys/module|	这里有系统中所有模块的信息，不论这些模块是以内联(inlined)方式编译到内核映像文件(vmlinuz)中还是编译为外部模块(ko文件)，都可能会出现在 /sys/module 中：<br>  编译为外部模块(ko文件)在加载后会出现对应的 /sys/module/ < module_name >/, 并且在这个目录下会出现一些属性文件和属性目录来表示此外部模块的一些信息，如版本号、加载状态、所提供的驱动程序等 <br>  编译为内联方式的模块则只在当它有非0属性的模块参数时会出现对应的 /sys/module/ < module_name >, 这些模块的可用参数会出现在 /sys/modules/ < modname >/parameters/ < param_name > 中，<br>  如 /sys/module/printk/parameters/time 这个可读写参数控制着内联模块 printk 在打印内核消息时是否加上时间前缀；<br>  所有内联模块的参数也可以由 "< module_name > . < param_name > = < value >" 的形式写在内核启动参数上，如启动内核时加上参数 "printk.time=1" 与 向 "/sys/module/printk/parameters/time" 写入1的效果相同；<br>  没有非0属性参数的内联模块不会出现于此。|
|/sys/power|	这里是系统中电源选项，这个目录下有几个属性文件可以用于控制整个机器的电源状态，如可以向其中写入控制命令让机器关机、重启等。|
|/sys/slab <br>(对应 2.6.23 内核，在 2.6.24 以后移至 /sys/kernel/slab)|	从2.6.23 开始可以选择 SLAB 内存分配器的实现，并且新的 SLUB（Unqueued Slab Allocator）被设置为缺省值；如果编译了此选项，在 /sys 下就会出现 /sys/slab ，里面有每一个 kmem_cache 结构体的可调整参数。对应于旧的 SLAB 内存分配器下的 /proc/slabinfo 动态调整接口，新式的 /sys/kernel/slab/ < slab_name > 接口中的各项信息和可调整项显得更为清晰。|

#### /sys/devices/
```bash
$ ls -F /sys/devices/
isa/  LNXSYSTM:00/  pci0000:00/  platform/  pnp0/  pnp1/  system/  virtual/
```
可以看到，在 /sys/devices/ 目录下是按照设备的基本总线类型分类的目录，再进去查看 PCI 类型的设备：
```bash
$ ls -F /sys/devices/pci0000:00/
0000:00:00.0/  0000:00:02.5/  0000:00:03.1/  0000:00:0e.0/   power/
0000:00:01.0/  0000:00:02.7/  0000:00:03.2/  firmware_node@  uevent
0000:00:02.0/  0000:00:03.0/  0000:00:03.3/  pci_bus/
```
在 /sys/devices/pci0000:00/ 下是按照 PCI 总线接入的设备号分类存放的目录。再进去查看其中的一个：
```bash
$ ls -F /sys/devices/pci0000:00/0000:00:01.0/
0000:01:00.0/         device         local_cpus  power/            subsystem_vendor
broken_parity_status  enable         modalias    resource          uevent
class                 irq            msi_bus     subsystem@        vendor
config                local_cpulist  pci_bus/    subsystem_device
```
可以看到，其中有一个目录 0000:01:00.0/ ，其它的都是属性文件和属性组，而如果对 0000:01:00.0/ 子目录中进行再列表查看则会得到之前我们看到过的目录结构。

层次图如下：
![](http://ww4.sinaimg.cn/large/ba061518gw1f5asygg3ebg20fw08q0t5.gif)
我们看到涉及了 ksets，kobjects，attrs 等。

## 统一设备模型
对于统一设备模型，我们可以看这一篇博文：

涉及到文件系统实现来说， sysfs 是一种基于 ramfs 实现的内存文件系统，与其它同样以 ramfs 实现的内存文件系统(configfs,debugfs,tmpfs,...)类似， sysfs 也是直接以 VFS 中的 struct inode 和 struct dentry 等 VFS 层次的结构体直接实现文件系统中的各种对象；同时在每个文件系统的私有数据 (如 dentry->d_fsdata 等位置) 上，使用了称为 struct sysfs_dirent 的结构用于表示 /sys 中的每一个目录项。
```
struct sysfs_dirent {
        atomic_t                s_count;
        atomic_t                s_active;
        struct sysfs_dirent     *s_parent;
        struct sysfs_dirent     *s_sibling;
        const char              *s_name;

        union {
                struct sysfs_elem_dir           s_dir;
                struct sysfs_elem_symlink       s_symlink;
                struct sysfs_elem_attr          s_attr;
                struct sysfs_elem_bin_attr      s_bin_attr;
        };

        unsigned int            s_flags;
        ino_t                   s_ino;
        umode_t                 s_mode;
        struct iattr            *s_iattr;
};
```
在上面的 kobject 对象中可以看到有向 sysfs_dirent 的指针，因此在sysfs中是用同一种 struct sysfs_dirent 来统一设备模型中的 kset/kobject/attr/attr_group.

具体在数据结构成员上， sysfs_dirent 上有一个 union 共用体包含四种不同的结构，分别是目录、符号链接文件、属性文件、二进制属性文件；其中目录类型可以对应 kobject，在相应的 s_dir 中也有对 kobject 的指针，因此在内核数据结构， kobject 与 sysfs_dirent 是互相引用的；
有了这些概念，再来回头看 之前 sysfs 目录层次图 所表达的 /sys 目录结构就是非常清晰明了:
* 在 /sys 根目录之下的都是 kset，它们组织了 /sys 的顶层目录视图；
* 在部分 kset 下有二级或更深层次的 kset；
* 每个 kset 目录下再包含着一个或多个 kobject，这表示一个集合所包含的 kobject 结构体；
* 在 kobject 下有属性(attrs)文件和属性组(attr_group)，属性组就是组织属性的一个目录，它们一起向用户层提供了表示和操作这个 kobject 的属性特征的接口；
* 在 kobject 下还有一些符号链接文件，指向其它的 kobject，这些符号链接文件用于组织上面所说的 device, driver, bus_type, class, module 之间的关系；
* 不同类型如设备类型的、设备驱动类型的 kobject 都有不同的属性，不同驱动程序支持的 sysfs 接口也有不同的属性文件；而相同类型的设备上有很多相同的属性文件；
注意，此表内容是按照最新开发中的 2.6.28 内核的更新组织的，在附录资源如 LDD3 等位置中有提到 sysfs 中曾有一种管理对象称为 subsys (子系统对象)，在最新的内核中经过重构认为它是不需要的，它的功能完全可以由 kset 代替，也就是说 sysfs 中只需要一种管理结构是 kset，一种代表具体对象的结构是 kobject，在 kobject 下再用属性文件表示这个对象所具有的属性；

## 常见 sysfs 属性的功能
### 使用设备(PCI)的 sysfs 属性文件
以桌面系统上的视频卡为例，列举它对应的 kobject 上的属性文件的对应用途;
一般来说，在 Linux 桌面上都有视频卡以支持 Xorg 软件包作为 XWindow 服务器来运行，因此 先找到 Xorg 的进程号，查看这个进程所使用的所有文件（注意查看这个进程属性需要 root 用户权限）；
```bash
# ps xfa |grep Xorg
 2001 tty1     Ss+    2:24      \_ /usr/bin/Xorg :0 -nr -verbose -auth \
/var/run/gdm/auth-for-gdm-NPrkZK/database -nolisten tcp vt1
# lsof -nP -p 2001
Xorg    2001 root  mem    REG        8,3    617732     231033 \
/usr/lib/xorg/modules/drivers/sis_drv.so
[...]
Xorg    2001 root  mem    REG        0,0 134217728       5529 \
/sys/devices/pci0000:00/0000:00:01.0/0000:01:00.0/resource0
Xorg    2001 root  mem    REG        0,0    131072       5531 \
/sys/devices/pci0000:00/0000:00:01.0/0000:01:00.0/resource1
[...]
Xorg    2001 root    7u   REG        0,0       256       5504 \
/sys/devices/pci0000:00/0000:00:00.0/config
Xorg    2001 root    8u  unix 0xdbe66000       0t0       8756 socket
Xorg    2001 root    9u   REG        0,0       256       5528 \
/sys/devices/pci0000:00/0000:00:01.0/0000:01:00.0/config
```
此 Xorg 服务器是以内存映射（mem）方式打开了 “/sys/devices/pci0000:00/0000:00:01.0/0000:01:00.0/resource0" 和 "/sys/devices/pci0000:00/0000:00:01.0/0000:01:00.0/resource1" ，同时以文件读写形式 (7u,9u) 打开了 "/sys/devices/pci0000:00/0000:00:00.0/config" 和 "/sys/devices/pci0000:00/0000:00:01.0/0000:01:00.0/config"

事实上， PCI 设备对应的 kobject 目录下的 config 正是代表PCI设备的 “配置空间”，对于普通 PCI (非PCI-E)设备而言，其配置空间大小一般是 256字节，这个空间可以使用十六进制工具 dump 出来，如下。(有关 PCI 设备本身的三种地址空间，请参考附录 LDD3)
```
# hexdump -C /sys/devices/pci0000:00/0000:00:01.0/0000:01:00.0/config
00000000  39 10 30 63 03 00 30 02  00 00 00 03 00 00 00 80  |9.0c..0.........|
00000010  08 00 00 d8 00 00 00 e1  01 d0 00 00 00 00 00 00  |................|
00000020  00 00 00 00 00 00 00 00  00 00 00 00 19 10 30 1b  |..............0.|
00000030  00 00 00 00 40 00 00 00  00 00 00 00 00 00 00 00  |....@...........|
00000040  01 50 02 06 00 00 00 00  00 00 00 00 00 00 00 00  |.P..............|
00000050  02 00 30 00 0b 02 00 ff  00 00 00 00 00 00 00 00  |..0.............|
00000060  00 00 00 00 00 00 00 00  00 00 00 00 00 00 00 00  |................|
*
00000100
```
这个空间正好是 256字节大小，熟悉 PCI 的人们还可以知道，从 PCI 配置空间可以读到有关此 PCI 设备的很多有用信息，如厂商代码，设备代码，IRQ 号码等；前四个字节 0x39 0x10 0x30 0x63 就是按小端(little endian)存放的2个短整数，因此其 PCI 厂商号码和 PCI 设备号码分别是 0x1039 和 0x6330
```
# lspci -v -d 1039:6330
01:00.0 VGA compatible controller: Silicon Integrated Systems [SiS] 661/741/760 PCI/AGP \
or 662/761Gx PCIE VGA Display Adapter (prog-if 00 [VGA controller])
	Subsystem: Elitegroup Computer Systems Device 1b30
	Flags: 66MHz, medium devsel
	BIST result: 00
	Memory at d8000000 (32-bit, prefetchable) [size=128M]
	Memory at e1000000 (32-bit, non-prefetchable) [size=128K]
	I/O ports at d000 [size=128]
	Capabilities: [40] Power Management version 2
	Capabilities: [50] AGP version 3.0
```
在 PCI 设备上除了有 config 是配置空间对用户的接口以外，还有 resource{0,1,2,...} 是资源空间，对应着 PCI 设备的可映射内存空间；此外 PCI 设备还提供了很多接口，全部列表如下：
```
# ls -lU /sys/devices/pci0000:00/0000:00:01.0/0000:01:00.0/
总计 0
-rw-r--r-- 1 root root      4096 12-09 00:28 uevent
-r--r--r-- 1 root root      4096 12-09 00:27 resource
-r--r--r-- 1 root root      4096 12-09 00:27 vendor
-r--r--r-- 1 root root      4096 12-09 00:27 device
-r--r--r-- 1 root root      4096 12-09 00:28 subsystem_vendor
-r--r--r-- 1 root root      4096 12-09 00:28 subsystem_device
-r--r--r-- 1 root root      4096 12-09 00:27 class
-r--r--r-- 1 root root      4096 12-09 00:27 irq
-r--r--r-- 1 root root      4096 12-09 00:28 local_cpus
-r--r--r-- 1 root root      4096 12-09 00:28 local_cpulist
-r--r--r-- 1 root root      4096 12-09 00:28 modalias
-rw------- 1 root root      4096 12-09 00:28 enable
-rw-r--r-- 1 root root      4096 12-09 00:28 broken_parity_status
-rw-r--r-- 1 root root      4096 12-09 00:28 msi_bus
lrwxrwxrwx 1 root root         0 12-09 00:28 subsystem -> ../../../../bus/pci
drwxr-xr-x 2 root root         0 12-09 00:28 power
-rw-r--r-- 1 root root       256 12-08 23:03 config
-rw------- 1 root root 134217728 12-08 23:03 resource0
-rw------- 1 root root 134217728 12-09 00:28 resource0_wc
-rw------- 1 root root    131072 12-08 23:03 resource1
-rw------- 1 root root       128 12-09 00:28 resource2
-r-------- 1 root root         0 12-09 00:28 rom
```
可以看到很多其它属性文件，这些属性文件的权限位也都是正确的，有 w 权限位的才是可以写入。其中大小为 4096字节的属性一般是纯文本描述的属性，可以直接 cat 读出和用 echo 字符串的方法写入；其它非 4096字节大小的一般是二进制属性，类似于上面的 config 属性文件；关于纯文本属性和二进制属性，在下文 编程实践：添加sysfs支持 一节会进一步说明。


从 vendor, device, subsystem_vendor, subsystem_device, class, resource 这些只读属性上分别可以读到此 PCI 设备的厂商号、设备号、子系统厂商号、子系统设备号、PCI类别、资源表等，这些都是相应 PCI 设备的属性，其实就是直接从 config 二进制文件读出来，按照配置空间的格式读出这些号码；
使用 enable 这个可写属性可以禁用或启用这个 PCI 设备，设备的过程很直观，写入1代表启用，写入0则代表禁用；
subsystem 和 driver 符号链接文件分别指向对应的 sysfs 位置；(这里缺少 driver 符号链接说明这个设备当前未使用内核级的驱动程序)
resource0, resource0_wc, resource1, resource2 等是从"PCI 配置空间"解析出来的资源定义段落分别生成的，它们是 PCI 总线驱动在 PCI 设备初始化阶段加上去的，都是二进制属性，但没有实现读写接口，只支持 mmap 内存映射接口，尝试进行读写会提示 IO 错误，其中 _wc 后缀表示 "合并式写入(write combined)" ，它们用于作应用程序的内存映射，就可以访问对应的 PCI 设备上相应的内存资源段落；
有了 PCI 核心对 sysfs 的完善支持，每个设备甚至不用单独的驱动程序，如这里的 "0000:01:00.0" 不需要一个内核级的驱动程序，有了 PCI 核心对该设备的配置空间发现机制，可以自动发现它的各个不同段落的资源属性，在 Xorg 应用程序中可以直接以 "/usr/lib/xorg/modules/drivers/sis_drv.so" 这个用户空间的驱动程序对其进行映射，就可以直接操作此视频卡了；
有了这一个 PCI 设备的示例可以知道，有了一个 PCI 设备的 /sys/devices/ 设备对象，去访问它的各项属性和设置属性都非常简单。


### 使用 uevent
在 sysfs 下的很多 kobject 下都有 uevent 属性，它主要用于内核与 udev (自动设备发现程序)之间的一个通信接口；从 udev 本身与内核的通信接口 netlink 协议套接字来说，它并不需要知道设备的 uevent 属性文件，但多了 uevent 这样一个接口，可用于 udevmonitor 通过内核向 udevd (udev 后台程序)发送消息，也可用于检查设备本身所支持的 netlink 消息上的环境变量，这个特性一般用于开发人员调试 udev 规则文件， udevtrigger 这个调试工具本身就是以写各设备的 uevent 属性文件实现的。
这些 uevent 属性文件一般都是可写的，其中 /sys/devices/ 树下的很多 uevent 属性在较新内核下还支持可读：
```
# find /sys/ -type f -name uevent -ls
    11    0 -rw-r--r--   1 root     root         4096 12月 12 21:10 \
/sys/devices/platform/uevent
  1471    0 -rw-r--r--   1 root     root         4096 12月 12 21:10 \
/sys/devices/platform/pcspkr/uevent
  3075    0 -rw-r--r--   1 root     root         4096 12月 12 21:10 \
/sys/devices/platform/vesafb.0/uevent
  3915    0 -rw-r--r--   1 root     root         4096 12月 12 21:10 \
/sys/devices/platform/serial8250/uevent
  3941    0 -rw-r--r--   1 root     root         4096 12月 12 21:10 \
/sys/devices/platform/serial8250/tty/ttyS2/uevent
  3950    0 -rw-r--r--   1 root     root         4096 12月 12 21:10 \
/sys/devices/platform/serial8250/tty/ttyS3/uevent
  5204    0 -rw-r--r--   1 root     root         4096 12月 12 21:10 \
/sys/devices/platform/i8042/uevent
[...]
   912    0 -rw-r--r--   1 root     root         4096 12月 12 21:17 \
/sys/devices/pci0000:00/0000:00:02.5/uevent
[...]
```
上面截取的最后一个是 SCSI 硬盘控制器设备的 uevent 属性文件，这些 /devices/ 属性文件都支持写入，当前支持写入的参数有 "add","remove","change","move","online","offline"。如，写入 "add"，这样可以向 udevd 发送一条 netlink 消息，让它再重新一遍相关的 udev 规则文件；这个功能对开发人员调试 udev 规则文件很有用。
```
# echo add > /sys/devices/pci0000:00/0000:00:02.5/uevent
```
### 使用驱动(PCI)的 sysfs 属性文件， bind, unbind 和 new_id
在设备驱动 /sys/bus/*/driver/... 下可以看到很多驱动都有 bind, unbind, new_id 这三个属性，
```
# find /sys/bus/*/drivers/ -name bind -ls
..
```

每一个设备驱动程序在程序内以某种方式注明了可用于哪些硬件，如所有的 PCI 驱动都使用 MODULE_DEVICE_TABLE 声明了所能驱动的 PCI 硬件的 PCI 设备号。但驱动程序不能预知未来，未来生产的新的硬件有可能兼容现有硬件的工作方式，就还可以使用现有硬件驱动程序来工作。在 bind 和 unbind 发明以前，这种情况除了修改 PCI 设备驱动程序的 DEVICE_TABLE 段落，重新编译驱动程序，以外别无他法，在 2.6 内核上添加了 bind 和 unbind 之后可以在不重新编译的情况下对设备和驱动之间进行手工方式地绑定。

而且对于有些硬件设备可以有多份驱动可用，但任何具体时刻只能有一个驱动程序来驱动这个硬件，这时可以使用 bind/unbind 来强制使用和不使用哪一个驱动程序；(注意关于多种驱动程序的选择，更好的管理方法是使用 modprobe.conf 配置文件，需要重启才生效，而 bind/unbind 提供的是一种临时的无需重启立即生效的途径；)

使用它们可以强制绑定某个设备使用或强制不使用某个驱动程序，操作方法就是通过 bind 和 unbind 接口。

```
# find /sys/ -type f \( -name bind -or -name unbind -or -name new_id \) -ls
    69    0 -rw-r--r--   1 root     root         4096 12月 12 22:12 \
/sys/devices/virtual/vtconsole/vtcon0/bind
  3072    0 --w-------   1 root     root         4096 12月 12 22:15 \
/sys/bus/platform/drivers/vesafb/unbind
[...]
  6489    0 --w-------   1 root     root         4096 12月 12 22:09 \
/sys/bus/pci/drivers/8139too/unbind
  6490    0 --w-------   1 root     root         4096 12月 12 22:09 \
/sys/bus/pci/drivers/8139too/bind
  6491    0 --w-------   1 root     root         4096 12月 12 22:15 \
/sys/bus/pci/drivers/8139too/new_id
```
这个结果中特别提到了 8139too 这份驱动程序的这三个属性文件，
```
# find /sys/bus/pci/drivers/8139too/ -ls
  6435    0 drwxr-xr-x   2 root     root            0 12月 12 22:08 \
/sys/bus/pci/drivers/8139too/
  6436    0 lrwxrwxrwx   1 root     root            0 12月 12 22:08 \
/sys/bus/pci/drivers/8139too/0000:00:0e.0 -> ../../../../devices/pci0000:00/0000:00:0e.0
  6485    0 lrwxrwxrwx   1 root     root            0 12月 12 22:08 \
/sys/bus/pci/drivers/8139too/module -> ../../../../module/8139too
  6488    0 --w-------   1 root     root         4096 12月 12 22:08 \
/sys/bus/pci/drivers/8139too/uevent
  6489    0 --w-------   1 root     root         4096 12月 12 22:08 \
/sys/bus/pci/drivers/8139too/unbind
  6490    0 --w-------   1 root     root         4096 12月 12 22:08 \
/sys/bus/pci/drivers/8139too/bind
  6491    0 --w-------   1 root     root         4096 12月 12 22:08 \
/sys/bus/pci/drivers/8139too/new_id
# echo 0000:00:0e.0 > /sys/bus/pci/drivers/8139too/unbind
-bash: echo: write error: 没有那个设备
# ip addr
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 16436 qdisc noqueue state UNKNOWN 
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
    inet 127.0.0.1/8 scope host lo
2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc pfifo_fast state \
UNKNOWN qlen 1000
    link/ether 00:14:2a:d1:16:72 brd ff:ff:ff:ff:ff:ff
    inet 192.168.1.102/24 brd 192.168.1.255 scope global eth0
3: bond0: <BROADCAST,MULTICAST,MASTER> mtu 1500 qdisc noop state DOWN 
    link/ether 00:00:00:00:00:00 brd ff:ff:ff:ff:ff:ff
# echo -n 0000:00:0e.0 > /sys/bus/pci/drivers/8139too/unbind
# ip addr
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 16436 qdisc noqueue state UNKNOWN 
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
    inet 127.0.0.1/8 scope host lo
3: bond0: <BROADCAST,MULTICAST,MASTER> mtu 1500 qdisc noop state DOWN 
    link/ether 00:00:00:00:00:00 brd ff:ff:ff:ff:ff:ff
# echo -n 0000:00:0e.0 > /sys/bus/pci/drivers/8139too/bind
# ip addr
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 16436 qdisc noqueue state UNKNOWN 
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
    inet 127.0.0.1/8 scope host lo
3: bond0: <BROADCAST,MULTICAST,MASTER> mtu 1500 qdisc noop state DOWN 
    link/ether 00:00:00:00:00:00 brd ff:ff:ff:ff:ff:ff
4: eth0: <BROADCAST,MULTICAST> mtu 1500 qdisc noop state DOWN qlen 1000
    link/ether 00:14:2a:d1:16:72 brd ff:ff:ff:ff:ff:ff
```
这一段操作过程演示了如何对 PCI 设备 "0000:00:0e.0" 强制取消绑定 "8139too" 驱动和强制绑定 "8139too" 驱动：
对 unbind 属性写入总线号码(bus_id)即是强制取消绑定；
对 bind 属性写入总线号码(bus_id)即是强制绑定；
注意，它要求的写入的是总线号码，对应于PCI设备的总线号码是按照 "domain(4位):bus(2位):slot(2位):function号(不限)" 的方式组织，是可以从其设备 kobject 节点上找到，而其它类型的总线有各自不同的规则；
请特别注意： 在这一个例子中， "echo 0000:00:0e.0 > /sys/bus/pci/drivers/8139too/unbind" 这第一个写入命令以 "No such device" 为错误退出，而后续的 "echo -n" 命令则可以成功。这是因为内核在对总线号码进行匹配时过于严格了，通常的 "echo" 命令写入一个字符串会以一个换行符结束输出，内核所接收到的是带有这个换行符的 bus_id 字符串，将它与内核数据结构中的真正的 bus_id 字符串相比较，当然不能找到；所幸的是，这个问题在最新的 2.6.28 开发中的内核上已已经解决，它将这个比较函数改为一个特殊实现的字符串比较，自动忽略结尾处的换行符，在 2.6.28-rc6 内核上测试，不带"-n"参数的 echo 命令已经可以写入成功。
而 new_id 属性文件也可以以另一种途径解决新的设备号问题：它是一个只写的驱动属性，可用于向其中写新的设备号。它支持写入 2至7个十六进制整形参数，分别代表 vendor, device, subvendor, subdevice, class, class_mask, driver_data 最少为 2个是因为一个 PCI设备主要以厂商号(vendor)和设备号(device)所唯一标定，其它 5个参数如果不输入则缺省值为 PCI_ANY_ID(0xffff)。

```
5441    0 --w-------   1 root     root         4096 12月 14 18:15 \
/sys/bus/pci/drivers/8139too/new_id
```
从 8139too 驱动上可以看到它当前所静态支持的设备号码列表，其中包括当前系统中的设备 10ec:8139, 假设未来有一款 8140 设备也满足 8139 设备的硬件通讯协议，于是可以使用 8139too 驱动程序来驱动它，操作如下

```
# echo '10ec 8140' > /sys/bus/pci/drivers/8139too/new_id
```
这在不更新驱动程序的情况下调试设备很有用处。

### 使用 scsi_host 的 scan 属性
在具有使用 SCSI 总线连接的主机上，与 PCI类似的是也采用四个号码作为一组来描述一个设备，其中位于最顶层的是 scsi_host。
我们从设备类别 /class/为起点来探索：
```
# ls -lU /sys/class/scsi_host
总计 0
lrwxrwxrwx 1 root root 0 12-13 01:59 host0 -> \
../../devices/pci0000:00/0000:00:02.5/host0/scsi_host/host0
lrwxrwxrwx 1 root root 0 12-13 01:59 host1 -> \
../../devices/pci0000:00/0000:00:02.5/host1/scsi_host/host1
```
注意这是 2.6.27 内核的最新变化，在 /sys/class/ 下的都改为符号链接，真实的 kobject 都存在于 /sys/devices/ 中；我们这里探索其中的 host0 这个 SCSI 控制器：
```
# readlink -f /sys/class/scsi_host/host0
/sys/devices/pci0000:00/0000:00:02.5/host0/scsi_host/host0
# ls -lU /sys/devices/pci0000:00/0000:00:02.5/host0/scsi_host/host0
总计 0
-rw-r--r-- 1 root root 4096 12-13 02:02 uevent
lrwxrwxrwx 1 root root    0 12-13 02:02 subsystem -> ../../../../../../class/scsi_host
lrwxrwxrwx 1 root root    0 12-13 02:02 device -> ../../../host0
-r--r--r-- 1 root root 4096 12-13 02:02 unique_id
-r--r--r-- 1 root root 4096 12-13 02:02 host_busy
-r--r--r-- 1 root root 4096 12-13 02:02 cmd_per_lun
-r--r--r-- 1 root root 4096 12-13 02:02 can_queue
-r--r--r-- 1 root root 4096 12-13 02:02 sg_tablesize
-r--r--r-- 1 root root 4096 12-13 02:02 unchecked_isa_dma
-r--r--r-- 1 root root 4096 12-13 02:02 proc_name
--w------- 1 root root 4096 12-13 02:02 scan
-rw-r--r-- 1 root root 4096 12-13 02:02 state
-rw-r--r-- 1 root root 4096 12-13 02:02 supported_mode
-rw-r--r-- 1 root root 4096 12-13 02:02 active_mode
-r--r--r-- 1 root root 4096 12-13 02:02 prot_capabilities
-r--r--r-- 1 root root 4096 12-13 02:02 prot_guard_type
drwxr-xr-x 2 root root    0 12-13 02:02 power
```
对这些属性文件解释如下：
有四个 SCSI 特有的可写参数： scan,state,supported_mode,active_mode；可以向其中写入不同的参数来控制此 SCSI 控制器的各种状态；
其它一些可读属性用于读取这个 SCSI 控制器的一些当前值；
其中的 scan 属性文件在调试一些 SCSI 硬件驱动时很有用，它是只写的，可以写入三个至四个以空格分开的整数，用于分别指定对应的 host, channel, id, lun 进行重新搜索。且这个 scan 属性支持以"-"作为通配符，如以下命令可以执行让整个 scsi_host 进行重新搜索，这个功能用于调试某些对热挺拔实现不完善的 SCSI 驱动程序很有用：
```
# echo '- - -' >/sys/devices/pci0000:00/0000:00:02.5/host0/scsi_host/host0/scan
```
### 内核模块中的 sysfs 属性文件
以一个 8139too 模块为例解释在这个 kboject 下每一个属性的用途；
```
# find /sys/module/8139too/ -ls
  6408    0 -r--r--r--   1 root     root         4096 12月 13 02:17 \
/sys/module/8139too/version
  6412    0 drwxr-xr-x   2 root     root            0 12月 13 02:17 \
/sys/module/8139too/sections
  6433    0 drwxr-xr-x   2 root     root            0 12月 13 02:17 \
/sys/module/8139too/notes
  6434    0 -r--r--r--   1 root     root           36 12月 13 02:17 \
/sys/module/8139too/notes/.note.gnu.build-id
  6486    0 drwxr-xr-x   2 root     root            0 12月 13 02:17 \
/sys/module/8139too/drivers
  6487    0 lrwxrwxrwx   1 root     root            0 12月 13 02:17 \
/sys/module/8139too/drivers/pci:8139too -> ../../../bus/pci/drivers/8139too
```
其中的属性文件都是只读的，用于提供信息。从 version, srcversion 上可以了解到这个模块所声明的版本号，源码版本号， refcnt 是模块引用计数， sections 属性组中有一些模块加载至内存的相应节信息， drivers/ 目录中是对所提供的驱动的链接；
因为模块是内核驱动编程的最佳选择，而一个模块有可能提供多个驱动程序，因而在未知一个设备在用哪一个驱动的情况下可以先从 /sys/module/ 查找相应模块的情况，再从 drivers/ 发现出真正的驱动程序。或者也可以完全反过来利用这些信息，先用 lspci/lshw 等工具找到 /sys/devices/ 下的设备节点，再从其设备的 driver 链接找到 /sys/bus/*/drivers/ 下的 device_driver, 再从 device_driver 下的 module 链接找到 /sys/module/*/，这样就可以得到已加载模块中空间是哪一个模块在给一个设备提供驱动程序。

### 更多 sysfs 属性文件
以上所举的例子仅仅是一些常见的 sysfs 属性用法，实际的系统中还常常有很多其它的从未见过的 sysfs 属性，因此只有举例是不够的，即使维护了一份 sysfs 属性用法参考大全也不够，未来的内核版本还会出现新的 sysfs 属性，因此还必须了解 Linux 内核代码以找到实现这些属性的代码位置，以学会在没有相应属性文档的情况从内核源代码来分析其 sysfs 属性功能。

### 一个实例
参考博客：

## 小结
sysfs 给应用程序提供了统一访问设备的接口，但可以看到， sysfs 仅仅是提供了一个可以统一访问设备的框架，但究竟是否支持 sysfs 还需要各设备驱动程序的编程支持；在 2.6 内核诞生 5年以来的发展中，很多子系统、设备驱动程序逐渐转向了 sysfs 作为与用户空间友好的接口，但仍然也存在大量的代码还在使用旧的 proc 或虚拟字符设备的 ioctl 方式；如果仅从最终用户的角度来说， sysfs 与 proc 都是在提供相同或类似的功能，对于旧的 proc 代码，没有绝对的必要去做 proc 至 sysfs 的升级；因此在可预见的将来， sysfs 会与 proc, debugfs, configfs 等共存很长一段时间。




