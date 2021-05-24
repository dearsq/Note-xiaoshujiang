title: 使用ffmpeg和recover_mp4修复损坏的视频文件
date: 2021-5-24 21:00:00
tags: win10

---

# 使用ffmpeg和recover_mp4修复损坏的视频文件

Platform: Windows10

Author: Younix

[TOC]

## Step1. recover_mp4.exe good.mp4 --analyze

通过 recover_mp4.exe 工具，获取正常的文件（good.mp4）的格式及参数。



D:\WorkSpace_Malong\04.Code\Android\LAB\debug\20210523_视频无法加载>recover_mp4.exe good.mp4 --analyze
recover_mp4 v1.92 (C) 2011-2017 Dmitry Vasilyev <slydiman@mail.ru>
http://slydiman.me

Analyzing file 'good.mp4':

'ftyp' 0x0 [24] Major Brand: 'mp42', Minor Version: 0x0
  Compatible brands: 'mp42', 'isom'
'free' 0x18 [136]
'mdat' 0xA0 [121755674]
'moov' 0x741D8BA [25989]
  'mvhd' 0x741D8C2 [108] Movie Header: Time scale 90000, Duration 26622000 (295.8 sec)
    Rate 1, Volume 1
    Creating time: 2021/05/23 2:34:13
    Modification time: 2021/05/23 2:39:23
    Next Track ID: 2
  'iods' 0x741D92E [24]
    Unprocessed 16 bytes
  'trak' 0x741D946 [25849]
    'tkhd' 0x741D94E [92] Track #1, Duration 26622000
      Resolution: 1920x1080
      Creating time: 2021/05/23 2:34:26
      Modification time: 2021/05/23 2:39:23
    'mdia' 0x741D9AA [25749]
      'mdhd' 0x741D9B2 [32] Media Header: Time scale 90000, Duration 26622000 (295.8 sec)
        Creating time: 2021/05/23 2:34:26
        Modification time: 2021/05/23 2:39:23
      'hdlr' 0x741D9D2 [33] Component Type: {0000}, Subtype: 'vide'
      'minf' 0x741D9F3 [25676]
        'vmhd' 0x741D9FB [20]
        'dinf' 0x741DA0F [36]
          'dref' 0x741DA17 [28]
            'url ' 0x741DA27 [12]
              Unprocessed 4 bytes 00 00 00 01
        'stbl' 0x741DA33 [25612]
          'stsd' 0x741DA3B [164]
            'avc1' 0x741DA4B [148] Video Sample 1920x1080, 24 bits, JVT/AVC Coding
              'avcC' 0x741DAA1 [62] AVC video 1920x1080, Main Profile, Level 4.0
          'stts' 0x741DADF [24] Time-to-Sample[1] (#: Count * Duration):
             0: 5916 * 4500
          'stsz' 0x741DAF7 [23684] Sample Size[5916] (#: Sample Size):
             0: 0x171c5
             1: 0x1345
             2: 0x4be8
             3: 0x3e56
             4: 0x3fd9
             5: 0x3b1f
             6: 0x3a60
             7: 0x368d
             8: 0x35dc
             9: 0x340a
            10: 0x30df
            ...
          'stsc' 0x742377B [40] Sample-to-Chunk[2] (#: FirstChunk / SamplesPerChunk / SampleDescIndex):
             0: 1 / 20 / 1
             1: 296 / 16 / 1
          'stco' 0x74237A3 [1200] Chunk Offset[296] (#: Chunk Offset):
             0: 0xa8
             1: 0x53cb8
             2: 0x98347
             3: 0xf337b
             4: 0x13cd29
             5: 0x1813fd
             6: 0x201b32
             7: 0x26a24a
             8: 0x2dc9ec
             9: 0x336f99
            10: 0x38c8f2
            ...
          'stss' 0x7423C53 [492] Sync Sample[119] (#: SamplesNumber):
             0: 1
             1: 51
             2: 101
             3: 151
             4: 201
             5: 251
             6: 301
             7: 351
             8: 401
             9: 451
            10: 501
            ...

'free' 0x7423E3F [136]

File 'video.hdr' created succesfully

Video statistics:
Sample Size: Min 0x636, Avg 0x4803, Max 0x22c3a
Samples Per Chunk: Min 16, Avg 20, Max 20

Count   119, [            21 e0 10] Size Min 0x155f, Avg 0x45ed, Max 0xc8c1
Count   118, [            21 e0 20] Size Min 0x1d48, Avg 0x4489, Max 0xb186
Count   118, [            21 e0 30] Size Min 0x16f2, Avg 0x4771, Max 0x8df6
Count   119, [            21 e2 01] Size Min 0x632, Avg 0x20af, Max 0xaa10
Count   118, [            21 e2 11] Size Min 0x1fa3, Avg 0x4420, Max 0xc4fd
Count   118, [            21 e2 21] Size Min 0x1e93, Avg 0x433f, Max 0xc011
Count   118, [            21 e2 31] Size Min 0x15c7, Avg 0x49f3, Max 0x98f8
Count   119, [            21 e4 02] Size Min 0x8ad, Avg 0x4fce, Max 0xa8e3
Count   118, [            21 e4 12] Size Min 0x2005, Avg 0x4879, Max 0xd0b5
Count   118, [            21 e4 22] Size Min 0x21ee, Avg 0x459e, Max 0xbd37
Count   119, [            21 e6 03] Size Min 0xa98, Avg 0x4e14, Max 0xeeeb
Count   118, [            21 e6 13] Size Min 0x1348, Avg 0x4619, Max 0xe59a
Count   118, [            21 e6 23] Size Min 0x2315, Avg 0x44eb, Max 0xc6ee
Count   119, [            21 e8 04] Size Min 0xce9, Avg 0x4ac0, Max 0xa42f
Count   118, [            21 e8 14] Size Min 0x18c2, Avg 0x462d, Max 0xebd9
Count   118, [            21 e8 24] Size Min 0x19c2, Avg 0x45dd, Max 0xc41f
Count   119, [            21 ea 05] Size Min 0xc91, Avg 0x4beb, Max 0xbde1
Count   118, [            21 ea 15] Size Min 0x1d91, Avg 0x499c, Max 0xf908
Count   118, [            21 ea 25] Size Min 0x18b8, Avg 0x4527, Max 0xca98
Count   119, [            21 ec 06] Size Min 0x155f, Avg 0x4b2c, Max 0xfa8f
Count   118, [            21 ec 16] Size Min 0x22cf, Avg 0x4774, Max 0xa3cf
Count   118, [            21 ec 26] Size Min 0x17f1, Avg 0x48c0, Max 0xe5f9
Count   119, [            21 ee 07] Size Min 0x15c5, Avg 0x4a87, Max 0xc117
Count   118, [            21 ee 17] Size Min 0x1fe2, Avg 0x4724, Max 0xda28
Count   118, [            21 ee 27] Size Min 0x17d1, Avg 0x461a, Max 0x8618
Count   119, [            21 f0 08] Size Min 0xd0d, Avg 0x4874, Max 0xc579
Count   118, [            21 f0 18] Size Min 0x207a, Avg 0x476c, Max 0xc844
Count   118, [            21 f0 28] Size Min 0x18de, Avg 0x4767, Max 0x9958
Count   119, [            21 f2 09] Size Min 0xed2, Avg 0x47b3, Max 0xe621
Count   118, [            21 f2 19] Size Min 0x20ea, Avg 0x456c, Max 0xbe60
Count   118, [            21 f2 29] Size Min 0x1b89, Avg 0x4423, Max 0xb7d4
Count   119, [            21 f4 0a] Size Min 0x10ef, Avg 0x49b8, Max 0xf03f
Count   118, [            21 f4 1a] Size Min 0x1ee2, Avg 0x45ff, Max 0xb1f4
Count   118, [            21 f4 2a] Size Min 0x1c4f, Avg 0x45ad, Max 0xc23c
Count   119, [            21 f6 0b] Size Min 0x104f, Avg 0x4b2f, Max 0x109c6
Count   118, [            21 f6 1b] Size Min 0x1776, Avg 0x43b7, Max 0xb80c
Count   118, [            21 f6 2b] Size Min 0x1b2f, Avg 0x46d3, Max 0xcaa5
Count   119, [            21 f8 0c] Size Min 0x13cd, Avg 0x4947, Max 0x117cb
Count   118, [            21 f8 1c] Size Min 0x1609, Avg 0x45bc, Max 0xb7f6
Count   118, [            21 f8 2c] Size Min 0x196b, Avg 0x4849, Max 0xed4e
Count   118, [            21 fa 0d] Size Min 0x1772, Avg 0x4717, Max 0x8f14
Count   118, [            21 fa 1d] Size Min 0x160e, Avg 0x43c0, Max 0xb63b
Count   118, [            21 fa 2d] Size Min 0x1968, Avg 0x4ba8, Max 0x14be9
Count   119, [            21 fc 0e] Size Min 0x15ec, Avg 0x46bc, Max 0xb2dc
Count   118, [            21 fc 1e] Size Min 0x16c4, Avg 0x450d, Max 0xb4c6
Count   118, [            21 fc 2e] Size Min 0x1a44, Avg 0x4b07, Max 0x16985
Count   119, [            21 fe 0f] Size Min 0x1403, Avg 0x48e8, Max 0xc403
Count   118, [            21 fe 1f] Size Min 0x1775, Avg 0x4419, Max 0xb41c
Count   118, [            21 fe 2f] Size Min 0x145a, Avg 0x4973, Max 0x10854
Count    59, [            25 b8 20] Size Min 0x8948, Avg 0x1796a, Max 0x22c36
Count    60, [            25 b8 40] Size Min 0x36af, Avg 0x177e3, Max 0x227b6

Now run the following command to start recovering:
recover_mp4.exe corrupted_file result.h264 --noaudio --ext

Then use ffmpeg to mux the final file:
ffmpeg.exe -r 20.000 -i result.h264 -c:v copy result.mp4



## Step2. recover_mp4.exe bad.mp4 result.h264 --noaudio --ext

使用 recover_mp4.exe 工具，将 bad.mp4 转为不带音频的 result.h264 源：



D:\WorkSpace_Malong\04.Code\Android\LAB\debug\20210523_视频无法加载>recover_mp4.exe ap845972899142565888-1.mp4 recovered.h264 --noaudio --ext
recover_mp4 v1.92 (C) 2011-2017 Dmitry Vasilyev <slydiman@mail.ru>
http://slydiman.me

Writing H264 video file 'result.h264'...
Video format: AVC video 1920x1080, Main Profile, Level 4.0
Assuming max AVC/HEVC NAL unit size (IDR) 0x3FFFFF, (non IDR) 0xFFFFF
Used AVC templates: Ext (Android, Samsung, Nokia, etc.)
Cannot open file 'audio.hdr'
Ignoring audio
Audio format: None
Searching 'mdat' atom in 'ap845972899142565888-1.mp4'...
mdat payload from 0xA8 to end of file
%0.000
H264: 0x000000A8 [0x    B20C] -> 0x      33 {25 B8 40 01} IDR frame
H264: 0x0000B2B4 [0x    380C] -> 0x    B23F {21 E2 01 09} P frame
H264: 0x0000EAC0 [0x    493C] -> 0x    EA4B {21 E4 02 0B} P frame
H264: 0x000133FC [0x    46B5] -> 0x   13387 {21 E6 03 0B} P frame
H264: 0x00017AB1 [0x    4362] -> 0x   17A3C {21 E8 04 0B} P frame
H264: 0x0001BE13 [0x    4087] -> 0x   1BD9E {21 EA 05 0B} P frame
H264: 0x0001FE9A [0x    3C69] -> 0x   1FE25 {21 EC 06 0B} P frame
H264: 0x00023B03 [0x    4143] -> 0x   23A8E {21 EE 07 0B} P frame
H264: 0x00027C46 [0x    56AE] -> 0x   27BD1 {21 F0 08 0B} P frame

...

H264: 0x03C6EF8A [0x    4B6F] -> 0x 3C6EF15 {21 F6 2B 0B} P frame
H264: 0x03C73AF9 [0x    4CF6] -> 0x 3C73A84 {21 F8 2C 0B} P frame
H264: 0x03C787EF [0x    5402] -> 0x 3C7877A {21 FA 2D 0B} P frame
H264: 0x03C7DBF1 [0x    51D9] -> 0x 3C7DB7C {21 FC 2E 0B} P frame
H264: 0x03C82DCA [0x    4935] -> 0x 3C82D55 {21 FE 2F 0B} P frame
H264: 0x03C876FF [0x    4DEA] -> 0x 3C8768A {21 E0 30 0B} P frame
H264: 0x03C8C4E9 [0x    55D5] -> 0x 3C8C474 {21 E2 31 0B} P frame
H264: 0x03C91ABE [0x    E800] -> 0x 3C91A49 {25 B8 40 01} IDR frame
H264: 0x03CA02BE [0x    3B72] -> 0x 3CA0249 {21 E2 01 09} P frame
H264: 0x03CA3E30 [0x    510B] -> 0x 3CA3DBB {21 E4 02 0B} P frame
%100.000
Complete!
H264 IDR NAL unit size: Min 0x6692, Avg 0xD631, Max 0x15F97
H264 non-IDR NAL unit size: Min 0x9E2, Avg 0x4D9B, Max 0xCB8C
Video=100.000
'result.h264' created, size 63606470 (100.000%)



## Step3. ffmpeg.exe -r 20 -i result.h264 -vcodec copy -f mp4 result.mp4

使用 ffmpeg.exe 将 result.h264 源转换为 mp4

-r 选项代表帧率

-i 代表输入文件

-f 指定输出文件格式

D:\WorkSpace_Malong\04.Code\Android\LAB\debug\20210523_视频无法加载>ffmpeg.exe -r 20 -i result.h264 -vcodec copy -f mp4 result.mp4
FFmpeg version SVN-r25512, Copyright (c) 2000-2010 the FFmpeg developers
  built on Oct 18 2010 04:06:45 with gcc 4.4.2
  configuration: --enable-gpl --enable-version3 --enable-libgsm --enable-pthreads --enable-libvorbis --enable-libtheora --enable-libspeex --enable-libmp3lame --enable-libopenjpeg --enable-libschroedinger --enable-libopencore_amrwb --enable-libopencore_amrnb --enable-libvpx --arch=x86 --enable-runtime-cpudetect --enable-libxvid --enable-libx264 --extra-libs='-lx264 -lpthread' --enable-librtmp --extra-libs='-lrtmp -lpolarssl -lws2_32 -lwinmm' --target-os=mingw32 --enable-avisynth --cross-prefix=i686-mingw32- --cc='ccache i686-mingw32-gcc' --enable-memalign-hack
  libavutil     50.32. 3 / 50.32. 3
  libavcore      0. 9. 1 /  0. 9. 1
  libavcodec    52.92. 0 / 52.92. 0
  libavformat   52.83. 0 / 52.83. 0
  libavdevice   52. 2. 2 / 52. 2. 2
  libavfilter    1.52. 0 /  1.52. 0
  libswscale     0.12. 0 /  0.12. 0
[h264 @ 0234bc10] max_analyze_duration reached
[h264 @ 0234bc10] Estimating duration from bitrate, this may be inaccurate

Seems stream 0 codec frame rate differs from container frame rate: 50.00 (50/1) -> 25.00 (50/2)
Input #0, h264, from 'result.h264':
  Duration: N/A, bitrate: N/A
    Stream #0.0: Video: h264, yuv420p, 1920x1080 [PAR 1:1 DAR 16:9], 25 fps, 25 tbr, 1200k tbn, 50 tbc
Output #0, mp4, to 'result.mp4':
  Metadata:
    encoder         : Lavf52.83.0
    Stream #0.0: Video: libx264, yuv420p, 1920x1080 [PAR 1:1 DAR 16:9], q=2-31, 25 tbn, 25 tbc
Stream mapping:
  Stream #0.0 -> #0.0
Press [q] to stop encoding
frame= 3000 fps=  0 q=-1.0 Lsize=   62140kB time=120.00 bitrate=4242.1kbits/s
video:62116kB audio:0kB global headers:0kB muxing overhead 0.039350%



**result.mp4 即为修复后的MP4文件**


## 后话
实际，Step1 的目的是生成 video.hdr 
所以只需要保证 video.hdr 在执行命令的根目录下，只需要执行 Step2、Step3
批处理脚本：略