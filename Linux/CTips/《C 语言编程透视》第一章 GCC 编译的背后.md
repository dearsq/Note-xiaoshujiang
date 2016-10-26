---
title: 《C 语言编程透视》第一章 GCC 编译的背后
tags: 
grammar_cjkRuby: true
---
[TOC]

预处理、编译、汇编、链接
-E，-S，-c 和 -O
cpp，cc1，as，ld

## 预处理
完成任务：预处理命令处理、头文件的包含、宏定义的拓展、条件编译的选择
-E
```
gcc -E hello.c
```

在命令行定义宏：
```
gcc -DDEBUG hello.c
```
等于
```
 #define DEBUG
 ```
 
 
## 编译（翻译）
完成任务：词法分析、语法分析、源码翻译为汇编代码
-S
```
$ gcc -S hello.c
```
编译器优化
```
$ gcc -o hello hello.c         # 采用默认选项，不优化
$ gcc -O2 -o hello2 hello.c    # 优化等次是2
$ gcc -Os -o hellos hello.c    # 优化目标代码的大小
```
大小： hellos < hello2 < hello
执行速度：hellos > hello2 > hello

## 汇编
完成任务：汇编代码翻译成机器代码（目标代码）
-c
```
gcc -c hello.s  #会生成hello.o

$ file hello.s
hello.s: ASCII assembler program text
$ gcc -c hello.s   #用gcc把汇编语言编译成目标代码
$ file hello.o     #file命令用来查看文件类型，目标代码可重定位的(relocatable)，
                   #需要通过ld进行进一步链接成可执行程序(executable)和共享库(shared)
hello.o: ELF 32-bit LSB relocatable, Intel 80386, version 1 (SYSV), not stripped
$ as -o hello.o hello.s        #用as把汇编语言编译成目标代码
$ file hello.o
hello.o: ELF 32-bit LSB relocatable, Intel 80386, version 1 (SYSV), not stripped
```
gcc 和 as 默认产生的目标代码都是 ELF 格式

### ELF文件
了解目标代码，区分三种类型  relocatable（可重定位）、executable（可执行）、shared libarary（共享库）的不同。
我们需要工具，bjdump，objcopy，nm，strip 或者 readelf。
```
ELF Header(ELF文件头)
Program Headers Table(程序头表，实际上叫段表好一些，用于描述可执行文件和可共享库)
Section 1
Section 2
Section 3
...
Section Headers Table(节区头部表，用于链接可重定位文件成可执行文件或共享库)
```
对于可重定位文件，程序头是可选的，而对于可执行文件和共享库文件（动态链接库），节区表则是可选的。
可以分别通过 readelf 文件的 -h，-l 和 -S 参数查看 ELF 文件头（ELF Header）、程序头部表（Program Headers Table，段表）和节区表（Section Headers Table）
### ELF文件头
文件头说明了文件的类型，大小，运行平台，节区数目等。
写一个小工程，三个文件来测试
```
/* myprintf.c */
#include <stdio.h>
void myprintf(void)
{
    printf("hello, world!\n");
}

/* test.h -- myprintf function declaration */
#ifndef _TEST_H_
#define _TEST_H_

void myprintf(void);
#endif

/* test.c */
#include "test.h"
int main()
{
    myprintf();
    return 0;
}
```
 
 test.o 类型是 REL（可重定位文件）
 myprintf.o 类型是 REL（可重定位文件） 
 test 类型是 EXEC（可执行文件）
 
 **ar 创建静态链接库**
 ar rcsv libmyprintf.a myprintf.o
 libmyprintf.a  类型也是 REL（可重定位文件）
.a 静态库可以是多个 REL 文件的集合
 
 **创建动态链接库**
 gcc myprintf.c -fPIC -shared -o libmyprintf.so
 libmyprintf.so 类型是 DYN（共享目标文件）
 
 ### ELF主体：节区（Section）
 ELF 文件中
 **文件头** 组织整个文件总体结构
 **节区表** 描述可重定位文件
 **程序头（段表）**描述可执行文件
 可重定位文件中 ，节区表描述的是其节区本身;
 可执行文件中，程序头描述的是由各个节区组成的段。

```
$ gcc -c myprintf.c
$ readelf -S myprintf.o	//节区表

There are 11 section headers, starting at offset 0xc0:

Section Headers:
  [Nr] Name              Type            Addr     Off    Size   ES Flg Lk Inf Al
  [ 0]                   NULL            00000000 000000 000000 00      0   0  0
  [ 1] .text             PROGBITS        00000000 000034 000018 00  AX  0   0  4
  [ 2] .rel.text         REL             00000000 000334 000010 08      9   1  4
  [ 3] .data             PROGBITS        00000000 00004c 000000 00  WA  0   0  4
  [ 4] .bss              NOBITS          00000000 00004c 000000 00  WA  0   0  4
  [ 5] .rodata           PROGBITS        00000000 00004c 00000e 00   A  0   0  1
  [ 6] .comment          PROGBITS        00000000 00005a 000012 00      0   0  1
  [ 7] .note.GNU-stack   PROGBITS        00000000 00006c 000000 00      0   0  1
  [ 8] .shstrtab         STRTAB          00000000 00006c 000051 00      0   0  1
  [ 9] .symtab           SYMTAB          00000000 000278 0000a0 10     10   8  4
  [10] .strtab           STRTAB          00000000 000318 00001a 00      0   0  1
Key to Flags:
  W (write), A (alloc), X (execute), M (merge), S (strings)
  I (info), L (link order), G (group), x (unknown)
  O (extra OS processing required) o (OS specific), p (processor specific)
```

**objdump -d 看反编译结果，-j 看指定节区**
```
$ objdump -d -j .text   myprintf.o
myprintf.o:     file format elf32-i386

Disassembly of section .text:

00000000 <myprintf>:
   0:   55                      push   %ebp
   1:   89 e5                   mov    %esp,%ebp
   3:   83 ec 08                sub    $0x8,%esp
   6:   83 ec 0c                sub    $0xc,%esp
   9:   68 00 00 00 00          push   $0x0
   e:   e8 fc ff ff ff          call   f <myprintf+0xf>
  13:   83 c4 10                add    $0x10,%esp
  16:   c9                      leave
  17:   c3                      ret
```
**用 -r 选项可以看到有关重定位的信息**
```
$ readelf -r myprintf.o

Relocation section '.rel.text' at offset 0x334 contains 2 entries:
 Offset     Info    Type            Sym.Value  Sym. Name
0000000a  00000501 R_386_32          00000000   .rodata
0000000f  00000902 R_386_PC32        00000000   puts
# R_386_32 和 R_386_PC32 是重定位类型，根据类型来进行重新定位
```

**.rodata 节区包含只读数据，即我们要打印的 hello,world! **
```
$ readelf -x .rodata myprintf.o

Hex dump of section '.rodata':
  0x00000000 68656c6c 6f2c2077 6f726c64 2100     hello, world!.
```
**.data 节区无内容, 它应该包含一些初始化的数据**
```
$ readelf -x .data myprintf.o

Section '.data' has no data to dump.
```

**.bss节区无内容，它应该包含未初始化的数据，默认初始为 0**
```
$ readelf -x .bss       myprintf.o

Section '.bss' has no data to dump.
```
**.comment 是一些注释，可以看到是是 Gcc 的版本信息 **
```
$ readelf -x .comment myprintf.o

Hex dump of section '.comment':
  0x00000000 00474343 3a202847 4e552920 342e312e .GCC: (GNU) 4.1.
  0x00000010 3200    
```

**.note.GNU-stack 这个节区也没有内容**
```
$ readelf -x .note.GNU-stack myprintf.o

Section '.note.GNU-stack' has no data to dump.
```

**.shstrtab 包括所有节区的名字**
```
$ readelf -x .shstrtab myprintf.o

Hex dump of section '.shstrtab':
  0x00000000 002e7379 6d746162 002e7374 72746162 ..symtab..strtab
  0x00000010 002e7368 73747274 6162002e 72656c2e ..shstrtab..rel.
  0x00000020 74657874 002e6461 7461002e 62737300 text..data..bss.
  0x00000030 2e726f64 61746100 2e636f6d 6d656e74 .rodata..comment
  0x00000040 002e6e6f 74652e47 4e552d73 7461636b ..note.GNU-stack
  0x00000050 00
```
**.symtab 包括所有用到的相关符号信息**
```
$ readelf -symtab myprintf.o

Symbol table '.symtab' contains 10 entries:
   Num:    Value  Size Type    Bind   Vis      Ndx Name
     0: 00000000     0 NOTYPE  LOCAL  DEFAULT  UND
     1: 00000000     0 FILE    LOCAL  DEFAULT  ABS myprintf.c
     2: 00000000     0 SECTION LOCAL  DEFAULT    1
     3: 00000000     0 SECTION LOCAL  DEFAULT    3
     4: 00000000     0 SECTION LOCAL  DEFAULT    4
     5: 00000000     0 SECTION LOCAL  DEFAULT    5
     6: 00000000     0 SECTION LOCAL  DEFAULT    7
     7: 00000000     0 SECTION LOCAL  DEFAULT    6
     8: 00000000    24 FUNC    GLOBAL DEFAULT    1 myprintf
     9: 00000000     0 NOTYPE  GLOBAL DEFAULT  UND puts
```
**字符串表 .strtab 包含用到的字符串，包括文件名、函数名、变量名等**
```
$ readelf -x .strtab myprintf.o

Hex dump of section '.strtab':
  0x00000000 006d7970 72696e74 662e6300 6d797072 .myprintf.c.mypr
  0x00000010 696e7466 00707574 7300              intf.puts.
```


### 汇编语言文件中的节区表述
```
$ gcc -S myprintf.c
$ cat myprintf.s
        .file   "myprintf.c"
        .section        .rodata
.LC0:
        .string "hello, world!"
        .text
.globl myprintf
        .type   myprintf, @function
myprintf:
        pushl   %ebp
        movl    %esp, %ebp
        subl    $8, %esp
        subl    $12, %esp
        pushl   $.LC0
        call    puts
        addl    $16, %esp
        leave
        ret
        .size   myprintf, .-myprintf
        .ident  "GCC: (GNU) 4.1.2"
        .section        .note.GNU-stack,"",@progbits
```

## 链接





