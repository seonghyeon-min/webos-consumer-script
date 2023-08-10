import os
import re
import platform
import shutil
import sys
import csv

PopularSocNameForVersion23 = {
    1: 'kf23f',
    2: 'kid23q',
   #3: 'k8hpp' ## drop Soc
}

PopularBranchNames = {
    'kid23q' : [
                '@52.webos4tv', # for kid23q from wall
               ],
    'kif23f' : [
                '@it.52.webos4tv.49',
                '@it.52.webos4tv.56',
               ] # for kf23f from itsw
}

'''
Make build-starfish git dir temporarily
The temp directory name will be changed
return: temp git directory
'''

def CloneConsumerGit() :
    SoC, branch = GetSoCBranchName()
    # make tmp dir
    progdir = os.path.dirname(os.path.realpath(__file__))
    tmpdir_wall = os.path.join(progdir, 'tmp_wall_starfish-customization-consumer')
    tmpdir_itsw = os.path.join(progdir, 'tmp_itwsw_starfish-customization-consumer')

    # clone git
    if SoC == 'kf23f' :
        cmdline = 'git clone "ssh://seonghyeon.min@itsw.lge.com:29418/starfish/starfish-customization-consumer" && + \
                   scp -p -P 29418 seonghyeon.min@itsw.lge.com:hooks/commit-msg "starfish-customization-consumer/.git/hooks/" ' + tmpdir_itsw
        gitdir = os.path.join(progdir, tmpdir_itsw)
    elif SoC == 'kid23q' :
        cmdline = 'git clone "ssh://seonghyeon.min@wall.lge.com:29448/starfish/starfish-customization-consumer" && +\
                  (cd "starfish-customization-consumer" && gitdir=$(git rev-parse --git-dir); + \
                   curl -o ${gitdir}/hooks/commit-msg https://wall.lge.com/static/commit-msg ; chmod +x ${gitdir}/hooks/commit-msg) ' + tmpdir_wall
        gitdir = os.path.join(progdir, tmpdir_wall)
    else :
        print('Unknown SoC ' + SoC )
        exit()

    if not os.path.exists(gitdir) :
        os.system(cmdline)

    if not os.path.exists(gitdir):
        print('  ** Check your git permission')
        print('  ** Check cmdline: "{0}"'.format(cmdline))
        return ''

    return gitdir


'''
Get branch names from git repo in the current working directory
And select the branch name 
return: selected branch name, SoC
'''

def GetSoCBranchName() :
    SoC, branchname = None, None
    PopularSoC, PopularBranchname = PopularSocNameForVersion23, PopularBranchNames
    while True :
        print('-- Select SoC--'.center(40))
        for key in PopularSoC.keys() :
            print('{0:10}. {1}'.format(key, PopularSoC[key]))
        print('---------------------------------'.center(40))
    
        try : 
            inputstr = str(input('> select num or input Soc name : '))
        except SystemError :
            inputstr = ''

        # in case of digit input
        print(type(inputstr))
        if inputstr.isdigit() :
            inputnum = int(inputstr)
            if inputnum in PopularSoC.keys() :
                SoC = PopularSoC[inputnum]
                break
            else :
                print('> Warning: select valid number')
                continue

        # in case of string input
        else :
            inputstr = str.lower(inputstr)
            if inputstr in PopularSoC.values() :
                SoC = inputstr
                break
            else :
                try :
                    flag = str(input('> Warning: cannot finr "' + inputstr + '". Do you want to see SoC list (y/N)'))
                except SyntaxError :
                    flag = ''

                if flag == 'y' or flag == 'Y' :
                    print('----------SoC list-----------'.center(40))
                    for key in PopularSoC.keys() :
                        print('{0:10}. {1}'.format(key, PopularSoC[key]))
                    print('---------------------------------\n'.center(40))
                continue

    while True :
    # select the branch list 
        print("-- select branch of SoC that you've selected--".center(40))
        for value in PopularBranchname[SoC] :
            print('{0:10}. {1}'.format(PopularBranchname[SoC].index(value), value))
        print('---------------------------------\n'.center(40))

        try : 
            inputstr = str(input('> select num or input branch : '))
        except SyntaxError :
            inputstr = ''

        if inputstr.isdigit() :
            inputnum = int(inputstr)
            if inputnum in range(len(PopularBranchname[SoC])-1) :
                branchname = PopularBranchname[SoC][inputnum]
                break
            else :
                print('> Warning: select valid number')
                continue
        
        else :
            if inputstr in PopularBranchname[SoC] :
                branchname = inputstr
                break
            else :
                print('> Warning: input right branch-name')
                continue

    cmdline = 'git checkout ' + branchname
    os.system(cmdline)

    return SoC, branchname

'''
Get app list to add or delete
return App list, mode(add or delete)
'''
def GetAppList() :
    # 뭔가 삭제할 앱을 가져와야할 듯? 국가마다 앱리스트가 다름...
    gitdir = CloneConsumerGit()
    Countrys = os.listdir(os.path.join(gitdir, 'SoC', 'launchpoints'))

    for country in Countrys :

