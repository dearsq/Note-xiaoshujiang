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

## 驱动框架
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
这里只是枚举类型，真正的 driver_info 是 probe 中的 usbtouch_device_info *type;

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


## 流程分析