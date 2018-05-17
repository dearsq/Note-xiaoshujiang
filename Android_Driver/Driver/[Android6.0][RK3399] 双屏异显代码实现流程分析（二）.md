---
title: [Android6.0][RK3399] 双屏异显代码实现流程分析（二）
tags: Rockchip,
grammar_cjkRuby: true
---
[toc]

Platform: RK3399 
OS: Android 6.0 
Version: v2016.08
LCD interface: eDP + mipi

## Patch Code
Date: Fri, 09 Dec 2016 10:53:11 +0800
Subject: [PATCH] video: rockchip: fb: add support dual lcd
Change-Id: I246f8e7d725d26abf2555d3077dd87da72920731
Signed-off-by: Huang Jiachai < ××× >


### **dtsi**
#### rk3399-android.dtsi

```
diff --git a/arch/arm64/boot/dts/rockchip/rk3399-android.dtsi b/arch/arm64/boot/dts/rockchip/rk3399-android.dtsi
index a009537..05a8377 100644
--- a/arch/arm64/boot/dts/rockchip/rk3399-android.dtsi
+++ b/arch/arm64/boot/dts/rockchip/rk3399-android.dtsi
@@ -287,7 +287,7 @@
 		status = "okay";
 		compatible = "rockchip,rk-fb";
 		rockchip,disp-mode = <DUAL>;
-		rockchip,uboot-logo-on = <1>;
+		rockchip,uboot-logo-on = <0>;
 		memory-region = <&rockchip_logo>;
 	};
```
 

#### rk3399-evb-rev3-android.dts
 在 rk_screen 中默认只有一个 screen0, 用于填充 primary screen 的 timing
 现在需要添加 screen1，用于填充 extend screen 的 timing
```
diff --git a/arch/arm64/boot/dts/rockchip/rk3399-evb-rev3-android.dts b/arch/arm64/boot/dts/rockchip/rk3399-evb-rev3-android.dts
index 3b3ff7c..3653205 100644
--- a/arch/arm64/boot/dts/rockchip/rk3399-evb-rev3-android.dts
+++ b/arch/arm64/boot/dts/rockchip/rk3399-evb-rev3-android.dts
@@ -51,18 +51,55 @@
 };
 
 &rk_screen {
-	#include <dt-bindings/display/screen-timing/lcd-tv080wum-nl0-mipi.dtsi>
+	status = "okay";
+	screen0 {
+		screen_prop = <PRMRY>;
+		native-mode = <DEFAULT_MODE>;
+		power_ctr {
+			lcd_en0: lcd-en {
+				rockchip,power_type = <GPIO>;
+				gpios = <&gpio1 13 GPIO_ACTIVE_HIGH>;
+				rockchip,delay = <10>;
+			};
+			/* lcd_cs {
+				rockchip,power_type = <GPIO>;
+				gpios = <&gpio7 GPIO_A4 GPIO_ACTIVE_HIGH>;
+				rockchip,delay = <10>;
+			}; */
+		};
+		#include <dt-bindings/display/screen-timing/lcd-tv080wum-nl0-mipi.dtsi>
+		//#include <dt-bindings/display/screen-timing/lcd-F402.dtsi>
+	};
+	screen1 {
+		screen_prop = <EXTEND>;
+		native-mode = <DEFAULT_MODE>;
+		power_ctr {
+			/* cd_en1: lcd-en {
+				rockchip,power_type = <GPIO>;
+				gpios = <&gpio1 13 GPIO_ACTIVE_HIGH>;
+				rockchip,delay = <10>;
+			};*/
+			/* lcd_cs {
+				rockchip,power_type = <GPIO>;
+				gpios = <&gpio7 GPIO_A4 GPIO_ACTIVE_HIGH>;
+				rockchip,delay = <10>;
+			}; */
+		};
+		#include <dt-bindings/display/screen-timing/lcd-F402.dtsi>
+		//#include <dt-bindings/display/screen-timing/lcd-tv080wum-nl0-mipi.dtsi>
+		//#include "lcd-box.dtsi"
+	};
 };
 
 &vopb_rk_fb {
 	status = "okay";
 	power_ctr: power_ctr {
 		rockchip,debug = <0>;
-		lcd_en: lcd-en {
+		/* lcd_en: lcd-en {
 			rockchip,power_type = <GPIO>;
 			gpios = <&gpio1 13 GPIO_ACTIVE_HIGH>;
 			rockchip,delay = <10>;
-		};
+		}; */
 
 		/*lcd_cs: lcd-cs {
 			rockchip,power_type = <GPIO>;
@@ -80,14 +117,23 @@
 
 &vopl_rk_fb {
 	status = "okay";
+	rockchip,uboot-logo-on = <0>;
 };

//设置 mipi 通道的为主屏， eDP 的为副屏

 &mipi0_rk_fb {
 	status = "okay";
+	prop = <PRMRY>;
+	//prop = <EXTEND>;
+};
+
+&edp_rk_fb {
+	status = "okay";
+	prop = <EXTEND>;
+	//prop = <PRMRY>;
 };
 
 &hdmi_rk_fb {
-	status = "okay";
+	status = "disabled";
 	rockchip,hdmi_video_source = <DISPLAY_SOURCE_LCDC1>;
 };
 ```
 
 ```
diff --git a/arch/arm64/boot/dts/rockchip/rk3399-evb.dtsi b/arch/arm64/boot/dts/rockchip/rk3399-evb.dtsi
index b3c7141..b72ce6c 100644
--- a/arch/arm64/boot/dts/rockchip/rk3399-evb.dtsi
+++ b/arch/arm64/boot/dts/rockchip/rk3399-evb.dtsi
@@ -101,7 +101,7 @@
 			232 233 234 235 236 237 238 239
 			240 241 242 243 244 245 246 247
 			248 249 250 251 252 253 254 255>;
-		default-brightness-level = <200>;
+		default-brightness-level = <128>;
 	};
 
 	clkin_gmac: external-gmac-clock {
@@ -370,7 +370,7 @@
 };
 
 &i2c4 {
-	status = "okay";
+	status = "disabled";
 	i2c-scl-rising-time-ns = <600>;
 	i2c-scl-falling-time-ns = <20>;
```

### **lcdc 控制器**
#### rk322x_lcdc.c
```
diff --git a/drivers/video/rockchip/lcdc/rk322x_lcdc.c b/drivers/video/rockchip/lcdc/rk322x_lcdc.c
index 93c996a..d6bdff3 100644
--- a/drivers/video/rockchip/lcdc/rk322x_lcdc.c
+++ b/drivers/video/rockchip/lcdc/rk322x_lcdc.c
@@ -5252,6 +5252,10 @@
 
 	rk322x_pdev = pdev;
 
+	if (dev_drv->cur_screen->type != SCREEN_HDMI &&
+		dev_drv->cur_screen->type != SCREEN_TVOUT)
+		dev_drv->hot_plug_state = 1;
+
 	if (dev_drv->cur_screen->refresh_mode == SCREEN_CMD_MODE) {
 		te_pin = of_get_named_gpio_flags(np, "te-gpio", 0, NULL);
 		if (IS_ERR_VALUE(te_pin)) {
```

#### rk_fb.c
```
diff --git a/drivers/video/rockchip/rk_fb.c b/drivers/video/rockchip/rk_fb.c
index 25563a4..80db2e2 100644
--- a/drivers/video/rockchip/rk_fb.c
+++ b/drivers/video/rockchip/rk_fb.c
@@ -73,9 +73,8 @@
 extern phys_addr_t uboot_logo_base;
 extern phys_addr_t uboot_logo_size;
 extern phys_addr_t uboot_logo_offset;
-static struct rk_fb_trsm_ops *trsm_lvds_ops;
-static struct rk_fb_trsm_ops *trsm_edp_ops;
-static struct rk_fb_trsm_ops *trsm_mipi_ops;
+static struct rk_fb_trsm_ops *trsm_prmry_ops;
+static struct rk_fb_trsm_ops *trsm_extend_ops;
 static int uboot_logo_on;
 
 static int rk_fb_debug_lvl;
@@ -115,26 +114,13 @@
 
 int rk_fb_trsm_ops_register(struct rk_fb_trsm_ops *ops, int type)
 {
-	switch (type) {
-	case SCREEN_RGB:
-	case SCREEN_LVDS:
-	case SCREEN_DUAL_LVDS:
-	case SCREEN_LVDS_10BIT:
-	case SCREEN_DUAL_LVDS_10BIT:
-		trsm_lvds_ops = ops;
-		break;
-	case SCREEN_EDP:
-		trsm_edp_ops = ops;
-		break;
-	case SCREEN_MIPI:
-	case SCREEN_DUAL_MIPI:
-		trsm_mipi_ops = ops;
-		break;
-	default:
-		pr_warn("%s: unsupported transmitter: %d!\n",
-			__func__, type);
-		break;
-	}
+	if (type == PRMRY)
+		trsm_prmry_ops = ops;
+	else if (type == EXTEND)
+		trsm_extend_ops = ops;
+	else
+		pr_err("%s, type:%d\n", __func__, type);
+
 	return 0;
 }
 
@@ -142,27 +128,12 @@
 {
 	struct rk_fb_trsm_ops *ops;
 
-	switch (type) {
-	case SCREEN_RGB:
-	case SCREEN_LVDS:
-	case SCREEN_DUAL_LVDS:
-	case SCREEN_LVDS_10BIT:
-	case SCREEN_DUAL_LVDS_10BIT:
-		ops = trsm_lvds_ops;
-		break;
-	case SCREEN_EDP:
-		ops = trsm_edp_ops;
-		break;
-	case SCREEN_MIPI:
-	case SCREEN_DUAL_MIPI:
-		ops = trsm_mipi_ops;
-		break;
-	default:
-		ops = NULL;
-		pr_warn("%s: unsupported transmitter: %d!\n",
-			__func__, type);
-		break;
-	}
+	if (type == PRMRY)
+		ops = trsm_prmry_ops;
+	else if (type == EXTEND)
+		ops = trsm_extend_ops;
+	else
+		pr_err("%s, type:%d\n", __func__, type);
 	return ops;
 }
 
@@ -317,10 +288,10 @@
 /*
  * rk display power control parse from dts
  */
-int rk_disp_pwr_ctr_parse_dt(struct rk_lcdc_driver *dev_drv)
+int rk_disp_pwr_ctr_parse_dt(struct device_node *np,
+			     struct rk_screen *rk_screen)
 {
-	struct device_node *root = of_get_child_by_name(dev_drv->dev->of_node,
-							"power_ctr");
+	struct device_node *root = of_get_child_by_name(np, "power_ctr");
 	struct device_node *child;
 	struct rk_disp_pwr_ctr_list *pwr_ctr;
 	struct list_head *pos;
@@ -329,10 +300,10 @@
 	u32 debug = 0;
 	int ret;
 
-	INIT_LIST_HEAD(&dev_drv->pwrlist_head);
+	INIT_LIST_HEAD(rk_screen->pwrlist_head);
 	if (!root) {
-		dev_err(dev_drv->dev, "can't find power_ctr node for lcdc%d\n",
-			dev_drv->id);
+		dev_err(rk_screen->dev, "can't find power_ctr node for lcdc%d\n",
+			rk_screen->lcdc_id);
 		return -ENODEV;
 	}
 
@@ -347,7 +318,7 @@
 				pwr_ctr->pwr_ctr.type = GPIO;
 				pwr_ctr->pwr_ctr.gpio = of_get_gpio_flags(child, 0, &flags);
 				if (!gpio_is_valid(pwr_ctr->pwr_ctr.gpio)) {
-					dev_err(dev_drv->dev, "%s ivalid gpio\n",
+					dev_err(rk_screen->dev, "%s ivalid gpio\n",
 						child->name);
 					return -EINVAL;
 				}
@@ -355,7 +326,7 @@
 				ret = gpio_request(pwr_ctr->pwr_ctr.gpio,
 						   child->name);
 				if (ret) {
-					dev_err(dev_drv->dev,
+					dev_err(rk_screen->dev,
 						"request %s gpio fail:%d\n",
 						child->name, ret);
 				}
@@ -364,9 +335,9 @@
 				pwr_ctr->pwr_ctr.type = REGULATOR;
 				pwr_ctr->pwr_ctr.rgl_name = NULL;
 				ret = of_property_read_string(child, "rockchip,regulator_name",
-							      &(pwr_ctr->pwr_ctr.rgl_name));
+							     &(pwr_ctr->pwr_ctr.rgl_name));
 				if (ret || IS_ERR_OR_NULL(pwr_ctr->pwr_ctr.rgl_name))
-					dev_err(dev_drv->dev, "get regulator name failed!\n");
+					dev_err(rk_screen->dev, "get regulator name failed!\n");
 				if (!of_property_read_u32(child, "rockchip,regulator_voltage", &val))
 					pwr_ctr->pwr_ctr.volt = val;
 				else
@@ -378,29 +349,30 @@
 			pwr_ctr->pwr_ctr.delay = val;
 		else
 			pwr_ctr->pwr_ctr.delay = 0;
-		list_add_tail(&pwr_ctr->list, &dev_drv->pwrlist_head);
+		list_add_tail(&pwr_ctr->list, rk_screen->pwrlist_head);
 	}
 
 	of_property_read_u32(root, "rockchip,debug", &debug);
 
 	if (debug) {
-		list_for_each(pos, &dev_drv->pwrlist_head) {
+		list_for_each(pos, rk_screen->pwrlist_head) {
 			pwr_ctr = list_entry(pos, struct rk_disp_pwr_ctr_list,
 					     list);
-			pr_info("pwr_ctr_name:%s\n"
-				"pwr_type:%s\n"
-				"gpio:%d\n"
-				"atv_val:%d\n"
-				"delay:%d\n\n",
-				pwr_ctr->pwr_ctr.name,
-				(pwr_ctr->pwr_ctr.type == GPIO) ? "gpio" : "regulator",
-				pwr_ctr->pwr_ctr.gpio,
-				pwr_ctr->pwr_ctr.atv_val,
-				pwr_ctr->pwr_ctr.delay);
+			printk(KERN_INFO "pwr_ctr_name:%s\n"
+			       "pwr_type:%s\n"
+			       "gpio:%d\n"
+			       "atv_val:%d\n"
+			       "delay:%d\n\n",
+			       pwr_ctr->pwr_ctr.name,
+			       (pwr_ctr->pwr_ctr.type == GPIO) ? "gpio" : "regulator",
+			       pwr_ctr->pwr_ctr.gpio,
+			       pwr_ctr->pwr_ctr.atv_val,
+			       pwr_ctr->pwr_ctr.delay);
 		}
 	}
 
 	return 0;
+
 }
 
 int rk_disp_pwr_enable(struct rk_lcdc_driver *dev_drv)
@@ -411,9 +383,14 @@
 	struct regulator *regulator_lcd = NULL;
 	int count = 10;
 
-	if (list_empty(&dev_drv->pwrlist_head))
+	if (!dev_drv->cur_screen->pwrlist_head) {
+		pr_info("error:  %s, lcdc%d screen pwrlist null\n",
+			__func__, dev_drv->id);
 		return 0;
-	list_for_each(pos, &dev_drv->pwrlist_head) {
+	}
+	if (list_empty(dev_drv->cur_screen->pwrlist_head))
+		return 0;
+	list_for_each(pos, dev_drv->cur_screen->pwrlist_head) {
 		pwr_ctr_list = list_entry(pos, struct rk_disp_pwr_ctr_list,
 					  list);
 		pwr_ctr = &pwr_ctr_list->pwr_ctr;
@@ -422,8 +399,7 @@
 			mdelay(pwr_ctr->delay);
 		} else if (pwr_ctr->type == REGULATOR) {
 			if (pwr_ctr->rgl_name)
-				regulator_lcd =
-					regulator_get(NULL, pwr_ctr->rgl_name);
+				regulator_lcd = regulator_get(NULL, pwr_ctr->rgl_name);
 			if (regulator_lcd == NULL) {
 				dev_err(dev_drv->dev,
 					"%s: regulator get failed,regulator name:%s\n",
@@ -456,9 +432,14 @@
 	struct regulator *regulator_lcd = NULL;
 	int count = 10;
 
-	if (list_empty(&dev_drv->pwrlist_head))
+	if (!dev_drv->cur_screen->pwrlist_head) {
+		pr_info("error:  %s, lcdc%d screen pwrlist null\n",
+			__func__, dev_drv->id);
 		return 0;
-	list_for_each(pos, &dev_drv->pwrlist_head) {
+	}
+	if (list_empty(dev_drv->cur_screen->pwrlist_head))
+		return 0;
+	list_for_each(pos, dev_drv->cur_screen->pwrlist_head) {
 		pwr_ctr_list = list_entry(pos, struct rk_disp_pwr_ctr_list,
 					  list);
 		pwr_ctr = &pwr_ctr_list->pwr_ctr;
@@ -474,8 +455,7 @@
 				continue;
 			}
 			while (regulator_is_enabled(regulator_lcd) > 0) {
-				if (regulator_disable(regulator_lcd) == 0 ||
-				    count == 0)
+				if (regulator_disable(regulator_lcd) == 0 || count == 0)
 					break;
 				else
 					dev_err(dev_drv->dev,
@@ -530,6 +510,8 @@
 		screen->pin_den = 1;
 	else
 		screen->pin_den = 0;
+	printk("hjc>>>prop:%d, x:%d, y:%d, dclk:%d\n", screen->prop,
+		screen->mode.xres, screen->mode.yres, screen->mode.pixclock);
 
 	return 0;
 }
@@ -544,7 +526,7 @@
 		pr_err("parse display timing err\n");
 		return -EINVAL;
 	}
-	dt = display_timings_get(disp_timing, disp_timing->native_mode);
+	dt = display_timings_get(disp_timing, screen->native_mode);
 	rk_fb_video_mode_from_timing(dt, screen);
 
 	return 0;
@@ -3942,7 +3924,8 @@
 		win = dev_drv->win[win_id];
 
 	if (!strcmp(fbi->fix.id, "fb0")) {
-		fb_mem_size = get_fb_size(dev_drv->reserved_fb);
+		fb_mem_size = get_fb_size(dev_drv->reserved_fb,
+					  dev_drv->cur_screen);
 #if defined(CONFIG_ION_ROCKCHIP)
 		if (rk_fb_alloc_buffer_by_ion(fbi, win, fb_mem_size) < 0)
 			return -ENOMEM;
@@ -3963,8 +3946,7 @@
 		if (dev_drv->prop == EXTEND && dev_drv->iommu_enabled) {
 			struct rk_lcdc_driver *dev_drv_prmry;
 			int win_id_prmry;
-
-			fb_mem_size = get_fb_size(dev_drv->reserved_fb);
+			fb_mem_size = get_fb_size(dev_drv->reserved_fb, dev_drv->cur_screen);
 #if defined(CONFIG_ION_ROCKCHIP)
 			dev_drv_prmry = rk_get_prmry_lcdc_drv();
 			if (dev_drv_prmry == NULL)
@@ -4129,14 +4111,9 @@
 		dev_drv->area_support[i] = 1;
 	if (dev_drv->ops->area_support_num)
 		dev_drv->ops->area_support_num(dev_drv, dev_drv->area_support);
-	rk_disp_pwr_ctr_parse_dt(dev_drv);
-	if (dev_drv->prop == PRMRY) {
-		rk_fb_set_prmry_screen(screen);
-		rk_fb_get_prmry_screen(screen);
-	}
-	dev_drv->trsm_ops = rk_fb_trsm_ops_get(screen->type);
-	if (dev_drv->prop != PRMRY)
-		rk_fb_get_extern_screen(screen);
+	rk_fb_set_screen(screen, dev_drv->prop);
+	rk_fb_get_screen(screen, dev_drv->prop);
+	dev_drv->trsm_ops = rk_fb_trsm_ops_get(dev_drv->prop);
 	dev_drv->output_color = screen->color_mode;
 
 	return 0;
@@ -4511,15 +4488,24 @@
 		struct fb_info *extend_fbi = rk_fb->fb[dev_drv->fb_index_base];
 
 		extend_fbi->var.pixclock = rk_fb->fb[0]->var.pixclock;
-		if (rk_fb->disp_mode == DUAL_LCD) {
-			extend_fbi->fbops->fb_open(extend_fbi, 1);
-			if (dev_drv->iommu_enabled) {
-				if (dev_drv->mmu_dev)
-					rockchip_iovmm_set_fault_handler(dev_drv->dev,
-									 rk_fb_sysmmu_fault_handler);
-			}
-			rk_fb_alloc_buffer(extend_fbi);
+		extend_fbi->var.xres_virtual = rk_fb->fb[0]->var.xres_virtual;
+		extend_fbi->var.yres_virtual = rk_fb->fb[0]->var.yres_virtual;
+		extend_fbi->var.xres = rk_fb->fb[0]->var.xres;
+		extend_fbi->var.yres = rk_fb->fb[0]->var.yres;
+		extend_fbi->fbops->fb_open(extend_fbi, 1);
+		if (dev_drv->iommu_enabled) {
+			if (dev_drv->mmu_dev)
+				rockchip_iovmm_set_fault_handler(dev_drv->dev,
+								 rk_fb_sysmmu_fault_handler);
+			if (dev_drv->ops->mmu_en)
+				dev_drv->ops->mmu_en(dev_drv);
 		}
+		rk_fb_alloc_buffer(extend_fbi);
+		//if (rk_fb->disp_mode == DUAL_LCD) {
+		extend_fbi->fbops->fb_set_par(extend_fbi);
+		extend_fbi->fbops->fb_pan_display(&extend_fbi->var,
+						  extend_fbi);
+		//}
 	}
 #endif
 	return 0;
```

### **timing 初始化**
#### rk_screen.c
```
diff --git a/drivers/video/rockchip/screen/rk_screen.c b/drivers/video/rockchip/screen/rk_screen.c
index 3a4e6c3..7473e5f 100644
--- a/drivers/video/rockchip/screen/rk_screen.c
+++ b/drivers/video/rockchip/screen/rk_screen.c
@@ -4,57 +4,102 @@
 #include "lcd.h"
 #include "../hdmi/rockchip-hdmi.h"
 
-static struct rk_screen *rk_screen;
+static struct rk_screen *prmry_screen;
+static struct rk_screen *extend_screen;
+
+static void rk_screen_info_error(struct rk_screen *screen, int prop)
+{
+	pr_err(">>>>>>>>>>>>>>>>>>>>error<<<<<<<<<<<<<<<<<<<<\n");
+	pr_err(">>please init %s screen info in dtsi file<<\n",
+		(prop == PRMRY) ? "prmry" : "extend");
+	pr_err(">>>>>>>>>>>>>>>>>>>>error<<<<<<<<<<<<<<<<<<<<\n");
+}
 
 int rk_fb_get_extern_screen(struct rk_screen *screen)
 {
-	if (unlikely(!rk_screen) || unlikely(!screen))
+	if (unlikely(!extend_screen) || unlikely(!screen))
 		return -1;
-
-	memcpy(screen, rk_screen, sizeof(struct rk_screen));
+	memcpy(screen, extend_screen, sizeof(struct rk_screen));
 	screen->dsp_lut = NULL;
 	screen->cabc_lut = NULL;
-	screen->type = SCREEN_NULL;
-
 	return 0;
 }
 
-int  rk_fb_get_prmry_screen(struct rk_screen *screen)
+int rk_fb_get_prmry_screen(struct rk_screen *screen)
 {
-	if (unlikely(!rk_screen) || unlikely(!screen))
+	if (unlikely(!prmry_screen) || unlikely(!screen))
 		return -1;
 
-	memcpy(screen, rk_screen, sizeof(struct rk_screen));
+	memcpy(screen, prmry_screen, sizeof(struct rk_screen));
 	return 0;
 }
 
-int rk_fb_set_prmry_screen(struct rk_screen *screen)
+int  rk_fb_get_screen(struct rk_screen *screen, int prop)
 {
-	if (unlikely(!rk_screen) || unlikely(!screen))
+	struct rk_screen *cur_screen = NULL;
+	if (unlikely(!screen))
 		return -1;
 
-	rk_screen->lcdc_id = screen->lcdc_id;
-	rk_screen->screen_id = screen->screen_id;
-	rk_screen->x_mirror = screen->x_mirror;
-	rk_screen->y_mirror = screen->y_mirror;
-	rk_screen->overscan.left = screen->overscan.left;
-	rk_screen->overscan.top = screen->overscan.left;
-	rk_screen->overscan.right = screen->overscan.left;
-	rk_screen->overscan.bottom = screen->overscan.left;
+	if (prop == PRMRY) {
+		if (unlikely(!prmry_screen)) {
+			rk_screen_info_error(screen, prop);
+			return -1;
+		}
+		cur_screen = prmry_screen;
+	} else {
+		if (unlikely(!extend_screen)) {
+			rk_screen_info_error(screen, prop);
+			return -1;
+		}
+		cur_screen = extend_screen;
+	}
+	memcpy(screen, cur_screen, sizeof(struct rk_screen));
 	return 0;
 }
 
-size_t get_fb_size(u8 reserved_fb)
+int rk_fb_set_screen(struct rk_screen *screen, int prop)
+{
+	struct rk_screen *cur_screen = NULL;
+
+	if (unlikely(!screen))
+		return -1;
+	if (prop == PRMRY) {
+		if (unlikely(!prmry_screen)) {
+			rk_screen_info_error(screen, prop);
+			return -1;
+		}
+	cur_screen = prmry_screen;
+	} else {
+		if (unlikely(!extend_screen)) {
+			rk_screen_info_error(screen, prop);
+			return -1;
+		}
+		cur_screen = extend_screen;
+	}
+
+	cur_screen->lcdc_id = screen->lcdc_id;
+	cur_screen->screen_id = screen->screen_id;
+	cur_screen->x_mirror = screen->x_mirror;
+	cur_screen->y_mirror = screen->y_mirror;
+	cur_screen->overscan.left = screen->overscan.left;
+	cur_screen->overscan.top = screen->overscan.left;
+	cur_screen->overscan.right = screen->overscan.left;
+	cur_screen->overscan.bottom = screen->overscan.left;
+
+	return 0;
+}
+
+size_t get_fb_size(u8 reserved_fb, struct rk_screen *screen)
 {
 	size_t size = 0;
 	u32 xres = 0;
 	u32 yres = 0;
 
-	if (unlikely(!rk_screen))
+	if (unlikely(!screen))
 		return 0;
 
-	xres = rk_screen->mode.xres;
-	yres = rk_screen->mode.yres;
+	xres = screen->mode.xres;
+	yres = screen->mode.yres;
 
 	/* align as 64 bytes(16*4) in an odd number of times */
 	xres = ALIGN_64BYTE_ODD_TIMES(xres, ALIGN_PIXEL_64BYTE_RGB8888);
@@ -73,22 +118,51 @@
 static int rk_screen_probe(struct platform_device *pdev)
 {
 	struct device_node *np = pdev->dev.of_node;
-	int ret;
+	struct device_node *screen_np;
+	struct rk_screen *rk_screen;
+	int ret, screen_prop;
 
 	if (!np) {
 		dev_err(&pdev->dev, "Missing device tree node.\n");
 		return -EINVAL;
 	}
-	rk_screen = devm_kzalloc(&pdev->dev,
-			sizeof(struct rk_screen), GFP_KERNEL);
-	if (!rk_screen) {
-		dev_err(&pdev->dev, "kmalloc for rk screen fail!");
-		return  -ENOMEM;
+
+	for_each_child_of_node(np, screen_np) {
+		rk_screen = devm_kzalloc(&pdev->dev,
+					 sizeof(struct rk_screen), GFP_KERNEL);
+		if (!rk_screen) {
+			dev_err(&pdev->dev, "kmalloc for rk screen fail!");
+			return  -ENOMEM;
+		}
+		rk_screen->pwrlist_head = devm_kzalloc(&pdev->dev,
+				sizeof(struct list_head), GFP_KERNEL);
+		if (!rk_screen->pwrlist_head) {
+			dev_err(&pdev->dev, "kmalloc for rk_screen pwrlist_head fail!");
+			return  -ENOMEM;
+		}
+		of_property_read_u32(screen_np, "screen_prop", &screen_prop);
+		if (screen_prop == PRMRY)
+			prmry_screen = rk_screen;
+		else if (screen_prop == EXTEND)
+			extend_screen = rk_screen;
+		else
+			dev_err(&pdev->dev, "unknow screen prop: %d\n",
+				screen_prop);
+		rk_screen->prop = screen_prop;
+		of_property_read_u32(screen_np, "native-mode", &rk_screen->native_mode);
+		rk_screen->dev = &pdev->dev;
+		ret = rk_fb_prase_timing_dt(screen_np, rk_screen);
+		pr_info("%s screen timing parse %s\n",
+			(screen_prop == PRMRY) ? "prmry" : "extend",
+			ret ? "failed" : "success");
+		ret = rk_disp_pwr_ctr_parse_dt(screen_np, rk_screen);
+		pr_info("%s screen power ctrl parse %s\n",
+			(screen_prop == PRMRY) ? "prmry" : "extend",
+			ret ? "failed" : "success");
 	}
-	ret = rk_fb_prase_timing_dt(np, rk_screen);
-	dev_info(&pdev->dev, "rockchip screen probe %s\n",
-				ret ? "failed" : "success");
-	return ret;
+
+	dev_info(&pdev->dev, "rockchip screen probe success\n");
+	return 0;
 }
 
 static const struct of_device_id rk_screen_dt_ids[] = {
```

#### rk32_dp.c
```
diff --git a/drivers/video/rockchip/transmitter/rk32_dp.c b/drivers/video/rockchip/transmitter/rk32_dp.c
index 6d386bc..0bffdb0 100755
--- a/drivers/video/rockchip/transmitter/rk32_dp.c
+++ b/drivers/video/rockchip/transmitter/rk32_dp.c
@@ -129,7 +129,7 @@
 	struct rk_screen *screen = &edp->screen;
 	u32 val = 0;
 
-	rk_fb_get_prmry_screen(screen);
+	rk_fb_get_screen(screen, edp->prop);
 
 	if (cpu_is_rk3288()) {
 		if (screen->lcdc_id == 1)  /*select lcdc*/
@@ -1734,17 +1734,21 @@
 	struct resource *res;
 	struct device_node *np = pdev->dev.of_node;
 	int ret;
+	int prop;
 
 	if (!np) {
 		dev_err(&pdev->dev, "Missing device tree node.\n");
 		return -EINVAL;
 	}
+	of_property_read_u32(np, "prop", &prop);
+	pr_info("Use EDP as %s screen\n", (prop == PRMRY) ? "prmry" : "extend");
 
 	edp = devm_kzalloc(&pdev->dev, sizeof(struct rk32_edp), GFP_KERNEL);
 	if (!edp) {
 		dev_err(&pdev->dev, "no memory for state\n");
 		return -ENOMEM;
 	}
+	edp->prop = prop;
 	edp->dev = &pdev->dev;
 	edp->video_info.h_sync_polarity	= 0;
 	edp->video_info.v_sync_polarity	= 0;
@@ -1756,7 +1760,7 @@
 
 	edp->video_info.link_rate	= LINK_RATE_1_62GBPS;
 	edp->video_info.lane_count	= LANE_CNT4;
-	rk_fb_get_prmry_screen(&edp->screen);
+	rk_fb_get_screen(&edp->screen, prop);
 	if (edp->screen.type != SCREEN_EDP) {
 		dev_err(&pdev->dev, "screen is not edp!\n");
 		return -EINVAL;
@@ -1852,7 +1856,7 @@
 		pm_runtime_get_sync(&pdev->dev);
 
 	rk32_edp = edp;
-	rk_fb_trsm_ops_register(&trsm_edp_ops, SCREEN_EDP);
+	rk_fb_trsm_ops_register(&trsm_edp_ops, prop);
 #if defined(CONFIG_DEBUG_FS)
 	edp->debugfs_dir = debugfs_create_dir("edp", NULL);
 	if (IS_ERR(edp->debugfs_dir)) {
diff --git a/drivers/video/rockchip/transmitter/rk32_dp.h b/drivers/video/rockchip/transmitter/rk32_dp.h
index 2dc41c6..fda0de2 100755
--- a/drivers/video/rockchip/transmitter/rk32_dp.h
+++ b/drivers/video/rockchip/transmitter/rk32_dp.h
@@ -571,6 +571,7 @@
 	bool edp_en;
 	int soctype;
 	struct dentry *debugfs_dir;
+	int prop;
 };
 ```
 #### rk32_mipi_dsi.c
 ```
diff --git a/drivers/video/rockchip/transmitter/rk32_mipi_dsi.c b/drivers/video/rockchip/transmitter/rk32_mipi_dsi.c
index 741fdb5..ed68d85 100644
--- a/drivers/video/rockchip/transmitter/rk32_mipi_dsi.c
+++ b/drivers/video/rockchip/transmitter/rk32_mipi_dsi.c
@@ -1609,7 +1609,7 @@
 		pm_runtime_get_sync(&dsi0->pdev->dev);
 #endif
 		opt_mode = dsi0->screen.refresh_mode;
-		rk_fb_get_prmry_screen(dsi0->screen.screen);
+		rk_fb_get_screen(dsi0->screen.screen, dsi0->prop);
 		dsi0->screen.lcdc_id = dsi0->screen.screen->lcdc_id;
 		rk32_init_phy_mode(dsi0->screen.lcdc_id);
 
@@ -1875,7 +1875,7 @@
 static int rk32_mipi_dsi_probe(struct platform_device *pdev)
 {
 	int ret = 0;
-	static int id;
+	static int id, prop;
 	struct dsi *dsi;
 	struct mipi_dsi_ops *ops;
 	struct rk_screen *screen;
@@ -1890,7 +1890,8 @@
 		return -ENODEV;
 	}
 	data = of_id->data;
-
+	of_property_read_u32(np, "prop", &prop);
+	pr_info("Use mipi as %s screen\n", (prop == PRMRY) ? "prmry" : "extend");
 	dsi = devm_kzalloc(&pdev->dev, sizeof(struct dsi), GFP_KERNEL);
 	if (!dsi) {
 		dev_err(&pdev->dev, "request struct dsi fail!\n");
@@ -1997,8 +1998,8 @@
 		dev_err(&pdev->dev, "request struct rk_screen fail!\n");
 		return -1;
 	}
-	rk_fb_get_prmry_screen(screen);
-
+	rk_fb_get_screen(screen, prop);
+	dsi->prop = prop;
 	dsi->pdev = pdev;
 	ops = &dsi->ops;
 	ops->dsi = dsi;
@@ -2056,7 +2057,7 @@
 		if(!support_uboot_display())
 			rk32_init_phy_mode(dsi_screen->lcdc_id);
 		*/
-		rk_fb_trsm_ops_register(&trsm_dsi_ops, SCREEN_MIPI);
+		rk_fb_trsm_ops_register(&trsm_dsi_ops, prop);
 #ifdef MIPI_DSI_REGISTER_IO
 		debugfs_create_file("mipidsi0", S_IFREG | S_IRUGO, dsi->debugfs_dir, dsi,
 							&reg_proc_fops);
```

#### rk32_mipi_dsi.h
```
diff --git a/drivers/video/rockchip/transmitter/rk32_mipi_dsi.h b/drivers/video/rockchip/transmitter/rk32_mipi_dsi.h
index f568254..473db82 100644
--- a/drivers/video/rockchip/transmitter/rk32_mipi_dsi.h
+++ b/drivers/video/rockchip/transmitter/rk32_mipi_dsi.h
@@ -307,6 +307,7 @@
 struct dsi {
 	u8 dsi_id;
 	u8 lcdc_id;
+	int prop;
 	u8 vid;
 	u8 clk_on;
 	struct regmap *grf_base;
```

#### rk_fb.h
```
diff --git a/include/dt-bindings/display/rk_fb.h b/include/dt-bindings/display/rk_fb.h
index 81c9855..ae7241d 100755
--- a/include/dt-bindings/display/rk_fb.h
+++ b/include/dt-bindings/display/rk_fb.h
@@ -14,6 +14,13 @@
 #define DUAL		2
 #define DUAL_LCD	3
 
+#define DEFAULT_MODE	0
+#define HDMI_720P	0
+#define HDMI_1080P	1
+#define HDMI_2160P	2
+#define NTSC_CVBS	3
+#define PAL_CVBS	4
+
 #define DEFAULT_MODE			0
 #define ONE_VOP_DUAL_MIPI_HOR_SCAN	1
 #define ONE_VOP_DUAL_MIPI_VER_SCAN	2
```

#### lcd 的 dtsi
```
diff --git a/include/dt-bindings/display/screen-timing/lcd-F402.dtsi b/include/dt-bindings/display/screen-timing/lcd-F402.dtsi
index a3ad25f..abe178f 100644
--- a/include/dt-bindings/display/screen-timing/lcd-F402.dtsi
+++ b/include/dt-bindings/display/screen-timing/lcd-F402.dtsi
@@ -4,9 +4,9 @@
  */
 
 
-disp_timings: display-timings {
-        native-mode = <&timing0>;
-        timing0: timing0 {
+display-timings {
+        native-mode = <&f402>;
+        f402: timing0 {
 		screen-type = <SCREEN_EDP>;
 		out-face    = <OUT_P666>;
 		clock-frequency = <205000000>;
```

```
diff --git a/include/dt-bindings/display/screen-timing/lcd-box.dtsi b/include/dt-bindings/display/screen-timing/lcd-box.dtsi
index 2109a89..20e2a21 100644
--- a/include/dt-bindings/display/screen-timing/lcd-box.dtsi
+++ b/include/dt-bindings/display/screen-timing/lcd-box.dtsi
@@ -3,36 +3,9 @@
  *
  */
 
-	disp_power_ctr: power_ctr {
-     /*                        rockchip,debug = <0>;
-        lcd_en:lcd_en {
-                rockchip,power_type = <GPIO>;
-                gpios = <&gpio0 GPIO_B0 GPIO_ACTIVE_HIGH>;
-                rockchip,delay = <10>;
-        };
-
-        bl_en:bl_en {
-                rockchip,power_type = <GPIO>;
-                gpios = <&gpio0 GPIO_A2 GPIO_ACTIVE_HIGH>;
-                rockchip,delay = <10>;
-        };
-
-        bl_ctr:bl_ctr {
-                rockchip,power_type = <GPIO>;
-                gpios = <&gpio3 GPIO_D6 GPIO_ACTIVE_HIGH>;
-                rockchip,delay = <10>;
-        };
-
-        lcd_rst:lcd_rst {
-                rockchip,power_type = <REGULATOR>;
-                rockchip,delay = <5>;
-        };*/
-
-};
-
-disp_timings: display-timings {
-	native-mode = <&timing0>;
-	timing0: timing0 {
+display-timings {
+	native-mode = <&hdmi_720p>;
+	hdmi_720p: timing0 {
 		screen-type = <SCREEN_RGB>;
 		out-face    = <OUT_P888>;
 		color-mode = <COLOR_YCBCR>;
@@ -53,7 +26,7 @@
 		swap-rg = <0>;
 		swap-gb = <0>;
 	};
-	timing1: timing1 {
+	hdmi_1080p: timing1 {
 		screen-type = <SCREEN_RGB>;
 		out-face    = <OUT_P888>;
 		color-mode = <COLOR_YCBCR>;
@@ -74,7 +47,7 @@
 		swap-rg = <0>;
 		swap-gb = <0>;
 	};
-	timing2: timing2 {
+	hdmi_2160p: timing2 {
 		screen-type = <SCREEN_RGB>;
 		out-face    = <OUT_P888>;
 		color-mode = <COLOR_YCBCR>;
```

```
diff --git a/include/dt-bindings/display/screen-timing/lcd-tv080wum-nl0-mipi.dtsi b/include/dt-bindings/display/screen-timing/lcd-tv080wum-nl0-mipi.dtsi
index b408d65..6a203a9 100644
--- a/include/dt-bindings/display/screen-timing/lcd-tv080wum-nl0-mipi.dtsi
+++ b/include/dt-bindings/display/screen-timing/lcd-tv080wum-nl0-mipi.dtsi
@@ -84,10 +84,10 @@
 	*/
 };
 
-disp_timings: display-timings {
-	native-mode = <&timing0>;
+display-timings {
+	native-mode = <&tv080wum_nl0_mipi>;
 	compatible = "rockchip,display-timings";
-	timing0: timing0 {
+	tv080wum_nl0_mipi: timing0 {
 		screen-type = <SCREEN_MIPI>;
 		lvds-format = <LVDS_8BIT_2>;
 		out-face    = <OUT_P888>;
diff --git a/include/linux/rk_fb.h b/include/linux/rk_fb.h
index d7634a8..1130ea4 100755
--- a/include/linux/rk_fb.h
+++ b/include/linux/rk_fb.h
@@ -811,7 +811,10 @@
 extern int rk_fb_get_prmry_screen( struct rk_screen *screen);
 extern int rk_fb_set_prmry_screen(struct rk_screen *screen);
 extern u32 rk_fb_get_prmry_screen_pixclock(void);
-extern int rk_disp_pwr_ctr_parse_dt(struct rk_lcdc_driver *dev_drv);
+extern int rk_fb_get_screen(struct rk_screen *screen, int prop);
+extern int rk_fb_set_screen(struct rk_screen *screen, int prop);
+extern int rk_disp_pwr_ctr_parse_dt(struct device_node *np,
+				    struct rk_screen *rk_screen);
 extern int rk_disp_pwr_enable(struct rk_lcdc_driver *dev_drv);
 extern int rk_disp_pwr_disable(struct rk_lcdc_driver *dev_drv);
 extern bool is_prmry_rk_lcdc_registered(void);
diff --git a/include/linux/rk_screen.h b/include/linux/rk_screen.h
index 5e5cd30..71a0d4d 100644
--- a/include/linux/rk_screen.h
+++ b/include/linux/rk_screen.h
@@ -61,13 +61,17 @@
 *ft: the time need to display one frame time
 */
 struct rk_screen {
-	u16 type;
+	struct device	*dev;
+	int prop;
 	u16 refresh_mode;
+	struct list_head *pwrlist_head;
+	u16 type;
 	u16 lvds_format;
 	u16 face;
 	u16 color_mode;
 	u8 lcdc_id;
 	u8 screen_id;
+	int native_mode;
 	struct fb_videomode mode;
 	u32 post_dsp_stx;
 	u32 post_dsp_sty;
@@ -145,7 +149,7 @@
 };
 
 extern void set_lcd_info(struct rk_screen *screen, struct rk29lcd_info *lcd_info);
-extern size_t get_fb_size(u8 reserved_fb);
+extern size_t get_fb_size(u8 reserved_fb, struct rk_screen *screen);
 
 extern void set_tv_info(struct rk_screen *screen);
 extern void set_hdmi_info(struct rk_screen *screen);
```
