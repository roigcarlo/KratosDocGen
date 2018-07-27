import os
import re
import json

from utils.io import GetApplicationsDirectory
from utils.io import GetKratosDirectory

def CheckClassNameInDir(where, name, appRep):
    for root, subfolder, files in os.walk(where):
        for f in [process for process in files if 'process.py' in process]:
            src = os.path.join(root, f)
            appExpr = re.compile('.+\/(.+Application|.+_application)\/.+')
            appName = appExpr.match(src).group(1)
            prcSoft = re.compile('(?:default_settings|default_parameters)')
            prcExpr = re.compile('(?:default_settings|default_parameters)\s+=\s+[a-zA-Z]+\.Parameters\([\s]*(?:""")([\r\n\s{}"a-zA-Z0-9_:,.()\[\]\+\-/]+)(?:""")')
            with open(src, 'r') as _file:
                raw = _file.read()
                # Check if default section exists
                try:
                    prcIsDefault = prcSoft.search(raw).group(0)
                except:
                    print("No default section found {} - {}".format(appName, f))
                else:
                    # Check if default section is parseable
                    try:
                        prcData = prcExpr.search(raw).group(1).strip()
                    except Exception as e:
                        print("Unable to obtain default parameters for {} - {}".format(appName, f))
                    else:
                        # Check if default section is valid json
                        try:
                            prcDataJson = json.loads(prcData)
                        except Exception as e:
                            print("Unable to parse json {} {}:\n {}".format(appName, f, prcData))
                        else:
                            if appName in appRep:
                                appRep[appName][f] = prcDataJson
                            else:
                                appRep[appName] = {f:prcDataJson}

    return appRep

appRep = {}

for root, dirs, files in os.walk(GetApplicationsDirectory()):
    for subapp in dirs:
        appRep = CheckClassNameInDir(
            GetApplicationsDirectory() + subapp,
            'process',
            appRep
        )

with open('process.json', 'w') as json_file:
    json.dump(appRep, json_file)

# for app in appRep:
#     print("*", app)
#     for process in appRep[app]:
#         print(process)
#         for processMame, processInfo in process.items():
#             print("\t\t + {}".format(processMame))
#             for key, value in processInfo.items():
#                 print("\t\t\t\t - {}:\t {}".format(key, value))


