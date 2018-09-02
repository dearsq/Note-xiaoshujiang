---
title: [Flutter] 开发环境搭建
tags: 
grammar_cjkRuby: true
---

```zsh
➜  Flutter flutter config --android-sdk /home/younix/WorkTools/Android/Sdk 
Setting "android-sdk" value to "/home/younix/WorkTools/Android/Sdk".
➜  Flutter flutter config --android-studio-dir /home/younix/WorkTools/android-studio/
Setting "android-studio-dir" value to "/home/younix/WorkTools/android-studio/".
➜  Flutter flutter doctor --android-licenses
```


```
➜  Flutter flutter doctor -v
[✓] Flutter (Channel beta, v0.5.1, on Linux, locale en_US.UTF-8)
    • Flutter version 0.5.1 at /home/younix/WorkSpace/02.SDK/Flutter/flutter
    • Framework revision c7ea3ca377 (3 months ago), 2018-05-29 21:07:33 +0200
    • Engine revision 1ed25ca7b7
    • Dart version 2.0.0-dev.58.0.flutter-f981f09760

[✓] Android toolchain - develop for Android devices (Android SDK 27.0.3)
    • Android SDK at /home/younix/WorkTools/Android/Sdk
    • Android NDK location not configured (optional; useful for native profiling support)
    • Platform android-27, build-tools 27.0.3
    • Java binary at: /home/younix/WorkTools/android-studio/jre/bin/java
    • Java version OpenJDK Runtime Environment (build 1.8.0_152-release-1024-b01)
    • All Android licenses accepted.

[✓] Android Studio (version 3.1)
    • Android Studio at /home/younix/WorkTools/android-studio
    ✗ Flutter plugin not installed; this adds Flutter specific functionality.
    ✗ Dart plugin not installed; this adds Dart specific functionality.
    • Java version OpenJDK Runtime Environment (build 1.8.0_152-release-1024-b01)

[✓] Android Studio
    • Android Studio at /home/younix/WorkTools/android-studio/
    ✗ Flutter plugin not installed; this adds Flutter specific functionality.
    ✗ Dart plugin not installed; this adds Dart specific functionality.
    • android-studio-dir = /home/younix/WorkTools/android-studio/
    • Java version OpenJDK Runtime Environment (build 1.8.0_152-release-1024-b01)

[!] VS Code (version 1.24.1)
    • VS Code at /usr/share/code
    • Flutter extension not installed; install from
      https://marketplace.visualstudio.com/items?itemName=Dart-Code.flutter

[✓] Connected devices (1 available)
    • MI 4LTE • 1f5a97c4 • android-arm • Android 6.0.1 (API 23)

! Doctor found issues in 1 category.

```