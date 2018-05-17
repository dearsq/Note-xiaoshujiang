---
title: [Android5.1][RK3288] LCD Mipi 初始化长包数据规范问题
tags: RockChip,LCD,MIPI
grammar_cjkRuby: true
---
## 目录
[TOC]

## 先说问题和结论
### 问题
首先是因为我出现了这样的 Bug：
![](https://ws4.sinaimg.cn/large/ba061518gw1f7bm3unagfj20y70gaad8.jpg)
我的 cmds7 明明填充的是 LP 模式，但是打印中却说是 HS 模式。
我在一个帖子中看到说 cmds 参数 不能为 8 和 16 的情况。
于是**错误地将地将两者联系起来，认为**参数为 8 或者 16 的情况下，LP 模式会被转换成 HS 模式。
于是希望跟着代码一探究竟。
### 真相
但是实际上两者是没有关联的。
真相是
**其实是可以传递 8 字节 和 16 字节的参数的。**

跟踪代码发现打印 LP mode 和 HS mode 这个输出信息的代码是根据 reg[0] 来判断的
```
MIPI_DBG("%d command sent in %s size:%d\n", __LINE__, regs[0] ? "LP mode" : "HS mode", liTmp);
```
我出现这种情况的原因，是因为擅自错误地将一个 36 字节的参数 拆分成 28 和 8 。
**而后面 8 字节 cmds 的首字节 为 0x00**。
也就是 reg[0] = 0x00 ，所以会输出 HS mode。

## 正文
假设我们有 8 个参数，那么 cmds 实际为 { 0x39,0x11,0x22,0x33,0x44,0x55,0x66,0x77,0x88 }
cmd_len = length / sizeof(u32) = 9
在 video/rockchip/screen/lcd_mipi.c 中的 rk_mipi_screen_cmd_init 可以看到是调用
dsi_send_packet 这个函数来进行参数传递
```c
//...
		dcs_cmd = list_entry(screen_pos, struct mipi_dcs_cmd_ctr_list, list);
		len = dcs_cmd->dcs_cmd.cmd_len + 1;	// len = 9 + 1 = 10
		for (i = 1; i < len ; i++) {  // 将 dcs_cmd->dcs_cmd.cmds 中的 9 个参数赋值给 cmds
			cmds[i] = dcs_cmd->dcs_cmd.cmds[i-1]; //cmds[1-9] 被 dcs_cmd.cmds[0-8] 赋值
		}
		MIPI_SCREEN_DBG("dcs_cmd.name:%s\n", dcs_cmd->dcs_cmd.name);
		if (dcs_cmd->dcs_cmd.type == LPDT) {
			cmds[0] = LPDT;	//cmds[0] 表示传输数据模式的标志 1
			if (dcs_cmd->dcs_cmd.dsi_id == 0) {
				MIPI_SCREEN_DBG("dcs_cmd.dsi_id == 0 line=%d\n", __LINE__);
                //调用这个函数进行 mipi 通信
                //这里的 cmds 中实际有 10 个字节
                // 0 为 数据类型的标志 1
                // 1-9 为参数 cmds[1] = 0x39 数据类型为长包数据 cmds[2-9] 为屏幕初始化参数
                // len 为 10
				dsi_send_packet(0, cmds, len);
			}
//...
```
跟代码发现在 video/rockchip/transmitter/mipi_dsi.c 中
```c
int dsi_send_dcs_packet(unsigned int id, unsigned char *packet, u32 n) {

	struct mipi_dsi_ops *ops = NULL;
    //printk("dsi_send_dcs_packet-------id=%d\n",id);
	if(id > (MAX_DSI_CHIPS - 1))
		return -EINVAL;
	ops = dsi_ops[id];
	if(!ops)
		return -EINVAL;
	if(ops->dsi_send_dcs_packet)
		ops->dsi_send_dcs_packet(ops->dsi, packet, n);
	return 0;
}
#ifdef CONFIG_MIPI_DSI
EXPORT_SYMBOL(dsi_send_dcs_packet);
```
ops->dsi_send_dcs_packet 这个实现是在 ops->的 dsi_send_dcs_packet
究其根源的实现是在
kernel/drivers/video/rockchip/transmitter/rk32_mipi_dsi.c
的 rk32_mipi_dsi_send_packet
```c
//arg 是要传输的通道，默认为 0
//cmds 就是 lcd dtsi 中的 cmds // 这里假设为{ 0x39,0x11,0x22,0x33,0x44,0x55,0x66,0x77,0x88 }
//length 就是 cmds 的长度 // 这里为 10
static int rk32_mipi_dsi_send_packet(void *arg, unsigned char cmds[], u32 length)
{
	struct dsi *dsi = arg;
	unsigned char *regs;
	u32 type, liTmp = 0, i = 0, j = 0, data = 0;

	if (rk32_dsi_get_bits(dsi, gen_cmd_full) == 1) {
		MIPI_TRACE("gen_cmd_full\n");
		return -1;
	}
	regs = kmalloc(0x400, GFP_KERNEL);
	if (!regs) {
		printk("request regs fail!\n");
		return -ENOMEM;
	}
	memcpy(regs, cmds, length);	//regs 现在为 cmds 中的内容了

	liTmp = length - 2;		//liTmp = 10 - 2 = 8
	type = regs[1];			//type = regs[1] = cmds[1] = 0x39 （采用长包模式传输）
	switch (type) { //0x39 即 DTYPE_DCS_LWRITE
    	//...
	case DTYPE_DCS_LWRITE:
		rk32_dsi_set_bits(dsi, regs[0], dcs_lw_tx);	// 设置标志位，根据 regs[0] 设置寄存器 dcs_lw_tx 中的标志
		for (i = 0; i < liTmp; i++) {
        	// 0-7 依次给 regs[0]-regs[7] 赋值，这8个值便是屏幕初始化的内容
            // {0x11,0x22,0x33,0x44,0x55.0x66,0x77,0x88}
			regs[i] = regs[i+2];
		}
		for (i = 0; i < liTmp; i++) {
			j = i % 4; //0 1 2 3 0 1 2 3
			data |= regs[i] << (j * 8);
            //data | (regs[0] << 0)
            //data | (regs[1] << 8)
            //data |  (regs[2] << 16)
            //data | (regs[3] << 24)
            // 8 个字节的内容被组合成两个 data
            // 0x44332211 0x88776655
			if (j == 3 || ((i + 1) == liTmp)) { //每当组成的 data 满了的时候，或者是所有的参数都填充了的时候
				if (rk32_dsi_get_bits(dsi, gen_pld_w_full) == 1) {
					MIPI_TRACE("gen_pld_w_full :%d\n", i);
					break;
				}
				rk32_dsi_set_bits(dsi, data, GEN_PLD_DATA);
				MIPI_DBG("write GEN_PLD_DATA:%d, %08x\n", i, data);
				data = 0; //清空 data，开始下个 data 的传输
			}
		}
		data = type;//data = 0x39
		data |= (liTmp & 0xffff) << 8;	//0x0839 //如果是 16 字节的话为 0x1039（16 的16进制是 0x10）
		break;
        //...
        }

	MIPI_DBG("%d command sent in %s size:%d\n", __LINE__, regs[0] ? "LP mode" : "HS mode", liTmp);
	//这里就会打印究竟是什么模式来传输
    //reg[0] 正是代表了 屏幕参数初始化的第一个字节！
    //它的含义是这块屏 IC 的 CMD！
    //0x11 0x22 0x33 0x44... 0x88 表示执行 0x11 这个 CMD，参数为 0x22 到 0x88
    //那为什么  8 个字节就会变成 HS mode 呢，
    //看我所传输的 cmds7 可以发现要传输的第一个参数为 0x00，所以被判别为 HS mode

	MIPI_DBG("write GEN_HDR:%08x\n", data);
	rk32_dsi_set_bits(dsi, data, GEN_HDR);

	i = 10;
	while (!rk32_dsi_get_bits(dsi, gen_cmd_empty) && i--) {
		MIPI_DBG(".");
		udelay(10);
	}
	udelay(10);
	kfree(regs);
	return 0;
}
```
![](https://ws3.sinaimg.cn/large/ba061518gw1f7bsgbi71fj20c403nq3a.jpg)

至此，疑问解决了。
看 **LCD 的 datasheet** 也可以发现，像之前所说的，
在 commond mode 的时候，这个参数，
也就是 屏IC 的 CMD，**是不会为 0x00** 的。
只有在 video mode 下才可能为 0x00。

而参数为 8 字节 和 16 字节 其实都可以，只要不超过 struct dsc_cmd 中定义的大小 400 ，就够了。
