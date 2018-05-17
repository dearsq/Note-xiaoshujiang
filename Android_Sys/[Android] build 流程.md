---
title: [Android] build 流程
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
Make 命令逐行执行了 makefile 中的命令。它一边执行着每条命令，一边向标准输出写命令（除非另有直接声明，比如用了 -s 选项）。一个 Makefile 必须使用 Tab 来进行缩进。
当一个命令通过 make 命令来执行。它使用的是 make 的执行环境。这个环境包括了 
1. 执行 make 命令的任何宏定义 
2. 定义在 MAKEFLAGS 变量中的所有环境变量。

> 注意：
> 当 make 命令遇到以 makefile 里面的关键字相同的 起始的命令时（比如 inclue、depend），make 命令将试图打开这文件，并去处理该文件就好像这个文件本来就在 makefile 中的 include 行中一样。这个现象只在第一个 makefile 的第一个非命令行被 make 命令作为非 POSIX 目标读的时候才会发生。否则，将发生一个语法错误。
> 注释：注释以 # 字符开始，除了 shell 命令行，其他的地方都可以用。
> 环境：make 命令会使用 MAKEFLAGS 环境变量。

## Target 规则
Target 规则的格式如下:

target[target...] : [prerequisite...] [;command]
< Tab>command
多个 target 和 prerequisite 用空格分开。后面的任何文本 ; （分号）和所有被认为是后续行以标签字符开头的命令被用于更新目标。如果新行不以制表符或＃字符开始，后面就是一个新的 target。
您也可以在Makefile教程看这里http://mrbook.org/tutorials/make/！
这是构建过程中最重要的组成部分，其中 make 文件组织编译的每个源文件，并将他们组合成有用的应用程序/二进制文件/库等。
where make files are resposible for compiling almost each of the files in the source and putting them together for the useful apps/binaries/libraries etc. 

## Build 技巧
* 使用 Wiki。
* 眼看用于构建实际的命令软件
* 使用“showcommands”目标上的'制作'行：

$make -j4 showcommands 
这可以与其他一起使用make目标，以查看该版本的命令。即，'showcommands'不是目标本身，而只是为指定的生成的改性剂。

在上面的例子中，-j4是无关的 showcommands选项，并且用于执行并行 4 线程。

make target
下面是你可以用它来构建系统的不同部分不同 target 的列表：
make sdk - build the tools that are part of an SDK (adb, fastboot, etc.)
make snod - build the system image from the current software binaries
make services
make runtime
make droid - make droid is the normal build.
make all - make everything, whether it is included in the product definition or not
make clean - remove all built files (prepare for a new build). Same as rm -rf out/< configuration>/
make modules - shows a list of submodules that can be built (List of all LOCAL_MODULE definitions)
make < local_module> - make a specific module (note that this is not the same as directory name. It is the LOCAL_MODULE definition in the Android.mk file)
make clean-< local_module> - clean a specific module

Helper macros and functions
There are some helper macros and functions that are installed when you source envsetup.sh. They are documented at the top of envesetup.sh, but here is information about a few of them:

辅助宏和函数
有一些辅助宏和函数，在安装时，你 source 了 envsetup.sh。它们在 envesetup.sh 顶部有文档，但这里是有关其中的几个信息：
croot - 回到目录树的根部
m - execute 'make' from the top of the tree (even if your current directory is somewhere else)
mm - builds all of the modules in the current directory
mmm < dir1> ... - build all of the modules in the supplied directories
cgrep < pattern> - grep on all local C/C++ files
jgrep < pattern> - grep on all local Java files
resgrep < pattern> - grep on all local res/*.xml files
godir < filename> - go to the directory containing a file

## 加快 build
### 你可以在 make 时使用'-j'选项，开启 make 使用多线程。
根据我的经验，你的机器上有多个处理器的话你应该指定 2个或线程。如果你有2个处理器，使用' make -j4'，如果 超线程（这意味着你有4个虚拟处理器），尝试'使-j6。
您还可以指定使用'ccache的“编译器缓存，这将加快的东西，一旦你已经建立的东西第一次。要做到这一点，在shell命令行中指定的出口USE_CCACHE = 1'。（注意：是的ccache包括在库的预建的部分，并没有单独的主机上安装。）

### 编译单独的程序或模块
如果您使用的 build/envsetup.sh，你可以使用一些定义功能去构建源码的一部分。使用“mm”或“mmm”命令来做到这一点。

“mm” 命令使东西在当前目录（和子目录）。
“mmm”命令，指定要编译的目录或目录列表。
'make snod' builds a new system image from current binaries. 在根目录运行 'make snod'。

### 设置模块特定的构建参数
Android 系统中的某些代码可在它们的 build时进行定制（从构建变量独立和发布与调试选项）。您可以设置控制单个编译选项变量，无论是在环境中设置它们或直接通过他们“make”（或“m...”功能，这称之为“make”）。
例如，“init”程序可以通过设置INIT_BOOTCHART变量 bootchart日志。（请参阅《 Using Bootchart on Android》了解为什么你可能想做到这一点。）

你可以做到：
```
$ touch system/init/init.c
$ export INIT_BOOTCHART=true
$ make
```
或者
```
$ touch system/init/init.c
$ m INIT_BOOTCHART=true
```
最后，经过 makefile 组织优化后，所有进程以及构建设备的指定部分（包括二进制文件、库、app、system 文件和 "boot.img" 都可以在 out/target/product/device 目录下找到）。在 META-INF文件的实例和系统boot.img被打包成一个zip文件（其名称也由makefile文件处理）并且MD5校验也准备好了。如果你运行“brunch”命令或“lunch+ mka”命令，将生成可擦写的 zip。

Build 技巧不是并不是为了好玩。这东西可以帮助我们更深层次的看问题！

- Younix 译


















