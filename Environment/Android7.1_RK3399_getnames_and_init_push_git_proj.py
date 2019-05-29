#!/usr/bin/python3

import os
import sys

remote = 'ssh://qxzn-git@10.10.7.83/repo'

if len(sys.argv) == 1:
    print('错误！请传入 xml 文件')
elif len(sys.argv) > 2:
    print('错误！传入参数太多')
else:
    print('传入的文件是 %s' % sys.argv[1])

with open(sys.argv[1], 'r') as fin:
    while True:
        linestr = fin.readline()
        if linestr == '':       #表示文件结束
            break
        #print(linestr)
        #下面开始对本行内容分析
        if (('name=' in linestr) or ('name =' in linestr)) and (('project' in linestr) or ('path' in linestr)):   #本行内容含有name信息
            #print(linestr)
            #先无条件提取name路径
            charistr1 = 'name="'
            charistr2 = '"'
            namestr = linestr[linestr.index(charistr1)+len(charistr1) : linestr.index(charistr1)+len(charistr1)+ linestr[linestr.index(charistr1)+len(charistr1):].index(charistr2)]
            if 'path=' in linestr:            #如果path存在则用path的路径作为本地路径
                charistr1 = 'path="'
                charistr2 = '"'
                pathstr = linestr[linestr.index(charistr1)+len(charistr1) : linestr.index(charistr1)+len(charistr1)+ linestr[linestr.index(charistr1)+len(charistr1):].index(charistr2)]
            else:                             #如果path不存在，则认为path路径（本地路径）就是name路径
                pathstr = namestr
            #print('name="%s", path="%s"' % (namestr, pathstr))
            #下面开始初始化并提交git工程
            localpath = sys.path[0] + '/' + pathstr        # git工程的本地绝对路径
            remotepath = remote + '/' + namestr            # git工程远程相对路径

            #判断本地目录是否为空，为空的话则新建一个文件，空目录会导致git提交失败
            if not os.listdir(localpath):       # 本地目录为空
                #cmd = 'touch %s/._USELESSFILE_' % (localpath)
                cmd = 'touch %s/.gitignore' % (localpath)
                print(cmd)
                os.system(cmd)
            
            cmd = 'cd %s && rm -rf .git && git init && git remote add origin %s && git add . -f && git commit -m "init" &&git push -u origin master && cd %s' % (localpath, remotepath, sys.path[0])
            print(cmd)
            os.system(cmd)
