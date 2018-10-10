---
title: [Android7.1][RK3399] RK reboot 机制驱动分析
tags: android
grammar_cjkRuby: true
---

Platform: RK3399 
OS: Android 7.1 
Kernel: v4.4.83


## 基本概念
kernel/Documentation/devicetree/bindings/power/reset/syscon-reboot.txt
```
Generic SYSCON mapped register reset driver

This is a generic reset driver using syscon to map the reset register.
The reset is generally performed with a write to the reset register
defined by the register map pointed by syscon reference plus the offset
with the mask defined in the reboot node.

Required properties:
- compatible: should contain "syscon-reboot"
- regmap: this is phandle to the register map node
- offset: offset in the register map for the reboot register (in bytes)
- mask: the reset value written to the reboot register (32 bit access)

Default will be little endian mode, 32 bit access only.

Examples:

        reboot {
           compatible = "syscon-reboot";
           regmap = <&regmapnode>;
           offset = <0x0>;
           mask = <0x1>;
        };
```
这个是使用 syscon 去映射重启寄存器的驱动.
通过 syscon 基地址加上偏移地址 (这个在 reboot 节点中有定义)

kernel/Documentation/devicetree/bindings/power/reset/reboot-mode.txt
```
Generic reboot mode core map driver

This driver get reboot mode arguments and call the write
interface to stores the magic value in special register
or ram . Then the bootloader can read it and take different
action according the argument stored.

All mode properties are vendor specific, it is a indication to tell
the bootloder what to do when the system reboot, and should be named
as mode-xxx = <magic> (xxx is mode name).

- mode-normal: Normal reboot mode, system reboot with command "reboot".
- mode-recovery: Android Recovery mode, it is a mode to format the device or update a new image.
- mode-bootloader: Android fastboot mode, it's a mode to re-flash partitions on the Android based device.
- mode-loader: A bootloader mode, it's a mode used to download image on Rockchip platform,
               usually used in development.

Example:
        reboot-mode {
                mode-normal = <BOOT_NORMAL>;
                mode-recovery = <BOOT_RECOVERY>;
                mode-bootloader = <BOOT_FASTBOOT>;
                mode-loader = <BOOT_LOADER>;
        }
```
这个驱动获取 reboot mode 的参数, 并且调用写接口在特定的寄存器或者ram中存储魔数 ,  然后 bootloader 可以获取魔数并采取相应的动作.
所有的 property 都是由 vendor 确定的, 这些 property 会告诉 bootloader 在重启时进行怎样的操作, 这些 property 的格式是 
`mode-xxx = <magic>` , 比如 recovery 模式是 `mode-recovery = <BOOT_RECOVERY>`


## 代码分析
### DTS 
```
 reboot-mode {
                        compatible = "syscon-reboot-mode";
                        offset = <0x300>;
                        mode-bootloader = <BOOT_BL_DOWNLOAD>;
                        mode-charge = <BOOT_CHARGING>;
                        mode-fastboot = <BOOT_FASTBOOT>;
                        mode-loader = <BOOT_BL_DOWNLOAD>;
                        mode-normal = <BOOT_NORMAL>;
                        mode-recovery = <BOOT_RECOVERY>;
                        mode-ums = <BOOT_UMS>;
                };
```
### Driver
代码在 `kernel/drivers/power/reset`
由 defconfig 中的`CONFIG_SYSCON_REBOOT_MODE`控制
```
obj-$(CONFIG_SYSCON_REBOOT_MODE) += syscon-reboot-mode.o
```

### 代码流程
**reboot mode 注册:**
```
syscon_reboot_mode_probe ->
  reboot_mode_register ->
    register_reboot_notifier -> //reboot_notifier的callback是reboot_mode_notify
      blocking_notifier_chain_register  //list是reboot_notifier_list
```

**reboot 调用:**
```
kernel_restart -> 
  kernel_restart_prepare ->
    blocking_notifier_call_chain -> 
      __blocking_notifier_call_chain -> 
        notifier_call_chain -> 
          nb->notifier_call -> //reboot_notifier_list被调用到
            reboot_mode_notify -> reboot-mode.c
              get_reboot_mode_magic -> //获取参数对应的magic
                reboot->write ->
                  syscon_reboot_mode_write ->
                    regmap_update_bits //使用regmap mmio更新到寄存器中
```

重启开机判断是在 uboot 中完成的:
```
static void fbt_handle_reboot(const char *cmdbuf)
{
    if (!strcmp(&cmdbuf[6], "-bootloader")) {
        FBTDBG("%s\n", cmdbuf);
        board_fbt_set_reboot_type(FASTBOOT_REBOOT_BOOTLOADER);
    }
    if (!strcmp(&cmdbuf[6], "-recovery")) {
        FBTDBG("%s\n", cmdbuf);
        board_fbt_set_reboot_type(FASTBOOT_REBOOT_RECOVERY);
    }
    if (!strcmp(&cmdbuf[6], "-recovery:wipe_data")) {
        FBTDBG("%s\n", cmdbuf);
        board_fbt_set_reboot_type(FASTBOOT_REBOOT_RECOVERY_WIPE_DATA);
    }

    strcpy(priv.response, "OKAY");
    priv.flag |= FASTBOOT_FLAG_RESPONSE;
    fbt_handle_response();
    udelay(1000000); /* 1 sec */

    do_reset(NULL, 0, 0, NULL);
}
```