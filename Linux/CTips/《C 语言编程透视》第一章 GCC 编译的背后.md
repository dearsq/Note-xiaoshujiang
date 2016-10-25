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
 文件头 组织整个文件总体结构
 节区表和段表 描述可重定位文件和可执行文件
 可重定位文件中


