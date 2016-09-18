---
title: build/envsetup.sh 流程分析
tags: Android,Makefile
grammar_cjkRuby: true
---
原文地址：http://forum.xda-developers.com/showthread.php?t=2751407
翻译地址：
翻译者：Younix

## 介绍
AOSP 相当复杂，也很难找到一个方法去更好地了解它。我准备尝试一种务实的方法来了解它它，分析研究一下**编译的过程（build process）**。
在你真正的准备去学习 Android 之前，我推荐大家先读一读我的这份指南。
这份指南详述了**从 envsetup.sh 到 makefile 到 package 完成编译 的 整个 Android 编译过程**

## 最初（envsetup.sh）
一切都从这条命令开始
```bash
source build/envsetup.sh
```
它的作用简单来说就是向你的环境添加了一些命令，你可以在稍后为你的设备编译 Android 的时候使用这些命令。
这些命令如下：
```
- lunch:   lunch <product_name>-<build_variant>
- tapas:   tapas [<App1> <App2> ...] [arm|x86|mips|armv5] [eng|userdebug|user]
- croot:   Changes directory to the top of the tree.
- cout:    Changes directory to out.
- m:       Makes from the top of the tree.
- mm:      Builds all of the modules in the current directory.
- mmp:     Builds all of the modules in the current directory and pushes them to the device.
- mmm:     Builds all of the modules in the supplied directories.
- mmmp:    Builds all of the modules in the supplied directories and pushes them to the device.
- mma:     Builds all of the modules in the current directory, and their dependencies.
- mmma:    Builds all of the modules in the supplied directories, and their dependencies.
- cgrep:   Greps on all local C/C++ files.
- jgrep:   Greps on all local Java files.
- resgrep: Greps on all local res/*.xml files.
- godir:   Go to the directory containing a file.
- cmremote: Add git remote for CM Gerrit Review.
- cmgerrit: A Git wrapper that fetches/pushes patch from/to CM Gerrit Review.
- cmrebase: Rebase a Gerrit change and push it again.
- aospremote: Add git remote for matching AOSP repository.
- cafremote: Add git remote for matching CodeAurora repository.
- mka:      Builds using SCHED_BATCH on all processors.
- mkap:     Builds the module(s) using mka and pushes them to the device.
- cmka:     Cleans and builds using mka.
- repolastsync: Prints date and time of last repo sync.
- reposync: Parallel repo sync using ionice and SCHED_BATCH.
- repopick: Utility to fetch changes from Gerrit.
- installboot: Installs a boot.img to the connected device.
- installrecovery: Installs a recovery.img to the connected device.
```
它也会扫描一遍你源码中的 vendorsetup.sh 文件并且用这种格式将他们列出来：
```
including device/generic/armv7-a-neon/vendorsetup.sh
including device/generic/goldfish/vendorsetup.sh
including device/generic/mips/vendorsetup.sh
including device/generic/x86/vendorsetup.sh
including vendor/cm/vendorsetup.sh
including sdk/bash_completion/adb.bash
including vendor/cm/bash_completion/git.bash
including vendor/cm/bash_completion/repo.bash
```

1. 所有的 make 相关命令只有在 source envsetup.sh 后才能使用
2. 浏览并且执行一些 build/core 目录中的内容
3. 会列出可选择的设备及编译项目（比如 "userdebug""user""eng")
4. 它也负责执行最重要的步骤。建立 Android 的编译路径并且为编译过程建立编译工具链。
5. 它也会调用 java 并设置一些编译的参数
6. 它将会展示默认的设备配置比如
```
add_lunch_combo aosp_arm-eng
add_lunch_combo aosp_x86-eng
add_lunch_combo aosp_mips-eng
add_lunch_combo vbox_x86-eng
```
7. 如果设备源码没有的话，它将会调用 build/tools 中的'roomservice.py' 文件来查找并下载设备的源码。
8. 它也包含了 CWR 和 TWRP 命令集，用来刷机。
9. 它也提供了设备端的 Bug 报告机制，可以从开发者工作所使用的机器上直接获取到 bug reports。
## lunch/brunch 命令
下一件事情就是使用 lunch 命令。
在执行了 envsetup.sh 后，lunch 命令被添加至我们的 bash shell 编译环境中。在作出了编译工程的选择后，所选择的产品被确认了，环境变量也都设定下来了，包括：
```bash
export TARGET_PRODUCT=$product 			# The chosen product
export TARGET_BUILD_VARIANT=$variant # The chosen variant
export TARGET_BUILD_TYPE=release # Only release type is available. Use choosecombo if you want to select type.
export ANDROID_BUILD_TOP=$(gettop) # The build root directory.
export ANDROID_TOOLCHAIN=... # The toolchain directory for the prebuilt cross-compiler matching the target architecture
export PATH=... # Among other stuff, the prebuilt toolchain is added to PATH.
export ANDROID_PRODUCT_OUT=... # Absolute path to the target product out directory
export ANDROID_HOST_OUT=... # Absolute path to the host out directory
```
用法相当简单，你仅仅只用输入 lunch ，然后将会列出用此源码你可以编译的设备工程清单，或者你可以输入 lunch cm_< device_name >-< variant_type >.
lunch 命令实际上**确定了编译工程的编译目标**，并负责锁定用来编译源码的环境变量和设备配置。
其实，只有在设备树中包含有 vendorsetup.sh 的时候 lunch 命令才能被使用。vendorsetup.sh 添加了我们设备的 lunch combo（当我们执行 lunch 时出现的那个 list）

## make 命令
make 工具的目的是**自动确定这个大工程的哪些模块需要重新编译，并且发出命令集来重编译它们**。
有一个描述 make 的 GNU 安装的手册，是 Richard Stallman 和 McGrath 写的。下面的例子是以 C 语言为例，因为 C 是最常见的，但是你也可以将 make 用在任何能够以 shell 命令来编译的编程语言中。你可以用它来描述任何需要自动更新的任务。
为了准备使用 make，我们需要编写一种叫做 makefile 的文件，这个文件描述了我们程序中各个文件的关系，并且展示了我们更新每个文件的命令。在程序中，执行文件的更新是由于某些文件的更新产生的，后者就是由某些代码编译而来的。
只要有合适的 makefile 存在，每次你改变源码后，都只需要简单的执行
```shell
make
```
就够了。
make 有能力完成所有的重编译。make 程序使用 makefile 数据库和文件的最近修改时间来确定哪些文件需要被更新。对于每一个（更新后的）文件，make 都将执行 makefile 数据库中对应的指令（commands）。

make 执行 makefile 中的命令来更新一个或者多个程序。如果没有显式地使用 -f 选项，make 将依次寻找 makefiles GNUmakefile 和 Makefile。

一般无论是 Makefile 还是 makefile 都将可以被调用（我推荐使用 Makefile，因为它在文件目录清单中最突出，就仅靠在最重要的文件 README 的旁边）。

如果一个文件被修改后，所依赖这个文件的编译结果会被 make 进行更新。
同样如果这个编译结果不存在或者被修改，都将会被 make 重新编译。

## Makefile 执行过程

The make command executes the commands in the makefile line by line. As make executes each command, it writes the command to standard output (unless otherwise directed, for example, using the -s flag). A makefile must have a Tab in front of the commands on each line.

When a command is executed through the make command, it uses make's execution environment. This includes any macros from the command line to the make command and any environment variables specified in the MAKEFLAGS variable. The make command's environment variables overwrite any variables of the same name in the existing environment.

Note:
Quote:
When the make command encounters a line beginning with the word include followed by another word that is the name of a makefile (for example, include depend), the make command attempts to open that file and process its contents as if the contents were displayed where the include line occurs. This behavior occurs only if the first noncomment line of the first makefile read by the make command is not the .POSIX target; otherwise, a syntax error occurs.
Comments: Comments begin with a # character, anywhere but in a shell command line, and continue to the end of the line.

Environment: The make command uses the MAKEFLAGS environment variable, if it exists.

Target Rules


Target rules have the following format:

target[target...] : [prerequisite...] [;command]
<Tab>command
Multiple targets and prerequisites are separated by spaces. Any text that follows the ; (semicolon) and all of the subsequent lines that begin with a Tab character are considered commands to be used to update the target. A new target entry is started when a new line does not begin with a Tab or # character.

You can also look up at the Makefile Tutorial here http://mrbook.org/tutorials/make/ !

That was the most important part of the build process, where make files are resposible for compiling almost each of the files in the source and putting them together for the useful apps/binaries/libraries etc. 

Build Tricks

Used from wiki.

Seeing the actual commands used to build the software
Use the "showcommands" target on your 'make' line:

$ make -j4 showcommands
This can be used in conjunction with another make target, to see the commands for that build. That is, 'showcommands' is not a target itself, but just a modifier for the specified build.

In the example above, the -j4 is unrelated to the showcommands option, and is used to execute 4 make sessions that run in parallel.

Make targets
Here is a list of different make targets you can use to build different parts of the system:
make sdk - build the tools that are part of an SDK (adb, fastboot, etc.)
make snod - build the system image from the current software binaries
make services
make runtime
make droid - make droid is the normal build.
make all - make everything, whether it is included in the product definition or not
make clean - remove all built files (prepare for a new build). Same as rm -rf out/<configuration>/
make modules - shows a list of submodules that can be built (List of all LOCAL_MODULE definitions)
make <local_module> - make a specific module (note that this is not the same as directory name. It is the LOCAL_MODULE definition in the Android.mk file)
make clean-<local_module> - clean a specific module

Helper macros and functions
There are some helper macros and functions that are installed when you source envsetup.sh. They are documented at the top of envesetup.sh, but here is information about a few of them:

croot - change directory to the top of the tree
Code:
m - execute 'make' from the top of the tree (even if your current directory is somewhere else)
mm - builds all of the modules in the current directory
mmm <dir1> ... - build all of the modules in the supplied directories
cgrep <pattern> - grep on all local C/C++ files
jgrep <pattern> - grep on all local Java files
resgrep <pattern> - grep on all local res/*.xml files
godir <filename> - go to the directory containing a file
Speeding up the build

You can use the '-j' option with make, to start multiple threads of make execution concurrently.

In my experience, you should specify about 2 more threads than you have processors on your machine. If you have 2 processors, use 'make -j4', If they are hyperthreaded (meaning you have 4 virtual processors), try 'make -j6.

You can also specify to use the 'ccache' compiler cache, which will speed up things once you have built things a first time. To do this, specify 'export USE_CCACHE=1' at your shell command line. (Note that ccache is included in the prebuilt section of the repository, and does not have to be installed on your host separately.)

Building only an individual program or module
If you use build/envsetup.sh, you can use some of the defined functions to build only a part of the tree. Use the 'mm' or 'mmm' commands to do this.

The 'mm' command makes stuff in the current directory (and sub-directories, I believe). With the 'mmm' command, you specify a directory or list of directories, and it builds those.

To install your changes, do 'make snod' from the top of tree. 'make snod' builds a new system image from current binaries.

Setting module-specific build parameters
Some code in Android system can be customized in the way they are built (separate from the build variant and release vs. debug options). You can set variables that control individual build options, either by setting them in the environment or by passing them directly to 'make' (or the 'm...' functions which call 'make'.)

For example, the 'init' program can be built with support for bootchart logging by setting the INIT_BOOTCHART variable. (See Using Bootchart on Android for why you might want to do this.)

You can accomplish either with:

$ touch system/init/init.c
$ export INIT_BOOTCHART=true
$ make
or

$ touch system/init/init.c
$ m INIT_BOOTCHART=true

At last, after makefiles optimize all the processes and build the device specific parts including binaries and libs and apps necessary for it to get booted, the 'system' folder and the 'boot.img' folder are prepared in the out/target/product/device. The META-INF folder is prepared at instance and the system and boot.img are packed into a zip file(whose name is also processed by the makefiles  ) and md5 sum prepared. The flashable zip gets prepared only if you run the "brunch" command or "lunch + mka" command. 

The Build Tricks aren't *for fun*. This stuff is always gonna help you in the long run!























