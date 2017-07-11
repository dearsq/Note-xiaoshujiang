---
title: [Linux] 中的阻塞与非阻塞（等待队列、轮询）
tags: Linux
grammar_cjkRuby: true
---
[TOC]

## 基本概念
**阻塞**指执行设备操作时，不能获得资源则挂起进程，被挂起的进程进入休眠，从调度器的进行队列中移走。
**非阻塞**指在不能获得资源的情况下，要么放弃，要么不停地查询，直到可以操作。

## 等待队列（Wait Queue）
Linux 中采用**等待队列**来实现阻塞进程的唤醒。
**等待队列**以队列为基础数据结构，结合进程调度机制，用来同步对系统资源的访问。
### 1. 定义等待队列头
```
wait_queue_head_t my_queue;
```
### 2.初始化等待队列头
```
init_waitqueue_head(&my_queue);
//或者
DECLAR_WAIT_QUEUE_HEAD(name)
```
### 3.定义等待队列元素
```
DECLARE_WAITQUEUE(name,tsk)
```
### 4.添加/移除等待队列
```
//将等待队列元素 wait 添加到等待队列头 q 指向的双向链表中
void add_wait_queue(wait_queue_head_t *q, wait_queue_t *wait);
//将等待队列元素 wait 从由 q 头部指向的链表中移除
void remove_wait_queue(wait_queue_head_t *q, wait_queue_t *wait);
```
### 5.等待事件
```
//等待队列头 queue 被唤醒
//condition 必须满足，否则继续阻塞
wait_event(queue,condition)	
wait_event_interruptible(queue, condition)				//可以被信号唤醒
wait_event_timeout(queue, condition, timeout)		//timeout 为阻塞等待超时时间, jiffy 为单位
wait_event_interruptible_timeout(queue, condition, timeout)
```
### 6.唤醒队列
```
void wake_up(wait_queue_head_t *queue);
void wake_up_interruptible(wait_queue_head_t *queue);
```
上述操作会唤醒以 queue 作为等待队列头部的队列中的所有进程。
wake_up 可以唤醒处于 TASK_INTERRUPTIBLE 和 TASK_UNINTERRUPTIBLE 的进程。
wake_up_interruptible 只能唤醒处于 TASK_INTERRUPTIBLE 的进程。
### 7.在等待队列上睡眠
```-
sleep_on(wait_queue_head_t *q);
interruptible_sleep_on(wait_queue_head_t *q);
```
## 轮询
### select()+poll() 或 epoll
```
/*
	readfds、writefds、 exceptfds 是监视的 读、写、异常处理的文件描述符集合
    numfs 是需要检查的号码的最高值+1
    readfds 如果有任何文件变得可读  或者  writefds 如果有任何文件变得可写，select() 就会返回
*/
int select(int numfs, fd_set *readfds, fd_set *writefds, fd_set *exceptfds, struct timeval *timeout)
```
```
FD_ZERO(fd_set *set)  //清除
FD_SET(int fd, fd_set *set) //添加
FD_CLR(int fd, fd_set *set) //删除
FD_ISSET(int fd,fd_set *set) //判断是否被置为
```
```
int poll(struct pollfd *fds, nfds_t nfds, int timeout);
```
但是我们一般用 epoll()
```
//1.  创建 epoll 句柄（返回文件描述符 epfd），size 是内核要监听的 fd 的个数
int epoll_create(int size);
//2.  监听事件类型
int epoll_ctl(int epfd, int op, int fd, struct epoll_event *event);
/* op:
 EPOLL_CTL_ADD 添加
 EPOLL_CTL_MOD 修改
 EPOLL_CTL_DEL  删除
   event:
 EPOLLIN 可读
 EPOLLOUT 可写
 EPOLLPRI 紧急可读（有 socket 带外数据到来）
 EPOLLERR fd 发生错误
 EPOLLHUP fd 被挂断
 EPOLLET 设置为边缘触发（高速模式：如果 fd 从未就绪变为就绪，内核通过 epoll 告诉用户，一次就绪通知）
 EPOLLONESHOT 一次性监听（监听完后不再监听）
*/
//3. 等待事件发生
int epoll_wait(int epfd, struct epoll_event *events, int maxevents, int timeout);
events 输入
maxevents 表示个数 < epoll_create 创建时的 size
timeout 超时时间 0 立即 -1 永久
```

### 设备驱动中的 poll() 模板
见实例

## 实例
### 等待队列
```
static ssize_t xxx_write(struct file *file, const char *buffer, size_t count, loff_t *ppos)
{
	...
	DECLARE_WAITQUEUE(wait, current);	/* 定义等待队列元素 */
	add_wait_queue( &xxx_wait , &wait);	/* 添加元素 wait 到等待队列 xxx_wait */

	/* 等待设备缓冲区可写 */
	do{
		avail = device_writable(...);
		if( avail < 0){
			if(file->f_flags & O_NONBLOCK)	//是非阻塞
			{
				ret = -EAGAIN;
				goto out;
			}
			__set_current_state(TASK_INTERRUPTIBLE); /* 改变进程状态 */
			schedule();							/* 调度其他进程执行 */
			if(signal_pending(current)) 		/* 如果是因为信号唤醒*/
			{
				ret = -ERESTARTSYS;
				goto out;
			}
		}
	} while( avail < 0);

	/* 写设备缓冲区 */
	device_write(...);
out:
	remove_wait_queue(&xxx_wait, &wait);
	set_current_sate(TASK_RUNNING);
	return ret;
}
```

### 轮询
```
#include <sys/select.h>
#include <sys/time.h>
#include <sys/types.h>
#include <unistd.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <stdio.h>

#define FIFO_CLEAR 0x1
#define BUFFER_LEN 20
void main(void)
{
	int fd, num;
	char rd_ch[BUFFER_LEN];
	fd_set rfds, wfds;	/* 读/写文件描述符集 */

	/* 以非阻塞方式打开/dev/globalfifo设备文件 */
	fd = open("/dev/globalfifo", O_RDONLY | O_NONBLOCK);
	if (fd != -1) {
		/* FIFO清0 */
		if (ioctl(fd, FIFO_CLEAR, 0) < 0)
			printf("ioctl command failed\n");

		while (1) {
			FD_ZERO(&rfds);						//FD_ZERO 清除文件描述符合集
			FD_ZERO(&wfds);
			FD_SET(fd, &rfds);					//FD_SET 将 fd 加入合集中
			FD_SET(fd, &wfds);

			select(fd + 1, &rfds, &wfds, NULL, NULL);
			/* 数据可获得 */
			if (FD_ISSET(fd, &rfds))
				printf("Poll monitor:can be read\n");
			/* 数据可写入 */
			if (FD_ISSET(fd, &wfds))
				printf("Poll monitor:can be written\n");
		}
	} else {
		printf("Device open failure\n");
	}
}

```






