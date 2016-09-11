---
title: 以 SPI 驱动模型为例分析 Linux 主机驱动与外设驱动分离模型
tags: Linux,SPI,统一设备模型
grammar_cjkRuby: true
---
## 一种简单却笨拙的解决方式
其实在对于一块板子，我们是可以直接操作 CPU （CPU_chip）上的 SPI Controller Register 来达到 访问 SPI 设备 （SPI_device）的目的。
但是这样对于一块板子一个设备我们就要写一套驱动：
```c
\\write
return_type CPUchip_write_SPIdevice(...)
{
CPUchip_write_spi_host_ctrl_reg(ctrl);
CPUchip_ write_spi_host_data_reg(buf);
while(!(CPUchip_spi_host_status_reg()&SPI_DATA_TRANSFER_DONE));
...
}
\\read
...
```
## 主机驱动与设备驱动的分离思想
那么对于三种 CPU 三种 SPI 设备，九种类型的组合方式，那我们就需要写 九种 驱动。这显然非常麻烦。
我们发现 三种 CPU A B C 的驱动 和 三种外设 a b c 的驱动并没有关系，前者不关心外设，后者也不关心主芯片。
所以就有了如下分离的模型

主控制器 A 驱动 ——| 核 心 层  core    |—— 外设 a 驱动
主控制器 B 驱动 ——| 主机通用驱动 |—— 外设 b 驱动
主控制器 C 驱动 ——| ___ API ____ |—— 外设 c 驱动

而且我们的 SPI、I2C、USB、ASoC（ALSA SoC）等子系统正是以这种分离设计思想来创建的。

## 设备驱动设计时的分层思想
前面我们将驱动分层了三层：
* 设备驱动
* 核心层 core
* 主机控制器驱动

**设备驱动 和 主机控制器驱动 之间的交互交由 核心层 提供的接口来完成。**
这样大大方便了我们驱动的开发，当我们要开发或者移植一个设备的时候，我们要做的就是编写 设备驱动 部分。

在设计设备驱动的时候，内核为 同类的设备 设计了一个框架，这个框架中的核心层中实现了这个设备一些通用的功能。而且当我们不想使用这些核心层函数的时候，我们可以自行重载。
```c
return_type core_funca(xxx_device * bottom_dev, param1_type param1, param1_type param2)  
{  
    if (bottom_dev->funca)  
    return bottom_dev->funca(param1, param2);  
    /* 核心层通用的funca代码 */  
    ...  
}  
```
比如在这个 core_funca 中，一开始会检查我们是否有重载这个 funca() ，如果有重载，就去调用底层的代码，否则，就采用默认的通用的核心层的。
这样的话，默认的核心层的代码可以处理绝大多数的同类设备，只有少数的特殊设备需要自行重载。

再比如，如果为了实现 funca() ，对于统一类设备，我们操作流程是一致的，过程是：
1. 通用代码 A 
2. 底层 ops1
3. 通用代码 B
4. 底层 ops2
5. 通用代码 C
6. 底层 ops3
```c
return_type core_funca(xxx_device * bottom_dev, param1_type param1, param1_type param2)  
{  
    /*通用的步骤代码A */  
    ...  
    bottom_dev->funca_ops1();  
    /*通用的步骤代码B */  
    ...  
    bottom_dev->funca_ops2();  
    /*通用的步骤代码C */  
    ...  
    bottom_dev->funca_ops3();  
}  
```
这样做的好处是，具体的底层驱动不需要再实现，而只需要关心 ops1 ops2 ops3 这些底层操作，即：

设备 的 core 层
.    | . . . . . . . .  | .
 .   | . . . . .  . . . | .
实例 A  . 实例 B


## 以 SPI 设备为例来分析 设备驱动与主控驱动分离的思想
### 几个重要的结构体和API
对 SPI 驱动模型不了解的可以参考我前面的几篇博文，这里只先提一下几个重要的结构体：
#### spi_master
spi_master 结构体来描述一个SPI主机控制器驱动，其主要成员是 1. 主机控制器的序号（系统中可能存在多个SPI主机控制器）、2. 片选数量、3. SPI模式和时钟设置用到的函数、4. 数据传输用到的函数等。
```c
struct spi_master {
	struct device dev;
	s16 bus_num;
	u16 num_chipselect;
	/* 设置模式和时钟 */
	int (*setup)(struct spi_device *spi);
	/* 双向数据传输 */
	int (*transfer)(struct spi_device *spi,
	struct spi_message *mesg);
	void (*cleanup)(struct spi_device *spi);
};
```
#### 分配、注册、注销 SPI主机控制器
这部分由 SPI 核心提供
```c
struct spi_master * spi_alloc_master(struct device *host, unsigned size);
	int spi_register_master(struct spi_master *master);
	void spi_unregister_master(struct spi_master *master);
```
#### spi_driver
spi_driver 用以描述一个 SPI 外设驱动，可以认为是 spi_master 的 client 驱动。
而且我们可以看到 它 和 platform_driver 结构体很相似。这其实几乎是一切 设备驱动 的模板。
```c
struct spi_driver {
	int (*probe)(struct spi_device *spi);
	int (*remove)(struct spi_device *spi);
	void (*shutdown)(struct spi_device *spi);
	int (*suspend)(struct spi_device *spi, pm_message_t mesg);
	int (*resume)(struct spi_device *spi);
	struct device_driver driver;
};
```
#### spi_transfer 与 spi_message
对于 SPI 外设驱动。
1. 当通过 SPI 总线进行数据传输的时候，使用了一个叫做 spi_async() 的函数来进行数据传输。通常这个函数被封装在 spi_sync() 中。
2. spi_async() 传输的数据就是 spi_message。
3. spi_message 中将包含由多个 spi_transfer 组成的 transfers。
```c
struct spi_transfer {
	const void *tx_buf;
	void *rx_buf;
	unsigned len;

	dma_addr_t tx_dma;
 	dma_addr_t rx_dma;
	unsigned cs_change:1;
	u8 bits_per_word;
	u16 delay_usecs;
	u32 speed_hz;

	struct list_head transfer_list;
};
```
一次完整的传输可能包含一个或多个 spi_transfer，他们的首地址被加入 transfers 的链表，然后被装在一个 spi_message 中。
```c
struct spi_message {
	struct list_head transfers;
	struct spi_device *spi;

	unsigned is_dma_mapped:1;

	 /* 完成被一个callback报告 */
	void (*complete)(void *context);
	void *context;
	unsigned actual_length;
	int status;
    struct list_head queue;
	void *state;
};
```
传输的流程为
```c
// 初始化 spi_message
spi_message_init()  
// 将 spi_transfer 添加到 spi_message 中
void spi_message_add_tail(struct spi_transfer *t, struct spi_message *m);
 /*发起一次 spi_message 的方式 有 同步 和 异步 两种 */
 // 使用同步API时，会阻塞等待这个消息被处理完。同步操作时使用的API是：
int spi_sync(struct spi_device *spi, struct spi_message *message);
// 使用异步API时，不会阻塞等待这个消息被处理完，但是可以在spi_message的complete字段挂接一个回调函数，当消息被处理完成后，该函数会被调用。异步操作时使用的API是：
int spi_async(struct spi_device *spi, struct spi_message *message);
```
#### 一个实例
```c
static inline int
spi_write(struct spi_device *spi, const u8 *buf, size_t len)
{
    struct spi_transfer t = {
    .tx_buf = buf,
    .len = len,
	};
    struct spi_message m;

    spi_message_init(&m);
    spi_message_add_tail(&t, &m);
    return spi_sync(spi, &m);
}
static inline int
spi_read(struct spi_device *spi, u8 *buf, size_t len)
{
    struct spi_transfer t = {
    .rx_buf = buf,
    .len = len,
	};
	struct spi_message m;

	spi_message_init(&m);
	spi_message_add_tail(&t, &m);
	return spi_sync(spi, &m);
}
```

### BSP 板级文件注册方式
SPI core 在 kernel/driver/spi/spi.c 当中，在其中实现了 spi_setup() 等成员函数。

和platform_driver对应着一个platform_device一样，spi_driver也对应着一个spi_device；
platform_device需要在BSP的板文件中添加板信息数据，而spi_device也同样需要。
spi_device的板信息用spi_board_info结构体描述，该结构体记录SPI外设使用的主机控制器序号、片选序号、数据比特率、SPI传输模式（即CPOL、CPHA）等。
然后在Linux启动过程中，在机器的init_machine()函数中，会通过如下语句注册这些spi_board_info：
spi_register_board_info(xxx_spi_board_info,
ARRAY_SIZE(xxx_spi_board_info));
这一点和启动时通过platform_add_devices()添加platform_device非常相似。

### DTS 设备树注册方式
我们 SPI 设备驱动中，通过 of_match_table 添加匹配的 .dts 中的相关节点的 compatible 属性， 和 DeviceTree 中设备节点 compatible 属性进行匹配。

另外还有一种别名匹配，我们知道 compatible 属性的组织形式为<manufacturer>,<model>。
别名其实就是去掉 compatible 属性中逗号前的manufacturer前缀。
根据这一点，可查看drivers/spi/spi.c的源代码，函数 spi_match_device() 暴露了更多的细节，如果别名出现在设备 spi_driver 的 id_table 里面，或者别名与spi_driver的name字段相同，SPI设备和驱动都可以匹配上。










