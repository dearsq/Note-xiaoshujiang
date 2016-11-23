---
title: [RK3399] Wifi Card 驱动流程分析
tags: SDIO,Wifi
grammar_cjkRuby: true
---

Platform: RockChip 
OS: Android 6.0 
Kernel: 4.4
WiFi/BT/FM 模组: AP6354 

Linux 4.4 的 Wifi 驱动部分和 2.6 的区别还是比较大。
前面的基本概念搜罗于网络;
后面的驱动流程分析是根据 RockChip 3399 的 Kernel 部分来进行分析的。

其他内核为 Linux 4.4 的平台流程也大致相仿。

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

![](https://ws4.sinaimg.cn/large/ba061518gw1fa28l6s62xj20ar08xmyb.jpg)

```c
rockchip_wifi_init_module_rkwifi    //创建了一个内核线程 wifi_init_thread
    wifi_init_thread
        dhd_module_init
            dhd_wifi_platform_register_drv    // 注册 wifi 驱动，注册成功调用后面的 probe
			    bcmdhd_wifi_plat_dev_drv_probe
				    dhd_wifi_platform_load    //两个操作
					    wl_android_init    //1. wlan 初始化
						dhd_wifi_platform_load_sdio    //2. 根据 接口类型 usb、sdio、pcie 选择不同的操作
						    dhd_bus_register    //
							    bcmsdh_register
								    bcmsdh_register_client_driver
```

### sdio_pwrseq
```
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
## WIFI 

&pinctrl {
	sdio-pwrseq {
		wifi_enable_h: wifi-enable-h {
			rockchip,pins =
				<0 10 RK_FUNC_GPIO &pcfg_pull_none>;
		};
	};
}


	wireless-wlan {
		compatible = "wlan-platdata";
		rockchip,grf = <&grf>;
		wifi_chip_type = "ap6354";
		sdio_vref = <1800>;
		WIFI,host_wake_irq = <&gpio0 3 GPIO_ACTIVE_HIGH>; /* GPIO0_a3 */
		status = "okay";
	};


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

