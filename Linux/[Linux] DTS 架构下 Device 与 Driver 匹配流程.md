---
title: [Linux] DTS 架构下 Device 与 Driver 匹配流程
tags: Device Tree, dts,Linux,kernel
grammar_cjkRuby: true
---
## 旧与新
我们知道原来采用 板级文件 架构的时候，device 与 driver 匹配的方式是 调用 platform 的 match 函数。如果 板级结构体 borad_info 中的 name 与 driver 中的 name 相同（匹配），则调用 probe 函数。

但是现在引入了 DTS 架构。所以这个流程也有些变化，加上最近在调 spi 的 Sensor，刚编写完最小驱动模块却发现 probe 没有被调用，所以借此机会梳理一下 device 与 driver 的匹配流程。
1. 分析初始化流程。（扫描 dts 生成的 dtb 文件，并展开成为 Device Tree Structure）
2. platform的识别流程与分析
3. Device Tree Structure 是如何加入 linux kernel 的设备驱动模型的

## 初始化流程
系统初始化流程可以参见 [展讯平台启动流程（uboot）](http://blog.csdn.net/dearsq/article/details/51063207)
### unflat
我们知道 dtb 是 dts 与 dtsi 编译的二进制文件，在系统初始化的过程中，我们将 dtb 转化成 device_node 的树状结构，便于后续的方便操作：
setup_ArchName -> unflatten_device_tree
drivers/of/fdt.c, line 1119
```c
1119 void __init unflatten_device_tree(void)
1120 {
1121         __unflatten_device_tree(initial_boot_params, &of_root,
1122                                 early_init_dt_alloc_memory_arch);
1123 
1124         /* Get pointer to "/chosen" and "/aliases" nodes for use everywhere */
1125         of_alias_scan(early_init_dt_alloc_memory_arch);
1126 }
1127 
```
我们利用 struct device_node 来抽象 设备树 中的一个节点：
```c
struct device_node { 
    const char *name;			//device node name 
    const char *type;			  //对应device_type的属性 
    phandle phandle;			 //对应该节点的phandle属性 
    const char *full_name; 		//从“/”开始的，表示该node的full path
    struct    property *properties;  //该节点的属性列表 
    struct    property *deadprops; //如果需要删除某些属性，kernel并非真的删除，而是挂入到deadprops的列表 
    struct    device_node *parent; //parent、child以及sibling将所有的device node连接起来 
    struct    device_node *child; 
    struct    device_node *sibling; 
    struct    device_node *next;  //通过该指针可以获取相同类型的下一个node 
    struct    device_node *allnext; //通过该指针可以获取node global list下一个node 
    struct    proc_dir_entry *pde;  //开放到userspace的proc接口信息 
    struct    kref kref;					//该node的reference count 
    unsigned long _flags; 
    void    *data; 
};
```
如上 device_node 被组织成 
1.global list。全局变量struct device_node *of_allnodes就是指向设备树的global list
2.tree。
_ _unflatten_device_tree 的主要功能就是扫描 DTB。
```c
static void __unflatten_device_tree(struct boot_param_header *blob;//需要扫描的DTB 
                 struct device_node **mynodes,//global list指针 
                 void * (*dt_alloc)(u64 size, u64 align))//内存分配函数 
{ 
    unsigned long size; 
    void *start, *mem; 
    struct device_node **allnextp = mynodes;
    此处删除了health check代码，例如检查DTB header的magic，确认blob的确指向一个DTB。
    /* scan过程分成两轮，第一轮主要是确定device-tree structure的长度，保存在size变量中 */ 
    start = ((void *)blob) + be32_to_cpu(blob->off_dt_struct); 
    size = (unsigned long)unflatten_dt_node(blob, 0, &start, NULL, NULL, 0); 
    size = ALIGN(size, 4);
    /* 初始化的时候，并不是扫描到一个node或者property就分配相应的内存，实际上内核是一次性的分配了一大片内存，这些内存包括了所有的struct device_node、node name、struct property所需要的内存。*/ 
    mem = dt_alloc(size + 4, __alignof__(struct device_node)); 
    memset(mem, 0, size);
    *(__be32 *)(mem + size) = cpu_to_be32(0xdeadbeef);   //用来检验后面unflattening是否溢出
    /* 这是第二轮的scan，第一次scan是为了得到保存所有node和property所需要的内存size，第二次就是实打实的要构建device node tree了 */ 
    start = ((void *)blob) + be32_to_cpu(blob->off_dt_struct); 
    unflatten_dt_node(blob, mem, &start, NULL, &allnextp, 0);     
    //... 此处略去校验溢出和校验OF_DT_END。 
}
```
### platform的识别流程与分析
Device Tree 是如何完成运行时的参数传递和 platform 识别功能的?
#### 汇编部分代码分析（关于参数传递）
linux/arch/arm/kernel/head.S文件定义了bootloader和kernel的参数传递要求：
```S
MMU = off, D-cache = off, I-cache = dont care, r0 = 0, r1 = machine nr, r2 = atags or dtb pointer.
```
目前的kernel支持旧的 tag list 的方式，同时也支持 device tree 的方式。
r2可能是device tree binary file的指针（bootloader要传递给内核之前要copy到memory中），也可以能是tag list的指针。
在ARM的汇编部分的启动代码中（主要是 head.S 和 head-common.S），machine type ID和指向DTB或者atags的指针被保存在变量__machine_arch_type和__atags_pointer中，这么做是为了后续c代码进行处理。


#### setup_ARCH
arch/arm/kernel/setup.c#L1052
```c
void __init setup_arch(char **cmdline_p) 
{ 
    const struct machine_desc *mdesc;
……
    mdesc = setup_machine_fdt(__atags_pointer); 
    if (!mdesc) 
        mdesc = setup_machine_tags(__atags_pointer, __machine_arch_type); 
    machine_desc = mdesc; 
    machine_name = mdesc->name;
…… 
}
```
对于如何确定HW platform这个问题。
旧的方法是静态定义若干的machine描述符（struct machine_desc ），在启动过程中，通过machine type ID作为索引，在这些静态定义的machine描述符中扫描，找到那个ID匹配的描述符。
在新的内核中，首先使用 setup_machine_fdt 来 setup machine描述符，如果返回 NULL，才使用传统的方法setup_machine_tags来setup machine描述符。
传统的方法需要给出_._machine_arch_type（bootloader通过r1寄存器传递给kernel的）和tag list的地址（用来进行tag parse）。
_._machine_arch_type用来寻找machine描述符；
tag list用于运行时参数的传递。随着内核的不断发展，相信有一天linux kernel会完全抛弃tag list的机制。

#### 匹配 platform（machine 描述符）
setup_machine_fdt 函数的功能就是根据Device Tree的信息，找到最适合的machine描述符。
```c
const struct machine_desc * __init setup_machine_fdt(unsigned int dt_phys) 
{ 
    const struct machine_desc *mdesc, *mdesc_best = NULL;
    if (!dt_phys || !early_init_dt_scan(phys_to_virt(dt_phys))) 
        return NULL;
    mdesc = of_flat_dt_match_machine(mdesc_best, arch_get_next_mach);
    if (!mdesc) {  
        出错处理 
    }
    /* Change machine number to match the mdesc we're using */ 
    __machine_arch_type = mdesc->nr;
    return mdesc; 
}
```
early_init_dt_scan 函数有两个功能，一个是为后续的DTB scan进行准备工作，另外一个是运行时参数传递。具体请参考下面一个section的描述。
of_flat_dt_match_machine是在machine描述符的列表中scan，找到最合适的那个machine描述符。我们首先看如何组成machine描述符的列表。和传统的方法类似，也是静态定义的。DT_MACHINE_START和MACHINE_END用来定义一个machine描述符。编译的时候，compiler会把这些machine descriptor放到一个特殊的段中（.arch.info.init），形成machine描述符的列表。machine描述符用下面的数据结构来标识（删除了不相关的member）：
```c
struct machine_desc { 
    unsigned int        nr;        /* architecture number    */ 
    const char *const     *dt_compat;    /* array of device tree 'compatible' strings    */
……
   };
```
nr成员就是过去使用的machine type ID。内核machine描述符的table有若干个entry，每个都有自己的ID。bootloader传递了machine type ID，指明使用哪一个machine描述符。目前匹配machine描述符使用compatible strings，也就是dt_compat成员，这是一个string list，定义了这个machine所支持的列表。在扫描machine描述符列表的时候需要不断的获取下一个machine描述符的compatible字符串的信息，具体的代码如下：
```c
static const void * __init arch_get_next_mach(const char *const **match) 
{ 
    static const struct machine_desc *mdesc = __arch_info_begin; 
    const struct machine_desc *m = mdesc;
    if (m >= __arch_info_end) 
        return NULL;
    mdesc++; 
    *match = m->dt_compat; 
    return m; 
}
```
_._arch_info_begin指向machine描述符列表第一个entry。通过mdesc++不断的移动machine描述符指针（Note：mdesc是static的）。match返回了该machine描述符的compatible string list。具体匹配的算法倒是很简单，就是比较字符串而已，一个是root node的compatible字符串列表，一个是machine描述符的compatible字符串列表，得分最低的（最匹配的）就是我们最终选定的machine type。

#### 运行时传递参数
运行时参数是在扫描DTB的chosen node时候完成的，具体的动作就是获取chosen node的bootargs、initrd等属性的value，并将其保存在全局变量（boot_command_line，initrd_start、initrd_end）中。使用tag list方法是类似的，通过分析tag list，获取相关信息，保存在同样的全局变量中。具体代码位于early_init_dt_scan函数中：
```c
bool __init early_init_dt_scan(void *params) 
{ 
    if (!params) 
        return false;
    /* 全局变量initial_boot_params指向了DTB的header*/ 
    initial_boot_params = params;
    /* 检查DTB的magic，确认是一个有效的DTB */ 
    if (be32_to_cpu(initial_boot_params->magic) != OF_DT_HEADER) { 
        initial_boot_params = NULL; 
        return false; 
    }
    /* 扫描 /chosen node，保存运行时参数（bootargs）到boot_command_line，此外，还处理initrd相关的property，并保存在initrd_start和initrd_end这两个全局变量中 */ 
    of_scan_flat_dt(early_init_dt_scan_chosen, boot_command_line);
    /* 扫描根节点，获取 {size,address}-cells信息，并保存在dt_root_size_cells和dt_root_addr_cells全局变量中 */ 
    of_scan_flat_dt(early_init_dt_scan_root, NULL);
    /* 扫描DTB中的memory node，并把相关信息保存在meminfo中，全局变量meminfo保存了系统内存相关的信息。*/ 
    of_scan_flat_dt(early_init_dt_scan_memory, NULL);
    return true; 
}
```
设定meminfo（该全局变量确定了物理内存的布局）有若干种途径：
1、通过tag list（tag是ATAG_MEM）传递memory bank的信息。
2、通过command line（可以用tag list，也可以通过DTB）传递memory bank的信息。
3、通过DTB的memory node传递memory bank的信息。
目前当然是推荐使用Device Tree的方式来传递物理内存布局信息。

### Device Tree Structure 是如何加入 linux kernel 的设备驱动模型的
在linux kernel引入统一设备模型之后，bus、driver和device形成了设备模型中的铁三角。在驱动初始化的时候会将代表该driver的一个数据结构（一般是xxx_driver）挂入bus上的driver链表。device挂入链表分成两种情况，一种是即插即用类型的bus，在插入一个设备后，总线可以检测到这个行为并动态分配一个device数据结构（一般是xxx_device，例如usb_device），之后，将该数据结构挂入bus上的device链表。bus上挂满了driver和device，那么如何让device遇到“对”的那个driver呢？那么就要靠缘分了，也就是bus的match函数。
上面是一段导论，我们还是回到Device Tree。导致Device Tree的引入ARM体系结构的代码其中一个最重要的原因的太多的静态定义的表格。例如：一般代码中会定义一个static struct platform_device *xxx_devices的静态数组，在初始化的时候调用platform_add_devices。这些静态定义的platform_device往往又需要静态定义各种resource，这导致静态表格进一步增大。如果ARM linux中不再定义这些表格，那么一定需要一个转换的过程，也就是说，系统应该会根据Device tree来动态的增加系统中的platform_device。当然，这个过程并非只是发生在platform bus上（具体可以参考“Platform Device”的设备），也可能发生在其他的非即插即用的bus上，例如AMBA总线、PCI总线。一言以蔽之，如果要并入linux kernel的设备驱动模型，那么就需要根据device_node的树状结构（root是of_allnodes）将一个个的device node挂入到相应的总线device链表中。只要做到这一点，总线机制就会安排device和driver的约会。
当然，也不是所有的device node都会挂入bus上的设备链表，比如cpus node，memory node，choose node等。

1、cpus node的处理
这部分的处理可以参考setup_arch->arm_dt_init_cpu_maps中的代码，具体的代码如下：
```c
void __init arm_dt_init_cpu_maps(void) 
{ 
    scan device node global list，寻找full path是“/cpus”的那个device node。cpus这个device node只是一个容器，其中包括了各个cpu node的定义以及所有cpu node共享的property。 
    cpus = of_find_node_by_path("/cpus");
 
    for_each_child_of_node(cpus, cpu) {           遍历cpus的所有的child node 
        u32 hwid;
        if (of_node_cmp(cpu->type, "cpu"))        我们只关心那些device_type是cpu的node 
            continue;

        if (of_property_read_u32(cpu, "reg", &hwid)) {    读取reg属性的值并赋值给hwid 
            return; 
        }
        reg的属性值的8 MSBs必须设置为0，这是ARM CPU binding定义的。 
        if (hwid & ~MPIDR_HWID_BITMASK)   
            return;
        不允许重复的CPU id，那是一个灾难性的设定 
        for (j = 0; j < cpuidx; j++) 
            if (WARN(tmp_map[j] == hwid, "Duplicate /cpu reg " 
                             "properties in the DT\n")) 
                return;
数组tmp_map保存了系统中所有CPU的MPIDR值（CPU ID值），具体的index的编码规则是： tmp_map[0]保存了booting CPU的id值，其余的CPU的ID值保存在1～NR_CPUS的位置。 
        if (hwid == mpidr) { 
            i = 0; 
            bootcpu_valid = true; 
        } else { 
            i = cpuidx++; 
        }
        tmp_map[i] = hwid; 
    }
根据DTB中的信息设定cpu logical map数组。
    for (i = 0; i < cpuidx; i++) { 
        set_cpu_possible(i, true); 
        cpu_logical_map(i) = tmp_map[i]; 
    } 
}
```
要理解这部分的内容，需要理解ARM CUPs binding的概念，可以参考linux/Documentation/devicetree/bindings/arm目录下的CPU.txt文件的描述。
2、memory的处理
这部分的处理可以参考setup_arch->setup_machine_fdt->early_init_dt_scan->early_init_dt_scan_memory中的代码。具体如下：
```c
int __init early_init_dt_scan_memory(unsigned long node, const char *uname, 
                     int depth, void *data) 
{ 
    char *type = of_get_flat_dt_prop(node, "device_type", NULL); 获取device_type属性值 
    __be32 *reg, *endp; 
    unsigned long l;
    在初始化的时候，我们会对每一个device node都要调用该call back函数，因此，我们要过滤掉那些和memory block定义无关的node。和memory block定义有的节点有两种，一种是node name是memory@形态的，另外一种是node中定义了device_type属性并且其值是memory。 
    if (type == NULL) { 
        if (depth != 1 || strcmp(uname, "memory@0") != 0) 
            return 0; 
    } else if (strcmp(type, "memory") != 0) 
        return 0;
    获取memory的起始地址和length的信息。有两种属性和该信息有关，一个是linux,usable-memory，不过最新的方式还是使用reg属性。
reg = of_get_flat_dt_prop(node, "linux,usable-memory", &l); 
    if (reg == NULL) 
        reg = of_get_flat_dt_prop(node, "reg", &l); 
    if (reg == NULL) 
        return 0;
    endp = reg + (l / sizeof(__be32));
reg属性的值是address，size数组，那么如何来取出一个个的address/size呢？由于memory node一定是root node的child，因此dt_root_addr_cells（root node的#address-cells属性值）和dt_root_size_cells（root node的#size-cells属性值）之和就是address，size数组的entry size。
    while ((endp - reg) >= (dt_root_addr_cells + dt_root_size_cells)) { 
        u64 base, size;
        base = dt_mem_next_cell(dt_root_addr_cells, ®); 
        size = dt_mem_next_cell(dt_root_size_cells, ®);
        early_init_dt_add_memory_arch(base, size);  将具体的memory block信息加入到内核中。 
    }
    return 0; 
}
```
3、interrupt controller的处理
初始化是通过start_kernel->init_IRQ->machine_desc->init_irq()实现的。我们用S3C2416为例来描述interrupt controller的处理过程。下面是machine描述符的定义。
```c
DT_MACHINE_START(S3C2416_DT, "Samsung S3C2416 (Flattened Device Tree)") 
…… 
    .init_irq    = irqchip_init, 
…… 
MACHINE_END
```
在driver/irqchip/irq-s3c24xx.c文件中定义了两个interrupt controller，如下：
```c
IRQCHIP_DECLARE(s3c2416_irq, "samsung,s3c2416-irq", s3c2416_init_intc_of);
IRQCHIP_DECLARE(s3c2410_irq, "samsung,s3c2410-irq", s3c2410_init_intc_of);
```
当然，系统中可以定义更多的irqchip，不过具体用哪一个是根据DTB中的interrupt controller node中的compatible属性确定的。在driver/irqchip/irqchip.c文件中定义了irqchip_init函数，如下：
```c
void __init irqchip_init(void) 
{ 
    of_irq_init(__irqchip_begin); 
}
```
_._irqchip_begin就是所有的irqchip的一个列表，of_irq_init函数是遍历Device Tree，找到匹配的irqchip。具体的代码如下：
```c
void __init of_irq_init(const struct of_device_id *matches) 
{ 
    struct device_node *np, *parent = NULL; 
    struct intc_desc *desc, *temp_desc; 
    struct list_head intc_desc_list, intc_parent_list;
    INIT_LIST_HEAD(&intc_desc_list); 
    INIT_LIST_HEAD(&intc_parent_list);
    遍历所有的node，寻找定义了interrupt-controller属性的node，如果定义了interrupt-controller属性则说明该node就是一个中断控制器。
    for_each_matching_node(np, matches) { 
        if (!of_find_property(np, "interrupt-controller", NULL) || 
                !of_device_is_available(np)) 
            continue; 
       
分配内存并挂入链表，当然还有根据interrupt-parent建立controller之间的父子关系。对于interrupt controller，它也可能是一个树状的结构。 
        desc = kzalloc(sizeof(*desc), GFP_KERNEL); 
        if (WARN_ON(!desc)) 
            goto err;
        desc->dev = np; 
        desc->interrupt_parent = of_irq_find_parent(np); 
        if (desc->interrupt_parent == np) 
            desc->interrupt_parent = NULL; 
        list_add_tail(&desc->list, &intc_desc_list); 
    }
    正因为interrupt controller被组织成树状的结构，因此初始化的顺序就需要控制，应该从根节点开始，依次递进到下一个level的interrupt controller。 
    while (!list_empty(&intc_desc_list)) {  intc_desc_list链表中的节点会被一个个的处理，每处理完一个节点就会将该节点删除，当所有的节点被删除，整个处理过程也就是结束了。 
         
        list_for_each_entry_safe(desc, temp_desc, &intc_desc_list, list) { 
            const struct of_device_id *match; 
            int ret; 
            of_irq_init_cb_t irq_init_cb;
            最开始的时候parent变量是NULL，确保第一个被处理的是root interrupt controller。在处理完root node之后，parent变量被设定为root interrupt controller，因此，第二个循环中处理的是所有parent是root interrupt controller的child interrupt controller。也就是level 1（如果root是level 0的话）的节点。
            if (desc->interrupt_parent != parent) 
                continue;
            list_del(&desc->list);      －－－－－从链表中删除 
            match = of_match_node(matches, desc->dev);－－－－－匹配并初始化 
            if (WARN(!match->data,－－－－－－－－－－match->data是初始化函数 
                "of_irq_init: no init function for %s\n", 
                match->compatible)) { 
                kfree(desc); 
                continue; 
            }
            irq_init_cb = (of_irq_init_cb_t)match->data; 
            ret = irq_init_cb(desc->dev, desc->interrupt_parent);－－－－－执行初始化函数 
            if (ret) { 
                kfree(desc); 
                continue; 
            }
           处理完的节点放入intc_parent_list链表，后面会用到 
            list_add_tail(&desc->list, &intc_parent_list); 
        }
        对于level 0，只有一个root interrupt controller，对于level 1，可能有若干个interrupt controller，因此要遍历这些parent interrupt controller，以便处理下一个level的child node。 
        desc = list_first_entry_or_null(&intc_parent_list, 
                        typeof(*desc), list); 
        if (!desc) { 
            pr_err("of_irq_init: children remain, but no parents\n"); 
            break; 
        } 
        list_del(&desc->list); 
        parent = desc->dev; 
        kfree(desc); 
    }
    list_for_each_entry_safe(desc, temp_desc, &intc_parent_list, list) { 
        list_del(&desc->list); 
        kfree(desc); 
    } 
err: 
    list_for_each_entry_safe(desc, temp_desc, &intc_desc_list, list) { 
        list_del(&desc->list); 
        kfree(desc); 
    } 
}
```
只有该node中有interrupt-controller这个属性定义，那么linux kernel就会分配一个interrupt controller的描述符（struct intc_desc）并挂入队列。通过interrupt-parent属性，可以确定各个interrupt controller的层次关系。在scan了所有的Device Tree中的interrupt controller的定义之后，系统开始匹配过程。一旦匹配到了interrupt chip列表中的项次后，就会调用相应的初始化函数。如果CPU是S3C2416的话，匹配到的是irqchip的初始化函数是s3c2416_init_intc_of。
OK，我们已经通过compatible属性找到了适合的interrupt controller，那么如何解析reg属性呢？我们知道，对于s3c2416的interrupt controller而言，其#interrupt-cells的属性值是4，定义为。每个域的解释如下：
（1）ctrl_num表示使用哪一种类型的interrupt controller，其值的解释如下：
      - 0 ... main controller 
      - 1 ... sub controller 
      - 2 ... second main controller
（2）parent_irq。对于sub controller，parent_irq标识了其在main controller的bit position。
（3）ctrl_irq标识了在controller中的bit位置。
（4）type标识了该中断的trigger type，例如：上升沿触发还是电平触发。
为了更顺畅的描述后续的代码，我需要简单的介绍2416的中断控制器，其block diagram如下：
![](http://ww1.sinaimg.cn/large/ba061518gw1f5tawr9fptg20hs085glp.gif)
53个Samsung2416的中断源被分成两种类型，一种是需要sub寄存器进行控制的，例如DMA，系统中的8个DMA中断是通过两级识别的，先在SRCPND寄存器中得到是DMA中断的信息，具体是哪一个channel的DMA中断需要继续查询SUBSRC寄存器。那些不需要sub寄存器进行控制的，例如timer，5个timer的中断可以直接从SRCPND中得到。 
中断MASK寄存器可以控制产生的中断是否要报告给CPU，当一个中断被mask的时候，虽然SRCPND寄存器中，硬件会set该bit，但是不会影响到INTPND寄存器，从而不会向CPU报告该中断。对于SUBMASK寄存器，如果该bit被set，也就是该sub中断被mask了，那么即便产生了对应的sub中断，也不会修改SRCPND寄存器的内容，只是修改SUBSRCPND中寄存器的内容。
不过随着硬件的演化，更多的HW block加入到SOC中，这使得中断源不够用了，因此中断寄存器又被分成两个group，一个是group 1（开始地址是0X4A000000，也就是main controller了），另外一个是group2（开始地址是0X4A000040，叫做second main controller）。group 1中的sub寄存器的起始地址是0X4A000018（也就是sub controller）。
了解了上面的内容后，下面的定义就比较好理解了：

```c
static struct s3c24xx_irq_of_ctrl s3c2416_ctrl[] = { 
    { 
        .name = "intc", －－－－－－－－－－－main controller 
        .offset = 0, 
    }, { 
        .name = "subintc", －－－－－－－－－sub controller 
        .offset = 0x18, 
        .parent = &s3c_intc[0], 
    }, { 
        .name = "intc2", －－－－－－－－－－second main controller 
        .offset = 0x40, 
    } 
};
```
对于s3c2416而言，irqchip的初始化函数是s3c2416_init_intc_of，s3c2416_ctrl作为参数传递给了s3c_init_intc_of，大部分的处理都是在s3c_init_intc_of函数中完成的，由于这个函数和中断子系统非常相关，这里就不详述了，后续会有一份专门的文档描述之。
4、GPIO controller的处理
暂不描述，后续会有一份专门的文档描述GPIO sub system。
5、machine初始化
machine初始化的代码可以沿着start_kernel->rest_init->kernel_init->kernel_init_freeable->do_basic_setup->do_initcalls路径寻找。在do_initcalls函数中，kernel会依次执行各个initcall函数，在这个过程中，会调用customize_machine，具体如下：
```c
static int __init customize_machine(void) 
{ 

    if (machine_desc->init_machine) 
        machine_desc->init_machine(); 
    else 
        of_platform_populate(NULL, of_default_bus_match_table, NULL, NULL); 

    return 0; 
} 
arch_initcall(customize_machine);
```
在这个函数中，一般会调用machine描述符中的init_machine callback函数来把各种Device Tree中定义的platform device设备节点加入到系统（即platform bus的所有的子节点，对于device tree中其他的设备节点，需要在各自bus controller初始化的时候自行处理）。如果machine描述符中没有定义init_machine函数，那么直接调用of_platform_populate把所有的platform device加入到kernel中。对于s3c2416，其machine描述符中的init_machine callback函数就是s3c2416_dt_machine_init，代码如下：
```c
static void __init s3c2416_dt_machine_init(void) 
{ 
    of_platform_populate(NULL, --------传入NULL参数表示从root node开始scan
of_default_bus_match_table, s3c2416_auxdata_lookup, NULL);
    s3c_pm_init(); －－－－－－－－power management相关的初始化 
}
```
由此可见，最终生成platform device的代码来自of_platform_populate函数。该函数的逻辑比较简单，遍历device node global list中所有的node，并调用of_platform_bus_create处理，of_platform_bus_create函数代码如下：
```c
static int of_platform_bus_create(struct device_node *bus,-------------要创建的那个device node 
                  const struct of_device_id *matches,-------要匹配的list 
                  const struct of_dev_auxdata *lookup,------附属数据 
                  struct device *parent, bool strict)---------------parent指向父节点。strict是否要求完全匹配 
{ 
    const struct of_dev_auxdata *auxdata; 
    struct device_node *child; 
    struct platform_device *dev; 
    const char *bus_id = NULL; 
    void *platform_data = NULL; 
    int rc = 0;
删除确保device node有compatible属性的代码。
    auxdata = of_dev_lookup(lookup, bus);  在传入的lookup table寻找和该device node匹配的附加数据 
    if (auxdata) { 
        bus_id = auxdata->name;-----------------如果找到，那么就用附加数据中的静态定义的内容 
        platform_data = auxdata->platform_data; 
    }
ARM公司提供了CPU core，除此之外，它设计了AMBA的总线来连接SOC内的各个block。符合这个总线标准的SOC上的外设叫做ARM Primecell Peripherals。如果一个device node的compatible属性值是arm,primecell的话，可以调用of_amba_device_create来向amba总线上增加一个amba device。
    if (of_device_is_compatible(bus, "arm,primecell")) { 
        of_amba_device_create(bus, bus_id, platform_data, parent); 
        return 0; 
    }
    如果不是ARM Primecell Peripherals，那么我们就需要向platform bus上增加一个platform device了
    dev = of_platform_device_create_pdata(bus, bus_id, platform_data, parent); 
    if (!dev || !of_match_node(matches, bus)) 
        return 0;
    一个device node可能是一个桥设备，因此要重复调用of_platform_bus_create来把所有的device node处理掉。
    for_each_child_of_node(bus, child) { 
        pr_debug("   create child: %s\n", child->full_name); 
        rc = of_platform_bus_create(child, matches, lookup, &dev->dev, strict); 
        if (rc) { 
            of_node_put(child); 
            break; 
        } 
    } 
    return rc; 
}
```
具体增加platform device的代码在of_platform_device_create_pdata中，代码如下：
```c
static struct platform_device *of_platform_device_create_pdata( 
                    struct device_node *np, 
                    const char *bus_id, 
                    void *platform_data, 
                    struct device *parent) 
{ 
    struct platform_device *dev;
    if (!of_device_is_available(np))---------check status属性，确保是enable或者OK的。 
        return NULL;
    of_device_alloc除了分配struct platform_device的内存，还分配了该platform device需要的resource的内存（参考struct platform_device 中的resource成员）。当然，这就需要解析该device node的interrupt资源以及memory address资源。
    dev = of_device_alloc(np, bus_id, parent); 
    if (!dev) 
        return NULL;
设定platform_device 中的其他成员 
    dev->dev.coherent_dma_mask = DMA_BIT_MASK(32); 
    if (!dev->dev.dma_mask) 
        dev->dev.dma_mask = &dev->dev.coherent_dma_mask; 
    dev->dev.bus = &platform_bus_type; 
    dev->dev.platform_data = platform_data;
    if (of_device_add(dev) != 0) {------------------把这个platform device加入统一设备模型系统中 
        platform_device_put(dev); 
        return NULL; 
    }
    return dev; 
}
```
