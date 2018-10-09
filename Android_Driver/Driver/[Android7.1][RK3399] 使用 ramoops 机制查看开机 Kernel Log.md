---
title: [Android7.1][RK3399] 使用 ramoops 机制查看开机 Kernel Log
tags: android
grammar_cjkRuby: true
---

Platform: RK3399 
OS: Android 7.1 
Kernel: v4.4.83

[TOC]

## 基本概念

### pstore
> pstore是persistent storage的缩写。内核发生异常时如果能将日志等信息保存下来不丢失，那么就可以通过这些信息来定位问题。
不同的平台可以提供的存储位置不同，例如有些平台支持硬盘，有些不支持。除了平台差异，异常类型也决定了在发生异常时该存储位置是否还可用。
pstore 的目标是提供一套通用的接口用来存储异常信息。pstore以文件系统的形式提供用户空间接口，可以通过mount命令挂载到指定目录下边，如xxx\pstore，那么保存的信息将以文件的形式出现在该目录下，可以使用文件读操作获取调试信息，通过删除操作清除调试信息。

在内核中使用pstore前需要首先初始化一个pstore_info类型的结构体变量，然后调用int pstore_register(struct pstore_info * )注册。
pstore_info结构体中有些变量可以不需要赋值，但是读写，删除用到的函数指针需要赋值。
pstore在内核中的开关是CONFIG_PSTORE，在2.6.39版本中第一次合入主线，3.10.40中的ramoops使用的就是pstore机制。pstore提供的是一套可扩展的机制，目前提供的类型包括以下四种：
PSTORE_TYPE_DMESG表示内核日志，PSTORE_TYPE_MCE表示硬件错误，PSTORE_TYPE_CONSOLE表示控制台输出，PSTORE_TYPE_FTRACE表示函数调用序列。

### ramoops
> ramoops 指的是采用ram保存oops信息的一个功能，这个功能最开始不是基于pstore实现的，在3.10.40中，它已经采用pstore机制实现了，在内核开关中用3个开关控制：PSTORE_CONSOLE控制是否保存控制台输出，PSTORE_FTRACE控制是否保存函数调用序列，PSTORE_RAM控制是否保存panic/oops信息。

使用ramoops功能也很简单，只要打开开关，注册一个名字ramoops的platform_device就可以了,platform_data要指向一个类型为ramoops_platform_data的变量地址。
ramoops_platform_data结构体中mem_size表示总共的ram大小为多大，mem_address表示ram的起始物理地址，record_size表示记录oops/panic单次记录的buffer大小，console_size表示控制台输出buffer的大小，ftrace_size表示函数调用序列buffer的大小，所有这些buffer都是整个mem_size的一部分，首先预留console_size和ftrace_size，剩下的空间能放几个record_size就保存几次的oops/panic记录，在产生oops/panic时后边的记录会冲掉前边的记录，这个和console/ftrace都是一样的，都是保留最新的。
dump_oops为1表示oops和panic都记录，为0表示仅记录panic。

控制台日志位于 pstore 目录下的console-ramoops文件中，因为采用console机制，该文件中的日志信息也受printk level控制，并不一定是全的。
oops/panic日志位于 pstore 目录下的dmesg-ramoops-x文件中，根据缓冲区大小可以有多个文件，x从0开始。
函数调用序列日志位于 pstore 目录下的ftrace-ramoops文件中。

在kernel3.10.40中，pstore和ramoops的代码都位于/kernel/fs/pstore/目录。
ramoops初始化函数位于ram.c中:postcore_initcall(ramoops_init);使用postcore_initcall的好处是更早，这样可以更早的记录异常。

### RK 平台中的 ramoops
由 defconfig 中的宏来控制 (默认开启)
CONFIG_PSTORE
CONFIG_PSTORE_CONSOLE
CONFIG_PSTORE_PMSG
CONFIG_PSTORE_RAM


## Kernel
### defconfig
```
CONFIG_PSTORE=y
CONFIG_PSTORE_CONSOLE=y
CONFIG_PSTORE_PMSG=y
CONFIG_PSTORE_RAM=y
```

### driver
```
kernel/fs/pstore
```

### dts
配置内存地址
```
ramoops_mem: ramoops_mem {
    reg = <0x0 0x110000 0x0 0xf0000>;
    reg-names = "ramoops_mem";
};

ramoops {
    compatible = "ramoops";
    record-size = <0x0 0x20000>;
    console-size = <0x0 0x80000>;
    ftrace-size = <0x0 0x00000>;
    pmsg-size = <0x0 0x50000>;
    memory-region = <&ramoops_mem>;
};
```

```
- compatible: must be "ramoops"
- memory-region: phandle to a region of memory that is preserved between reboots
Optional properties:
- ecc-size: enables ECC support and specifies ECC buffer size in bytes (defaults to no ECC)
- record-size: maximum size in bytes of each dump done on oops/panic (defaults to 0)
- console-size: size in bytes of log buffer reserved for kernel messages (defaults to 0)
- ftrace-size: size in bytes of log buffer reserved for function tracing and profiling (defaults to 0)
- pmsg-size: size in bytes of log buffer reserved for userspace messages (defaults to 0)
- unbuffered: if present, use unbuffered mappings to map the reserved region (defaults to buffered mappings)
- no-dump-oops: if present, only dump panics (defaults to panics and oops) 
```

### mount when boot
system/core/rootdir/init.rc
```
# pstore/ramoops previous console log
mount pstore pstore /sys/fs/pstore
chown system log /sys/fs/pstore/console-ramoops
chmod 0440 /sys/fs/pstore/console-ramoops
chown system log /sys/fs/pstore/pmsg-ramoops-0
chmod 0440 /sys/fs/pstore/pmsg-ramoops-0
```
