---
title: [Android6.0][RK3399] 实现耳机和喇叭自动切换功能
tags: 
grammar_cjkRuby: true
---

Platform: RK3399 
OS: Android 6.0 
Kernel: Linux4.4 
Version: v2017.03


[TOC]

## 需求分析
RK 默认的声卡 RT5651（Card 0）是从耳机（device 0）输出。
但是我们的产品上同时具有 Speaker 和 Headphone，两者无法切换。
所以需要实现默认从喇叭输出，插上耳机的情况下从耳机输出的功能。

## 实现方式
查阅原理图
HP_DET_H 为耳机状态检测脚。

![](http://ww1.sinaimg.cn/large/ba061518gy1fissb50xpij20xu0f4gnd.jpg)

SPK_CTL_H 为控制 Speaker 使能管脚。

所以整个的逻辑很简单即 

![](http://ww1.sinaimg.cn/large/ba061518gy1fisse40sdcj20yl0elgnl.jpg)

HP_DET_H 检测耳机状态 
————> 为高  耳机插入，拉底 SPK_CTL_H 禁能喇叭
————> 为低  耳机拔出，拉高 SPK_CTL_H 使能喇叭


## 进行编码

### dts 中添加相应 GPIO，并打开声卡驱动

```
diff --git a/arch/arm64/boot/dts/rockchip/rk3399-orangepi.dts b/arch/arm64/boot/dts/rockchip/rk3399-orangepi.dts
index b9002f7..039c95a 100644
--- a/arch/arm64/boot/dts/rockchip/rk3399-orangepi.dts
+++ b/arch/arm64/boot/dts/rockchip/rk3399-orangepi.dts
@@ -63,6 +63,8 @@
 		compatible = "rockchip,rockchip-rt5651-tc358749x-sound";
 		rockchip,cpu = <&i2s0 &i2s0>;
 		rockchip,codec = <&rt5651 &rt5651 &tc358749x>;
+		spk-con-gpio = <&gpio0 11 GPIO_ACTIVE_HIGH>;
+		hp-det-gpio = <&gpio4 28 GPIO_ACTIVE_HIGH>;
 		status = "okay";
 	};
 
@@ -147,7 +149,7 @@
 		int-gpios = <&gpio2 12 GPIO_ACTIVE_HIGH>;
 		pinctrl-names = "default";
 		pinctrl-0 = <&hdmiin_gpios>;
-		status = "disabled";
+		status = "okay";
 	};
 };
 
```

### 修改 snd_soc_card 结构体添加相关成员变量

```
diff --git a/include/sound/soc.h b/include/sound/soc.h
index fb955e6..e6b3ac7 100644
--- a/include/sound/soc.h
+++ b/include/sound/soc.h
@@ -1080,8 +1080,16 @@ struct snd_soc_card {
 	struct mutex mutex;
 	struct mutex dapm_mutex;
 
+	int debounce_time;
+	int hp_det_invert;
+	struct delayed_work work;
+	bool spk_active_level;
+	bool hp_inserted;
+
 	bool instantiated;
 
+	int spk_ctl_gpio;
+	int hp_det_gpio;
 	int (*probe)(struct snd_soc_card *card);
 	int (*late_probe)(struct snd_soc_card *card);
 	int (*remove)(struct snd_soc_card *card);
```

### 添加驱动代码

```
diff --git a/sound/soc/rockchip/rockchip_rt5651_tc358749x.c b/sound/soc/rockchip/rockchip_rt5651_tc358749x.c
index 21f8ee2..14acebd 100644
--- a/sound/soc/rockchip/rockchip_rt5651_tc358749x.c
+++ b/sound/soc/rockchip/rockchip_rt5651_tc358749x.c
@@ -18,12 +18,18 @@
 #include <linux/module.h>
 #include <sound/soc.h>
 
+#include <linux/gpio.h>
+#include <linux/of_gpio.h>
+#include <linux/clk.h>
+
 #include "rockchip_i2s.h"
 #include "../codecs/rt5651.h"
 #include "../codecs/tc358749x.h"
 
 #define DRV_NAME "rk3399-rt5651-tc358749x"
 
+#define INVALID_GPIO -1
+
 static const struct snd_soc_dapm_widget rockchip_dapm_widgets[] = {
 	SND_SOC_DAPM_HP("Headphones", NULL),
 	SND_SOC_DAPM_SPK("Lineout", NULL),
@@ -184,11 +190,58 @@ static struct snd_soc_card rockchip_sound_card = {
 	.num_controls = ARRAY_SIZE(rockchip_controls),
 };
 
+static irqreturn_t rt5651_irq_handler(int irq, void *data)
+{
+	struct snd_soc_card *card = data;
+	queue_delayed_work(system_power_efficient_wq, &card->work,
+			   msecs_to_jiffies(card->debounce_time));
+
+	return IRQ_HANDLED;
+}
+
+static void rt5651_enable_spk(struct snd_soc_card *card, bool enable)
+{
+	bool level;
+
+	level = enable ? card->spk_active_level : !card->spk_active_level;
+	gpio_set_value(card->spk_ctl_gpio, level);
+}
+
+static void hp_work(struct work_struct *work)
+{
+	struct snd_soc_card *card;
+	int enable;
+
+	card = container_of(work, struct snd_soc_card, work.work);
+	enable = gpio_get_value(card->hp_det_gpio);
+	if(card->hp_det_invert)
+		enable = !enable;
+
+	card->hp_inserted = enable ? true : false;
+	if(card->hp_inserted){
+		//printk("hp_work rt5651_enable_spk false\n");
+		rt5651_enable_spk(card, false);
+	}	else {
+		//printk("hp_work rt5651_enable_spk true\n");
+		rt5651_enable_spk(card,true);
+	}
+}
+
 static int rockchip_sound_probe(struct platform_device *pdev)
 {
 	struct snd_soc_card *card = &rockchip_sound_card;
 	struct device_node *cpu_node;
-	int i, ret;
+	int i;
+	int ret = -1;
+
+	int hp_irq;
+	enum of_gpio_flags flags;
+
+	card->debounce_time = 200;
+	card->hp_det_invert = 0;
+	card->hp_inserted = false;
+	card->spk_ctl_gpio = INVALID_GPIO;
+	card->hp_det_gpio = INVALID_GPIO;
 
 	dev_info(&pdev->dev, "%s\n", __func__);
 
@@ -213,6 +266,47 @@ static int rockchip_sound_probe(struct platform_device *pdev)
 		}
 	}
 
+	card->spk_ctl_gpio = of_get_named_gpio_flags(pdev->dev.of_node, "spk-con-gpio", 0, &flags);
+	if(!gpio_is_valid(card->spk_ctl_gpio))	{
+		dev_err(&pdev->dev,"spk-ctl-gpio: %d is invalid\n", card->spk_ctl_gpio);
+		card->spk_ctl_gpio = INVALID_GPIO;
+	}else {
+		dev_info(&pdev->dev,"spk-ctl-gpio: %d is arrivable\n", card->spk_ctl_gpio);
+		card->spk_active_level = !(flags & OF_GPIO_ACTIVE_LOW);
+		ret = devm_gpio_request_one(&pdev->dev, card->spk_ctl_gpio,
+																GPIOF_DIR_OUT,NULL);
+		if(ret) {
+			dev_err(&pdev->dev,"spk_ctl_gpio: request failed!\n");
+		}
+		rt5651_enable_spk(card, true);
+	}
+
+	card->hp_det_gpio = of_get_named_gpio_flags(pdev->dev.of_node,"hp-det-gpio", 0, &flags);
+	if(!gpio_is_valid(card->hp_det_gpio)) {
+		printk("hp-det-gpio: %d is invalid\n",card->hp_det_gpio);
+		card->hp_det_gpio = INVALID_GPIO;
+	}else {
+		INIT_DELAYED_WORK(&card->work, hp_work);
+		card->hp_det_invert = !!(flags & OF_GPIO_ACTIVE_LOW);
+		ret = devm_gpio_request_one (&pdev->dev, card->hp_det_gpio,GPIOF_IN,"hp det");
+		if( ret < 0)
+			return ret;
+		hp_irq = gpio_to_irq(card->hp_det_gpio);
+		ret = devm_request_threaded_irq(&pdev->dev, hp_irq, NULL,
+										rt5651_irq_handler,
+										IRQF_TRIGGER_FALLING |
+										IRQF_TRIGGER_RISING |
+										IRQF_ONESHOT,
+										"rt5651_interrupt", card);
+		if( ret < 0) {
+			dev_err(&pdev->dev, "request_irq: failed %d\n", ret);
+			return ret;
+		}
+
+		schedule_delayed_work(&card->work,
+					msecs_to_jiffies(card->debounce_time));
+	}
+
 	card->dev = &pdev->dev;
 	platform_set_drvdata(pdev, card);
 	ret = devm_snd_soc_register_card(&pdev->dev, card);
```