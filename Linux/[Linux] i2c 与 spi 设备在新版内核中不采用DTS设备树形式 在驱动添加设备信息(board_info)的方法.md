---
title: i2c 与 spi 设备在新版内核中不采用DTS设备树形式 在驱动添加设备信息(board_info)的方法
tags: Linux,dts
grammar_cjkRuby: true
---
## i2c 设备模型
```c
#include <linux/module.h>
#include <linux/i2c.h>

#define SENSOR_BUS_NUM 0
#define SENSOR_SLAVE_ADDRESS 0x3e
#define SENSOR_NAME "sensor"
struct i2c_client *sensor_client=NULL;

static int sensor_probe(struct i2c_client *client,const struct i2c_device_id *id)
{
    sensor_client=client;
    return 0;
}

static int sensor_remove(struct i2c_client *client)
{
    return 0;
}
//首先需要一个 id_table
static const struct i2c_device_id sensor_id[] = {
    {SENSOR_NAME, 0},
    { }
};
MODULE_DEVICE_TABLE(i2c, sensor_id);
//在 driver中添加 id_table
static struct i2c_driver sensor_driver = {
    .driver = {
             .name = SENSOR_NAME,
    },
    .probe    = sensor_probe,
    .remove   = sensor_remove,
    .id_table = sensor_id,
};
//填充 board_info 
static struct i2c_board_info sensor_device = {
    I2C_BOARD_INFO("hmc5883l-i2c", SENSOR_SLAVE_ADDRESS),
};

static int __init sensor_init(void)
{
    struct i2c_adapter *adap;
    struct i2c_client *client;

    adap = i2c_get_adapter(sensor_bus_num);
    if (!adap) {
        printk("i2c adapter %d\n",sensor_bus_num);
        return -ENODEV;
    } else {
        printk("get ii2 adapter %d ok\n", sensor_bus_num);
        client = i2c_new_device(adap, &sensor_device);
    }
    if (!client) {
        printk("get i2c client %s @ 0x%02x fail!\n", sensor_device.type,
                sensor_device.addr);
        return -ENODEV;
    } else {
        printk("get i2c client ok!\n");
    }
    i2c_put_adapter(adap);
    i2c_add_driver(&sensor_driver);
    printk("sensor init success!\n");
    return 0;
}

static void __exit sensor_exit(void)
{
    i2c_del_driver(&sensor_driver);
    if(sensor_client!=NULL)
    i2c_unregister_device(sensor_client);
    printk("Module removed\n");
}

module_init(sensor_init);
module_exit(sensor_exit);
ODULE_AUTHOR("GPL");
ODULE_LICENSE("GPL");
```
## spi设备驱动模型
spi的驱动模板如下
```c
#include <linux/module.h>
#include <linux/spi/spi.h>

#define DEVICE_NAME   "sensor"
#define SENSOR_SPI_BUS 0
struct spi_device *sensor_spi=NULL;


int sensor_spi_write(void)
{
	return 0;
}

int sensor_spi_read(void)
{
	return 0;
}

static const struct spi_device_id sensor_spi_id[] = {
	{ DEVICE_NAME, 0 },
	{ }
};

MODULE_DEVICE_TABLE(spi, sensor_spi_id);

static int  sensor_probe(struct spi_device *spi)
{
	sensor_spi=spi;
	return 0;
}

static int  sensor_remove(struct spi_device *spi)
{
	return 0;
}

static struct spi_driver sensor_driver = {
	.driver = {
		.name  = DEVICE_NAME,
		.owner = THIS_MODULE,
	},
	.probe    =  sensor_probe,
	.remove   =  sensor_remove,
	.id_table =  sensor_spi_id,
};

static __init int sensor_spi_init(void)
{
	int status=-1;
	struct spi_master *master;
	struct spi_device *spi;
	struct spi_board_info chip =
	{
        .modalias	  = DEVICE_NAME,
        .mode         = 0x00,
        .bus_num	  = 0,
        .chip_select  = 0,
        .max_speed_hz = 2000000,
    };
	spi_register_driver(&sensor_driver);
	if (status<0)
	{
		pr_err("%s: spi_register_driver spi_driver failure. status = %d\n", __func__, status);
	}
	pr_err("%s: spi_register_driver spi_driver success. status = %d\n", __func__, status);
	master = spi_busnum_to_master(SENSOR_SPI_BUS);
    if (!master)
    {
        status = -ENODEV;
        goto error_busnum;
    }
    spi = spi_new_device(master, &chip);
    if (!spi)
    {
        status = -EBUSY;
        goto error_mem;
    }
	return status;

error_mem:
error_busnum:
    spi_unregister_driver(&sensor_driver);
    return status;
}

static __exit void sensor_spi_exit(void)
{
	spi_unregister_driver(&sensor_driver);
	if(sensor_spi!=NULL)
	spi_unregister_device(sensor_spi);
}

module_init(sensor_spi_init);
module_exit(sensor_spi_exit);
MODULE_LICENSE("GPL v2");
```

