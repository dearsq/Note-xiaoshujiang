---
title: [Android] init.rc 文件浅析
tags: Android,rc
grammar_cjkRuby: true
---
Wiki：UNIX 世界，rc 经常被用作程序之启动脚本的文件名。它是“run commands”（运行命令）的缩写。
我们以 init.rc 来入手，学习 rc 的用法。
## AIL 
对于 init.rc 文件，Android 有特定的格式及规则。我们称之为初始化语言 AIL（Android Init Language）
init.rc 基本单位是 section（区块）。
section 有三种类型：
1. on
2. service
3. import

还有一种 options 的选项表示对 service 的描述。

### **on 类型**
on 类型 表示一系列的命令组合，
语法：
```AIL
on <trigger>
        <command>
		<command>
		...
```
eg：
```bash
on init
    mkdir /productinfo 0771 system system
    # SPRD: modify for storage manage @{
    mount tmpfs tmpfs /storage mode=0751,gid=1028
    # @}
    mkdir /mnt/media_rw/sdcard0 0700 media_rw media_rw
    mkdir /storage/sdcard0 0700 root root
    mkdir /mnt/shell/emulated 0700 shell shell
    mkdir /storage/emulated 0555 root root

    # SPRD: move this to board level init @{
    #export EXTERNAL_STORAGE /storage/emulated/legacy
    #export SECONDARY_STORAGE /storage/sdcard0
    # @}
    # SPRD: for storage manage @{
    export LEGACY_STORAGE /storage/emulated/legacy
    # @}
```
这样一个 section 里面包含了多个命令。命令的执行是以 section 为单位的。
上面这些命令都会一起顺序执行，不会单独执行。
他们的执行由 init.c 的 main() 决定。在当其中调用  
```c
action_for_each_trigger("init",action_add_queue_tail);
```
时，就将 on init 开始的这样一个 section 里所有的命令加入到一个执行队列，在未来某个时候会顺序执行队列里的命令。

### **service 类型**
service 类型 的 section 表示一个可执行的程序，
```AIL
service <name> <pathname> [<argument>]*
        <option>
		<option>
		...
```
e.g.：
```
service poweroffalarm /system/bin/poweroff_alarm
    disabled
    oneshot
```
poweroffalarm 作为一个名字标识了这个 service，这个可执行程序的位置在 /system/bin/poweroff_alarm。
下面的 disable、oneshot 被称为 options，options 是用来描述的 service 的特点，不同的 service 有不同的 options。
service 的执行时间是在 class_start 这个命令被执行的时候，这个命令总存在于某个 on 类型的section 中。
比如 class_start core 被执行，则会启动所有类型为 core 的 service。
e.g.：
```
service yo_service1 /system/bin/yo_service1
	class core
    user system
    disabled
    group system radio shell
    oneshot

on yo_fs
	class_start core
```
其中 yo_service1 这个 service 的类型是 core。
在 yo_fs 被调用的时候则将会 class_start 而执行所有 类型为 core 的 service。

### import 类型
**import 类型**表示包含了另外一些 section，在解析完 init.rc 后会继续调用 init_parse_config_file 来解析引入的 .rc 文件。
eg：
比如我们在 init.sc8830.rc 的开始可以看到
```
import /init.board.rc
import /init.sc8830.usb.rc
```
表示在运行完本 rc 后还将继续运行 init.board.rc 和 init.sc8830.usb.rc。

## init.rc 文件解析过程
解析 init.rc 的过程就是识别一个个 section 的过程。
在 init.c 中的 main() 中去执行一个个命令。
（android采用双向链表来存储section的信息，解析完成之后，会得到三个双向链表action_list、service_list、import_list来分别存储三种section的信息上。）

1. system/core/init/init.c
在 init.c 中调用     
```
init_parse_config_file("/init.rc");
```
其代码实现如下：
```
int init_parse_config_file(const char *fn)
{
    char *data;
    data = read_file(fn, 0);        //read_file()调用open\lseek\read 将init.rc读出来
    if (!data) return -1;
 
    parse_config(fn, data);        //调用parse_config开始解析
    DUMP();
    return 0;
}
```
2. parse_config() 代码：
```
static void parse_config(const char *fn, char *s)
{
    struct parse_state state;
    struct listnode import_list;
    struct listnode *node;
    char *args[INIT_PARSER_MAXARGS];
    int nargs;
 
    nargs = 0;
    state.filename = fn;	//文件名
    state.line = 0;
    state.ptr = s;				//文字指针
    state.nexttoken = 0;
    state.parse_line = parse_line_no_op;
 
    list_init(&import_list);
    state.priv = &import_list;
 
    for (;;) {
        switch (next_token(&state)) {                         //next_token()根据从state.ptr开始遍历
        case T_EOF:                               					//遍历到文件结尾，然后goto解析import的.rc文件
            state.parse_line(&state, 0, 0);
            goto parser_done;
        case T_NEWLINE:                                         //到了一行结束
            state.line++;
            if (nargs) {
                int kw = lookup_keyword(args[0]);      //找到这一行的关键字
                if (kw_is(kw, SECTION)) {                        //如果这是一个section的第一行                                            
                    state.parse_line(&state, 0, 0);
                    parse_new_section(&state, kw, nargs, args);
                } else {                                                   //如果这不是一个section的第一行
                    state.parse_line(&state, nargs, args);
                }
                nargs = 0;
            }
            break;
        case T_TEXT:                                                   //遇到普通字符
            if (nargs < INIT_PARSER_MAXARGS) {
                args[nargs++] = state.text;
            }
            break;
        }
    }
parser_done:
    list_for_each(node, &import_list) {
         struct import *import = node_to_item(node, struct import, list);
         int ret;
 
         INFO("importing '%s'", import->filename);
         ret = init_parse_config_file(import->filename);
         if (ret)
             ERROR("could not import file '%s' from '%s'\n",
                   import->filename, fn);
    }
}
```
next_token() 解析完 init.rc 中一行之后，
会返回T_NEWLINE，这时调用 lookup_keyword 函数来找出这一行的关键字, lookup_keyword返回的是一个整型值，对应keyword_info[]数组的下标，keyword_info[]存放的是keyword_info结构体类型的数据，
 ```
struct {
    const char *name;                                          //关键字的名称
    int (*func)(int nargs, char **args);            //对应的处理函数
    unsigned char nargs;                                //参数个数
    unsigned char flags;                                 //flag标识关键字的类型,
                                                                                   包括COMMAND、OPTION、SECTION
} keyword_info
 ```
因此keyword_info[]中存放的是所有关键字的信息，每一项对应一个关键字。
根据每一项的flags就可以判断出关键字的类型，如新的一行是SECTION，就调用parse_new_section()来解析这一行,
如新的一行不是一个SECTION的第一行，那么调用state.parseline()来解析(state.parseline所对应的函数会根据section类型的不同而不同)，在parse_new_section()中进行动态设置。
 
三种类型的section: service、on、import,  
service对应的state.parseline为parse_line_service,
on对应的state.parseline为parse_line_action,
import section中只有一行所以没有对应的state.parseline。






