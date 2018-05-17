---
title: [Android6.0][RK3399] PWM Backlight 驱动分析
tags: 
---
Platform: RK3399 
OS: Android 6.0 
Kernel: 4.4

## DTS
```dts
backlight: backlight {
		status = "disabled";
		compatible = "pwm-backlight";
		pwms = <&pwm0 0 25000 0>;
		brightness-levels = <
			  0   1   2   3   4   5   6   7
			  8   9  10  11  12  13  14  15
			 16  17  18  19  20  21  22  23
			 24  25  26  27  28  29  30  31
			 32  33  34  35  36  37  38  39
			 40  41  42  43  44  45  46  47
			 48  49  50  51  52  53  54  55
			 56  57  58  59  60  61  62  63
			 64  65  66  67  68  69  70  71
			 72  73  74  75  76  77  78  79
			 80  81  82  83  84  85  86  87
			 88  89  90  91  92  93  94  95
			 96  97  98  99 100 101 102 103
			104 105 106 107 108 109 110 111
			112 113 114 115 116 117 118 119
			120 121 122 123 124 125 126 127
			128 129 130 131 132 133 134 135
			136 137 138 139 140 141 142 143
			144 145 146 147 148 149 150 151
			152 153 154 155 156 157 158 159
			160 161 162 163 164 165 166 167
			168 169 170 171 172 173 174 175
			176 177 178 179 180 181 182 183
			184 185 186 187 188 189 190 191
			192 193 194 195 196 197 198 199
			200 201 202 203 204 205 206 207
			208 209 210 211 212 213 214 215
			216 217 218 219 220 221 222 223
			224 225 226 227 228 229 230 231
			232 233 234 235 236 237 238 239
			240 241 242 243 244 245 246 247
			248 249 250 251 252 253 254 255>;
		default-brightness-level = <50>;
		//enable-gpios = <GPIO>
	};
```
```
pwms = <&pwm0 0 25000 0>;
```
**第一个参数** 表示此背光接在 pwm0 上;

![](http://ww3.sinaimg.cn/large/ba061518gw1f9u1my0q8dj20hz00o74j.jpg)

![](http://ww1.sinaimg.cn/large/ba061518gw1f9u1nioy43j20m70bgwha.jpg)

**第二个参数** 表示 index 为 0，pwm0 下只有 1个 pwm，所以填 0

**第三个参数** 表示周期为 25000ns，即 频率 为 40k

**第四个参数** 表示极性，0 正极性，1 负极性
正极性 0 表示 背光为正极 0～255 ，占空比从 0～100% 变化
负极性 1 表示 背光为负极 255～0 ，占空比从 100～0% 变化
```
default-brightness-level = <50>
```
表示默认的背光,它存在于开机时候背光初始化到安卓
设置下来新的背光这段时间, default-brightness-level = < 50 > 表示为第 50 个元素的背光亮度

```
enable-gpios 
```
表示背光使能脚，这个根据电路原理图配置即可；
有的硬件没有这个背光使能脚，那么将这个配置删除，背光驱动通过配置 brightness-levels 数组的第 0 个元素将显示调黑


## 驱动分析
kernel/drivers/video/backlight/pwm_bl.c 
```
pwm_backlight_probe 
    pwm_backlight_parse_dt 	  //解析 dts 中的 brightness-levels、default-brightness-level
    //RK3288 还会在这里解析 enable-gpios ，但是 3399 没有，3399 是在 probe 里面用 devm_gpiod_get_optional      //获取 enable-gpio 状态的
    devm_gpiod_get_optional  //实际上就是封装了 gpio_request_one
    devm_gpio_request_one 	//申请背光使能 gpio
    devm_pwm_get ->     /drivers/pwm/core.c //获得一个pwm
        pwm_get ->
            of_pwm_get ->
                of_parse_phandle_with_args    解析上面dts中的pwms属性.
                of_node_to_pwmchip
                pwm = pc->of_xlate    //最终生成struct pwm_device类型.    
    pwm_request    //申请pwm,防止其他驱动也会使用.
	pwm_set_period    //pb->pwm->period = data->pwm_period_ns
    pwm_get_period    //获取period.
    dev_set_name(&pdev->dev, "rk28_bl");    //name不能改,用户空间会被用到:/sys/class/backlight/rk28_bl
    backlight_device_register    -> /drivers/video/baklight/backlight.c   //注册标准背光设备
        device_register
        backlight_register_fb ->
            fb_register_client    //callback 是 fb_notifier_callback 
			fb_register_client   // 注册内核通知链
    backlight_update_status ->        //用默认值更新.
        bd->ops->update_status ->
            pwm_backlight_update_status ->
                compute_duty_cycle    //计算占空比
                pwm_config    //配置pwm 
                pwm_backlight_power_on    //enable背光
    platform_set_drvdata //可以将 pdev 保存成平台总线设备的私有数据，以后再要使用它时只需调用 platform_get_drvdata
```
计算占空比：
compute_duty_cycle:
```
static int compute_duty_cycle(struct pwm_bl_data *pb, int brightness)
{
    /*一般情况下这个值都为0*/
    unsigned int lth = pb->lth_brightness;
	/*占空比*/
    int duty_cycle;
    /*pb->levels这个表格就是从dts节点brightness-levels中获取的,
    假设进来的参数brightness是254,那么得到的duty_cycle就是1,
    如果没有这个表格,那么就直接是进来的亮度值.*/
    if (pb->levels)
        duty_cycle = pb->levels[brightness];
    else
        duty_cycle = brightness;
		
    /*假设这里lth是0,那么公式就是duty_cycle * pb->period / pb->scale
	pb->period也就是dts节点 pwms 的第三个参数周期值为 25000
    pb->scale为pb->levels数组中的最大值
	所以这个公式就是按照将Android的纯数值转换成事件周期值对应的占空比.*/
    return (duty_cycle * (pb->period - lth) / pb->scale) + lth;
}
```
KrisFei 的小结:
其实不管用哪种方式都是调用backlight_update_status来改变背光,syfs也是,看下backlight.c
backlight_class_init ->    backlight.c
    class_create    //创建class,名字是backlight.
    backlight_class->dev_attrs = bl_device_attributes;
```
static struct device_attribute bl_device_attributes[] = {  
    __ATTR(bl_power, 0644, backlight_show_power, backlight_store_power),  
    __ATTR(brightness, 0644, backlight_show_brightness,  
             backlight_store_brightness),  
    __ATTR(actual_brightness, 0444, backlight_show_actual_brightness,  
             NULL),  
    __ATTR(max_brightness, 0444, backlight_show_max_brightness, NULL),  
    __ATTR(type, 0444, backlight_show_type, NULL),  
    __ATTR_NULL,  
};  
```
其中backlight_store_brightness() 最终调用backlight_update_status().
还有一种情况是亮屏/灭屏时调用,记得前面有注册一个fb notify callback.
```
static int fb_notifier_callback(struct notifier_block *self,  
                unsigned long event, void *data)  
{  
...  
    /*只处理亮屏和灭屏事件.*/  
    /* If we aren't interested in this event, skip it immediately ... */  
    if (event != FB_EVENT_BLANK && event != FB_EVENT_CONBLANK)  
        return 0;  
...  
    if (bd->ops)  
        if (!bd->ops->check_fb ||  
            bd->ops->check_fb(bd, evdata->info)) {  
            bd->props.fb_blank = *(int *)evdata->data;  
            //亮屏情况  
            if (bd->props.fb_blank == FB_BLANK_UNBLANK)  
                bd->props.state &= ~BL_CORE_FBBLANK;  
            //灭屏时  
            else  
                bd->props.state |= BL_CORE_FBBLANK;  
            backlight_update_status(bd);  
        }  
...  
}
```
可以看到最后也是调用backlight_update_status()


## 问题集锦
### 占空比到 20% 就黑了，到 80% 就满了
有时候屏 pwm 占空比到 20% 就灭了，到 80% 就很亮了，即 brightness-levels 到 50 就灭了，到 200 就足够亮了。
此时不需要 0～49 和 201 ～ 255
所以我们 brightness-levels 数组的时候可以**均匀的重复某些值**。
比如
brightness-levels = <
			255 50  51  51  52  53  53  54 
			 54  55  56  56  57  57  58  59
			 59  60  60  61  62  62  63  63
			 ... 198  199 199  200>


参考文章：
[1] KrisFei http://blog.csdn.net/kris_fei/article/details/52485635
