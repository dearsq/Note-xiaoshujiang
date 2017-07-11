---
title: [Linux] 统一设备模型
tags: Linux,统一设备模型
grammar_cjkRuby: true
---
统一设备模型是  Linux 2.5 内核开始开发的一套新设备模型。目的是为了**对计算机上所有的设备进行统一的操作和表示**。
这个模型是在分析了 PCI 和 USB 的总线驱动过程中得到的，他们两种总线类型能代表当前系统中大多数设备类型，它们都有完善的热插拔机制和电源管理的支持，也有级联机制的支持，以桥接 PCI/USB 总线控制器的方式可以支持更多的设备。

比如典型的 PC 系统中， CPU 控制的是 PCI 总线，USB 总线是以一个 PCI-USB 桥的形式接在 PCI 总线设备上，外部 USB 再接在 USB 总线设备上。
当 计算机 挂起（suspend）时，Linux 内核应该以“外部USB->USB总线->PCI总线设备”的顺序通知每一个设备将电源挂起;
执行恢复（resume）时，则以相反的顺序通知;
反之如果不按此顺序将有设备得不到正确 电源状态变迁的通知，将无法正常工作。

基本结构：
|类型|所包含内容|对应内核数据结构|对应/sys项目|
|--|--|--|--|
|设备<br>Devices|设备是此模型中最基本的类型，以设备本身的链接按层次组织|struct device|/sys/devices/ * / * / .../ |
|设备驱动<br>Device Drivers|在一个系统中安装多个相同设备，只需要一份驱动程序的支持|struct device_driver|/sys/bus/pci/drivers/ * /|
|总线类型<br>Bus Types|在整个总线级别上对如此总线上连接的所有设备进行管理|struct bus_type| /sys/bus/ * / |
|设备类别<br>Device Classes|这是按照功能进行分类组织的设备层次树；如 USB 接口和 PS/2 接口的鼠标都是输入设备，都会出现在 /sys/class/input/ 下	| struct class |/sys/class/ * /|

从内核实现它们时所使用的数据结构来说，Linux 统一设备模型又是以两种**基本数据结构**进行树型和链表型结构组织的。
* kobject  在 Linux 设备模型中最基本的对象，它的功能是提供引入计数和维持父子（parent）结构 、平级（sibling）目录关系，上面的 device ，device_driver 等各对象都是以 kobject 基础功能之上实现的;
```
struct kobject {
	const char			*name;
    struct list_head	entry;
    struct kobject          *parent;
    struct kset             *kset;
    struct kobj_type        *ktype;
    struct sysfs_dirent     *sd;
    struct kref             kref;
    unsigned int state_initialized:1;
	unsigned int state_in_sysfs:1;
    unsigned int state_add_uevent_sent:1;
    unsigned int state_remove_uevent_sent:1;
};
```
其中 struct kref 内含一个 atuomic_t 类型用于引用计数，parent 是单个指向 父节点的指针，entry 用于父 kset 以链表结构将 kobject 维护成双向链表。
*  kset：它用来对同类型对象提供一个包装集合，在内核数据结构上它也是由内嵌(继承)一个 kboject 实现，因而它同时也是一个 kobject ，具有 kobject 的全部功能；
```
struct kset {
        struct list_head list;
        spinlock_t list_lock;
        struct kobject kobj;
        struct kset_uevent_ops *uevent_ops;
};
```
其中的 struct list_head list 用于将集合中的 kobject 按 struct list_head entry 维护成双向链表；
