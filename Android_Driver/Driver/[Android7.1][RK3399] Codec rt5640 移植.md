---
title: [Android7.1][RK3399] Codec rt5640 移植.md
tags: android
grammar_cjkRuby: true
---

Platform: RK3399 
OS: Android 7.1 
Kernel: v4.4.83

## 硬件原理图

![](https://ws1.sinaimg.cn/large/ba061518gy1fw21hwfzimj210w0kiwjv.jpg)

* 数据走I2S1通道
* 控制走I2C1通道
* 输出走HPOUTL/HPOUTR

## DTS
./rk3399-excavator-sapphire.dtsi
参考 rt5651-sound 的配置:
```
      rt5651-sound {
                compatible = "simple-audio-card";
                simple-audio-card,format = "i2s";
                simple-audio-card,name = "realtek,rt5651-codec";
                simple-audio-card,mclk-fs = <256>;
                simple-audio-card,widgets =
                        "Microphone", "Mic Jack",
                        "Headphone", "Headphone Jack";
                simple-audio-card,routing =
                        "Mic Jack", "MICBIAS1",
                        "IN1P", "Mic Jack",
                        "Headphone Jack", "HPOL",
                        "Headphone Jack", "HPOR";
                simple-audio-card,cpu {
                        sound-dai = <&i2s0>;
                };
                simple-audio-card,codec {
                        sound-dai = <&rt5651>;
                };
        };
```
完成 rt5640 DTS 的配置:
```
    rt5640-sound {
        compatible = "simple-audio-card";
        simple-audio-card,format = "i2s";
        simple-audio-card,name = "rockchip,rt5640-codec";
        simple-audio-card,mclk-fs = <256>;
        simple-audio-card,widgets =
            "Microphone", "Mic Jack",
            "Headphone", "Headphone Jack";
        simple-audio-card,routing =
            "Mic Jack", "MICBIAS1",
            "IN1P", "Mic Jack",
            "Headphone Jack", "HPOL",
            "Headphone Jack", "HPOR";
        simple-audio-card,cpu {
            sound-dai = <&i2s1>;
        };
        simple-audio-card,codec {
            sound-dai = <&rt5640>;
        };
    };
	
&i2s1 {
    status = "okay";
    rockchip,i2s-broken-burst-len;
    rockchip,playback-channels = <8>;
    rockchip,capture-channels = <8>;
    #sound-dai-cells = <0>;
};

&i2c1 {
    status = "okay";
    i2c-scl-rising-time-ns = <140>;
    i2c-scl-falling-time-ns = <30>;

    rt5640: rt5640@1c {
        #sound-dai-cells = <0>;
        compatible = "realtek,rt5640";
        reg = <0x1c>;
        clocks = <&cru SCLK_I2S_8CH_OUT>;
        clock-names = "mclk";
        realtek,in1-differential;
        pinctrl-names = "default";
        pinctrl-0 = <&rt5640_hpcon &i2s_8ch_mclk>;
        io-channels = <&saradc 4>;
        hp-det-adc-value = <500>;
        status = "okay";
    };
};
```

clock 的 driver 部分对应进行修改:
rk3399.dtsi
```
diff --git a/arch/arm64/boot/dts/rockchip/rk3399.dtsi b/arch/arm64/boot/dts/rockchip/rk3399.dtsi
index d3f0f76..1759a91 100644
--- a/arch/arm64/boot/dts/rockchip/rk3399.dtsi
+++ b/arch/arm64/boot/dts/rockchip/rk3399.dtsi
@@ -1692,6 +1692,9 @@
        dma-names = "tx", "rx";
        clock-names = "i2s_clk", "i2s_hclk";
        clocks = <&cru SCLK_I2S1_8CH>, <&cru HCLK_I2S1_8CH>;
+       assigned-clocks = <&cru SCLK_I2S_8CH>;
+       assigned-clock-parents = <&cru SCLK_I2S1_8CH>;
        pinctrl-names = "default";
        pinctrl-0 = <&i2s1_2ch_bus>;

```
clk-rk3399.c
```
diff --git a/drivers/clk/rockchip/clk-rk3399.c b/drivers/clk/rockchip/clk-rk3399.c
index b0e4daa..e2d872f 100644
--- a/drivers/clk/rockchip/clk-rk3399.c
+++ b/drivers/clk/rockchip/clk-rk3399.c
@@ -711,8 +711,9 @@ static struct rockchip_clk_branch rk3399_clk_branches[] __initdata = {
            &rk3399_i2s2_fracmux),
    GATE(SCLK_I2S2_8CH, "clk_i2s2", "clk_i2s2_mux", CLK_SET_RATE_PARENT,
            RK3399_CLKGATE_CON(8), 11, GFLAGS),
-
-   MUX(0, "clk_i2sout_src", mux_i2sch_p, CLK_SET_RATE_PARENT,
+   //MUX(0, "clk_i2sout_src", mux_i2sch_p, CLK_SET_RATE_PARENT,
+   MUX(SCLK_I2S_8CH, "clk_i2sout_src", mux_i2sch_p, CLK_SET_RATE_PARENT,
            RK3399_CLKSEL_CON(31), 0, 2, MFLAGS),
    COMPOSITE_NODIV(SCLK_I2S_8CH_OUT, "clk_i2sout", mux_i2sout_p, CLK_SET_RATE_PARENT,
            RK3399_CLKSEL_CON(30), 8, 2, MFLAGS,

```
pl330.c
```
diff --git a/drivers/dma/pl330.c b/drivers/dma/pl330.c
index 1e5c79b..08179f5 100644
--- a/drivers/dma/pl330.c
+++ b/drivers/dma/pl330.c
@@ -1169,6 +1169,16 @@ static inline int _ldst_devtomem(struct pl330_dmac *pl330, unsigned dry_run,
        off += _emit_WFP(dry_run, &buf[off], cond, pxs->desc->peri);
        off += _emit_LDP(dry_run, &buf[off], cond, pxs->desc->peri);
        off += _emit_ST(dry_run, &buf[off], ALWAYS);
+#ifdef CONFIG_ARCH_ROCKCHIP
+       /*
+        * Make suree dma has finish transmission, or later flush may
+        * cause dma second transmission,and fifo is overrun.
+        */
+       off += _emit_WMB(dry_run, &buf[off]);
+       off += _emit_NOP(dry_run, &buf[off]);
+       off += _emit_WMB(dry_run, &buf[off]);
+       off += _emit_NOP(dry_run, &buf[off]);
+#endif

        if (!(pl330->quirks & PL330_QUIRK_BROKEN_NO_FLUSHP))
            off += _emit_FLUSHP(dry_run, &buf[off],
@@ -1189,6 +1199,16 @@ static inline int _ldst_memtodev(struct pl330_dmac *pl330,
        off += _emit_WFP(dry_run, &buf[off], cond, pxs->desc->peri);
        off += _emit_LD(dry_run, &buf[off], ALWAYS);
        off += _emit_STP(dry_run, &buf[off], cond, pxs->desc->peri);
+#ifdef CONFIG_ARCH_ROCKCHIP
+       /*
+        * Make suree dma has finish transmission, or later flush may
+        * cause dma second transmission,and fifo is overrun.
+        */
+       off += _emit_WMB(dry_run, &buf[off]);
+       off += _emit_NOP(dry_run, &buf[off]);
+       off += _emit_WMB(dry_run, &buf[off]);
+       off += _emit_NOP(dry_run, &buf[off]);
+#endif

        if (!(pl330->quirks & PL330_QUIRK_BROKEN_NO_FLUSHP))
            off += _emit_FLUSHP(dry_run, &buf[off],
@@ -1327,7 +1347,11 @@ static inline int _loop_cyclic(struct pl330_dmac *pl330, unsigned dry_run,
    /* forever loop */
    off += _emit_MOV(dry_run, &buf[off], SAR, x->src_addr);
    off += _emit_MOV(dry_run, &buf[off], DAR, x->dst_addr);
-
+#ifdef CONFIG_ARCH_ROCKCHIP
+   if (!(pl330->quirks & PL330_QUIRK_BROKEN_NO_FLUSHP))
+       off += _emit_FLUSHP(dry_run, &buf[off],
+                   pxs->desc->peri);
+#endif
    /* loop0 */
    off += _emit_LP(dry_run, &buf[off], 0,  lcnt0);
    ljmp0 = off;
@@ -1366,7 +1390,7 @@ static inline int _loop_cyclic(struct pl330_dmac *pl330, unsigned dry_run,
            ccr &= ~(0xf << CC_SRCBRSTLEN_SHFT);
            ccr &= ~(0xf << CC_DSTBRSTLEN_SHFT);
            off += _emit_MOV(dry_run, &buf[off], CCR, ccr);
-           off += _emit_LP(dry_run, &buf[off], 1, c - 1);
+           off += _emit_LP(dry_run, &buf[off], 1, c);
            ljmp1 = off;
            off += _bursts(pl330, dry_run, &buf[off], pxs, 1);
            lpend.cond = ALWAYS;
@@ -1403,7 +1427,11 @@ static inline int _setup_loops(struct pl330_dmac *pl330,
    u32 ccr = pxs->ccr;
    unsigned long c, bursts = BYTE_TO_BURST(x->bytes, ccr);
    int off = 0;
-
+#ifdef CONFIG_ARCH_ROCKCHIP
+   if (!(pl330->quirks & PL330_QUIRK_BROKEN_NO_FLUSHP))
+       off += _emit_FLUSHP(dry_run, &buf[off],
+                   pxs->desc->peri);
+#endif
    while (bursts) {
        c = bursts;
        off += _loop(pl330, dry_run, &buf[off], &c, pxs);
@@ -1757,16 +1785,17 @@ static int pl330_update(struct pl330_dmac *pl330)

            /* Detach the req */
            descdone = thrd->req[active].desc;
+           if (descdone) {
+               if (!descdone->cyclic) {
+                   thrd->req[active].desc = NULL;
+                   thrd->req_running = -1;
+                   /* Get going again ASAP */
+                   _start(thrd);
+               }

-           if (!descdone->cyclic) {
-               thrd->req[active].desc = NULL;
-               thrd->req_running = -1;
-               /* Get going again ASAP */
-               _start(thrd);
+               /* For now, just make a list of callbacks to be done */
+               list_add_tail(&descdone->rqd, &pl330->req_done);
            }
-
-           /* For now, just make a list of callbacks to be done */
-           list_add_tail(&descdone->rqd, &pl330->req_done);
        }
    }

@@ -1817,7 +1846,6 @@ static bool _chan_ns(const struct pl330_dmac *pl330, int i)
 static struct pl330_thread *pl330_request_channel(struct pl330_dmac *pl330)
 {
    struct pl330_thread *thrd = NULL;
-   unsigned long flags;
    int chans, i;

    if (pl330->state == DYING)
@@ -1825,8 +1853,6 @@ static struct pl330_thread *pl330_request_channel(struct pl330_dmac *pl330)

    chans = pl330->pcfg.num_chan;

-   spin_lock_irqsave(&pl330->lock, flags);
-
    for (i = 0; i < chans; i++) {
        thrd = &pl330->channels[i];
        if ((thrd->free) && (!_manager_ns(thrd) ||
@@ -1844,8 +1870,6 @@ static struct pl330_thread *pl330_request_channel(struct pl330_dmac *pl330)
        thrd = NULL;
    }

-   spin_unlock_irqrestore(&pl330->lock, flags);
-
    return thrd;
 }

@@ -1863,7 +1887,6 @@ static inline void _free_event(struct pl330_thread *thrd, int ev)
 static void pl330_release_channel(struct pl330_thread *thrd)
 {
    struct pl330_dmac *pl330;
-   unsigned long flags;

    if (!thrd || thrd->free)
        return;
@@ -1875,10 +1898,8 @@ static void pl330_release_channel(struct pl330_thread *thrd)

    pl330 = thrd->dmac;

-   spin_lock_irqsave(&pl330->lock, flags);
    _free_event(thrd, thrd->ev);
    thrd->free = true;
-   spin_unlock_irqrestore(&pl330->lock, flags);
 }

 /* Initialize the structure for PL330 configuration, that can be used
@@ -2248,19 +2269,19 @@ static int pl330_alloc_chan_resources(struct dma_chan *chan)
    struct pl330_dmac *pl330 = pch->dmac;
    unsigned long flags;

-   spin_lock_irqsave(&pch->lock, flags);
+   spin_lock_irqsave(&pl330->lock, flags);

    dma_cookie_init(chan);

    pch->thread = pl330_request_channel(pl330);
    if (!pch->thread) {
-       spin_unlock_irqrestore(&pch->lock, flags);
+       spin_unlock_irqrestore(&pl330->lock, flags);
        return -ENOMEM;
    }

    tasklet_init(&pch->task, pl330_tasklet, (unsigned long) pch);

-   spin_unlock_irqrestore(&pch->lock, flags);
+   spin_unlock_irqrestore(&pl330->lock, flags);

    return 1;
 }
@@ -2363,19 +2384,20 @@ static int pl330_pause(struct dma_chan *chan)
 static void pl330_free_chan_resources(struct dma_chan *chan)
 {
    struct dma_pl330_chan *pch = to_pchan(chan);
+   struct pl330_dmac *pl330 = pch->dmac;
    unsigned long flags;

    tasklet_kill(&pch->task);

    pm_runtime_get_sync(pch->dmac->ddma.dev);
-   spin_lock_irqsave(&pch->lock, flags);
+   spin_lock_irqsave(&pl330->lock, flags);

    pl330_release_channel(pch->thread);
    pch->thread = NULL;

    list_splice_tail_init(&pch->work_list, &pch->dmac->desc_pool);

-   spin_unlock_irqrestore(&pch->lock, flags);
+   spin_unlock_irqrestore(&pl330->lock, flags);
    pm_runtime_mark_last_busy(pch->dmac->ddma.dev);
    pm_runtime_put_autosuspend(pch->dmac->ddma.dev);

```

rk3399-cru.h
```
diff --git a/include/dt-bindings/clock/rk3399-cru.h b/include/dt-bindings/clock/rk3399-cru.h
index 37e665f..54ac812 100644
--- a/include/dt-bindings/clock/rk3399-cru.h
+++ b/include/dt-bindings/clock/rk3399-cru.h
@@ -226,6 +226,9 @@
 #define ACLK_GIC_PRE           262
 #define ACLK_VOP0_PRE          263
 #define ACLK_VOP1_PRE          264
+#define SCLK_I2S_8CH            265
+

 /* pclk gates */
 #define PCLK_PERIHP            320
```