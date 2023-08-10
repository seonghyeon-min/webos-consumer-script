'''
2015. 03. 20. (kyungnam.bae) Initial Release for webOS auto build tool
2015. 03. 21. (kyungnam.bae) Change Build Directory Name to [platform] + [branch] + [versionNum]
2015. 06. 27. (kyungnam.bae) Add webOS 3.0 build feature
2015. 07. 08. (kyungnam.bae) Parsing the multiple lines for the platform types
2016. 05. 06. (kyungnam.bae) Add webOS 4.0 (= master branch) build feature
2016. 07. 09. (kyungnam.bae) Add @deua branch for webOS 3.0. The drd4tv branch is for 17year webos.
2017. 04. 30. (kyungnam.bae) Add @dharug branch for webOS 3.5 and webOS 4.0 (=gld4tv branch) build feature. The version of master branch is moved to webOS 5.0.
2017. 11. 30. (kyungnam.bae) Add branches based on the 'http://collab.lge.com/main/display/WOSTVBUILD/webOS+TV+Build+Collab' page.
                             Add the supported version webOS 3.5. Some branches are moved to webOS 3.5 from webOS 3.0 version.
                             Add region(ATSC|DVB|ARIB) and image(flash|nfs|secured) and develop type to build tv image.
2017. 12. 12. (kyungnam.bae) Add branches for 'webOS TV 4.0 Initial Release Branch'.
2018. 06. 18. (kyungnam.bae) Add webOS 4.5 as default build version.
                             Currently o18 and m16p3 are using 64bit kernel. So when building an image 'lib32-' prefix is needed.
                             In other words, use 'bitbake lib32-starfish-atsc-flash' in the m16p3 and o18 platform. Use 'bitbake starfish-atsc-flash' for the others.
2019. 01. 16  (kyungnam.bae) Add webOS 4.5 product branches and webOS 5.0 branch
2019. 02. 22  (kyungnam.bae) Add webOS 4.5 MR Minor branch
2019. 03. 13  (kyungnam.bae) Add webOS 5.0 branch and webOS 6 for master
2019. 05. 27  (kyungnam.bae) Set default version to webOS 5.0 and check the ubuntu version to build it
2019. 06. 13  (kyungnam.bae) Copy *webos-local.conf file if it's exists
2019. 09. 11  (kyungnam.bae) Delete lib32- prefix when build k6hp, k6lp, lm20u, lm20a
2020. 03. 23  (kyungnam.bae) Add webOS 5.0 & 6.0 branches and modify webOS 6.0 repo url to wall from lgsvl
2020. 07. 02  (kyungnam.bae) Add 'global' region for webOS 6.0 and @japoon.nmrm branch for o20t
2020. 07. 10  (kyungnam.bae) Fix webOS 6.0 build error and follow http://collab.lge.com/main/pages/viewpage.action?pageId=1117897747 guide
2020. 10. 14  (kyungnam.bae) Add webOS 6.0 Initial Product Branch
2020. 11. 18  (kyungnam.bae) Add webOS 6.0 nmrm branch
2021. 07. 13  (kyungnam.bae) Add webOS 22 machine and use lib32- prefix for the bitbake command
2021. 09. 06  (kyungnam.bae) Add webOS 22 develop branch mlt4tv and webOS 6.0 MR3 branch kavir
2022. 03. 22  (kyungnam.bae) Change raw_input to input to support python3
2022. 06. 20  (kyungnam.bae) Assert if do not use python3 or upper version
2022. 08. 12  (kyungnam.bae) Add webOS 23 branches
2022. 11. 02  (kyungnam.bae) Change the cmd_bitbake.sh path fromt the working directory to the path of the webos_build_script.py file
2023. 05. 09  (kyungnam.bae) Apply configuration file for the full auto build. Apply submodule of build-starfish repo in order not to download it every time.
2023. 05. 09  (kyungnam.bae) Apply new parameters for mcf and Modify branch names

@author: kyungnam.bae@lge.com
'''

import os
import re
import platform
import shutil
import sys
import csv

'''
If you want to add the Popular Branch Names,
please follow below format
  num : 'branchname'

See the details for branch names in the weblink below
 - http://collab.lge.com/main/pages/viewpage.action?pageId=1091732245
'''
PopularBranchNamesForVersion24 = {
    1: '@obr4tv', # webOS TV 24 Develop Branch
    2: '@odaesan', # webOS 24 Initial
    3: '@webos4tv'
}

PopularBranchNamesForVersion23 = {
    1: '@nbr4tv', # webOS TV 23 Develop Branch
    2: '@naejangsan', # webOS 23 Initial / 양산 브랜치
    3: '@nairobi', # webOS 23 MR1 / 양산 브랜치
    4: '@14.nairobi', # webOS 23 Wireless M3 개발 / 양산 브랜치
    4: '@nairobi.rtk23', # webOS 23 MR1 / 양산 브랜치 (kf23f, kf23fwee only)
    5: '@nambung', # webOS 23 MR2 / 양산 브랜치
    6: '@nambung.pine' # PINE23 (webOS23 MR2 + PINE) /양산 브랜치
}

PopularBranchNamesForVersion22 = {
    1: '@mlt4tv', # webOS 22 + WEE 2.0 / 개발 브랜치
    2: '@manas', # webOS 22 Initial / 양산 브랜치
    3: '@maria', # webOS 22 MR1 (First Day SU) MR4 / 양산 브랜치
    4: '@marine', # webOS 22 MR5 / 양산 브랜치
    5: '@maria.wee', # WEE 2.0 Initial / 개발/양산 브랜치
    6: '@22.maria.wee', # WEE 2.0 Smart Screen / 개발/양산 브랜치
    7: '@mebbin', # webOS 22 MR3/MR7/MR9
    8: '@mebbin.wee', # webOS 22 WEE 2.0 MR2/MR3 / 개발/양산 브랜치
    9: '@mebbin.nmrm' # webOS 22 WEEKND 개발/양산 브랜치
}

PopularBranchNamesForVersion6 = {
    1: '@kcl4tv', # develop branch - webOS 6.0
    2: '@kalaupapa', # Initial - 6.0.0
    3: '@45.kalaupapa', # MR1 - 6.0.1
    4: '@katmai', # MR2 - 6.1.0
    5: '@kavir', # MR3 - 6.2.0
    6: '@24.kavir', # MR4 알폰소 ACR , 북미 Only - 6.2.1
    7: '@kinglake', # MR5 - 6.3.0
    8: '@4.kinglake', #MR6 - 6.3.1, MR7 - 6.3.2, MR9 - 6.3.3
    9: '@kluane', # 6.4.0

    # StandbyMe branches
    10: '@kcl4tv.nmrm', # develop branch - StanbyMe
    11: '@kalaupapa.nmrm', # KOR Initial - 6.0.1
    12: '@48.kalaupapa.nmrm', # Global Initial - 6.0.1
    13: '@katmai.nmrm', # MR2 - 6.1.0
    14: '@kavir.nmrm', # MR3 - 6.2.0
    15: '@kinglake.nmrm', # MR4 - 6.3.1
    16: '@kluane.nmrm' # MR5 - 6.4.0
}

PopularBranchNamesForVersion5 = {
    1: '@jcl4tvmr', # develop branch
    2: '@jasper', # MR4 - 5.3.0 & 5.3.1 (wee MR3)
    3: '@22.jasper', # MR6 - 5.3.2 알폰소 ACR , 북미 Only
    4: '@jebil', # MR7 - 5.4.1, MR8 - 5.4.2, MR9 - 5.4.3
    5: '@jervisbay' # MR10 - 5.5.0
}

PopularBranchNamesForVersion4_5 = {
    1: '@gld4tv', # develop branch
    2: '@gympie', # MR8 4.9.5
    3: '@1.gympie', # MR8 - 4.9.6 알폰소 ACR , 북미 Only
    4: '@gyeon' # MR10 - 4.9.7
}

PopularBranchNamesForVersion4 = {
    1: '@glacier', # develop branch
    2: '@194.gayasan.m16ppez', # Initial - 4.0.0 m16p 한국 Easy TV
    3: '@gorce', # MR5 - 4.4.0
    4: '@10.gorce', # MR6 - 4.4.1 알폰소 ACR , 북미 Only
    5: '@gorongosa' # MR7 - 4.4.2
}

PopularBranchNamesForVersion3_5 = {
    1: '@drd4tv', # develop branch
    2: '@9.dorrigo.m16pbno', # MR - 3.6.1 M16p BNO
    3: '@439.dixie.m16pstb', # Initial - 3.5.0 M16p STB

    # MR3 - 3.9.0
    4: '@627.dudhwa.m16p',
    5: '@628.dudhwa.m16plite',
    6: '@629.dudhwa.k3lp',
    7: '@630.dudhwa.m2r',

    # MR4 - 3.9.1 알폰소 ACR , 북미 Only
    8: '@62709.dudhwa.m16p',
    9: '@62804.dudhwa.m16plite'
}

PopularBranchNamesForVersion3 = {
    1: '@dharug', # develop branch
    2: '@235.deathvalley.k2lpez', # Initial - 3.0.0 한국향 Eazy TV
    3: '@19818.deathvalley.k2lptl', # Initial - 3.0.0 tunerless TV

    # MR3 - 3.4.0
    4: '@57.digya.k2l',
    5: '@58.digya.k2lp',
    6: '@59.digya.m16lite',
    7: '@60.digya.h15',
    8: '@61.digya.m16',
    9: '@62.digya.m2',

    # MR4 - 3.4.1 알폰소 ACR , 북미 Only
    10: '@6107.digya.m16',
    11: '@5908.digya.m16lite',
    12: '@5709.digya.k2l',
    13: '@5805.digya.k2lp'
}

PopularBranchNamesForVersion2 = {
    1: '@21.biscayne.lm15u',
    2: '@1.biscayne.m14tv',
    3: '@3.biscayne.h15',
    4: '@13.biscayne.lm14a',
    5: '@31.bighorn.mtka5lr',
    6: '@34.bighorn.lm14alite'
}

PopularBranchNamesForVersion1 = {
    1: '@23.ashley.goldfinger',
    2: '@25.ashley.m14tv'
}

'''
Make build-starfish git dir temporarily
The temp directory name will be changed
return: temp git directory
'''
def CloneBuildStarfishGit(version):
    # make temp dir
    progdir = os.path.dirname(os.path.realpath(__file__))
    tmpdir_polar = os.path.join(progdir, 'cached_polar_build-starfish')
    tmpdir_wall = os.path.join(progdir, 'cached_wall_build-starfish')

    # git clone to cached_* dir
    if version == '2' or version == '1':
        cmdline = 'git clone ssh://gpro.palm.com/starfish/build-starfish.git ' + tmpdir_polar
        gitdir = os.path.join(progdir, tmpdir_polar)
    elif float(version) >= 3.0:
        cmdline = 'git clone ssh://wall.lge.com/starfish/build-starfish.git ' + tmpdir_wall
        gitdir = os.path.join(progdir, tmpdir_wall)
    else:
        print('Unknown version ' + version)
        exit()

    if not os.path.exists(gitdir):
        os.system(cmdline)

    # check git clone error case
    if not os.path.exists(gitdir):
        print('  ** Check your git permission')
        print('  ** Check cmdline: "{0}"'.format(cmdline))
        return ''

    return gitdir

'''
Get branch names from git repo in the current working directory
And select the branch name for build
return: selected branch name
'''
def GetBranchName(version):
    branchname = None
    if version == '24':
        PopularBranchNames = PopularBranchNamesForVersion24
    elif version == '23':
        PopularBranchNames = PopularBranchNamesForVersion23
    elif version == '22':
        PopularBranchNames = PopularBranchNamesForVersion22
    elif version == '6':
        PopularBranchNames = PopularBranchNamesForVersion6
    elif version == '5':
        PopularBranchNames = PopularBranchNamesForVersion5
    elif version == '4.5':
        PopularBranchNames = PopularBranchNamesForVersion4_5
    elif version == '4':
        PopularBranchNames = PopularBranchNamesForVersion4
    elif version == '3.5':
        PopularBranchNames = PopularBranchNamesForVersion3_5
    elif version == '3':
        PopularBranchNames = PopularBranchNamesForVersion3
    elif version == '2':
        PopularBranchNames = PopularBranchNamesForVersion2
    elif version == '1':
        PopularBranchNames = PopularBranchNamesForVersion1
    else:
        print('Unknown version ' + version)
        exit()

    # set command line for getting branch names
    cmdline = 'git branch --all'

    fp = os.popen(cmdline)
    branchnames = fp.read()
    fp.close()

    # extract branch names to list
    branchnames = re.split('\n\s*remotes/origin/', branchnames)

    # 1st item will be changed from '* master' to 'master'
    branchnames[0] = branchnames[0][2:]
    # last item will be changed from '....\n' to '....'
    branchnames[-1] = branchnames[-1][0:-1]

    while True:
        while True:
            # print popular branch names
            print('-- select popular branch names --'.center(40))
            for key in PopularBranchNames.keys():
                print('{0:10}. {1}'.format(key, PopularBranchNames[key]))
            print('---------------------------------'.center(40))

            try:
                inputstr = str(input('> select num or input branch name: '))
            except SyntaxError:
                inputstr = ''

            # in case of digit input
            print(type(inputstr))
            if inputstr.isdigit():
                inputnum = int(inputstr)
                if inputnum in PopularBranchNames.keys():
                    branchname =  PopularBranchNames[inputnum]
                    break
                else:
                    print('> Warning: select valid number')
                    continue
            # in case of string input
            else:
                if inputstr in branchnames:
                    branchname = inputstr
                    break
                else:
                    try:
                        flag = str(input('> Warning: cannot find "' + inputstr + '". DO you want to see branch names (y/N)'))
                    except SyntaxError:
                        flag = ''

                    if flag == 'y' or flag == 'Y':
                        print('----------branch names-----------'.center(40))
                        for name in branchnames:
                                print('{0:10}{1}'.format(' ', name))
                        print('---------------------------------\n'.center(40))
                    continue

        # change branch in the git
        cmdline = 'git checkout ' + branchname
        if os.system(cmdline) == 0:
            os.system('git pull --all')
            break
        else:
            print(cmdline + ' error')
            print('select branch again')

    return branchname

'''
Parsing weboslayers.py file for extracting platform types
And select the platform type for build
return: selected branch name
'''
def GetPlatformType():
    # set command line for getting platform types
    cmdline = "cat weboslayers.py | grep 'Machines '"

    platformtypes = []

    # extract platform types to list
    with os.popen(cmdline) as fp:
        for line in iter(fp.readline, ''):
            line = line[ line.find("'") + 1 : line.rfind("'") ]
            platformtypes.extend(re.split("'\s*,\s*'", line))

        fp.close()

    platformtype = None

    while True:
        # print platform types
        print('----- select platform types -----'.center(40))
        idx = 0
        for type in platformtypes:
            idx += 1
            print('{0:10}. {1}'.format(idx, type))
        print('---------------------------------\n'.center(40))

        try:
            inputstr = str(input('> select num: '))
        except SyntaxError:
            inputstr = ''

        # in case of digit input
        if inputstr.isdigit():
            idx = int(inputstr)

            if idx <= len(platformtypes):
                platformtype = platformtypes[idx - 1]
                break
            else:
                print('> Warning: select valid number')
                continue
        else:
            print('> Warning: select valid number')
            continue

    return platformtype

'''
Parsing the tags of git
And select the tag name and then extract Hash value for git reset
return: (Tag name, Hash)
'''
def GetVersionNumber(branchname, inputVersion = ''):
    # set command line for getting tags
    if "@" in branchname:
        cmdline = 'git show-ref | grep /' + branchname[1:]
    else:
        cmdline = 'git show-ref | grep ' + branchname

    tags = dict()
    digittags = list()

    with os.popen(cmdline) as fp:
        # tag sample "hash reference"
        # "666f245f007380341085e03c509cce0b0c21a2e6 refs/tags/builds/beehive4tv/252"
        # tags = { reference : hash }
        for line in iter(fp.readline, ''):
            tagreference = line[ line.rfind('/') + 1 : -1 ]
            taghash = line[ : line.find(' ')]
            tags[tagreference] = taghash

            # if the tag reference is number, append it to temp list for extracting max value
            if tagreference.isdigit():
                digittags.append(int(tagreference))
        fp.close()

    if len(digittags) == 0:
        exit('> Error: tag does NOT exist (cmd: "{0}")'.format(cmdline))

    # extract max number from tag reference
    latesttag = max(digittags)

    if inputVersion == '':
        while True:
            try:
                inputstr = str(input('> select version num. latest(default) is {0} : '.format(latesttag)))
            except SyntaxError:
                inputstr = ''

            if inputstr == '':
                inputstr = str(latesttag)
                break

            if inputstr in tags.keys():
                break

            else:
                print('> Warning: cannot find "' + inputstr + '"')
                continue
    elif inputVersion == 'latest':
        inputstr = str(latesttag)
    else:
        inputstr = inputVersion


    # git reset for the specific tag
    cmdline = 'git reset --hard {0}'.format(tags[inputstr])
    os.system(cmdline)

    return (inputstr, tags[inputstr])

'''
Change build-starfish temp dir to the build directory what user wants
return: changed build-starfish git directory
'''
def ChangeBuildDirectory(gitdir, branch, platform, tags, custompath):
    if "@" in branch:
        defaultdir = 'build-starfish_' + platform + '_' + branch[1:] + '_' + tags[0]
    else:
        defaultdir = 'build-starfish_' + platform + '_' + branch + '_' + tags[0]

    if not custompath:
        outputdir = os.path.join(os.getcwd(), defaultdir)

        while True:
            if os.path.exists(outputdir):
                print('> Warning: already exist the dir "' + outputdir + '"')
                outputdir += '_'
                continue
            else:
                break
    else:
        while True:
            try:
                inputstr = str(input('> write build dir (default is {0}) : '.format(defaultdir)))
            except SyntaxError:
                inputstr = ''

            if not inputstr == '':
                outputdir = inputstr
            else :
                outputdir = defaultdir

            outputdir = os.path.join(os.getcwd(), outputdir)

            if os.path.exists(outputdir):
                print('> Warning: already exist the dir "' + outputdir + '"')
                continue
            else :
                break

    os.system('cp -r ' + gitdir + ' ' + outputdir)
    return outputdir

'''
Select one of the *webos-local.conf file and copy it to build directory
return: changed build-starfish git directory
'''
def CopyLocalBuildFiles(builddir, inputfile):
    if not os.path.exists(builddir):
        return

    if inputfile == '':
        localbuildfiles = ['not use']
        localbuildfile = ''

        for fname in os.listdir('.'):
            if fname.endswith('webos-local.conf'):
                localbuildfiles.append(fname)

        if len(localbuildfiles) == 1:
            return

        print('---- select local build file ----'.center(40))
        idx = 0
        for fname in localbuildfiles:
            idx += 1
            print('{0:10}. {1}'.format(idx, fname))
        print('---------------------------------'.center(40))

        while True:
            try:
                inputstr = str(input('> select num: (default is 1 (=not use)) : '))
            except SyntaxError:
                inputstr = ''

            if inputstr == '' or inputstr == '1':
                return

            if inputstr.isdigit():
                idx = int(inputstr)

                if idx <= len(localbuildfiles):
                    localbuildfile = localbuildfiles[idx - 1]
                    break
                else:
                    print('> Warning: select valid number')
                    continue
            else:
                print('> Warning: select valid number')
                continue
    else:
        localbuildfile = inputfile

    if os.path.exists(localbuildfile):
        print('> use local build file. ' + localbuildfile + '.')
        shutil.copy2(localbuildfile, os.path.join(builddir, 'webos-local.conf'))
    else:
        print('> Warning: cannot find ' + localbuildfile + '.')


'''
Select ATSC / DVB / ARIB type
'''
def GetBuildRegion(webosVersion):
    print('--------- select region ---------'.center(40))
    if float(webosVersion) >= 6.0:
        print('         1. global')
        print('         2. arib')
    else:
        print('         1. atsc')
        print('         2. dvb')
        print('         3. arib')
    print('---------------------------------'.center(40))

    while True:
        if float(webosVersion) >= 6.0:
            try:
                inputstr = str(input('> select region num (default is 1 (=global)) : '))
            except SyntaxError:
                inputstr = ''

            if inputstr == '1' or inputstr == '':
                output = 'global'
            elif inputstr == '2':
                output = 'arib'
            else:
                print('')
                continue
            break
        else:
            try:
                inputstr = str(input('> select region num (default is 1 (=atsc)) : '))
            except SyntaxError:
                inputstr = ''

            if inputstr == '1' or inputstr == '':
                output = 'atsc'
            elif inputstr == '2':
                output = 'dvb'
            elif inputstr == '3':
                output = 'arib'
            else:
                print('')
                continue
            break

    return output

'''
Select nfs or flash (=.epk) or secured (=usb update) type
'''
def GetImageType():
    print('--------- select image type ---------'.center(40))
    print('         1. epk(=flash)')
    print('         2. nfs')
    print('         3. secured(=usb update)')
    print('-------------------------------------'.center(40))

    while True:
        try:
            inputstr = str(input('> select image type num (default is 1. (=epk)): '))
        except SyntaxError:
            inputstr = ''

        if inputstr == '1' or inputstr == '':
            output = 'flash'
        elif inputstr == '2':
            output = 'nfs'
        elif inputstr == '3':
            output = 'secured'
        else:
            print('')
            continue
        break

    return output

'''
Select develop image
'''
def IsDeveloperImage():
    try:
        inputstr = str(input('> Do you want make image for DEVELOPER (y/N): '))
    except SyntaxError:
        inputstr = ''

    if inputstr == 'y' or inputstr == 'Y':
        output = 'devel'
    else:
        output = ''

    return output

'''
Execute bitbake command line script
'''
def MakeImage(progdir, platformtype, version, region, imagetype, fordevelop):
    # make mcf command
    if version == '1':
        cmdline = './mcf -b 8 -p 8 {0} --premirror=file:///starfish_afro/downloads --sstatemirror=file:///starfish_afro/sstate-cache'.format(platformtype)
    elif version == '2':
        cmdline = './mcf -b 8 -p 8 {0} --premirror=file:///starfish_beehive/downloads --sstatemirror=file:///starfish_beehive/sstate-cache'.format(platformtype)
    elif version == '3':
        cmdline = './mcf -b 8 -p 8 {0} --premirror=file:///starfish_drd/downloads --sstatemirror=file:///starfish_drd/sstate-cache'.format(platformtype)
    elif version == '3.5':
        cmdline = './mcf -b 8 -p 8 {0} --premirror=file:///starfish_drd/downloads --sstatemirror=file:///starfish_drd/sstate-cache'.format(platformtype)
    elif version == '4':
        cmdline = './mcf -b 8 -p 8 {0} --premirror=file:///starfish_gld/downloads --sstatemirror=file:///starfish_gld/sstate-cache'.format(platformtype)
    elif version == '4.5':
        cmdline = './mcf -b 8 -p 8 {0} --premirror=file:///starfish_gld/downloads --sstatemirror=file:///starfish_gld/sstate-cache'.format(platformtype)
    else:
        cmdline = './mcf -b 8 -p 8 {0} --premirror=file:///starfish/downloads --sstatemirror=file:///starfish/sstate-cache'.format(platformtype)

    os.system(cmdline)

    if version == '2' or version == '1':
        # change the working directory for bitbake command
        builddir = os.path.join(os.getcwd(), 'BUILD-{0}'.format(platformtype))
        os.chdir(builddir)

        # copy the shell script for bitbake
        cmdline = 'cp ' + os.path.join(progdir, 'cmd_bitbake.sh') + ' ' + builddir
        os.system(cmdline)
    else:
        # copy the shell script for bitbake
        cmdline = 'cp ' + os.path.join(progdir, 'cmd_bitbake.sh') + ' ./'
        os.system(cmdline)

    # modify webos version for kernel 64bit build
    if (platformtype == 'm3r' or platformtype == 'lm19a' or platformtype == 'k5lp' or platformtype == 'k5ap' or platformtype == 'lm20a' or platformtype == 'lm20u' or platformtype == 'k6hp' or platformtype == 'k6lp' or platformtype == 'lm21a' or platformtype == 'lm21u' or platformtype == 'lm21ut' or platformtype == 'k7hp' or platformtype == 'k7lp') and (version == '4.5' or version == '5' or version == '6'):
        version = '4'

    # execute bitbake shell script file
    cmdline = './cmd_bitbake.sh ' + version + ' '
    if (imagetype == 'flash' or imagetype == 'nfs' or imagetype == 'secured'):
        if (fordevelop == 'devel'):
            cmdline = cmdline + 'starfish-{0}-{1}-{2}'.format(region, imagetype, fordevelop)
        else:
            cmdline = cmdline + 'starfish-{0}-{1}'.format(region, imagetype)
    else:
        cmdline = cmdline + imagetype

    print(cmdline)
    return os.system(cmdline)

def CliMode():
    curdir = os.getcwd()
    progdir = os.path.dirname(os.path.realpath(__file__))
    ubuntuVersion = platform.dist()[1]

    print('<< Start webOS TV auto build for CLI mode>>')
    try:
        webosVersion = str(input('> select webOS Version 22 ~ 24 or 2 ~ 6 (Default 24):'))
    except SyntaxError:
        webosVersion = ''

    if webosVersion == '':
        webosVersion = '24'

    if webosVersion == '1' or webosVersion == '2' or webosVersion == '3' or webosVersion == '3.5' or webosVersion == '4' or webosVersion == '4.5':
        if float(ubuntuVersion) > 14.04:
            exit('> Do not support the webOS version ' + webosVersion + ' in the host ' + ubuntuVersion + '. use less than or equal to 14.04 host')
    elif float(webosVersion) >= 5:
        if float(ubuntuVersion) < 18.04:
            exit('> Do not support the webOS version ' + webosVersion + ' in the host ' + ubuntuVersion + '. use more than or equal to 18.04 host')
    else:
        exit('> Do not support the webOS version ' + webosVersion + ' in this system')

    print('')

    # Clone temp build_starfish or cached it from submodule
    tempgitdir = CloneBuildStarfishGit(webosVersion)
    os.chdir(tempgitdir)
    os.system('git checkout master')
    os.system('git pull --all')

    if len(tempgitdir) > 0:
        # Get Branch Names
        branchname = GetBranchName(webosVersion)
        print('name: ' + branchname + ' version: ' + webosVersion)

        # Search a product branch name like '@152.gayasan.m16pp'
        p = re.compile('@\d+\.\w+\.\w+')
        m = p.findall(branchname)

        # Get Platfrom Types
        if len(m) == 0:
            # Find platform types
            platformtype = GetPlatformType()
        else:
            # Extract the platform type from the product branch name
            platformtype = m[0][m[0].rfind('.') + 1 : ]

        # Get Build Version
        tags = GetVersionNumber(branchname)
        print('')

        # Get the other build options
        region = GetBuildRegion(webosVersion)
        print('')
        imagetype = GetImageType()
        print('')
        fordevelop = IsDeveloperImage()
        print('')

        print('branch name = ' + branchname + ' webOS ' + webosVersion)
        print('platform type = ' + platformtype)
        print('version = ' + tags[0] + '  SHA = '+ tags[1])
        print('starfish-' + region + '-' + imagetype)
        if not fordevelop == '':
            print('for {0} image'.format(fordevelop))
        print('')

        os.chdir(curdir)
        realbuilddir = ChangeBuildDirectory(tempgitdir, branchname, platformtype, tags, True)

        os.chdir(curdir)
        CopyLocalBuildFiles(realbuilddir, '')

        # Get Build Dir
        return [(progdir, realbuilddir, platformtype, webosVersion, region, imagetype, fordevelop)]

    assert True, 'CLI Mode fail'

def AutoMode():
    curdir = os.getcwd()
    progdir = os.path.dirname(os.path.realpath(__file__))
    conf = sys.argv[1]
    ret = []

    if conf.endswith('.csv'):
        with open(conf, newline='') as f:
            data = csv.reader(f)
            next(data, None)
            for row in data:
                webosVersion = row[0]
                branchname = row[1]
                platformtype = row[2]
                buildVersion = row[3]
                region = row[4]
                imagetype = row[5]
                fordevelop = 'devel' if row[6] == 'yes' else ''
                localfile = 'none' if row[7] == 'none' else row[7]

                tmpdir = CloneBuildStarfishGit(webosVersion)
                os.chdir(tmpdir)
                os.system('git checkout ' + branchname)
                os.system('git pull --all')
                tags = GetVersionNumber(branchname, buildVersion)

                os.chdir(curdir)
                realbuilddir = ChangeBuildDirectory(tmpdir, branchname, platformtype, tags, False)

                os.chdir(curdir)
                CopyLocalBuildFiles(realbuilddir, localfile)

                ret.append((progdir, realbuilddir, platformtype, webosVersion, region, imagetype, fordevelop))
    else:
        with open(conf) as f:
            data = f.read().splitlines()
            assert len(data) == 9, 'txt conf file line len should be 8'

            webosVersion = data[1].split(' ')[0]
            branchname = data[2].split(' ')[0]
            platformtype = data[3].split(' ')[0]
            buildVersion = data[4].split(' ')[0]
            region = data[5].split(' ')[0]
            imagetype = data[6].split(' ')[0]
            fordevelop = 'devel' if data[7].split(' ')[0] == 'yes' else ''
            localfile = 'none' if data[8].split(' ')[0] == 'none' else data[8].split(' ')[0]

            tmpdir = CloneBuildStarfishGit(webosVersion)
            os.chdir(tmpdir)
            os.system('git checkout ' + branchname)
            os.system('git pull --all')
            tags = GetVersionNumber(branchname, buildVersion)

            os.chdir(curdir)
            realbuilddir = ChangeBuildDirectory(tmpdir, branchname, platformtype, tags, False)

            os.chdir(curdir)
            CopyLocalBuildFiles(realbuilddir, localfile)

            ret.append((progdir, realbuilddir, platformtype, webosVersion, region, imagetype, fordevelop))

    return ret

if __name__ == '__main__':
    print('Use python version 3 above')
    assert sys.version_info >= (3, 0)

    rets = []
    curdir = os.getcwd()
    params = CliMode() if len(sys.argv) != 2 else AutoMode()

    for param in params:
        progdir = param[0]
        builddir = param[1]
        platformtype = param[2]
        webosVersion = param[3]
        region = param[4]
        imagetype = param[5]
        fordevelop = param[6]

        if (imagetype != 'none'):
            os.chdir(builddir)
            rets.append(MakeImage(progdir, platformtype, webosVersion, region, imagetype, fordevelop))
        else:
            rets.append(False)

    print('------------ Build Result -----------'.center(40))
    for i in range(len(rets)):
        builddir = params[i][1]
        platformtype = params[i][2]
        webosVersion = params[i][3]
        region = params[i][4]
        imagetype = params[i][5]
        fordevelop = params[i][6]

        if (imagetype != 'none'):
            print('{0}) Build {1}({2}) with param (builddir:{3}, platform:{4}, webosVersion:{5}, region:{6}, target:{7}, fordevelop:{8})'
                .format(i + 1, "Success" if rets[i] == 0 else "Fail", rets[i],
                    builddir, platformtype, webosVersion, region, imagetype, fordevelop))
        else:
            print('{0}) Build Skip with param (builddir:{1}, platform:{2}, webosVersion:{3}, region:{4}, target:{5}, fordevelop:{6})'
                .format(i + 1, builddir, platformtype, webosVersion, region, imagetype, fordevelop))
    print('-------------------------------------'.center(40))
