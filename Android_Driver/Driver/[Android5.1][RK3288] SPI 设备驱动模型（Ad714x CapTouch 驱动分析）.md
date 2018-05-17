---
title: [Android5.1][RK3288] SPI 设备驱动模型（Ad714x CapTouch 驱动分析）
tags: linux, g-sensor,spi,
grammar_cjkRuby: true
---
之前有归纳过传统 board-info 形式下的 spi 驱动模型：[Linux 内核中 SPI 设备驱动模型（Platform设备驱动方式）](http://blog.csdn.net/dearsq/article/details/51790337)。

但是这里代码的环境是 Android5.1。
所以我们先来分析一下 DTS。

## DTS 
根据硬件工程师给出的信息，这颗 GSensor 接到 Spi0 上，我们可以看一下 DTS 中的信息：
```dts
#spi0
spi0: spi@70a00000{
	compatible = "sprd, sprd-spi";
    interrupts = <0 7 0x0>
    reg = <0x70a00000 0x1000>
    clock-names = "clk_spi0";
    #address-cells = <1>;
    #size-cells = <0>;
};
# spi1...
```

## SPI 部分驱动
这种 SPI 类的 Sensor 一般会将驱动分为两个部分，一部分是 CHIP_spi.c 一部分是 CHIP.c。
### CHIP_spi.c
#### CHIP_spi_driver
在 CHIP_SPI.c 中完成的任务是 CHIP_spi_read 及 CHIP_spi_write 等回调函数的实现。
SPI 协议驱动有些类似平台设备驱动：
```c
static struct spi_driver ad714x_spi_driver = {
	.driver = {
		.name	= "ad714x_captouch",
		.owner	= THIS_MODULE,
		.pm	= &ad714x_spi_pm,
	},
	.probe		= ad714x_spi_probe,
	.remove		= ad714x_spi_remove,
};
```
#### module_spi_driver() 宏
内核将调用  module_spi_driver() 这个宏来注册和卸载 spi 设备，这个 module_spi_driver 是专门针对于 spi 架构定义的。
在 include/linux/spi/spi.h 中，我们可以看到：
```c
281 /**
282  * module_spi_driver() - Helper macro for registering a SPI driver
283  * @__spi_driver: spi_driver struct
284  *
285  * Helper macro for SPI drivers which do not do anything special in module
286  * init/exit. This eliminates a lot of boilerplate. Each module may only
287  * use this macro once, and calling it replaces module_init() and module_exit()
288  */
289 #define module_spi_driver(__spi_driver) \
290         module_driver(__spi_driver, spi_register_driver, \
291                         spi_unregister_driver)
```
可以还可以往下去追看 module_driver() 这个宏 ，它将 spi_register/unregister_driver()  与 module_init 和 module_exit 封装了起来。所以说实际上 module_spi_driver() 和  module_init/exit 几乎是没有区别的。
之所以直接将其封装的原因是因为**这个 SPI 设备本身是不可插拔的**，也就不需要 init 和 exit 的过程，系统上电就直接注册了。

#### CHIP_spi_probe()
```c
static int ad714x_spi_probe(struct spi_device *spi)
{
	// struct CHIP_chip 被定义在 .h 文件中，其中封装了 CHIP_platform_data、CHIP_driver_data、device 等结构体，以及一些回调函数
    // 我们可以将其理解为 spi_device 的封装
	struct ad714x_chip *chip; 
	int err;

	spi->bits_per_word = 8; //定义每个字传输的 bit 数
	err = spi_setup(spi); // 配置 SPI 的通信相关的信息，实现在 driver/spi/spi.c 中
	if (err < 0)
		return err;

	// 将我们实现的 CHIP_spi_read 和 CHIP_spi_write 传到 CHIP.c 文件中的主 probe 中
   	// 在 主 probe 中调用 read 和 write 来进行和从设备的通信，主 probe() 我们在下一段分析
	chip = ad714x_probe(&spi->dev, BUS_SPI, spi->irq,
			    ad714x_spi_read, ad714x_spi_write);
	if (IS_ERR(chip))
		return PTR_ERR(chip);
	
	spi_set_drvdata(spi, chip);	
    //=> dev_set_drvdata(&spi->dev,chip)
    //=> spi->dev->driver_data = chip

	return 0;
}
```
抽象出来就是
```c
static int __devinit CHIP_spi_probe(struct spi_device *spi)
        {
               struct CHIP                   *chip;
               struct CHIP_platform_data     *pdata; //也可以将这个封装到上面的 CHIP 里面
               /* assuming the driver req一个"spi_masteruires board-specific data: */
               pdata = &spi->dev.platform_data;
               if (!pdata)
                      return -ENODEV;
               /* get memory for driver\'s per-chip state */
               chip = kzalloc(sizeof *chip, GFP_KERNEL);
               if (!chip)
                      return -ENOMEM;
               spi_set_drvdata(spi, chip);
               ... etc
               return 0;中
        }
```
其中的主 probe 放到后面去分析。
其中的 spi_setup() 中可以修改 spi_device 特征，如传输模式、字长或时钟速率。

#### CHIP_spi_read / CHIP_spi_write 
先介绍一下 struct spi_message
```c
789 struct spi_message {
790         struct list_head        transfers;
792         struct spi_device       *spi;
			   ...
814         /* for optional use by whatever driver currently owns the
815          * spi_message ...  between calls to中 spi_async and then later
816          * complete(), that's the spi_master controller driver.
817          */
818         struct list_head        queue;
821         /* list of spi_res reources when the spi message is processed */
822         struct list_head        resources;##### spi_message 
823 };
```
一个 message 是一次数据交换的原子请求， spi_message 是多个 spi_transfer 结构组成，这些 spi_transfer 通过一个链表 transfers 组织在一起。具体可以看这篇博文：[SPI 数据传输的队列化](http://blog.csdn.net/DroidPhone/article/details/24663659)。
spi_message 结构有一个链表头字段 transfers。
spi_transfer 结构包含一个链表头字段 transfer_list。
通过这两个链表头字段，所有属于这次 message 传输的 transfer 都会挂在 spi_messages.transfers 下。
我们通过 **spi_message_add_tail** 来向 spi_message 结构中添加一个 spi_transfer 结构。
然后调用 **spi_async** 同步 或者 **spi_sync** 异步来发起一个 message 传输请求，通常 spi_async 或 spi_sync 由将被封装在 read 和 write 中。

```c
//read 有四个参数
//1. 之前封装了 device 的结构体
//2. 需要读取的寄存器
//3. 用来接受数据的 data
//4. 传输的字节数
static int ad714x_spi_read(struct ad714x_chip *chip,源码
			   unsigned short reg, unsigned short *data, size_t len)
{
	struct spi_device *spi = to_spi_device(chip->dev);//利用 container_of 将封装的 dev 提取出来	
	struct spi_message message;
	struct spi_transfer xfer[2]; // SPI 控制器 和 协议驱动 之间的 I/O 接口
	int i;
	int error;

	spi_message_init(&message); // 先初始化 message
	memset(xfer, 0, sizeof(xfer));

	chip->xfer_buf[0] = cpu_to_be16(AD714x_SPI_CMD_PREFIX |
					AD714x_SPI_READ | reg);
	xfer[0].tx_buf = &chip->xfer_buf[0];
	xfer[0].len = sizeof(chip->xfer_buf[0]);
	spi_message_add_tail(&xfer[0], &message);

	xfer[1].rx_buf = &chip->xfer_buf[1];
	xfer[1].len = sizeof(chip->xfer_buf[1]) * len;
	spi_message_add_tail(&xfer[1], &message);

	error = spi_sync(spi, &message);//调用spi_sync 来发起 message 传输请求
	if (unlikely(error)) {
		dev_err(chip->dev, "SPI read error: %d\n", error);
		return error;
	}

	for (i = 0; i < len; i++)
		data[i] = be16_to_cpu(chip->xfer_buf[i + 1]);

	return 0;
}
```
```c
// 三个参数
// 1. 封装了 device 的结构体
// 2. 要写入的寄存器
// 3. 要写入的数据
static int ad714x_spi_write(struct ad714x_chip *chip,
			    unsigned short reg, unsigned short data)
{
	struct spi_device *spi = to_spi_device(chip->dev);
	int error;

	chip->xfer_buf[0] = cpu_to_be16(AD714x_SPI_CMD_PREFIX | reg);
	chip->xfer_buf[1] = cpu_to_be16(data);

	error = spi_write(spi, (u8 *)chip->xfer_buf,  2 * sizeof(*chip->xfer_buf));
	/* 这里的 spi_write 等价于
    struct spi_transfer t = {
    		.tx_buf	= chip->xfer_buf,
            .len	  = 2*sizeof(*chip->xfer_buf),
    };
    struct spi_message	m;
    spi_message_init(&m);
    spi_message_add_tail(&t,&m);
    return spi_sync(spi, &m);
    */
	if (unlikely(error)) {
		dev_err(chip->dev, "SPI write error: %d\n", error);
		return error;
	}
	return 0;
}
```

### CHIP.c
之前我们在 CHIP_spi_probe() 中可以注意到，有如下代码
```c
chip = ad714x_probe(&spi->dev, BUS_SPI, spi->irq,
			    ad714x_spi_read, ad714x_spi_write);
```
这里 CHIP_probe() 的定义在 CHIP.c 
我们来读一下 CHIP_probe() 的代码
```c
// 有 5 个参数
// 1. device
// 2. 总线类型
// 3. 中断号
// 4. 5. read 和 write 的实现函数（封装了 spi_async）
// 代码太长，我们直接看哪些地方调用了  read 和 write，其他的地方省略
struct ad714x_chip *ad714x_probe(struct device *dev, u16 bus_type, int irq,
				 ad714x_read_t read, ad714x_write_t write)
{
	int i, alloc_idx;
	int error;
	struct input_dev *input[MAX_DEVICE_NUM];

	struct ad714x_platform_data *plat_data = dev->platform_data;
	struct ad714x_chip *ad714x;
	void *drv_mem;
	unsigned long irqflags;

	struct ad714x_button_drv *bt_drv;
	struct ad714x_slider_drv *sd_drv;
	struct ad714x_wheel_drv *wl_drv;
	struct ad714x_touchpad_drv *tp_drv;

	if (irq <= 0) {
		dev_err(dev, "IRQ not configured!\n");
		error = -EINVAL;
		goto err_out;
	}

	if (dev->platform_data == NULL) {
		dev_err(dev, "platform data for ad714x doesn't exist\n");
		error = -EINVAL;
		goto err_out;
	}

	ad714x = kzalloc(sizeof(*ad714x) + sizeof(*ad714x->sw) +
			 sizeof(*sd_drv) * plat_data->slider_num +
			 sizeof(*wl_drv) * plat_data->wheel_num +
			 sizeof(*tp_drv) * plat_data->touchpad_num +
			 sizeof(*bt_drv) * plat_data->button_num, GFP_KERNEL);
	if (!ad714x) {
		error = -ENOMEM;
		goto err_out;
	}

	ad714x->hw = plat_data;

	drv_mem = ad714x + 1;
	ad714x->sw = drv_mem;
	drv_mem += sizeof(*ad714x->sw);
	ad714x->sw->slider = sd_drv = drv_mem;
	drv_mem += sizeof(*sd_drv) * ad714x->hw->slider_num;
	ad714x->sw->wheel = wl_drv = drv_mem;
	drv_mem += sizeof(*wl_drv) * ad714x->hw->wheel_num;
	ad714x->sw->touchpad = tp_drv = drv_mem;
	drv_mem += sizeof(*tp_drv) * ad714x->hw->touchpad_num;
	ad714x->sw->button = bt_drv = drv_mem;
	drv_mem += sizeof(*bt_drv) * ad714x->hw->button_num;

	ad714x->read = read;
	ad714x->write = write;
	ad714x->irq = irq;
	ad714x->dev = dev;
	
    //读硬件寄存器中的 chip ID，判断具体是哪种 CapTouch
	error = ad714x_hw_detect(ad714x);	
	if (error)
		goto err_free_mem;

	/* initialize and request sw/hw resources */
	ad714x_hw_init(ad714x);
	mutex_init(&ad714x->mutex);
	/*
	 * Allocate and register AD714X input device
	 */
	alloc_idx = 0;
	/* a slider uses one input_dev instance */
	if (ad714x->hw->slider_num > 0) {
		struct ad714x_slider_plat *sd_plat = ad714x->hw->slider;

		for (i = 0; i < ad714x->hw->slider_num; i++) {
			sd_drv[i].input = input[alloc_idx] = input_allocate_device();
			if (!input[alloc_idx]) {
				error = -ENOMEM;
				goto err_free_dev;
			}

			__set_bit(EV_ABS, input[alloc_idx]->evbit);
			__set_bit(EV_KEY, input[alloc_idx]->evbit);
			__set_bit(ABS_X, input[alloc_idx]->absbit);
			__set_bit(BTN_TOUCH, input[alloc_idx]->keybit);
			input_set_abs_params(input[alloc_idx],
				ABS_X, 0, sd_plat->max_coord, 0, 0);

			input[alloc_idx]->id.bustype = bus_type;
			input[alloc_idx]->id.product = ad714x->product;
			input[alloc_idx]->id.version = ad714x->version;
			input[alloc_idx]->name = "ad714x_captouch_slider";
			input[alloc_idx]->dev.parent = dev;

			error = input_register_device(input[alloc_idx]);
			if (error)
				goto err_free_dev;

			alloc_idx++;
		}
	}

	/* a wheel uses one input_dev instance */
	if (ad714x->hw->wheel_num > 0) {
		struct ad714x_wheel_plat *wl_plat = ad714x->hw->wheel;

		for (i = 0; i < ad714x->hw->wheel_num; i++) {
			wl_drv[i].input = input[alloc_idx] = input_allocate_device();
			if (!input[alloc_idx]) {
				error = -ENOMEM;
				goto err_free_dev;
			}

			__set_bit(EV_KEY, input[alloc_idx]->evbit);
			__set_bit(EV_ABS, input[alloc_idx]->evbit);
			__set_bit(ABS_WHEEL, input[alloc_idx]->absbit);
			__set_bit(BTN_TOUCH, input[alloc_idx]->keybit);
			input_set_abs_params(input[alloc_idx],
				ABS_WHEEL, 0, wl_plat->max_coord, 0, 0);

			input[alloc_idx]->id.bustype = bus_type;
			input[alloc_idx]->id.product = ad714x->product;
			input[alloc_idx]->id.version = ad714x->version;
			input[alloc_idx]->name = "ad714x_captouch_wheel";
			input[alloc_idx]->dev.parent = dev;

			error = input_register_device(input[alloc_idx]);
			if (error)
				goto err_free_dev;

			alloc_idx++;
		}
	}

	/* a touchpad uses one input_dev instance */
	if (ad714x->hw->touchpad_num > 0) {
		struct ad714x_touchpad_plat *tp_plat = ad714x->hw->touchpad;

		for (i = 0; i < ad714x->hw->touchpad_num; i++) {
			tp_drv[i].input = input[alloc_idx] = input_allocate_device();
			if (!input[alloc_idx]) {
				error = -ENOMEM;
				goto err_free_dev;
			}

			__set_bit(EV_ABS, input[alloc_idx]->evbit);
			__set_bit(EV_KEY, input[alloc_idx]->evbit);
			__set_bit(ABS_X, input[alloc_idx]->absbit);
			__set_bit(ABS_Y, input[alloc_idx]->absbit);
			__set_bit(BTN_TOUCH, input[alloc_idx]->keybit);
			input_set_abs_params(input[alloc_idx],
				ABS_X, 0, tp_plat->x_max_coord, 0, 0);
			input_set_abs_params(input[alloc_idx],
				ABS_Y, 0, tp_plat->y_max_coord, 0, 0);

			input[alloc_idx]->id.bustype = bus_type;
			input[alloc_idx]->id.product = ad714x->product;
			input[alloc_idx]->id.version = ad714x->version;
			input[alloc_idx]->name = "ad714x_captouch_pad";
			input[alloc_idx]->dev.parent = dev;

			error = input_register_device(input[alloc_idx]);
			if (error)
				goto err_free_dev;

			alloc_idx++;
		}
	}

	/* all buttons use one input node */
	if (ad714x->hw->button_num > 0) {
		struct ad714x_button_plat *bt_plat = ad714x->hw->button;

		input[alloc_idx] = input_allocate_device();
		if (!input[alloc_idx]) {
			error = -ENOMEM;
			goto err_free_dev;
		}

		__set_bit(EV_KEY, input[alloc_idx]->evbit);
		for (i = 0; i < ad714x->hw->button_num; i++) {
			bt_drv[i].input = input[alloc_idx];
			__set_bit(bt_plat[i].keycode, input[alloc_idx]->keybit);
		}

		input[alloc_idx]->id.bustype = bus_type;
		input[alloc_idx]->id.product = ad714x->product;
		input[alloc_idx]->id.version = ad714x->version;
		input[alloc_idx]->name = "ad714x_captouch_button";
		input[alloc_idx]->dev.parent = dev;

		error = input_register_device(input[alloc_idx]);
		if (error)
			goto err_free_dev;

		alloc_idx++;
	}

	irqflags = plat_data->irqflags ?: IRQF_TRIGGER_FALLING;
	irqflags |= IRQF_ONESHOT;

	error = request_threaded_irq(ad714x->irq, NULL, ad714x_interrupt_thread,
				     irqflags, "ad714x_captouch", ad714x);
	if (error) {
		dev_err(dev, "can't allocate irq %d\n", ad714x->irq);
		goto err_unreg_dev;
	}
	return ad714x;

 err_free_dev:
	dev_err(dev, "failed to setup AD714x input device %i\n", alloc_idx);
	input_free_device(input[alloc_idx]);
 err_unreg_dev:
	while (--alloc_idx >= 0)
		input_unregister_device(input[alloc_idx]);
 err_free_mem:
	kfree(ad714x);
 err_out:
	return ERR_PTR(error);
}
EXPORT_SYMBOL(ad714x_probe);
```


参考：
1. 内核源码 /kernel/driver/spi/spi.c   spi.h
2.这个没有纠结于代码实现，归纳了Linux内核对 SPI 的支持方法。还有抽象出来说如何实现 SPI 驱动： http://linux.it.net.cn/m/view.php?aid=18852
3.这个以 一个 eeprom 的代码来进行分析 SPI 总线 http://www.cnblogs.com/jason-lu/p/3165327.html
