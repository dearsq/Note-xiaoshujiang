---
title: [OpenGL]创建一个三角形
tags: OpenGL
grammar_cjkRuby: true
---
Platform: Ubuntu16.04
IDE: QT5
Tools: OpenGL3

[TOC]

## 代码
```cpp
// Include standard headers
#include <stdio.h>
#include <stdlib.h>

// Include GLEW
#include <GL/glew.h>

// Include GLFW
#include <glfw3.h>
GLFWwindow* window;

// Include GLM
#include <glm/glm.hpp>
using namespace glm;

#include <common/shader.hpp>

int main( void )
{
    // Initialise GLFW
    if( !glfwInit() )
    {
        fprintf( stderr, "Failed to initialize GLFW\n" );
        getchar();
        return -1;
    }

    glfwWindowHint(GLFW_SAMPLES, 4);
    glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 3);
    glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 3);
    glfwWindowHint(GLFW_OPENGL_FORWARD_COMPAT, GL_TRUE); // To make MacOS happy; should not be needed
    glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE);

    // Open a window and create its OpenGL context
    window = glfwCreateWindow( 1024, 768, "Tutorial 02 - Red triangle", NULL, NULL);
    if( window == NULL ){
        fprintf( stderr, "Failed to open GLFW window. If you have an Intel GPU, they are not 3.3 compatible. Try the 2.1 version of the tutorials.\n" );
        getchar();
        glfwTerminate();
        return -1;
    }
    glfwMakeContextCurrent(window);

    // Initialize GLEW
    glewExperimental = true; // Needed for core profile
    if (glewInit() != GLEW_OK) {
        fprintf(stderr, "Failed to initialize GLEW\n");
        getchar();
        glfwTerminate();
        return -1;
    }

    // Ensure we can capture the escape key being pressed below
    glfwSetInputMode(window, GLFW_STICKY_KEYS, GL_TRUE);

    // Dark blue background
    glClearColor(0.0f, 0.0f, 0.4f, 0.0f);

	//1. 生成顶点数组 VAO 
    GLuint VertexArrayID;
    glGenVertexArrays(1, &VertexArrayID);
    //2. 绑定 VAO
    glBindVertexArray(VertexArrayID);

    // Create and compile our GLSL program from the shaders
    GLuint programID = LoadShaders( "SimpleVertexShader.vertexshader", "SimpleFragmentShader.fragmentshader" );

	// 三角形三个顶点的坐标(-1,-1,0),(1,-1,0),(0,1,0)
    static const GLfloat g_vertex_buffer_data[] = {
        -1.0f, -1.0f, 0.0f,
         1.0f, -1.0f, 0.0f,
         0.0f,  1.0f, 0.0f,
    };
    
	//3. 产生缓冲区对象 VBOs 
    GLuint vertexbuffer;
    glGenBuffers(1, &vertexbuffer);
    //4. 激活（绑定）缓冲区对象
    glBindBuffer(GL_ARRAY_BUFFER, vertexbuffer);
    //5. 用数据分配和初始化缓冲区对象
    //void glBufferData(GLenum target,  是GL_ARRAY_BUFFER()（顶点数据）或GL_ELEMENT_ARRAY_BUFFER(索引数据)
    //        GLsizeiptr size 缓冲区对象字节数,
    //        const GLvoid * data用于拷贝缓冲区对象数据的指针,
    //        GLenum usage);
    glBufferData(GL_ARRAY_BUFFER, sizeof(g_vertex_buffer_data), g_vertex_buffer_data, GL_STATIC_DRAW);

   // 设置清除颜色为 蓝色
    glClearColor(0.0f, 0.5f, 0.5f, 0.0f); 

    do{
        // 执行清除任务
        glClear( GL_COLOR_BUFFER_BIT );

        // Use our shader
        glUseProgram(programID);

        // 1rst attribute buffer : vertices
        //6. 定义存放顶点数据的数组
        //void glEnableVertexAttribArray(      GLuint    index);
		//index：指定了需要启用的顶点属性数组的索引
        glEnableVertexAttribArray(0);
        // ？？又绑定一次？
        glBindBuffer(GL_ARRAY_BUFFER, vertexbuffer);
        // 给对应的顶点属性数组指定数据
        glVertexAttribPointer(
            0,                  // attribute 0. No particular reason for 0, but must match the layout in the shader.
            3,                  // size
            GL_FLOAT,           // type
            GL_FALSE,           // normalized?
            0,                  // stride
            (void*)0            // array buffer offset
        );

        // Draw the triangle !
        glDrawArrays(GL_TRIANGLES, 0, 3); // 3 indices starting at 0 -> 1 triangle
        glDisableVertexAttribArray(0);

        // Swap buffers
        glfwSwapBuffers(window);
        glfwPollEvents();

    } // Check if the ESC key was pressed or the window was closed
    while( glfwGetKey(window, GLFW_KEY_ESCAPE ) != GLFW_PRESS &&
           glfwWindowShouldClose(window) == 0 );

    // Cleanup VBO
    glDeleteBuffers(1, &vertexbuffer);
    glDeleteVertexArrays(1, &VertexArrayID);
    glDeleteProgram(programID);

    // Close OpenGL window and terminate GLFW
    glfwTerminate();

    return 0;
}

```

## API 分析
#### 顶点数组对象 VAO
VAO，是这样一种方式：把对象信息直接存储在图形卡中，而不是在当我们需要的时候传输到图形卡。
**使用方法**
```cpp
// 顶点数组对象 VertexArrayID
GLuint VertexArrayID;
// 产生 VAO （数量，存放产生 VAO 对象的名称）
void glGenVertexArrays(GLsizei n,  GLuint *arrays);
// 绑定 VAO（要绑定的顶点数组的名字）
void glBindVertexArray(GLuint array);
```
这个**必须在任何其他OpenGL调用前完成。**

### 屏幕坐标系
**右手定则**：面对电脑，指向右边是 X，指向上边是 Y，指向背后是 Z。


## Bug 集锦
### Error：The program has unexpectedly finished.
现象：程序中已经正确包含glew相关的头文件和库文件，glew也已经通过glewInit()正确初始化，程序运行到glGenVertexArrays处时仍然出现运行时错误：.exe（某opengl可执行程序）中的0x********（某内存地址） 处有未处理的异常： Ox********: Access violation
解决方案：
 在glewInit()之前加上glewExperimental = true;
Reason:
GLEW obtains information on the supported extensions from the graphics driver. Experimental or pre-release drivers, however, might not report every available extension through the standard mechanism, in which case GLEW will report it unsupported. To circumvent this situation, the glewExperimental global switch can be turned on by setting it to GL_TRUE before calling glewInit(), which ensures that all extensions with valid entry points will be exposed. 

###

##  参考
VBO，VAO 介绍：http://blog.csdn.net/xiajun07061225/article/details/7628146