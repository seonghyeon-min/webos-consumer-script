import os
import re
import platform
import shutil
import sys
import csv
import json

MODULE_NAME = 'starfish-customization-consumer'

PopularSocNameForVersion23 = {
    1: 'kf23f',
    2: 'kid23q',
   #3: 'k8hpp' ## drop Soc
}

PopularBranchNames = {
    'kid23q' : [
                '@52.webos4tv', # for kid23q from wall
               ],
    'kf23f' : [
                '@it.52.webos4tv.49',
                '@it.52.webos4tv.56',
               ] # for kf23f from itsw
}

PopularAppNames = {
    1: 'com.webos.app.discovery',
    2: 'com.webos.app.sportsteamsettings',
    3: 'com.webos.app.homeconnect',
    4: 'com.webos.app.browser',
    5: 'com.webos.app.mediadiscovery',
    6: 'amozon.alexa.view'
}

'''
Make build-starfish git dir temporarily
The temp directory name will be changed
return: temp git directory
'''

def CloneConsumerGit() :
    SoC, branchname = GetSoCBranchName()
    # make tmp dir
    progdir = os.getcwd() # get current directory
    
    if SoC == 'kf23f' :
        cmdline = 'mkdir cached_itsw_starfish_customization_consumer'
    elif SoC == 'kid23q' :
        cmdline = 'mkdir cached_wall_starfish_customization_consumer'
    else :
        print('Unknown SoC ' + SoC)
        exit()    
    
    tmpdir_wall = os.path.join(progdir, 'cached_wall_starfish_customization_consumer')
    tmpdir_itsw = os.path.join(progdir, 'cached_itsw_starfish_customization_consumer')

        
    # clone git
    if SoC == 'kf23f' :
        if not os.path.exists(tmpdir_itsw) :
            os.system(cmdline)
        os.chdir(tmpdir_itsw)
        cmdline = 'git clone "ssh://seonghyeon.min@itsw.lge.com:29418/starfish/starfish-customization-consumer" && scp -p -P 29418 seonghyeon.min@itsw.lge.com:hooks/commit-msg "starfish-customization-consumer/.git/hooks/"'
        gitdir = os.path.join(progdir, tmpdir_itsw)
    elif SoC == 'kid23q' :
        if not os.path.exists(tmpdir_wall) :
            os.system(cmdline)
        os.chdir(tmpdir_wall)
        cmdline = 'git clone "ssh://seonghyeon.min@wall.lge.com:29448/starfish/starfish-customization-consumer" && (cd "starfish-customization-consumer" && gitdir=$(git rev-parse --git-dir); curl -o ${gitdir}/hooks/commit-msg https://wall.lge.com/static/commit-msg ; chmod +x ${gitdir}/hooks/commit-msg)'
        gitdir = os.path.join(progdir, tmpdir_wall)
    else :
        print('Unknown SoC ' + SoC )
        exit()

    os.system(cmdline) # git-clone cmdline  
    gitdir = os.path.join(gitdir, MODULE_NAME)
    os.chdir(gitdir)
    
    if not os.path.exists(gitdir) :
        os.system(cmdline)

    if not os.path.exists(gitdir):
        print('  ** Check your git permission')
        print('  ** Check cmdline: "{0}"'.format(cmdline))
        return ''
    
    cmdline = 'git checkout ' + branchname
    os.system(cmdline)

    return gitdir, SoC, branchname


'''
Get branch names from git repo in the current working directory
And select the branch name 
return: selected branch name, SoC
'''

def GetSoCBranchName() :
    SoC, branchname = None, None
    PopularSoC, PopularBranchname = PopularSocNameForVersion23, PopularBranchNames
    while True :
        print('-- Select SoC --'.center(40))
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
                    flag = str(input('> Warning: cannot find "' + inputstr + '". Do you want to see SoC list (y/N)'))
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
            if inputnum in range(len(PopularBranchname[SoC])) :
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
            
    return SoC, branchname

'''
Get app list to add or delete
return App list, mode(add or delete)
'''
def GetAppList(currentdir) :
    countrys = os.listdir(currentdir)

    Apps = []
    while True :
        # show the app list or input app name by themselves.
        flag = str(input('> Do you want to show Popular app list (y/N) ?'))
        if flag == 'y' or flag == 'Y' :
            print('-- select popular App names --'.center(40))
            for key in PopularAppNames.keys() :
                print('{0:10}. {1}'.format(key, PopularAppNames[key]))
            print('---------------------------------'.center(40))

            try :
                inputstrs = input('> select several number from applist : ').replace(' ', '').split(',')
                inputstrs = list(filter(None, inputstrs))
            except SyntaxError :
                inputstrs = ''
            
            for inputstr in inputstrs :
                if inputstr.isdigit() :
                    inputnum = int(inputstr)
                    if inputnum in PopularAppNames.keys() :
                        Apps.append(PopularAppNames[inputnum])
                else :
                    print('> Warning: select valid number : {}, please make sure app-name.'.format(inputstr))
            break
        else :
            Apps = input('> Input App names you want to modify : ').replace(' ', '').split(',')
            print('Apps list = ', Apps)
            break
    
    if Apps != [] :
        for country in countrys :
            AppDir = os.path.join(currentdir, country, 'applist.json')
            with open(AppDir, 'rb') as file :
                content = file.read()
                
            content_decoded = content.decode('utf-8')
            data = json.loads(content_decoded)
            
            for key, value in data.items() :
                for App in Apps :
                    if App in value :
                        data[key].remove(App)
            
            json_str = json.dumps(data, indent=4).replace('\n', '\r\n')
            json_bytes = json_str.encode('utf-8')
            
            with open(AppDir, 'wb') as file :
                file.write(json_bytes)
    
    elif Apps == [] :
        print('> Warning : There are no some apps to delete')

            
def DoCommit(branchname) :
    cmdline = ['git status', 'git add .', 'git commit']
    for cmd in cmdline :
        os.system(cmd)
        
    # after writing commit message 
    os.system('git push origin HEAD:refs/for/' + branchname)

def CliMode() :
    curdir = os.getcwd()
    progdir = os.path.dirname(os.path.realpath(__file__))
    print('<< Start starfish-customization-consumer Modification for CLI mode >>')
    tempgitdir, SoC, branchname = CloneConsumerGit()
    os.chdir(os.path.join(tempgitdir, SoC, 'launchpoints'))
    GetAppList(os.getcwd())
    DoCommit(branchname)

if __name__ == '__main__' :
    print('<< Start Modification of Apps >>')
    print('')
    CliMode()
    print('<< End Modification of Apps >>')