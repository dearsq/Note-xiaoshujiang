---
title: LinuxC中的mem操作
tags: Linux
grammar_cjkRuby: true
---
[TOC]

## 概述
头文件 string.h
* memcpy、memmove 拷贝一定长度mem内容
* memset buffer填充工作
* memchr 字符查找
* memcmp 比较mem中buffer大小

## 详述
### memcpy 拷贝内存，不可重叠
**定义：**
```c
void *memcpy(void *dst,const void *src,size_t n)
```
**作用：**
拷贝 src 所指向的内存内容的前 n 个字节到 dst 所指向的内存地址上。
返回指向 dst 的指针。
另外 src 和 dst 指向的 内存区域 **不可重叠**。
**区别于 strcpy 的不同是：**
memcpy 完成 n 个字节的复制。
strcpy 遇到 \0 字符才结束。
```c
#include<iostream>
#include<string.h>
using namespace std;
int main()
{
    int a[10] = {0};
    for (int i = 0; i < 10; i++)
        a[i] = i;
    memcpy(&a[4],a,sizeof(int)*6);
    //memmove(&a[4], a, sizeof(int) * 6);
    for (int i = 0; i < 10; i++)
        cout << a[i];
    getchar();
    return 0;
}
```
输出 0123012301 

### memmove 拷贝内存，可重叠
**定义：**
```c
void* memmove(void* dst,const void* src,size_t n)
```
**作用：**
与memcpy()一样都是用来拷贝src所指的内存前n个字节到dst所指的内存上。
不同的是，当src和dest所指的内存区域重叠时，memmove仍然可以正确的处理，不过执行效率上会比memcpy略慢。
src 与 dst 的区域**可以重叠**。
**从高地址拷到低地址，和从低地址拷到高地址 是不同的。**
### memset 批处理
**定义：**
```c
void* memset(void *s,int ch,size_t n)
```
**作用：**
将 s 中前 n 个字节用 ch 替换并返回 s 。

### memchr 查找内存中的某个字符
**定义：**
```c
extern void* memchr(const void* buf,int ch,size_t count)
```
**作用：**
从 buf 所指内存区的前 count 个字节查找字符 ch，当第一次遇到字符 ch 时停止查找。如果成功，返回指向字符 ch 的指针；
否则返回 null。

### memcmp 内存中字节比较
**定义：**
```c
int memcmp(const void* buf1,const void* buf2,unsigned int count)
```
**作用：**
比较buf1和buf2的前count个字节
返回值：当buf1 < buf2 时，返回值 < 0
　　　　当buf1 == buf2时，返回值 = 0
　　　　当buf1 > buf2时，返回值 > 0
## 实现
### memcpy
```c
/**
 * memcpy - Copy one area of memory to another
 * @dest: Where to copy to
 * @src: Where to copy from
 * @count: The size of the area.
 *
 * You should not use this function to access IO space, use memcpy_toio()
 * or memcpy_fromio() instead.
 */
void * memcpy(void * dest,const void *src,size_t count)
{
    char *tmp = (char *) dest, *s = (char *) src;
    while (count--)
        *tmp++ = *s++;
    return dest;
}
```
### memmove
```c
/* Normally compiler builtins are used, but sometimes the compiler calls out
   of line code. Based on asm-i386/string.h.
 */
#define _STRING_C
#include <linux/string.h>
#undef memmove
void *memmove(void * dest,const void *src,size_t count)
{
    if (dest < src) { 
        __inline_memcpy(dest,src,count);
    } else {
        char *p = (char *) dest + count;
        char *s = (char *) src + count;
        while (count--)
            *--p = *--s;
    }
    return dest;
}
```
### memset
```c
void *(memset) (void *s,int c,size_t n)
{
    const unsigned char uc = c;
    unsigned char *su;
    for(su = s;0 < n;++su,--n)
        *su = uc;
    return s;
}
```
### memchr
```c
void *memchr (const void *ptr, int value, int num)
{
	if (ptr == NULL)
    {
        perror("ptr");
        return NULL;
    }
	char * p = (char *)ptr;
	while (num--)
    {
        if (*p != (char)value)
            p++;
        else
            return p;
	}
	return NULL;
}
```

### memcmp
```c
/*  因为类型可以为任意，所以形参应为void * 
 *  相等则返回0，否则不为0 
 */  
int my_memcmp(const void *s1,const void *s2,size_t count)  
{  
    int res = 0;  
    const unsigned char *p1 =(const unsigned char *)s1;//注意是unsigned char *  
    const unsigned char *p2 =(const unsigned char *)s2;   
    for(p1 ,p2;count > 0;p1++,p2++,count--)  
        if((res =*p1 - *p2) != 0)   //不相当则结束比较  
            break;  
    return res;  
}
```