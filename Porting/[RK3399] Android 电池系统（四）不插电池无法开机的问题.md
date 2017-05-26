---
title: [RK3399] Android 电池系统（四）不插电池无法开机的问题
tags: charger,android,rockchip
grammar_cjkRuby: true
---


[TOC]

在前面我们
1. 分析了 Charger IC BQ25700 的驱动流程
2. 添加了 BQ IC 的 DC 充电功能
3. 分析了 电量计 CW2015 的驱动流程

在这一章，我们完成电量计的移植，并且整合电量计与充电IC。使其协同为电池工作。

## 已知问题与需求分析

现在的 BQ IC Driver 有一个大 Bug。
在接上电池的时候，Battery、Battery+TypeC、Battery+DC 都是可以正常开机的。
但是没有电池的时候，单独 TypeC 或者 DC 开机是有问题的。

RK 反馈他们那边也有这个问题，定位问题在于 bq25600_hw_init ，BQ IC 的初始化配置。
当屏蔽该函数的时候，单独 TypeC 或者 DC 是可以正常开机的。
但是电池的正常工作又必须依赖于它的初始化。

## 解决思路
三条：
1. 寻找 DC / TypeC 开机时对 BQ IC 寄存器初始化的操作   和   bq_hw_init 中进行的操作对比。
2. 在 dts 中配置一个标志位，has_battery，当 has_battery = 1 的时候，加载 bq_hw_init ，没有的时候屏蔽 bq_hw_init
3. 利用 cw2015 电量计 IC ，检测是否有无电池，并根据检测结果决定是否屏蔽 bq_hw_init。

1 当然是正解。
但是寻求了 BQ IC FAE 的帮助，无果，他们反馈理论上 bq_hw_init 中的配置是没问题的，不因采用哪种供电方式而发生改变。
2 缺陷是会生成两套 resource.img ，根据不同的条件使用不同的 resource.img ，这显然是不好的
3 需要移植 cw2015。

综上，只能选择第三种方式了

## 代码移植
### dts
dts 中 对于 cw2015 的配置
```dts
  cw2015@62 {
 		compatible = "cw201x";
 		reg = <0x62>;
 		dc_det_gpio = <&gpio1 23 GPIO_ACTIVE_LOW>; //  DC_DET_H GPIO1_C7
 		//bat_low_gpio = <&gpio0 GPIO_A7 GPIO_ACTIVE_LOW>; 
		//chg_ok_gpio = <&gpio1 1 GPIO_ACTIVE_HIGH>; // CHG_OK_H GPIO1_A1
 		bat_config_info = <0x15 0x42 0x60 0x59 0x52 0x58 0x4D 0x48 0x48 0x44 0x44 0x46 0x49 0x48 0x32
 			0x24 0x20 0x17 0x13 0x0F 0x19 0x3E 0x51 0x45 0x08 0x76 0x0B 0x85 0x0E 0x1C 0x2E 0x3E 0x4D 0x52 0x52
 			0x57 0x3D 0x1B 0x6A 0x2D 0x25 0x43 0x52 0x87 0x8F 0x91 0x94 0x52 0x82 0x8C 0x92 0x96 0xFF 0x7B 0xBB
 			0xCB 0x2F 0x7D 0x72 0xA5 0xB5 0xC1 0x46 0xAE>;
 		is_dc_charge = <1>;
		is_usb_charge = <1>;
};
```

### Makefile 和 Kconfig
//Todo
obj-y

### cw2015_battery.c
修改 cw2015_battery 的代码是适用于 rk3288 平台的，有些接口进行了升级。
包括 i2c_master_reg8_send/write 和 register_power_supply
并且我们还 定义了 have_battery 标志位，判断出电池有无，并将标志位送给 bq 进行下一步电池初始化的操作。
```
diff --git a/drivers/power/cw2015_battery.c b/drivers/power/cw2015_battery.c
index aaf01fc..5e35216 100755
--- a/drivers/power/cw2015_battery.c
+++ b/drivers/power/cw2015_battery.c
@@ -28,6 +28,12 @@
 
 #include <linux/power/cw2015_battery.h>
 
+int have_battery;
+
+#define VCELL_VOLTAGE 3000000
+#define DEBUG 1
+#define DOUBLE_SERIES_BATTERY 1
+
 static int i2c_master_reg8_send(const struct i2c_client *client, const char reg,
 				const char *buf, int count, int scl_rate)
 {
@@ -47,7 +53,7 @@ static int i2c_master_reg8_send(const struct i2c_client *client, const char reg,
 	msg.flags = client->flags;
 	msg.len = count + 1;
 	msg.buf = (char *)tx_buf;
-	msg.scl_rate = scl_rate;
+	//msg.scl_rate = scl_rate;
 
 	ret = i2c_transfer(adap, &msg, 1);
 	kfree(tx_buf);
@@ -67,13 +73,13 @@ static int i2c_master_reg8_recv(const struct i2c_client *client, const char reg,
 	msgs[0].flags = client->flags;
 	msgs[0].len = 1;
 	msgs[0].buf = &reg_buf;
-	msgs[0].scl_rate = scl_rate;
+	//msgs[0].scl_rate = scl_rate;
 
 	msgs[1].addr = client->addr;
 	msgs[1].flags = client->flags | I2C_M_RD;
 	msgs[1].len = count;
 	msgs[1].buf = (char *)buf;
-	msgs[1].scl_rate = scl_rate;
+	//msgs[1].scl_rate = scl_rate;
 
 	ret = i2c_transfer(adap, msgs, 2);
 
@@ -562,6 +568,9 @@ static int cw_get_vol(struct cw_battery *cw_bat)
 	}
 
 	voltage = value16_1 * 305;
+	
+	if(DOUBLE_SERIES_BATTERY)
+		voltage = voltage * 2;
 
 	dev_dbg(&cw_bat->client->dev, "the cw201x voltage=%d,reg_val=%x %x\n",
 		voltage, reg_val[0], reg_val[1]);
@@ -813,14 +822,14 @@ static void cw_bat_work(struct work_struct *work)
 	if (cw_bat->plat_data.is_dc_charge == 1) {
 		ret = rk_ac_update_online(cw_bat);
 		if (ret == 1)
-			power_supply_changed(&cw_bat->rk_ac);
+			power_supply_changed(cw_bat->rk_ac);
 	}
 
 	if (cw_bat->plat_data.is_usb_charge == 1) {
 		ret = rk_usb_update_online(cw_bat);
 		if (ret == 1) {
-			power_supply_changed(&cw_bat->rk_usb);
-			power_supply_changed(&cw_bat->rk_ac);
+			power_supply_changed(cw_bat->rk_usb);
+			power_supply_changed(cw_bat->rk_ac);
 		}
 	}
 
@@ -830,12 +839,12 @@ static void cw_bat_work(struct work_struct *work)
 	rk_bat_update_time_to_empty(cw_bat);
 
 	if (cw_bat->bat_change) {
-		power_supply_changed(&cw_bat->rk_bat);
+		power_supply_changed(cw_bat->rk_bat);
 		cw_bat->bat_change = 0;
 	}
 
 	queue_delayed_work(cw_bat->battery_workqueue,
-			   &cw_bat->battery_delay_work, msecs_to_jiffies(1000));
+			   &cw_bat->battery_delay_work, msecs_to_jiffies(10000));
 
 	dev_dbg(&cw_bat->client->dev,
 		"cw_bat->bat_change = %d, cw_bat->time_to_empty = %d, cw_bat->capacity = %d\n",
@@ -851,9 +860,9 @@ static int rk_usb_get_property(struct power_supply *psy,
 			       union power_supply_propval *val)
 {
 	int ret = 0;
-	struct cw_battery *cw_bat;
+	struct cw_battery *cw_bat = power_supply_get_drvdata(psy);
 
-	cw_bat = container_of(psy, struct cw_battery, rk_usb);
+	//cw_bat = container_of(psy, struct cw_battery, rk_usb);
 	switch (psp) {
 	case POWER_SUPPLY_PROP_ONLINE:
 		val->intval = (cw_bat->charger_mode == USB_CHARGER_MODE);
@@ -873,9 +882,9 @@ static int rk_ac_get_property(struct power_supply *psy,
 			      union power_supply_propval *val)
 {
 	int ret = 0;
-	struct cw_battery *cw_bat;
+	struct cw_battery *cw_bat = power_supply_get_drvdata(psy);
 
-	cw_bat = container_of(psy, struct cw_battery, rk_ac);
+	//cw_bat = container_of(psy, struct cw_battery, rk_ac);
 	switch (psp) {
 	case POWER_SUPPLY_PROP_ONLINE:
 		val->intval = (cw_bat->charger_mode == AC_CHARGER_MODE);
@@ -895,9 +904,9 @@ static int rk_battery_get_property(struct power_supply *psy,
 				   union power_supply_propval *val)
 {
 	int ret = 0;
-	struct cw_battery *cw_bat;
+	struct cw_battery *cw_bat = power_supply_get_drvdata(psy);
 
-	cw_bat = container_of(psy, struct cw_battery, rk_bat);
+	//cw_bat = container_of(psy, struct cw_battery, rk_bat);
 	switch (psp) {
 	case POWER_SUPPLY_PROP_CAPACITY:
 		val->intval = cw_bat->capacity;
@@ -941,6 +950,67 @@ static enum power_supply_property rk_battery_properties[] = {
 	POWER_SUPPLY_PROP_TECHNOLOGY,
 };
 
+
+static  const struct power_supply_desc cw_bat_desc = {
+	.name	= "rk-bat",
+	.type	= POWER_SUPPLY_TYPE_BATTERY,
+	.properties = rk_battery_properties,
+	.num_properties = ARRAY_SIZE(rk_battery_properties),
+	.get_property = rk_battery_get_property,
+};
+
+static  const struct power_supply_desc cw_ac_desc = {
+	.name	= "rk-ac",
+	.type	= POWER_SUPPLY_TYPE_MAINS,
+	.properties = rk_ac_properties,
+	.num_properties = ARRAY_SIZE(rk_ac_properties),
+	.get_property = rk_ac_get_property,
+};
+
+static  const struct power_supply_desc cw_usb_desc = {
+	.name	= "rk-usb",
+	.type	= POWER_SUPPLY_TYPE_USB,
+	.properties = rk_usb_properties,
+	.num_properties = ARRAY_SIZE(rk_usb_properties),
+	.get_property = rk_usb_get_property,
+};
+
+
+static int cw_init_power_supply(struct cw_battery *bat)
+{
+	struct power_supply_config psy_cfg = {.drv_data = bat, };
+	
+	bat->rk_bat = power_supply_register(&bat->client->dev, &cw_bat_desc, &psy_cfg);
+	if (IS_ERR(bat->rk_bat)) {
+		dev_err(&bat->client->dev,
+			"power supply register rk_bat error\n");
+		return PTR_ERR(bat->rk_bat);
+	}
+	
+	bat->rk_ac = power_supply_register(&bat->client->dev, &cw_ac_desc, &psy_cfg);
+	if (IS_ERR(bat->rk_ac)) {
+		dev_err(&bat->client->dev,
+			"power supply register rk_ac error\n");
+		return PTR_ERR(bat->rk_ac);
+	}
+
+	if(bat->plat_data.is_usb_charge == 1) {
+		bat->rk_usb = power_supply_register(&bat->client->dev, &cw_usb_desc, &psy_cfg);
+		if (IS_ERR(bat->rk_usb)) {
+			dev_err(&bat->client->dev,
+				"power supply register rk_usb error\n");
+			return PTR_ERR(bat->rk_usb);
+		}
+		bat->charger_init_mode = dwc_otg_check_dpdm();
+		pr_info("%s cw2015 support charger by usb. usb_mode=%d\n",
+			__func__, bat->charger_init_mode);
+	}
+	return 0;
+}
+
 static int cw_bat_gpio_init(struct cw_battery *cw_bat)
 {
 	int ret;

@@ -1236,45 +1308,10 @@ static int cw_bat_probe(struct i2c_client *client,
 		return ret;
 	}
 
-	cw_bat->rk_bat.name = "rk-bat";
-	cw_bat->rk_bat.type = POWER_SUPPLY_TYPE_BATTERY;
-	cw_bat->rk_bat.properties = rk_battery_properties;
-	cw_bat->rk_bat.num_properties = ARRAY_SIZE(rk_battery_properties);
-	cw_bat->rk_bat.get_property = rk_battery_get_property;
-	ret = power_supply_register(&client->dev, &cw_bat->rk_bat);
-	if (ret < 0) {
-		dev_err(&cw_bat->client->dev,
-			"power supply register rk_bat error\n");
-		goto rk_bat_register_fail;
-	}
-
-	cw_bat->rk_ac.name = "rk-ac";
-	cw_bat->rk_ac.type = POWER_SUPPLY_TYPE_MAINS;
-	cw_bat->rk_ac.properties = rk_ac_properties;
-	cw_bat->rk_ac.num_properties = ARRAY_SIZE(rk_ac_properties);
-	cw_bat->rk_ac.get_property = rk_ac_get_property;
-	ret = power_supply_register(&client->dev, &cw_bat->rk_ac);
-	if (ret < 0) {
-		dev_err(&cw_bat->client->dev,
-			"power supply register rk_ac error\n");
-		goto rk_ac_register_fail;
-	}
-
-	if (cw_bat->plat_data.is_usb_charge == 1) {
-		cw_bat->rk_usb.name = "rk-usb";
-		cw_bat->rk_usb.type = POWER_SUPPLY_TYPE_USB;
-		cw_bat->rk_usb.properties = rk_usb_properties;
-		cw_bat->rk_usb.num_properties = ARRAY_SIZE(rk_usb_properties);
-		cw_bat->rk_usb.get_property = rk_usb_get_property;
-		ret = power_supply_register(&client->dev, &cw_bat->rk_usb);
-		if (ret < 0) {
-			dev_err(&cw_bat->client->dev,
-				"power supply register rk_usb error\n");
-			goto rk_usb_register_fail;
-		}
-		cw_bat->charger_init_mode = dwc_otg_check_dpdm();
-		pr_info("%s cw2015 support charger by usb. usb_mode=%d\n",
-			__func__, cw_bat->charger_init_mode);
+	ret = cw_init_power_supply(cw_bat);
+	if (ret) {
+		dev_err(&cw_bat->client->dev, "init power supply fail!\n");
+		return ret;
 	}
 
 	cw_bat->dc_online = 0;
@@ -1304,7 +1341,7 @@ static int cw_bat_probe(struct i2c_client *client,
 		}
 		irq_flags = level ? IRQF_TRIGGER_FALLING : IRQF_TRIGGER_RISING;
 		ret =
-		    request_irq(irq, dc_detect_irq_handler, irq_flags,
+		    request_irq(irq, dc_detect_irq_handler, irq_flags | IRQF_SHARED,
 				"dc_detect", cw_bat);
 		if (ret < 0)
 			pr_err("%s: request_irq(%d) failed\n", __func__, irq);
@@ -1331,14 +1368,17 @@ static int cw_bat_probe(struct i2c_client *client,
 
 	dev_info(&cw_bat->client->dev,
 		 "cw2015/cw2013 driver v1.2 probe sucess\n");
+
+	ret = cw_get_vol(cw_bat);
+	if(ret > VCELL_VOLTAGE){		
+		have_battery = 1;
+		dev_info(&cw_bat->client->dev,"FOUND BAT! have_battery = %d\n",have_battery);
+	}else{
+		have_battery = 0;
+		dev_dbg(&cw_bat->client->dev,"NOT FOUND BAT! have_battery = %d\n",have_battery);
+	}
 	return 0;
 
-rk_usb_register_fail:
-	power_supply_unregister(&cw_bat->rk_usb);
-rk_ac_register_fail:
-	power_supply_unregister(&cw_bat->rk_ac);
-rk_bat_register_fail:
-	power_supply_unregister(&cw_bat->rk_bat);
 pdate_fail:
 	dev_info(&cw_bat->client->dev,
 		 "cw2015/cw2013 driver v1.2 probe error!!!!\n");

diff --git a/include/linux/power/cw2015_battery.h b/include/linux/power/cw2015_battery.h
index 6f14aa7..1a3c203 100644
--- a/include/linux/power/cw2015_battery.h
+++ b/include/linux/power/cw2015_battery.h
@@ -78,9 +78,9 @@ struct cw_battery {
 	struct delayed_work bat_low_wakeup_work;
 	struct cw_bat_platform_data plat_data;
 
-	struct power_supply rk_bat;
-	struct power_supply rk_ac;
-	struct power_supply rk_usb;
+	struct power_supply *rk_bat;
+	struct power_supply *rk_ac;
+	struct power_supply *rk_usb;
 
 	long sleep_time_capacity_change;
 	long run_time_capacity_change;
@@ -102,7 +102,10 @@ struct cw_battery {
 };
 
 #if defined(CONFIG_ARCH_ROCKCHIP)
-int get_gadget_connect_flag(void);
+int get_gadget_connect_flag(void)
+{
+	return 0;
+}
 int dwc_otg_check_dpdm(void);
 int dwc_vbus_status(void);
 #else
@@ -116,10 +119,11 @@ static inline int dwc_otg_check_dpdm(bool wait)
 	return 0;
 }
 
-static inline int dwc_vbus_status(void);
+static inline int dwc_vbus_status(void)
 {
 	return 0;
 }
+
 #endif
 
 #endif

```

### bq25700_charger.c
在 bq 中我们会根据 cw 中获得到的电池的状态来操作 是否进行 BQ IC 寄存器的初始化（hw_init）
```diff
--- a/drivers/power/bq25700_charger.c
+++ b/drivers/power/bq25700_charger.c
@@ -33,6 +33,8 @@
 #include <linux/of_gpio.h>
 #include <linux/rk_keys.h>
 
+extern int have_battery;
+
 static int dbg_enable = 1;
 module_param_named(dbg_level, dbg_enable, int, 0644);
 
@@ -741,7 +743,7 @@ static int bq25700_chip_reset(struct bq25700_device *charger)
 {
 	int ret;
 	int rst_check_counter = 10;
-	return 0;
+	//return 0;  // hw_init 中不需要 chip reset ，关掉
 
 	DBG("BQ25700: bq25700_chip_reset\n");
 	ret = bq25700_field_write(charger, RESET_REG, 1);
@@ -781,7 +783,14 @@ static int bq25700_hw_init(struct bq25700_device *charger)
 		{OTG_CURRENT,	 charger->init_data.otg_current},
 	};
 
-	DBG("BQ25700: bq25700_hw_init.\n");
+	if(!have_battery)  //如果没有电池，就 bq25700_hw_init 就直接返回
+	{
+		DBG("BQ25700: CW said NO BAT FOUND!\n");
+		return -1;
+	}
+
+	DBG("BQ25700: We have BAT,bq25700_hw_init.\n");
 	ret = bq25700_chip_reset(charger);
 	if (ret < 0)
 		return ret;
@@ -887,6 +896,46 @@ static int bq25700_hw_init(struct bq25700_device *charger)
 		return ret;
 	}
 
 
 // 将中断设为 共享中断
@@ -1079,7 +1139,7 @@ static irqreturn_t bq25700_irq_handler_thread(int irq, void *private)
 		charger->typec1_status = USB_STATUS_NONE;
 		DBG("BQ25700: irq_flag = IRQF_TRIGGER_HIGH\n");
 	}
-	irq_set_irq_type(irq, irq_flag | IRQF_ONESHOT);
+	irq_set_irq_type(irq, irq_flag | IRQF_ONESHOT | IRQF_SHARED);
 	rk_send_wakeup_key();
 
 	DBG("BQ25700: bq25700_irq_handler_thread done\n");
@@ -1815,7 +1875,7 @@ while(1) {
 
 	ret = devm_request_threaded_irq(dev, client->irq, NULL,
 					bq25700_irq_handler_thread,
-					irq_flag | IRQF_ONESHOT,
+					irq_flag | IRQF_ONESHOT | IRQF_SHARED,
 					"bq25700_irq", charger);
 	if (ret)
 		goto irq_fail;
@@ -1825,18 +1885,6 @@ while(1) {
 
 	DBG("BQ25700: enable_irq_wake done.\n");
```
 
 
 ## 验证结果
 ```
 ls sys/class/power_supply/ 
 bq25700_charger rk_ac rk_usb rk_bat
 ```
 可以看到四个设备
bq25700_charger rk_ac rk_usb rk_bat
bq25700_charger 是在 bq 中注册的 Type = POWER_SUPPLY_TYPE_USB 的设备
rk_ac 是在 cw 中注册的 Type = POWER_SUPPLY_TYPE_MAINS 的设备
rk_usb 是在 cw 中注册的 Type = POWER_SUPPLY_TYPE_USB 的设备
rk_bat  是在 cw 中注册的 Type = POWER_SUPPLY_TYPE_BATTERY 的设备

均注册正常。
而且无论是否接电池，现在都可以正常开机。
