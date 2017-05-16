---
title: [RK3399] Android 电池系统（一）BQ25700 IC 驱动分析
tags: rockchip,battery
grammar_cjkRuby: true
---

Platform: RK3399 
OS: Android 6.0 
Kernel: 4.4 
Version: v2017.04
IC: TI BQ25700、RK808

## 基本概念
**TypeC PD 快充**：在USB Type-C接口中，拥有PD标准可承受3A或5A的大电流，根据不同电压，传输的最大功率可达100W。需要充电器（适配器）和被充电设备（手机、平板、电脑）均支持 PD 协议才行。

**标准下行端口(SDP)**这与USB 2.0规范定义的端口相同，也是台式机和笔记本电脑常见的典型端口。挂起时，最大负载电流为2.5A；连接且非挂起状态下为100mA，可以配置电流为500mA (最大)。设备可利用硬件识别SDP，USB数据线D+和D-分别通过15kΩ接地，但仍然需要枚举，以符合USB规范。尽管现在许多硬件不经枚举即消耗功率，但在USB 2.0规范中，从严格意义上并不合法，违反规范要求。

**充电下行端口(CDP)** BC1.1为PC、笔记本电脑及其它硬件规定了这种较大电流的新型USB口。现在，CDP可提供高达1.5A电流，由于可在枚举之前提供电流，所以有别于USB 2.0。插入CDP的装置可通过操纵和监测D+、D-线，从而利用硬件握手识别CDP (参见USB电池充电规范第3.2.3部分)。在将数据线转为USB收发之前进行硬件测试，这样就能够在枚举之前检测到CDP (以及开始充电)。

**专用充电端口(DCP)** BC1.1规定了不进行枚举的电源，例如墙上适配器电源和汽车适配器，不需要数字通信即可启动充电。DCP可提供高达1.5A电流，通过短路D+和D-进行识别，从而能够设计DCP“墙上适配器电源”，采用USB mini或微型插孔，而非圆形插头或自制连接器的固定安装线。这样的适配器可采用任意USB电缆(配备正确插头)进行充电。

## 驱动分析
默认 3399 SDK 中，BQ IC 驱动仅实现了 TypeC 充电（不支持 DC 充电）。首先我们分析一下其驱动的函数调用链。

### 函数调用链
```
bq25700_probe
  i2c_check_functionality //是否支持 SMBUS 通信
  devm_regmap_init_i2c //采用 regmap api 操作 i2c，初始化 bq25700 的 regmap_config 
  devm_regmap_field_alloc //为 regmap 分配内存空间
  i2c_set_clientdata 
  bq25700_field_read //读 chip id
  bq25700_fw_probe 
    bq25700_fw_read_u32_props //获取 dts 中的属性，包括 charge-current、max-charge-voltage、input-current-sdp/dcp/cdp、minimum-sys-voltage 、otg-voltage、otg-current
  bq25700_hw_init
    //1. bq25700_chip_reset //芯片重启
    //2. WDTWR_ADJ = 0 //disable watchdog
    //3. 初始化电流电压和其他参数
    //4. 配置 ADC 用以持续转化，禁能
  bq25700_parse_dt //获取 dts 中的属性 pd-charge-only 
  bq25700_init_usb 
    usb_charger_wq = alloc_ordered_workqueue //分配工作队列，用于事件通知链
    extcon_get_edev_by_phandle(dev, 0) //获取外部连接器 fusb302
    bq25700_register_cg_nb(charger); //注册 charger 通知链。如果 pd_charge_only 为 0 ，表示不仅仅采用 TypeC 充电，则执行。添加等待队列。 
      bq25700_charger_evt_worker //初始化 charger 等待队列
        bq25700_charger_evt_handel //判断 charger 类型，并使能 INPUT_CURRENT/CHARGE_CURRENT
      bq25700_charger_evt_notifier //添加 charger 事件通知链
      bq25700_register_cg_extcon //注册 charger 外部控制器，以及其事件通知链
    bq25700_register_host_nb(charger); //注册 host 通知链
    bq25700_register_discnt_nb(charger); //注册 disconnect 通知链
    bq25700_register_pd_nb(charger); //注册 pd 通知链
    schedule_delayed_work //提交任务到工作队列
  bq25700_init_sysfs //创建 sysfs 中的属性节点
  //根据 AC_STAT 确定触发条件，设定中断触发条件
  device_init_wakeup 
  devm_request_threaded_irq 
  enable_irq_wake //使能中断唤醒
  bq25700_power_supply_init //注册 power supply 的 desc
    bq25700_power_supply_get_property //获取系统属性的接口
```
其中要注意的是 bq25700_hw_init。在其中完成了比较重要寄存器配置工作，可以在其后 dump 出寄存器信息，对照 datasheet 进行校对。


## 调试流程
一开始最直观的效果是，电池电压没有升高，所以没有充电。

根据 datasheet 我们查看标准充电流程：

   ![enter description here][1]

1. 先检查芯片供电是否正常。
2. 再检查 CHARGER_OK_H 引脚电平，在插入电源（TypeC 或者 DC）的时候是否改变（被拉高）
 
    ![enter description here][2]

3. 检查 I2C 通信是否正常。包括 I2C 组别是否设置正确，I2C 地址是否有误。**注意，如果你的代码中是通过 smbus api 的方式和 IC 通信的，地址需要设置为 0x09，如果是采用 I2C 通信，地址为 6a**。
4. 检查电池相关的参数配置的是否有误。比如  charge-current、max-charge-voltage、input-current-sdp/dcp/cdp、minimum-sys-voltage 、otg-voltage、otg-current。
双节电池 7.4 V 配置如下，单节电池 3.7V 的差异在注释中有标注。
```
	bq25700: bq25700@09 {//09 for SMBUS,6a for I2C
			compatible = "ti,bq25700";
			reg = <0x09>;
			extcon = <&fusb0>;
			interrupt-parent = <&gpio1>;
			interrupts = <1 IRQ_TYPE_LEVEL_LOW>;	//GPIO1_A1
			pinctrl-names = "default";
			pinctrl-0 = <&charger_ok>;
			ti,charge-current = <2500000>;
			ti,max-input-voltage = <20000000>;
			ti,max-input-current = <6000000>;
			ti,max-charge-voltage = <8750000>; // single battery is 4000000 dual is 8750000
			ti,input-current = <5000000>;
			ti,input-current-sdp = <500000>;
			ti,input-current-dcp = <2000000>;
			ti,input-current-cdp = <2000000>;
			ti,minimum-sys-voltage = <7400000>; // single battery is 3400000 dual is 7400000
			ti,otg-voltage = <5000000>;
			ti,otg-current = <500000>;
			pd-charge-only = <0>;
			//typec0-enable-gpios = <&gpio1 3 GPIO_ACTIVE_HIGH>; //GPIO1 GPIO1_A3
			//typec0-discharge-gpios = <&gpio0 12 GPIO_ACTIVE_HIGH>; //GPIO0 GPIO0_B4
		};
```
5.　检查 Input Voltage 和 Current Limit 相关的寄存器设置是否正常。寄存器是在函数 bq25700_hw_init 中进行寄存器初始化。可以通过 dump_regs 打印出寄存器信息观察。
也可以通过 ` cat /sys/class/i2c-adapter/i2c-4/4-0009/charge_info ` 节点来各个观察寄存器中的信息。
如果 CHARGE_CURRENT 过低，可能是 input current 有一部分跑到系统上去了，供电不足，可以将 input-current 调大试试（比如将现在的 input-current 从 500mA 改为 1A ` ti,input-current = <10000000>;` 。

6.　观察 INPUT_CURRENT 和 CHARGE_CURRENT 寄存器值是否正确，rk 将这两个操作封装在了 bq25700_enable_charger 这个函数中。在其中加入打印信息，观察否是调用该函数。
对于我的板子而言，这个函数没有调用，观察其函数调用链
bq25700_register_cg_nb->bq25700_charger_evt_worker->bq25700_charger_evt_handel-> bq25700_enable_charger 
bq25700_register_cg_nb 函数调用的逻辑是
```
	if (!charger->pd_charge_only)
		bq25700_register_cg_nb(charger);
```
而我的 pd_charge_only 设置为 1 。它表示**只采用 PD 充电**，而我是直流电源（TypeC 接口）充电，如果设置为 1 ，则不会进入 bq25700_enable_charger 的逻辑。故无法充电。
硬件要满足 PD 充电的条件必须是采用 PD 专用的适配器，市面上大概 100 多一个，所以如果你的适配器没有这么贵的话，果断关掉 pd-charge-only 选项吧。
改为 0 后可以充电。问题解决。


另外，因为部分寄存器为 16bit ，i2c-tools 仅能读出 8bit，差点被其误导以为寄存器中的数据有误。

  [1]: http://wx3.sinaimg.cn/large/ba061518ly1ffnfkdssl9j20mf048aat.jpg
  [2]: http://wx4.sinaimg.cn/large/ba061518ly1ffnfght5ykj20c602rdfx.jpg