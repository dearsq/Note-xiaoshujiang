---
title: [OpenGL]一些基本概念和基于状态的方法
tags: OpenGL
grammar_cjkRuby: true
---
Platform: Ubuntu16.04
IDE: QT5
Tools: OpenGL3

[TOC]


## 前言——基于状态

在写 OpenGL 的 “Hello World” （三角形） 的时候，非常困扰！gen、bind、active、 都不知道自己是在干什么。
后来查到 OpenGL 和 C++、C# 等面向对象的语言不通，OpenGL 大多数函数使用的是 **基于状态** 的方法。

即 **大多数OpenGL对象都需要在使用前把该对象绑定到context上**。

### Context 
顾名思义，就好像一篇文章的上下文**上下文**。
可以把它理解成 包含了所有 **OpenGL 状态**的对象。

### OpenGL 对象
可以把 OpenGL对象 理解成一个状态的集合。（其实还包括其他的数据，但是我们这里只关注状态）
但是 OpenGL对象 的状态  和 Context 的状态并不重合， 只有当 OpenGL对象  绑定（bind）到 context 上时，OpenGL对象 的状态才会映射到 Context 的状态。
绑定（bind）后，如果我们改变 Context 状态，这个 OpenGL对象 也会被影响。
绑定（bind）后，这些依赖 Context 状态的函数，也将会使用存储在这个 OpenGL对象 上的数据。

OpenGL 对象包含以下一些类型：Buffer Objects，Vertex Array Objects，Textures，Framebuffer Objects等等。
我们等下会讲到Vertex Array Objects这个对象。

这些对象有三个重要的函数：

```cpp
void glGen*(GLsizei n, GLuint *objects);   //负责生成一个对象的name。而name就是这个对象的引用。

void glDelete*(GLsizei n, const GLuint *objects);   //负责销毁一个对象。

void glBind*(GLenum target, GLuint object);  	//将对象绑定到context上。
```

### 图形名词

#### **像素（pixel）**
像素是我们显示器上的最小可见元素。我们系统中的像素被存储在一个帧缓存（framebuffer）中。帧缓存是一块由图形硬件管理的内存空间，用于供给给我们的显示设备。

#### **模型（Models）/ 对象（Objects）**
这里两者的含义是一样的。指从几何图元——点、线、三角形中创建的东西，由顶点指定。

#### **渲染（Rendering）**
计算机从模型到创建一张图像的过程。OpenGL仅仅是其中一个渲染系统。它是一个基于光栅化的系统，其他的系统还有光线追踪（但有时也会用到OpenGL）等。

#### **Shaders**
这是一类特殊的函数，是在图形硬件（GPU）上执行的。我们可以理解成，Shader是一些为图形处理单元（GPU）编译的小程序。
OpenGL包含了编译工具来把我们编写的 Shader 源代码编译成可以在GPU上运行的代码。
在 OpenGL 中，我们可以使用**四种shader阶段**。
最常见的就是 vertex shaders——它们可以处理顶点数据；
以及fragment shaders，它们处理光栅化后生成的fragments。
vertex shaders 和 fragment shaders是每个OpenGL程序必不可少的部分。

## OpenGL 的命名规范
OpenGL里面的函数长得都有一个特点，都是由“gl”开头的，然后紧跟一个或多个大写字母（例如，glBindVertexArray()）。而且所有的OpenGL函数都长这样。

在程序里面还有一些函数是“glut”开头的，这是来自OpenGL实用工具（OpenGL Utility Toolkit）——GLUT。这是一个非常流行的跨平台工具，可以用于打开窗口、管理输入等操作。同样，还有一个函数，glewInit()，它来自GLEW库。GLUT和GLEW就是龙书所用的两个库了。

和OpenGL函数的命名规范类似，在display()函数里见到的GL_COLOR_BUFFER_BIT这样的常量，也是OpenGL定义的。它们由GL_开头，实用下划线来分割字符。它们的定义就是通过OpenGL头文件（glcorearb.h和glewt.h）里面的#define指令定义的。

OpenGL为了跨平台还自己定义了一系列数据类型，如GLfloat。而且，因为OpenGL是一个“C”语言库，它不使用函数重载来解决不同类型的数据问题，而是使用函数命名规范来组织不同的函数。例如，后面我们会碰到一个函数叫glUniform*()，这个函数有很多形式，例如，glUniform2f()和glUniform3fv。这些函数名字后面的后缀——2f和3fv，提供了函数的参数信息。例如，2f中的2表示有两个数据将会传递给函数，f表示这两个参数的类型是GLfloat。而3fv中最后的v，则是vector的简写，表明这三个GLfloat将以vector的形式传递给函数，而不是三个独立的参数。

## GL 中 顶点 是怎么传到 GLSL 的？
答案是
创建**顶点流**（Vertex Stream）

我们负责创建这个顶点流，然后只需要告诉OpenGL怎样解读它就可以了。
为了渲染一个对象，我们必须使用一个**shader program**。而这个program会定义一系列顶点属性，例如上一篇文章中 Vertex Shader中的gl_Position 一行。这些属性决定了我们需要传递哪些顶点数据。每一个属性对应了一个数组，并且这些数据的维度都必须相等，即是一一对应的关系。



## VAO 和 VBO
OpenGL 使用 VAO 来实现上述管理顶点数据的作用，以及 VBO 来存放真正的顶点数据。