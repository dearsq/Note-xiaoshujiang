---
title: [RK3399]USB接口Touchscreen驱动流程分析
tags: Rockchip,Touchscreen,usb
grammar_cjkRuby: true
---
Platform: RK3399 
OS: Android 6.0 
Version: v2016.08

[toc]

## 前言


## 流程分析

### module_usb_driver
register/unregister  usbtouch_driver
注册到总线接口的驱动是 usbtouch_driver
```c
static struct usb_driver usbtouch_driver = {
	.name		= "usbtouchscreen",
	.probe		= usbtouch_probe,
	.disconnect	= usbtouch_disconnect,   //与 probe 相反
	.suspend	= usbtouch_suspend,       //挂起
	.resume		= usbtouch_resume,         //唤醒
	.reset_resume	= usbtouch_reset_resume,  //重置唤醒
	.id_table	= usbtouch_devices,           //支持的设备的 ID 表
	.supports_autosuspend = 1,
};
```
name = "usbtouchscreen"

其中 id_table 的数据类型是 usb_device_id
```c
struct usb_device_id {  
    /* which fields to match against? */  
    __u16       match_flags;  
  
    /* Used for product specific matches; range is inclusive */  
    __u16       idVendor;  
    __u16       idProduct;  
    __u16       bcdDevice_lo;  
    __u16       bcdDevice_hi;  
  
    /* Used for device class matches */  
    __u8        bDeviceClass;  
    __u8        bDeviceSubClass;  
    __u8        bDeviceProtocol;  
  
    /* Used for interface class matches */  
    __u8        bInterfaceClass;  
    __u8        bInterfaceSubClass;  
    __u8        bInterfaceProtocol;  
  
    /* not matched against */  
    kernel_ulong_t  driver_info;  
};
```
只有这里的信息和 usb 设备驱动那边收集到的设备信息匹配上，才会调用进这个驱动。
id_table ：
```c
static const struct usb_device_id usbtouch_devices[] = {
#ifdef CONFIG_TOUCHSCREEN_USB_EGALAX
	/* ignore the HID capable devices, handled by usbhid */
	{USB_DEVICE_HID_CLASS(0x0eef, 0x0001), .driver_info = DEVTYPE_IGNORE},
	{USB_DEVICE_HID_CLASS(0x0eef, 0x0002), .driver_info = DEVTYPE_IGNORE},

	/* normal device IDs */
	{USB_DEVICE(0x3823, 0x0001), .driver_info = DEVTYPE_EGALAX},
	...
#endif
	...
};
```
USB_DEVICE 参数分别是 idVendor （厂商id）和 idProduct（产品id），一般用其作为设备标识

后面的 driver_info 是枚举值
```c
/* device types */
enum {
	DEVTYPE_IGNORE = -1,
	DEVTYPE_EGALAX,
	DEVTYPE_PANJIT,
	DEVTYPE_3M,
	DEVTYPE_ITM,
	DEVTYPE_ETURBO,
	DEVTYPE_GUNZE,
	DEVTYPE_DMC_TSC10,
	DEVTYPE_IRTOUCH,
	DEVTYPE_IRTOUCH_HIRES,
	DEVTYPE_IDEALTEK,
	DEVTYPE_GENERAL_TOUCH,
	DEVTYPE_GOTOP,
	DEVTYPE_JASTEC,
	DEVTYPE_E2I,
	DEVTYPE_ZYTRONIC,
	DEVTYPE_TC45USB,
	DEVTYPE_NEXIO,
	DEVTYPE_ELO,
	DEVTYPE_ETOUCH,
};
```
这里只是枚举类型，真正的 driver_info 是 probe 中的 usbtouch_device_info \*type; 
这个 usbtouch_device_info 我们放在后面来分析

### usbtouch_probe  
```c
static int usbtouch_probe(struct usb_interface *intf,
			  const struct usb_device_id *id)
{
	struct usbtouch_usb *usbtouch;    //usbtouch 设备
	struct input_dev *input_dev;         //输入设备
	struct usb_endpoint_descriptor *endpoint;   //usb 端点
	struct usb_device *udev = interface_to_usbdev(intf);    //从 usb 接口获取对应设备
	struct usbtouch_device_info *type;  //真正的 driver_info
	int err = -ENOMEM;

	/* some devices are ignored */
	if (id->driver_info == DEVTYPE_IGNORE)
		return -ENODEV;

	//获取端点
	endpoint = usbtouch_get_input_endpoint(intf->cur_altsetting);
	if (!endpoint)
		return -ENXIO;
    //分配内存，申请 input 设备结构
	usbtouch = kzalloc(sizeof(struct usbtouch_usb), GFP_KERNEL);
	input_dev = input_allocate_device();
	if (!usbtouch || !input_dev)
		goto out_free;
    //用到前面的枚举值，真正的 driver_info 是在 usbtouch_dev_info 中的
	type = &usbtouch_dev_info[id->driver_info];
	usbtouch->type = type;
	if (!type->process_pkt)
		type->process_pkt = usbtouch_process_pkt;

	usbtouch->data_size = type->rept_size;
	if (type->get_pkt_len) {
		/*
		 * When dealing with variable-length packets we should
		 * not request more than wMaxPacketSize bytes at once
		 * as we do not know if there is more data coming or
		 * we filled exactly wMaxPacketSize bytes and there is
		 * nothing else.
		 */
		usbtouch->data_size = min(usbtouch->data_size,
					  usb_endpoint_maxp(endpoint));
	}

	usbtouch->data = usb_alloc_coherent(udev, usbtouch->data_size,
					    GFP_KERNEL, &usbtouch->data_dma);
	if (!usbtouch->data)
		goto out_free;

	if (type->get_pkt_len) {
		usbtouch->buffer = kmalloc(type->rept_size, GFP_KERNEL);
		if (!usbtouch->buffer)
			goto out_free_buffers;
	}
	//分配一个 urb 用来获取 TP 设备返回触摸事件的数据
	usbtouch->irq = usb_alloc_urb(0, GFP_KERNEL);
	if (!usbtouch->irq) {
		dev_dbg(&intf->dev,
			"%s - usb_alloc_urb failed: usbtouch->irq\n", __func__);
		goto out_free_buffers;
	}
    
	usbtouch->interface = intf;
	usbtouch->input = input_dev;

	if (udev->manufacturer)
		strlcpy(usbtouch->name, udev->manufacturer, sizeof(usbtouch->name));

	if (udev->product) {
		if (udev->manufacturer)
			strlcat(usbtouch->name, " ", sizeof(usbtouch->name));
		strlcat(usbtouch->name, udev->product, sizeof(usbtouch->name));
	}

	if (!strlen(usbtouch->name))
		snprintf(usbtouch->name, sizeof(usbtouch->name),
			"USB Touchscreen %04x:%04x",
			 le16_to_cpu(udev->descriptor.idVendor),
			 le16_to_cpu(udev->descriptor.idProduct));

	usb_make_path(udev, usbtouch->phys, sizeof(usbtouch->phys));
	strlcat(usbtouch->phys, "/input0", sizeof(usbtouch->phys));

	input_dev->name = usbtouch->name;
	input_dev->phys = usbtouch->phys;
	usb_to_input_id(udev, &input_dev->id);
	input_dev->dev.parent = &intf->dev;

	input_set_drvdata(input_dev, usbtouch);

	input_dev->open = usbtouch_open;
	input_dev->close = usbtouch_close;

	//input 设备触摸坐标初始化赋值
	input_dev->evbit[0] = BIT_MASK(EV_KEY) | BIT_MASK(EV_ABS);
	input_dev->keybit[BIT_WORD(BTN_TOUCH)] = BIT_MASK(BTN_TOUCH);
	input_set_abs_params(input_dev, ABS_X, type->min_xc, type->max_xc, 0, 0);
	input_set_abs_params(input_dev, ABS_Y, type->min_yc, type->max_yc, 0, 0);
	if (type->max_press)
		input_set_abs_params(input_dev, ABS_PRESSURE, type->min_press,
		                     type->max_press, 0, 0);

	if (usb_endpoint_type(endpoint) == USB_ENDPOINT_XFER_INT)
		usb_fill_int_urb(usbtouch->irq, udev,
			 usb_rcvintpipe(udev, endpoint->bEndpointAddress),
			 usbtouch->data, usbtouch->data_size,
			 usbtouch_irq, usbtouch, endpoint->bInterval);
	else
		usb_fill_bulk_urb(usbtouch->irq, udev,
			 usb_rcvbulkpipe(udev, endpoint->bEndpointAddress),
			 usbtouch->data, usbtouch->data_size,
			 usbtouch_irq, usbtouch);  // 初始化 urb 的回调函数

	usbtouch->irq->dev = udev;
	usbtouch->irq->transfer_dma = usbtouch->data_dma;
	usbtouch->irq->transfer_flags |= URB_NO_TRANSFER_DMA_MAP;

	/* device specific allocations */
	if (type->alloc) {
		err = type->alloc(usbtouch);
		if (err) {
			dev_dbg(&intf->dev,
				"%s - type->alloc() failed, err: %d\n",
				__func__, err);
			goto out_free_urb;
		}
	}

	/* device specific initialisation*/
	if (type->init) {
		err = type->init(usbtouch);
		if (err) {
			dev_dbg(&intf->dev,
				"%s - type->init() failed, err: %d\n",
				__func__, err);
			goto out_do_exit;
		}
	}

	err = input_register_device(usbtouch->input);
	if (err) {
		dev_dbg(&intf->dev,
			"%s - input_register_device failed, err: %d\n",
			__func__, err);
		goto out_do_exit;
	}

	usb_set_intfdata(intf, usbtouch);

	if (usbtouch->type->irq_always) {
		/* this can't fail */
		usb_autopm_get_interface(intf);
		err = usb_submit_urb(usbtouch->irq, GFP_KERNEL);
		if (err) {
			usb_autopm_put_interface(intf);
			dev_err(&intf->dev,
				"%s - usb_submit_urb failed with result: %d\n",
				__func__, err);
			goto out_unregister_input;
		}
	}

	return 0;

out_unregister_input:
	input_unregister_device(input_dev);
	input_dev = NULL;
out_do_exit:
	if (type->exit)
		type->exit(usbtouch);
out_free_urb:
	usb_free_urb(usbtouch->irq);
out_free_buffers:
	usbtouch_free_buffers(udev, usbtouch);
out_free:
	input_free_device(input_dev);
	kfree(usbtouch);
	return err;
}
```
###  usbtouch_device_info 
 usbtouch_device_info 就是上面driver_info 以及usbtouch_probe 中抽取的驱动模块的info数组，不同的usbtouchscreen 注册的时候就是注册了一个枚举值，这个值就是usbtouch_dev_info 数组的第几元素.
```c
struct usbtouch_device_info {
	int min_xc, max_xc;
	int min_yc, max_yc;
	int min_press, max_press;
	int rept_size;

	/*
	 * Always service the USB devices irq not just when the input device is
	 * open. This is useful when devices have a watchdog which prevents us
	 * from periodically polling the device. Leave this unset unless your
	 * touchscreen device requires it, as it does consume more of the USB
	 * bandwidth.
	 */
	bool irq_always;
    //这个函数指针用来接受 处理 中断
	void (*process_pkt) (struct usbtouch_usb *usbtouch, unsigned char *pkt, int len);

	/*
	 * used to get the packet len. possible return values:
	 * > 0: packet len
	 * = 0: skip one byte
	 * < 0: -return value more bytes needed
	 */
	int  (*get_pkt_len) (unsigned char *pkt, int len);

	int  (*read_data)   (struct usbtouch_usb *usbtouch, unsigned char *pkt);
	int  (*alloc)       (struct usbtouch_usb *usbtouch);
	int  (*init)        (struct usbtouch_usb *usbtouch);
	void (*exit)	    (struct usbtouch_usb *usbtouch);
};
```
### usbtouch_dev_info
这个数组的成员都是以前面说到的注册枚举值来区分. x y 参数及回调函数，都在 usbtouch_probe 中被抽离出来使用
```c
static struct usbtouch_device_info usbtouch_dev_info[] = {  
#ifdef CONFIG_TOUCHSCREEN_USB_EGALAX  
    [DEVTYPE_EGALAX] = {  
        .min_xc        = 0x0,  
        .max_xc        = 0x07ff,  
        .min_yc        = 0x0,  
        .max_yc        = 0x07ff,  
        .rept_size    = 16,  
        .process_pkt    = usbtouch_process_multi,//用于中断回调函数，用于处理中断，得到input的event，上传数据  
        .get_pkt_len    = egalax_get_pkt_len,  
        .read_data    = egalax_read_data, //用于中断回调函数，用于读取数据  
    },  
#endif  
  
...  
  
#ifdef CONFIG_TOUCHSCREEN_USB_IRTOUCH  
    [DEVTYPE_IRTOUCH] = {  
        .min_xc        = 0x0,  
        .max_xc        = 0x0fff,  
        .min_yc        = 0x0,  
        .max_yc        = 0x0fff,  
        .rept_size    = 8,  
        .read_data    = irtouch_read_data,  
    },  
#endif   
  
...  
  
};  
```
### usbtouch_irq
```c
static void usbtouch_irq(struct urb *urb)  
{  
...
    usbtouch->type->process_pkt(usbtouch, usbtouch->data, urb->actual_length);    
  
//这个type的类型就是 usbtouch_device_info，此时的process_pkt指针自然指向的是上面对应的函数，如果此时是触发的设备type为 DEVTYPE_EGALAX，那么这里调用的 usbtouch_process_multi  
  
//如果此时是DEVTYPE_IRTOUCH 那么就是执行 usbtouch_process_pkt函数，因为usbtouch_probe中：  
  
//    if (!type->process_pkt)  
//        type->process_pkt = usbtouch_process_pkt;  
  
...  
  
}  
```
接下来的都会调用到usbtouch_process_pkt中，通过type->read_data，和上面一样的指针读取，然后调用input_report_key发送，input_sync用于同步.
