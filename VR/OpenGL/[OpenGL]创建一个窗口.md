---
title: [OpenGL]创建一个窗口
tags: openGL
grammar_cjkRuby: true
---
## 代码
```cpp
#include <stdio.h>
#include <stdlib.h>

//GLEW  的库
#include <GL/glew.h> 
 //GLFW 的库，处理窗口和键盘的消息
#include <glfw3.h>  
GLFWwindow* window;

////三维数学的库
#include <glm/glm.hpp>  
using namespace glm;

int main( void )
{
    //初始化 GLFW
    if( !glfwInit() )
    {
        fprintf( stderr, "Failed to initialize GLFW\n" );
        getchar();
        return -1;
    }
    
	//设置一些 hint
    //glfwWindowHint(int hint, int mode);
    glfwWindowHint(GLFW_SAMPLES, 4);
    glfwWindowHint(GLFW_RESIZABLE,GL_FALSE);
    glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 3); //set Vision to 3.3
    glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 3);
    glfwWindowHint(GLFW_OPENGL_FORWARD_COMPAT, GL_TRUE); // To make MacOS happy; should not be needed
    glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE);

    // Open a window and create its OpenGL context
    window = glfwCreateWindow( 1024, 768, "HelloWorld", NULL, NULL);
    if( window == NULL ){
        fprintf( stderr, "Failed to open GLFW window. If you have an Intel GPU, they are not 3.3 compatible. Try the 2.1 version of the tutorials.\n" );
        getchar();
        glfwTerminate();
        return -1;
    }
    glfwMakeContextCurrent(window);

    // Initialize GLEW
    if (glewInit() != GLEW_OK) {
        fprintf(stderr, "Failed to initialize GLEW\n");
        getchar();
        glfwTerminate();    //destory all remain
        return -1;
    }

    // Ensure we can capture the escape key being pressed below
    // 确保当某些键按下的时候，后面 glfwGetKey 可以获得 GLFW_PRESS
    glfwSetInputMode(window, GLFW_STICKY_KEYS, GL_TRUE);

    // Dark blue background
    // glClearColor(0.0f, 0.0f, 0.4f, 0.0f);
    // glClearColor(Red, Green, Blue, 0.0f);
    // 为色彩缓冲区指定用于清除的值
    glClearColor(0.0f, 0.0f, 0.0f, 0.0f);

    do{
    	//执行清除色彩缓冲区的任务
        glClear( GL_COLOR_BUFFER_BIT );

        // Swap buffers
        glfwSwapBuffers(window);
        glfwPollEvents();

    } // Check if the ESC key was pressed or the window was closed
    while( glfwGetKey(window, GLFW_KEY_ESCAPE ) != GLFW_PRESS &&
           glfwWindowShouldClose(window) == 0 );

    // Close OpenGL window and terminate GLFW
    glfwTerminate();

    return 0;
}
```
## API 分析
#### glfwSetInputMode
设置特定窗口的输入模式
```
void glfwSetInputMode	(	GLFWwindow * 	window, int 	mode, int 	value )	
```
mode 可以为 GLFW_CURSOR, GLFW_STICKY_KEYS or GLFW_STICKY_MOUSE_BUTTONS.
**当 mode = GLFW_CURSOR**
value 为
GLFW_CURSOR_NORMAL makes the cursor visible and behaving normally. 让光标可见，且正常
GLFW_CURSOR_HIDDEN makes the cursor invisible when it is over the client area of the window but does not restrict the cursor from leaving. 当光标到窗口区域的时候，光标隐藏
GLFW_CURSOR_DISABLED hides and grabs the cursor, providing virtual and unlimited cursor movement. This is useful for implementing for example 3D camera controls. 强行夺取光标，光标消失
**当 mode = GLFW_STICKY_KEYS**
value 为 
GLFW_TRUE 使能粘滞键。确保按键将会使  **glfwGetKey** returns **GLFW_PRESS**。它常常被用在你只关注键是否被按下，而不关注键什么时候按下或者以什么顺序按下时。
GLFW_FALSE 禁能粘滞键。
**当 mode = GLFW_STICKY_MOUSE_BUTTONS**
value 为 
GLFW_TRUE 使能鼠标粘滞键。确保鼠标按钮将会使 **glfwGetMouseButton** returns **GLFW_PRESS**。
GLFW_FALSE 禁能鼠标粘滞键。


#### glClearColor & glClear
```
void glClearColor(GLclampf red,GLclampf green,GLclampf blue,GLclampf alpha)
```
设置颜色缓冲区颜色为（红，绿，蓝，透明）
```
void glClear(GLbitfield mask);
```
执行清理命令
GLbitfield mask：可以使用 | 运算符组合不同的缓冲标志位，表明需要清除的缓冲
GL_COLOR_BUFFER_BIT:    当前可写的颜色缓冲 glClearColor
GL_DEPTH_BUFFER_BIT:    深度缓冲 glClearDepth
GL_ACCUM_BUFFER_BIT:   累积缓冲 glClearAccum
GL_STENCIL_BUFFER_BIT: 模板缓冲 glClearStencil


####  glfwSwapBuffers &   glfwPollEvents
**glfwSwapBuffers**
This function swaps the front and back buffers of the specified window when rendering with OpenGL or OpenGL ES. 交换前后端缓冲区？不懂——>[[OpenGL中的缓冲区]](http://blog.csdn.net/Haohan_Meng/article/details/25246519) OpenGL 在绘制图元时，先是在一个缓冲区中完成渲染，然后再把渲染结果交换到屏幕上。我们把这两个缓冲区称为前颜色缓冲区（屏幕）和后颜色缓冲区。
**glfwPollEvents**
This function processes only those events that are already in the event queue and then returns immediately. Processing events will cause the window and input callbacks associated with those events to be called.
作用是 **Processes all pending events.**

#### glfwGetKey
```
int glfwGetKey（GLFWwindow * 	window, int 	key  )	
```
返回上一次特定窗口中某个按键的状态（按下GLFW_PRESS 或者 释放GLFW_RELEASE）
```
    while( glfwGetKey(window, GLFW_KEY_ESCAPE ) != GLFW_PRESS &&
           glfwWindowShouldClose(window) == 0 );
```
1. 获取 windows 窗口 ESC 键的状态
2. 如果没有按下返回 GLFW_RELEASE 不会进入 && 后面的判断
3. 如果有被按下返回 GLFW_PRESS 就进入后面的判断
4. 执行 glfwWindowShouldClose 指令，返回 close flag 
5. 0 && 0 ，跳出 while 循环

## 参考
glfw 若干函数列表：http://blog.csdn.net/ccsdu2004/article/details/3838184
OpenGL 中的缓冲区：http://blog.csdn.net/Haohan_Meng/article/details/25246519
