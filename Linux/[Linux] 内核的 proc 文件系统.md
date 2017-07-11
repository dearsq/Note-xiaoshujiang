---
title: [Linux] 内核的 proc 文件系统
tags: Linux
grammar_cjkRuby: true
---
内核现在采用的是 sysfs 文件系统。
在 sysfs 诞生之前我们采用的是 proc 文件系统。
sysfs 是一个与 /proc 类似的文件系统，但是它的组织更好（从 /proc 中学习了很多教训）。不过 /proc 已经确立了自己的地位，因此即使 sysfs 与 /proc 相比有一些优点，/proc 也依然会存在。本文对 /proc 文件系统一些基础的知识进行归纳和整理。

另外还有一个 debugfs 文件系统，不过（顾名思义）它提供的更多是调试接口。debugfs 的一个优点是它将一个值导出给用户空间非常简单（实际上这不过是一个调用而已）。


proc 是一个虚拟的文件系统，我们利用它实现 **Linux 内核空间与用户空间** 的通信。在 proc 文件系统中，我们可以将对虚拟文件的读写作为与内核中实体进行通信的一种手段，但是与普通文件不同的是，这些虚拟文件的内容都是动态创建的。

## proc 虚拟文件系统介绍
最初这个是为了提供有关文件系统中进程的信息。
后来因为很有用，内核中其他元素也用其报告信息，或进行动态运行配置。
/proc 文件系统包含了一些目录和虚拟文件。
虚拟文件向用户呈现内核中的信息，同时也是用户空间向内核发送信息的手段。
### 呈现内核信息
```shell
[root@younixPC]# ls /proc
1     2040  2347  2874  474          fb           mdstat      sys
104   2061  2356  2930  9            filesystems  meminfo     sysrq-trigger
113   2073  2375  2933  acpi         fs           misc        sysvipc
1375  21    2409  2934  buddyinfo    ide          modules     tty
1395  2189  2445  2935  bus          interrupts   mounts      uptime
1706  2201  2514  2938  cmdline      iomem        mtrr        version
179   2211  2515  2947  cpuinfo      ioports      net         vmstat
180   2223  2607  3     crypto       irq          partitions
181   2278  2608  3004  devices      kallsyms     pci
182   2291  2609  3008  diskstats    kcore        self
2     2301  263   3056  dma          kmsg         slabinfo
2015  2311  2805  394   driver       loadavg      stat
2019  2337  2821  4     execdomains  locks        swaps
```
左边是一系列数字编号的文件。每个实际上都是一个目录，表示系统中的一个进程。
由于在 GNU/Linux 中创建的第一个进程是 init 进程，因此它的 process-id 为 1。
然后对这个目录执行一个 ls 命令，这会显示很多文件。
```
[root@younixPC]# ls /proc/1
auxv     cwd      exe  loginuid  mem     oom_adj    root  statm   task
cmdline  environ  fd   maps      mounts  oom_score  stat  status  wchan
```
每个文件都提供了有关这个特殊进程的详细信息。例如，要查看 init 的 command-line 项的内容，只需对 cmdline 文件执行 cat 命令。
```
[root@younixPC]# cat /proc/1/cmdline
init [5]
```
/proc 中另外一些有趣的文件有：cpuinfo，它标识了处理器的类型和速度；pci，显示在 PCI 总线上找到的设备；modules，标识了当前加载到内核中的模块。
### 配置内核信息
下面对 /proc 中的一个虚拟文件进行读写（配置），首先检查内核的 TCP/IP 栈中 IP 转发的目前设置，然后启动这种功能。
```
root@younixPC:/# cat /proc/sys/net/ipv4/ip_forward
0
root@younixPC:/# echo "1" > /proc/sys/net/ipv4/ip_forward
root@younixPC:/# cat /proc/sys/net/ipv4/ip_forward
1
```
我们还可以用 sysctl 来配置这些内核条目。

## 内核模块简介
可加载内核模块（LKM）是用来展示 /proc 文件系统的一种方法。
它用来动态地向 Linux 内核添加或者删除代码。
LKM 也是 Linux 内核中为设备驱动程序和文件系统使用的一种机制。

如果一个驱动程序被直接编译到了内核中，那么即使这个驱动程序没有运行，它的代码和静态数据也会占据一部分空间。为了节省空间，我们采用动态模块编译的方法，将这个驱动程序编译成一个模块 .ko ，那么就只在其需要内存并将其加载进内核时才占用内存空间。

这样可以根据可用硬件和连接的设备来加载对应的模块。
### 一个最简单的 LKM 实例（simple-lkm.c）
```
#include <linux/module.h>
/* Defines the license for this LKM */
MODULE_LICENSE("GPL");
/* Init function called on module entry */
int my_module_init( void )
{
  printk(KERN_INFO "my_module_init called.  Module is now loaded.\n");
  return 0;
}
/* Cleanup function called on module exit */
void my_module_cleanup( void )
{
  printk(KERN_INFO "my_module_cleanup called.  Module is now unloaded.\n");
  return;
}
/* Declare entry and exit functions */
module_init( my_module_init );
module_exit( my_module_cleanup );
```
对于这个文件 simple-lkm.c 我们可以创建一个 Makefile ，其内容如下：
```
obj-m += simple-lkm.o
```
使用 make 来进行编译：
```
younix@younixPC:~/Code/Linux/Moudle$ make -C /usr/src/linux-headers-4.4.0-24-generic SUBDIRS=$PWD modules
make: Entering directory '/usr/src/linux-headers-4.4.0-24-generic'
  CC [M]  /home/younix/Code/Linux/Moudle/simple-lkm.o
  Building modules, stage 2.
  MODPOST 1 modules
  CC      /home/younix/Code/Linux/Moudle/simple-lkm.mod.o
  LD [M]  /home/younix/Code/Linux/Moudle/simple-lkm.ko
make: Leaving directory '/usr/src/linux-headers-4.4.0-24-generic'
```
结果生成了一个 simple-lkm.ko 的文件。
现在可以加载或者卸载这个模块了，然后可以查看其输出。
insmod 命令加载
rmmod 命令卸载
lsmod 显示当前的加载项
```bash
root@younixPC:/home/younix/Code/Linux/Moudle# insmod simple-lkm.ko
root@younixPC:/home/younix/Code/Linux/Moudle# lsmod
Module                  Size  Used by
simple_lkm             16384  0
root@younixPC:/home/younix/Code/Linux/Moudle# rmmod simple-lkm
```
另外，内核的输出进入了 内核的环形缓冲区中，并没有打印到 stdout 上。
使用 dmesg 工具或者使用 cat /proc/kmsg 来查看其内容。
```bash
root@younixPC:/home/younix/Code/Linux/Moudle# dmesg > dmesg.txt
my_module_init called.  Module is now loaded.
my_module_cleanup called.  Module is now unloaded.
```
## 将 LKM 集成到 /proc 文件系统中
这里简单地介绍一下在展示一个更有用的 LKM 时所使用的几个元素。
### 创建并删除 /proc 项
#### create_proc_entry 
创建一个虚拟文件。
这个函数可以接收一个文件名、一组权限和这个文件在 /proc 文件系统中出现的位置。create_proc_entry 的返回值是一个 proc_dir_entry 指针（或者为 NULL，说明在 create 时发生了错误）。然后就可以使用这个返回的指针来配置这个虚拟文件的其他参数，例如在对该文件执行读操作时应该调用的函数。create_proc_entry 的原型和 proc_dir_entry 结构中的一部分如下所示。
```C
struct proc_dir_entry *create_proc_entry( const char *name, mode_t mode,
                                             struct proc_dir_entry *parent );
struct proc_dir_entry {
	const char *name;			// virtual file name
	mode_t mode;				// mode permissions
	uid_t uid;				// File's user id
	gid_t gid;				// File's group id
	struct inode_operations *proc_iops;	// Inode operations functions
	struct file_operations *proc_fops;	// File operations functions
	struct proc_dir_entry *parent;		// Parent directory
	...
	read_proc_t *read_proc;			// /proc read function
	write_proc_t *write_proc;		// /proc write function
	void *data;				// Pointer to private data
	atomic_t count;				// use count
	...
};
```
#### read_proc / write_proc
插入对这个虚拟文件进行读写的函数。

#### remove_proc_entry 
需要提供文件名字符串，以及这个文件在 /proc 文件系统中的位置（parent）。
```C
void remove_proc_entry( const char *name, struct proc_dir_entry *parent );
```
parent 参数可以为 NULL（表示 /proc 根目录），也可以是很多其他值，这取决于我们希望将这个文件放到什么地方。下面列出了可以使用的其他一些父 proc_dir_entry，以及它们在这个文件系统中的位置。
|proc_dir_entry	|在文件系统中的位置|
|--|--|
|proc_root_fs|	/proc|
|proc_net|	/proc/net|
|proc_bus|	/proc/bus|
|proc_root_driver|	/proc/driver|

#### 写回调函数
write 函数原型
```c
int mod_write( struct file *filp, const char __user *buff,
               unsigned long len, void *data );
```
filp 参数实际上是一个打开文件结构（我们可以忽略这个参数）。
buff 参数是传递给您的字符串数据。缓冲区地址实际上是一个用户空间的缓冲区，因此我们不能直接读取它。
len 参数定义了在 buff 中有多少数据要被写入。
data 参数是一个指向私有数据的指针。
在这个模块中，我们声明了一个这种类型的函数来处理到达的数据。
我们使用 copy_from_user 函数来维护用户空间的数据。
#### 读回调函数
read 写回调函数
```c
int mod_read( char *page, char **start, off_t off,
              int count, int *eof, void *data );
```
page 参数是这些数据写入到的位置
count 定义了可以写入的最大字符数。
在返回多页数据（通常一页是 4KB）时，我们需要使用 start 和 off 参数。
当所有数据全部写入之后，就需要设置 eof（文件结束参数）。
与 write 类似，data 表示的也是私有数据。此处提供的 page 缓冲区在内核空间中。因此，我们可以直接写入，而不用调用 copy_to_user。

#### 其他有用的 proc 函数
proc_mkdir、symlinks 以及 proc_symlink 在 /proc 文件系统中创建目录。
对于只需要一个 read 函数的简单 /proc 项来说，可以使用 create_proc_read_entry，这会创建一个 /proc 项，并在一个调用中对 read_proc 函数进行初始化。
```c
/* Create a directory in the proc filesystem */
struct proc_dir_entry *proc_mkdir( const char *name,
                                     struct proc_dir_entry *parent );
/* Create a symlink in the proc filesystem */
struct proc_dir_entry *proc_symlink( const char *name,
                                       struct proc_dir_entry *parent,
                                       const char *dest );
/* Create a proc_dir_entry with a read_proc_t in one call */
struct proc_dir_entry *create_proc_read_entry( const char *name,
                                                  mode_t mode,
                                                  struct proc_dir_entry *base,
                                                  read_proc_t *read_proc,
                                                  void *data );
/* Copy buffer to user-space from kernel-space */
unsigned long copy_to_user( void __user *to,
                              const void *from,
                              unsigned long n );
/* Copy buffer to kernel-space from user-space */
unsigned long copy_from_user( void *to,
                                const void __user *from,
                                unsigned long n );
/* Allocate a 'virtually' contiguous block of memory */
void *vmalloc( unsigned long size );
/* Free a vmalloc'd block of memory */
void vfree( void *addr );
/* Export a symbol to the kernel (make it visible to the kernel) */
EXPORT_SYMBOL( symbol );
/* Export all symbols in a file to the kernel (declare before module.h) */
EXPORT_SYMTAB
```
### 由 proc 文件系统实现**财富分发**
下面是可以支持读写的 LKM。
在加载了这个模块后，用户可以使用 echo 命令向其中导入文本财富。再利用 cat 命令逐一输出。
下面给出了基本的模块函数和变量。
init 函数（init_fortune_module）负责使用 vmalloc 来为这个点心罐分配空间，然后使用 memset 将其全部清零。
使用所分配并已经清空的 cookie_pot 内存，我们在 /proc 中创建了一个 proc_dir_entry 项，并将其称为 fortune。
当 proc_entry 成功创建之后，对自己的本地变量和 proc_entry 结构进行了初始化。
我们加载了 /proc read 和 write 函数，并确定这个模块的所有者。
cleanup 函数简单地从 /proc 文件系统中删除这一项，然后释放 cookie_pot 所占据的内存。
cookie_pot 是一个固定大小（4KB）的页，它使用两个索引进行管理。第一个是 cookie_index，标识了要将下一个 cookie 写到哪里去。变量 next_fortune 标识了下一个 cookie 应该从哪里读取以便进行输出。在所有的 fortune 项都读取之后，我们简单地回到了 next_fortune。
```c
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/proc_fs.h>
#include <linux/string.h>
#include <linux/vmalloc.h>
#include <asm/uaccess.h>
MODULE_LICENSE("GPL");
MODULE_DESCRIPTION("Fortune Cookie Kernel Module");
MODULE_AUTHOR("M. Tim Jones");
#define MAX_COOKIE_LENGTH       PAGE_SIZE
static struct proc_dir_entry *proc_entry;
static char *cookie_pot;  // Space for fortune strings
static int cookie_index;  // Index to write next fortune
static int next_fortune;  // Index to read next fortune
int init_fortune_module( void )
{
  int ret = 0;
  cookie_pot = (char *)vmalloc( MAX_COOKIE_LENGTH );
  if (!cookie_pot) {
    ret = -ENOMEM;
  } else {
    memset( cookie_pot, 0, MAX_COOKIE_LENGTH );
    proc_entry = create_proc_entry( "fortune", 0644, NULL );
    if (proc_entry == NULL) {
      ret = -ENOMEM;
      vfree(cookie_pot);
      printk(KERN_INFO "fortune: Couldn't create proc entry\n");
    } else {
      cookie_index = 0;
      next_fortune = 0;
      proc_entry->read_proc = fortune_read;
      proc_entry->write_proc = fortune_write;
      proc_entry->owner = THIS_MODULE;
      printk(KERN_INFO "fortune: Module loaded.\n");
    }
  }
  return ret;
}
void cleanup_fortune_module( void )
{
  remove_proc_entry("fortune", &proc_root);
  vfree(cookie_pot);
  printk(KERN_INFO "fortune: Module unloaded.\n");
}
module_init( init_fortune_module );
module_exit( cleanup_fortune_module );
```
向这个罐中新写入一个 cookie 非常简单。
使用这个写入 cookie 的长度，我们可以检查是否有这么多空间可用。如果没有，就返回 -ENOSPC，它会返回给用户空间。否则，就说明空间存在，我们使用 copy_from_user 将用户缓冲区中的数据直接拷贝到 cookie_pot 中。然后增大 cookie_index（基于用户缓冲区的长度）并使用 NULL 来结束这个字符串。最后，返回实际写入 cookie_pot 的字符的个数，它会返回到用户进程。
```c
ssize_t fortune_write( struct file *filp, const char __user *buff,
                        unsigned long len, void *data )
{
  int space_available = (MAX_COOKIE_LENGTH-cookie_index)+1;
  if (len > space_available) {
    printk(KERN_INFO "fortune: cookie pot is full!\n");
    return -ENOSPC;
  }
  if (copy_from_user( &cookie_pot[cookie_index], buff, len )) {
    return -EFAULT;
  }
  cookie_index += len;
  cookie_pot[cookie_index-1] = 0;
  return len;
}
```
对 fortune 进行读取也非常简单，如下所示。由于我们刚才写入数据的缓冲区（page）已经在内核空间中了，因此可以直接对其进行操作，并使用 sprintf 来写入下一个 fortune。如果 next_fortune 索引大于 cookie_index（要写入的下一个位置），那么我们就将 next_fortune 返回为 0，这是第一个 fortune 的索引。在将这个 fortune 写入用户缓冲区之后，在 next_fortune 索引上增加刚才写入的 fortune 的长度。这样就变成了下一个可用 fortune 的索引。这个 fortune 的长度会被返回并传递给用户。
```C
int fortune_read( char *page, char **start, off_t off,
                   int count, int *eof, void *data )
{
  int len;
  if (off > 0) {
    *eof = 1;
    return 0;
  }
  /* Wrap-around */
  if (next_fortune >= cookie_index) next_fortune = 0;
  len = sprintf(page, "%s\n", &cookie_pot[next_fortune]);
  next_fortune += len;
  return len;
}
```
从这个简单的例子中，我们可以看出通过 /proc 文件系统与内核进行通信实际上是件非常简单的事情。现在让我们来看一下这个 fortune 模块的用法：
```
[root@younixPC]# insmod fortune.ko
[root@younixPC]# echo "Success is an individual proposition.  
          Thomas Watson" > /proc/fortune
[root@younixPC]# echo "If a man does his best, what else is there?  
                Gen. Patton" > /proc/fortune
[root@younixPC]# echo "Cats: All your base are belong to us.  
                      Zero Wing" > /proc/fortune
[root@younixPC]# cat /proc/fortune
Success is an individual proposition.  Thomas Watson
[root@younixPC]# cat /proc/fortune
If a man does his best, what else is there?  General Patton
```
/proc 虚拟文件系统可以广泛地用来报告内核的信息，也可以用来进行动态配置。我们会发现它对于驱动程序和模块编程来说都是非常完整的。
