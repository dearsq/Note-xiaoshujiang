---
title: [RK3399] Android 电池系统（二）BQ IC 添加 DC 充电功能
tags: rockchip,battery
grammar_cjkRuby: true
---
Platform: RK3399 
OS: Android 6.0 
Kernel: 4.4 
Version: v2017.04 
IC: TI BQ25700、RK808

在上一章 [[RK3399] Android 电池系统(一) BQ25700 IC 驱动分析](http://blog.csdn.net/dearsq/article/details/72335905) 中我们分析了 BQ IC 的驱动加载流程。

我们也知道了平台默认的代码，定位是 PD 充电，不支持 DC 充电。
这一章我们来添加 DC 充电的功能。

## 解决思路
首先我们知道 DC 插入的时候， CHG_OK_H 会被拉高。所以我们思考是否可以在 CHG_OK 的中断处理函数中完成对 BQ IC DC 充电功能的配置。
但是当 TypeC 适配器插入的时候，CHG_OK_H 也会被拉高。
不过利用 TypeC 充电时候的配置和 利用 DC 充电的配置是相同的。

另外需要说明的是，硬件上实现了，在插入 DC 的时候，会关断 TypeC 的供电。以方式两边同时往板子充电而引起的异常。

所以，一共有以下几种情况：
仅插上 TypeC 适配器，代码默认实现正常充电。
仅插上 DC 适配器，在 CHG_OK 中断处理函数中完成充电配置。
插上 TypeC 适配器后，再插入 DC 适配器，不会触发中断处理函数，但是在 BQ IC 中的配置此时是适用于 DC 充电的。所以没问题。硬件上 TypeC 充电被关断。
插上 DC 适配器后，再插入 TypeC 适配器，先利用中断处理函数中对 BQ IC 的配置进行充电。由于硬件上此时已经关断了 TypeC 充电。所以没问题。

分析得知这样是可行的，那么我们开始在 CHG_OK 的中断处理函数中完成对 BQ IC 的操作。

## 代码添加
根据  datasheet ，我们了解到开启 BQ IC 充电需要完成 INPUT_CURRENT 与 CHARGE_CURRENT 寄存器的写操作。
其次，深入 TypeC 检测后的处理函数，我们也可以看到最后其是调用了 bq25700_enable_charger 完成充电：
```
static void bq25700_enable_charger(struct bq25700_device *charger,
				   u32 input_current)
{
	bq25700_field_write(charger, INPUT_CURRENT, input_current);
	bq25700_field_write(charger, CHARGE_CURRENT, charger->init_data.ichg);
}
```

那么我们仿照其使能 BQ IC 充电的方式来完成中断处理函数中的操作：
```
bq25700_probe
{
...
    ret = devm_request_threaded_irq(dev, client->irq, NULL,
					bq25700_irq_handler_thread,
					irq_flag | IRQF_ONESHOT ,   
					"bq25700_irq", charger);
	if (ret)
...
}

static irqreturn_t bq25700_irq_handler_thread(int irq, void *private)
{
	struct bq25700_device *charger = private;
	int irq_flag;
	struct bq25700_state state;
	DBG("BQ25700: bq25700_irq_handler_thread\n");

	if (bq25700_field_read(charger, AC_STAT)) {
		irq_flag = IRQF_TRIGGER_LOW;

++		bq25700_field_write(charger, INPUT_CURRENT, charger->init_data.input_current_cdp);
++		bq25700_field_write(charger, CHARGE_CURRENT, charger->init_data.ichg);
++		bq25700_get_chip_state(charger, &state);
++		charger->state = state;
++		power_supply_changed(charger->supply_charger);
++		DBG("BQ25700: set irq_flag = IRQF_TRIGGER_LOW\n");
	} else {
		irq_flag = IRQF_TRIGGER_HIGH;
		
		bq25700_field_write(charger, INPUT_CURRENT, charger->init_data.input_current);
		bq25700_disable_charge(charger);
		bq25700_get_chip_state(charger, &state);
		charger->state = state;
		power_supply_changed(charger->supply_charger);
		charger->typec0_status = USB_STATUS_NONE;
		charger->typec1_status = USB_STATUS_NONE;
++    DBG("BQ25700:set irq_flag = IRQF_TRIGGER_HIGH\n");
	}
	irq_set_irq_type(irq, irq_flag | IRQF_ONESHOT );
	rk_send_wakeup_key();

	DBG("BQ25700: bq25700_irq_handler_thread done\n");
	return IRQ_HANDLED;
}

```

## 验证结果
在插拔 DC 的时候我们
```
cat /sys/class/i2c-adapter/i2c-4/4-0009/charge_info
```
发现插入 DC 时充电电流为 2.3 A，表示其是可以正常工作的。



## 遇到 Bug
过程中遇到两个问题。
第一个问题是使能 BQ IC 充电的方式
当时查阅 Datasheet 发现说需要 给 CHRG_INHIBIT 写 0 ，表示使能 BQ IC。写 1 表示禁能 BQ IC。如下：
```
bq25700_field_write(charger, CHRG_INHIBIT, 0);
```
所以我就这样写了，但是这个导致的问题是输入电流极大，为 3.25A。再仔细查阅 datasheet 发现，如果采用 CHRG_INHIBIT 来使能 BQ IC 的话，会自动对 INPUT_CURRENT 配置，默认为 3.25A。

![](http://ww1.sinaimg.cn/large/ba061518gy1ffym27db6aj20ej04twew.jpg)

第二个问题很蠢
如下完成写这两个寄存器
```
		bq25700_field_write(charger, INPUT_CURRENT, charger->init_data.input_current);
		bq25700_field_write(charger, CHARGE_CURRENT, charger->init_data.ichg);
```
我们 dts 是这样配的
```
		ti,charge-current = <2500000>;
		ti,input-current = <2000000>;     //2A
		ti,input-current-sdp = <500000>;
		ti,input-current-dcp = <2000000>;
		ti,input-current-cdp = <2000000>;
		ti,minimum-sys-voltage = <7400000>;
```
看起来这样就是配置 INPUT_CURRENT 为 2A 、配置 CHAGRE_CURRENT 为 2.5A 了？
错！
实际上在 dts 解析的过程是没有解析 input_current 的，也就是说其是为 0 的：
```
	struct {
		char *name;
		bool optional;
		enum bq25700_table_ids tbl_id;
		u32 *conv_data; /* holds converted value from given property */
	} props[] = {
		/* required properties */
		{"ti,charge-current", false, TBL_ICHG,
		 &init->ichg},
		{"ti,max-charge-voltage", false, TBL_CHGMAX,
		 &init->max_chg_vol},
		{"ti,input-current-sdp", false, TBL_INPUTCUR,
		 &init->input_current_sdp},
		{"ti,input-current-dcp", false, TBL_INPUTCUR,
		 &init->input_current_dcp},
		{"ti,input-current-cdp", false, TBL_INPUTCUR,
		 &init->input_current_cdp},
		{"ti,minimum-sys-voltage", false, TBL_SYSVMIN,
		 &init->sys_min_voltage},
		{"ti,otg-voltage", false, TBL_OTGVOL,
		 &init->otg_voltage},
		{"ti,otg-current", false, TBL_OTGCUR,
		 &init->otg_current},
	};
```
所以要充 2A 应该改为
```
		bq25700_field_write(charger, INPUT_CURRENT, charger->init_data.input_current_cdp);
```