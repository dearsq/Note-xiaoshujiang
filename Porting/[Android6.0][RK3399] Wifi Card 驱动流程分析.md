---
title: [Android6.0][RK3399] Wifi Card 驱动流程分析
tags: SDIO,Wifi
grammar_cjkRuby: true
---

Platform: RockChip 
OS: Android 6.0 
Kernel: 4.4
WiFi/BT/FM 模组: AP6354 

前面的基本概念搜罗于网络;
后面的驱动流程分析是根据 RockChip 3399 的 Kernel 部分来进行分析的。

[TOC]

## 基本概念

### Wifi 
wifi 英文全称是 WIreless-FIdelity，翻译成中文就是无线保真，英文简称WiFi。

### WLAN
wlan 英文全名：Wireless Local Area Networks， 无线局域网络。

### 关系
wifi 是实现 wlan 的一种技术。

### STA 模式 和 AP 模式
AP模式: Access Point，提供无线接入服务，允许其它无线设备接入，提供数据访问，一般的无线路由/网桥工作在该模式下。AP和AP之间允许相互连接。
Sta模式: Station, 类似于无线终端，sta本身并不接受无线的接入，它可以连接到AP，一般无线网卡即工作在该模式。

### 无线接入过程的三个阶段
 STA（工作站）启动初始化、开始正式使用AP传送数据帧前，要经过三个阶段才能够接入（802.11MAC层负责客户端与AP之间的通讯，功能包括扫描、接入、认证、加密、漫游和同步等功能）：
1）扫描阶段（SCAN）
2）认证阶段 (Authentication)
3）关联（Association）

![](https://ws3.sinaimg.cn/large/ba061518gw1fa0m77eskwj208t08mwet.jpg)

更详细的 wifi 相关介绍可以参考这篇文章 [WiFi基础知识解析](http://blog.csdn.net/zqixiao_09/article/details/51103615)

后面介绍 Wifi 的接口 SDIO 的基本概念。

### SD  和 MMC
SD (Secure Digital) 与 MMC (Multimedia Card)
**MMC** 是较早的一种记忆卡标准，**目前已经被 SD 标准取代**。
**SD** 是一种 flash memory card 的标准,也就是一般常见的 SD 记忆卡。

### SDIO（Secure Digital I/O）
SDIO 就是 SD 的 I/O 接口的意思。
更具体的说，SD 本来是记忆卡的标准,但是现在也可以把 SD 拿来插上一些外围接口使用,这样的技术便是 SDIO。

SDIO 通过 SD 的 I/O 管脚来**连接外部**的外围 device 并**传输数据**。这些外围设备，我们称为 SDIO 卡，常见的有：

*  Wi-Fi card(无线网络卡)
* CMOS sensor card(照相模块)
* GPS card
* GSM/GPRS modem card
* Bluetooth card
* Radio/TV card

### SDIO 卡 和 SD 卡 的区别
SD卡使用的是SD卡协议，而SDIO卡使用的是SDIO协议！
协议不一样，初始化/读写方式也不一样！

### SDIO-Wifi 模块
**SDIO-Wifi 模块**是基于 SDIO 接口的符合 wifi 无线网络标准的嵌入式模块，内置无线网络协议IEEE802.11协议栈以及TCP/IP协议栈，能够实现用户主平台数据通过SDIO口到无线网络之间的转换。
SDIO 具有传输数据快，兼容SD、MMC接口等特点。

对于SDIO接口的wifi，首先，它是一个sdio的卡的设备，然后具备了wifi的功能。
所以，**注册的时候还是先以sdio的卡的设备去注册的。然后检测到卡之后就要驱动他的wifi功能**。

### SDIO 总线
SDIO总线 和 USB总线 类似，SDIO也有两端，其中一端是HOST端，另一端是device端。**所有的通信都是由HOST端 发送 命令 开始的，Device端只要能解析命令，就可以相互通信。**
CLK信号：HOST给DEVICE的 时钟信号，每个时钟周期传输一个命令。
CMD信号：双向 的信号，用于传送 命令 和 反应。
DAT0-DAT3 信号：四条用于传送的数据线。
VDD信号：电源信号。
VSS1，VSS2：电源地信号。

### SDIO 命令
SDIO总线上都是HOST端发起请求，然后DEVICE端回应请求。
SDIO 命令由6个字节组成。

a -- Command:用于开始传输的命令，是由HOST端发往DEVICE端的。其中命令是通过CMD信号线传送的。
b -- Response:回应是DEVICE返回的HOST的命令，作为Command的回应。也是通过CMD线传送的。
c -- Data:数据是双向的传送的。可以设置为1线模式，也可以设置为4线模式。数据是通过DAT0-DAT3信号线传输的。

SDIO的每次操作都是由HOST在CMD线上发起一个CMD，对于有的CMD，DEVICE需要返回Response，有的则不需要。
**对于读命令**，首先HOST会向DEVICE发送命令，紧接着DEVICE会返回一个握手信号，此时，当HOST收到回应的握手信号后，会将数据放在4位的数据线上，在传送数据的同时会跟随着CRC校验码。当整个读传送完毕后，HOST会再次发送一个命令，通知DEVICE操作完毕，DEVICE同时会返回一个响应。
**对于写命令**，首先HOST会向DEVICE发送命令，紧接着DEVICE会返回一个握手信号，此时，当HOST收到回应的握手信号后，会将数据放在4位的数据线上，在传送数据的同时会跟随着CRC校验码。当整个写传送完毕后，HOST会再次发送一个命令，通知DEVICE操作完毕，DEVICE同时会返回一个响应。

## WIFI 模块解析和启动流程
对于 Wifi 模组的 Android 上层的分析，这篇文章讲的非常不错：
http://blog.csdn.net/ylyuanlu/article/details/7711433
这篇文章将下图蓝色的和绿色的部分讲的非常详细。

![](https://ws4.sinaimg.cn/large/ba061518gw1fa20uev7gaj20m70jmq64.jpg)
![android中wifi原理及流程分析](http://blog.csdn.net/pochuanpiao/article/details/7477652)

我这个板子上所采用的 WiFi 模组是 AP6354, 它是一个 Wifi / BT4.0 / FM 三合一模组。接口是 SDIO。
本文主要分析 Kernel Driver 部分。所以先从 SDIO 接口的驱动来切入。

## SDIO 接口驱动
**SDIO 接口的 wifi，首先，它是一个 sdio 卡 设备，然后具备了 wifi 的功能，所以 SDIO 接口的 WiFi 驱动就是在 wifi 驱动 外面套上了一个 SDIO 驱动 的外壳。**

SDIO 驱动部分代码结构如下

![](https://ws3.sinaimg.cn/large/ba061518gw1fa21doio94j20fw079jsp.jpg)

drivers/mmc 下有 mmc卡、sd卡、sdio 卡驱动。

SDIO驱动仍然符合设备驱动的分层与分离思想。

设备驱动层（wifi 设备）:
				|
核心层（向上向下提供接口）
			|
主机驱动层（实现 SDIO 驱动）

我们主要关心 core 目录（CORE 层），其中是媒体卡的通用代码。包括 core.c host.c stdio.c。
CORE 层完成了
1. 不同协议和规范的实现
2. 为 HOST 层的驱动提供了接口函数
3. 完成了 SDIO 总线注册
4. 对应 ops 操作
5. 以及支持 mmc 的代码

host 目录（HOST 层）是根据不通平台而编写的 host 驱动。

## WIFI 驱动流程分析

rockchip_wifi_init_module_rkwifi    //创建了一个内核线程 wifi_init_thread
    wifi_init_thread    //->
        dhd_module_init    
            dhd_wifi_platform_register_drv    // 查找设备，注册 wifi 驱动，注册成功调用后面的 bcmdhd_wifi_plat_dev_drv_probe
			    wifi_ctrlfunc_register_drv
				|    bus_find_device    //查找 wifi 设备
				|    platform_driver_register(&wifi_platform_dev_driver)    //注册 wifi 驱动
			    bcmdhd_wifi_plat_dev_drv_probe    //->
				    dhd_wifi_platform_load    //两个操作
					    wl_android_init    //1. wlan 初始化
						dhd_wifi_platform_load_sdio    //2. 根据 接口类型 usb、sdio、pcie 选择不同的操作
						    dhd_bus_register    // 注册成功就调用 dhd_sdio.dhdsdio_probe
								bcmsdh_register(&dhd_sdio)
								|    bcmsdh_register_client_driver
								|	    sdio_register_driver(&bcmsdh_sdmmc_driver)    //注册成功就调用 bcmsdh_sdmmc_driver.bcmsdh_sdmmc_probe
								|		    bcmsdh_sdmmc_probe    //->
								|			    sdioh_probe
							    dhdsdio_probe

参考文章
[在全志平台调试博通的wifi驱动（类似ap6212）](http://blog.csdn.net/fenzhi1988/article/details/44809779)
[wifi 详解(三)](http://blog.csdn.net/ylyuanlu/article/details/7711441#t2)


## 调试问题
### 调试步骤
#### **1.确保配置无误**

![](https://ws1.sinaimg.cn/large/ba061518gw1fa31cvoj27j20zk0hatlq.jpg)

dts文件的配置wifi部分是在net/rfkill-wlan.c中进行配置；先通过内核启动日志确认相关配置是否有正常解析，如果解析过程出现异常，确认是所配置的gpio是否存在冲突；

#### **2.检查供电是否正常**
确认wifi的供电控制是否受控
      Echo 0 > /sys/class/rkwifi/power //对wifi模块掉电
      Echo 1 > /sys/class/rkwifi/power//对wifi模块上电
如果执行上面命令对模块进行上下电，而 实际测量对应管脚不受控，可以通过io 命令读取对应的寄存器，确认是否写入，如果正确写入但是实际测量不受控请检查硬件部分；

#### **3. 扫描模块初始化模块**
检查内核中是否配置
CONFIG_WIFI_LOAD_DRIVER_WHEN_KERNEL_BOOTUP=y；
调测wifi时请把该宏配置为 n；
执行 echo 1 > /sys/class/rkwifi/driver 命令会调用模块的驱动的初始化操作，初始化成功后看到wlan0 节点；

**如何判断是否识别到模块**
* Usb接口的模块：出现如下 log
 ![](https://ws3.sinaimg.cn/large/ba061518gw1fa31i7abojj20jt02jta8.jpg)
* SDIO 接口的模块
对于sdio接口的模块，执行” echo 1 > /sys/class/rkwifi/driver”命令 ，正常情况下 sdio_clk 和sdio_cmd 能够测量到相关波形，内核打印上能够看到如下打印，如果没有测量到波形也没有看到如下打印，根据配置文档检查是否正确配置sdio;

![](https://ws4.sinaimg.cn/large/ba061518gw1fa31k2s6o8j20yh09gqdc.jpg)
Wifi驱动会根据扫描到的sdio模块的vid pid 进行驱动匹配，rtl的驱动会根据读取到的vid，pid进行驱动匹配；其中正基系列的模块会根据后面从data数据线上读取到F1 function 读取的数值进行 驱动与固件匹配（正基目前的驱动兼容所有sdio接口正基模块，根据F1 function 读取的值 匹配固件）；
如果能够扫描模块但是初始化过程看到data fifo error,检查下 sdio接口电平是否一致；方法如下：
       echo 1 > /sys/class/rkwifi/power
测量 VDDIO sdio_clk sdio_cmd sdio_data0~sdio_data3 的电压；正常情况下 sdio_clk 为 0V，sdio其他五根线与vddio电压一致；
如果电压不一致：312x平台确认下 sdio接口的内部上下拉是否禁掉，参看文档RK Kernel 3.10平台WiFi BT不工作异常排查.pdf Part C；其他平台考虑加外部上拉(注clk绝对不要加外部上拉)；
同时测量执行echo 1 > /sys/class/rkwifi/driver 时 外部晶体是否有起振，如果扫描时没有起振检查下硬件；同时建议测量外部晶体频偏，频偏比较大情况下，会出现能扫描到模块但是初始化失败；除检查晶振外，正基系列还需要外部32k，测量32k的峰峰值（峰峰值>=0.7*VDDIO && 峰峰值 <= 1*VDDIO）；【注：频偏和峰峰值一定要测量检查，频偏过大峰峰值不对会影响wifi（扫描连接热点）和蓝牙（扫描连接设备））】
电压一致情况下，晶振频偏和32k的峰峰值没有问题（正基系列的要考虑晶振频偏与32k峰峰值，具体结合自己电路实际情况）但是初始化依然出问题；
考虑降低sdio_clk ，重新测试；如果降低clk可以，考虑硬件上走线；
如果降低clk依然不行，考虑使用sdio单线模式方法如下
```
&sdio {
		...
		bus-width = <1>;
		...
};
```
使用 sdio 单线模式。如果单线模式可以而使用4线模式不行，检查硬件上sdio_data0~sdio_data3 四根线的线序是否弄错；
如果降低clk，使用单线模式均不可以检查下是否是使用最新的sdk代码和最新的wifi驱动（ftp服务器上有相关patch）；
   上述检查均无结果，check 图纸 是否周围器件有贴错器件；
   
#### **4.检查模块能否处于工作状态** 
  netcfg wlan0 up 或busybox ifconfig wlan0 up //执行完成后检查 wlan0 是否处于up状态；如果没有处于up状态;做如下检查确认
  1 确认相关固件是否存在(正基系列，通过看内核日志可以看到)，固件不存在考虑到ftp下载固件；此时如果还报其他错误从两个方面排查1 上电时序，2检查sdio部分走线；
  2 尝试使用原始最新的sdk代码做测试；（有客户出现过，上层做了相关修改导致wifi初始化成功，但是执行netcfg wlan0 up 报告无法识别 ioctl 命令等奇怪错误，原生sdk生成的sysytem.img 没有问题）
  执行iwlist wlan0 scanning ，测试扫描热点是否正常（3368平台下执行iwlist 命令有问题，忽略此步骤）

#### **5. 确认Android层是否能够打开**
述检查各个步骤可以工作，而通过上层settings界面打开失败；以下几个方面排查
   1 dts中的wifi_type配置是否正确;cat /sys/class/rkwifi/chip 确认 下 打印的结果和你的模块是否匹配
   2 确认 wpa_supplicant 相关服务是否生成，libhardware_leacy 启动的wpa服务是否正确；
   3 抓取logcat 日志上传readmine

### 吞吐率问题
1. pcb检查，一定要让模块原厂检查确认 pcb是否存在问题
2. RF指标确认是否ok
3. 天线是否做过匹配
4. Sdio 接口的可以考虑 提到sdio的clk 启用sdio3.0【前提 平台支持 sdio3.0 ,模块支持sdio3.0】
### 其他问题
#### **无法连接热点**
1.无法连接热点，正基系列模块检查确认晶振频偏和32k峰峰值；
rtl模块考虑驱动配置是否正确，是否匹配；
2.检查确认p2p wlan0 的mac地址是否一致如果检查是否有调用rockchip_wifi_mac_addr读取mac地址，如果有考虑直接在该函数中return -1；
3.检查确认是否有做RF指标测试以及天线匹配测试
4.上述检查没有问题，做如下测试 （首先用给手机连接所测试的热点做确认）
1 连接无加密热点 2 连接加密热点 测试能否连接成功，并记录对应的logcat 日志与内核日志（开机到打开wifi以及连接热点的整个过程）
#### **softap 无法打开（正基系列的）**
1.查看打开热点时的内核日志，确认下 下载固件是否正确 ，正基系列的模块 softap 下载的固件一般是带ap后缀结尾的；
2.固件下载没有问题 ，考虑使用原始的sdk代码做测试
#### **P2P 问题**
**P2p 无法打开**：确认是否有p2p节点，有p2p节点的检查确认mac地址是否与wlan0 一样，如果一样按照热点问题中的step 2 处理；
**第一次开机能够打开，重启后无法打开**：考虑检查上电时序，目前遇到都是rtl的模块出现过，问题在于chipen 脚不受控，建议做成受控，在重启时对chipen脚下电；可以通过如下方法实现net/rfkill-wlan.c中的rfkill_wlan_driver 中增加shutdown函数 在该函数中对chip_en 下电；
**休眠唤醒出现wifi无法打开**：
1 对比检查休眠唤醒前后 sdio 的iomux 是否发生变更
2 对比 休眠前后以及休眠中 wifi的外围供电是否发生变更



### sdio_pwrseq
```c
sdio_pwrseq: sdio-pwrseq {
		compatible = "mmc-pwrseq-simple";
		clocks = <&rk808 1>;
		clock-names = "ext_clock";
		pinctrl-names = "default";
		pinctrl-0 = <&wifi_enable_h>;

		/*
		 * On the module itself this is one of these (depending
		 * on the actual card populated):
		 * - SDIO_RESET_L_WL_REG_ON
		 * - PDN (power down when low)
		 */
		reset-gpios = <&gpio0 10 GPIO_ACTIVE_LOW>; /* GPIO0_B2 */
	};
```	
根据 compatible 匹配到 mmc_pwrseq_simple_alloc
```
struct mmc_pwrseq_match {
	const char *compatible;
	struct mmc_pwrseq *(*alloc)(struct mmc_host *host, struct device *dev);
};

static struct mmc_pwrseq_match pwrseq_match[] = {
	{
		.compatible = "mmc-pwrseq-simple",
		.alloc = mmc_pwrseq_simple_alloc,
	}, {
		.compatible = "mmc-pwrseq-emmc",
		.alloc = mmc_pwrseq_emmc_alloc,
	},
};
```
逻辑在 drivers/mmc/core/pwrseq.c  的 mmc_pwrseq_alloc 中
```
int mmc_pwrseq_alloc(struct mmc_host *host)
```
在其中调用 match->alloc(host, &pdev->dev) 即 mmc_pwrseq_simple_alloc 
注册 mmc_pwrseq_simple_ops 并返回 pwrseq
```
static struct mmc_pwrseq_ops mmc_pwrseq_simple_ops = {
	.pre_power_on = mmc_pwrseq_simple_pre_power_on,
	.post_power_on = mmc_pwrseq_simple_post_power_on,
	.power_off = mmc_pwrseq_simple_power_off,
	.free = mmc_pwrseq_simple_free,
};
```


### wireless-wlan
kernel/net/rfkill/rfkill-wlan.c
```
static int rfkill_wlan_probe(struct platform_device *pdev)
{
    //解析 dts
    ret = wlan_platdata_parse_dt(&pdev->dev, pdata);
	//rfkill 注册 GPIO poweren 和 reset
	 ret = rfkill_rk_setup_gpio(&pdata->power_n, wlan_name, "wlan_poweren");
	 ret = rfkill_rk_setup_gpio(&pdata->reset_n, wlan_name, "wlan_reset");
	 //默认关掉 wifi
	 if (gpio_is_valid(pdata->power_n.io))
    {
        gpio_direction_output(pdata->power_n.io, !pdata->power_n.enable);
    }
	//最后调用 rockchip_wifi_power(1) ，这也是最重要的地方，我们在后面单独分析
	 if (pdata->wifi_power_remain)
    {
        rockchip_wifi_power(1);
    }
}
```

```
//1——>on  
//0——>off
int rockchip_wifi_power(int on)
{
	struct rfkill_wlan_data *mrfkill = g_rfkill; // mrfkill 是一个开关
    struct rksdmmc_gpio *poweron, *reset; // 两个 gpio（poweron 和 reset）
    struct regulator *ldo = NULL;
    int power = 0;
    bool toggle = false;

	//不管怎么样先 power off
	if (!on && primary_sdio_host)
		mmc_pwrseq_power_off(primary_sdio_host);

    if (!rfkill_get_bt_power_state(&power, &toggle)) {
        if (toggle == true && power == 1) {
            LOG("%s: wifi shouldn't control the power, it was enabled by BT!\n", __func__);
            return 0;
        }
    }

    if (mrfkill->pdata->mregulator.power_ctrl_by_pmu) {
        int ret = -1;
        char *ldostr;
        int level = mrfkill->pdata->mregulator.enable;

        ldostr = mrfkill->pdata->mregulator.pmu_regulator;
        if (ldostr == NULL) {
            LOG("%s: wifi power set to be controled by pmic, but which one?\n", __func__);
            return -1;
        }
        ldo = regulator_get(NULL, ldostr);
        if (ldo == NULL || IS_ERR(ldo)) {
            LOG("\n\n\n%s get ldo error,please mod this\n\n\n", __func__);
            return -1;
        } else {
			if (on == level) {
				regulator_set_voltage(ldo, 3000000, 3000000);
			    LOG("%s: %s enabled\n", __func__, ldostr);
				ret = regulator_enable(ldo);
                wifi_power_state = 1;
			    LOG("wifi turn on power.\n");
            } else {
				LOG("%s: %s disabled\n", __func__, ldostr);
                while (regulator_is_enabled(ldo) > 0) {
				    ret = regulator_disable(ldo);
                }
                wifi_power_state = 0;
			    LOG("wifi shut off power.\n");
			}
			regulator_put(ldo);
			msleep(100);
		}
    } else {
		poweron = &mrfkill->pdata->power_n;
		reset = &mrfkill->pdata->reset_n;

		if (on){
			if (gpio_is_valid(poweron->io)) {
				gpio_set_value(poweron->io, poweron->enable);
				msleep(100);
			}

			if (gpio_is_valid(reset->io)) {
				gpio_set_value(reset->io, reset->enable);
				msleep(100);
			}

            wifi_power_state = 1;
			LOG("wifi turn on power. %d\n", poweron->io);
		}else{
			if (gpio_is_valid(poweron->io)) {
				gpio_set_value(poweron->io, !(poweron->enable));
				msleep(100);
			}

			if (gpio_is_valid(reset->io)) {
				gpio_set_value(reset->io, !(reset->enable));
			}

            wifi_power_state = 0;
			LOG("wifi shut off power.\n");
		}
    }

    return 0;
}
}
```

老规矩，在 linux 下 make menuconfig，我们用的是 AP6354，搜 ap6xxx， 发现有
[IMG]

cd ~/3399/kernel/drivers/net/wireless/rockchip_wlan/rkwifi/
Makefile 中可以看到
[IMG]


~/3399/kernel/drivers/net/wireless/rockchip_wlan/rkwifi/rk_wifi_config.c 
中用来设置固件的路径
在
```
int rkwifi_set_firmware(char *fw, cahr *nvram)
```
中，通过
```
extern int get_wifi_chip_type(void);
```
获取 chip 类型是 WIFI_AP6354
设置 fw = "/system/etc/firmware/fw_bcm4354a1_ag.bin"
设置 nvram = "/system/etc/firmware/nvram_ap6354.txt"

