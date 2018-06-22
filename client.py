from imagify import Imagify
from shutil import move
import configparser
import os
import sys
import time
import json
import requests

# set globals
filesToOptimize  = []
successFiles     = []
errorFiles       = []
fileSizeOriginal = 0
fileSizeNew      = 0

# convert string to boolean
def strToBool(s):
    if(s.lower() == 'true'):
         return True
    else:
        return False

# convert byte to MB / GB..
# thanks to https://stackoverflow.com/a/31631711
def humanbytes(B):
   'Return the given bytes as a human friendly KB, MB, GB, or TB string'
   B = float(B)
   KB = float(1024)
   MB = float(KB ** 2) # 1,048,576
   GB = float(KB ** 3) # 1,073,741,824
   TB = float(KB ** 4) # 1,099,511,627,776

   if B < KB:
      return '{0} {1}'.format(B,'Bytes' if 0 == B > 1 else 'Byte')
   elif KB <= B < MB:
      return '{0:.2f} KB'.format(B/KB)
   elif MB <= B < GB:
      return '{0:.2f} MB'.format(B/MB)
   elif GB <= B < TB:
      return '{0:.2f} GB'.format(B/GB)
   elif TB <= B:
      return '{0:.2f} TB'.format(B/TB)

# Recursive directory traversing for files
def getFiles( root, extensions=[] ):
    global filesToOptimize
    for dirpath, dirs, files in os.walk(root):	
        for filename in files:
            fname = os.path.join(dirpath,filename)
            filename = ''
            if(len(extensions)>0):
                for i, entry in enumerate(extensions):
                    if fname.endswith(entry):
                        filename = fname  
            else:
                filename = fname
            if('filename' in locals() and len(filename)>0):
                filesToOptimize.append(filename)

# optimize images with imagify.io
def optimizeImages(param):
    global filesToOptimize, imagify, errorFiles, successFiles, KEEP_SOURCEFILE, fileSizeOriginal, fileSizeNew
    if(len(filesToOptimize)==0):
        return
        
    for row in filesToOptimize:
        try:
            response = imagify.upload(row, param)
            success = response['success']
            if(success == True):
                currentPath = os.path.dirname(os.path.abspath(row))
                filename    = os.path.basename(row)
                name, ext   = os.path.splitext(filename)
                nameSourceFile = name + '-original' + ext
                pathSourceFile = currentPath + '/' + nameSourceFile
                try:
                    os.rename(row, pathSourceFile)
                except WindowsError:
                    os.remove(pathSourceFile)
                    move(row, pathSourceFile)

                # download file
                image = response['image']
                percent = int(response['percent'])
                fileSizeOriginal = fileSizeOriginal + int(response['original_size'])
                fileSizeNew = fileSizeNew + int(response['new_size'])
                try:
                    with open(row, 'wb') as f:
                        f.write(requests.get(image).content)
                except Exception as ex:
                    print('Download file ' + image)
                    template = "An exception of type {0} occurred. Arguments:\n{1!r}"
                    message = template.format(type(ex).__name__, ex.args)
                    print(message)
                    input("Bitte mit der Eingabetaste bestätigen!")
                    sys.exit()

                print('Bild %s wurde erfolgreich Optimiert. Dateigröße hat sich um %i Prozent verringert' % (row, percent))
                successFiles.append(row)
                
                if(KEEP_SOURCEFILE != True):
                    os.remove(pathSourceFile)
            else:
                print('INFO: imagify.io hat folgendes Bild nicht optimieren: %s' % (row))
                errorFiles.append(row)

        except Exception as ex:
            if(type(ex).__name__ == 'UnknownError'):
                print('\nImagify.io liefert einen unbekannten Fehler, ist der API Key korrekt?')
                input("Bitte mit der Eingabetaste bestätigen!")
                sys.exit()
            elif(type(ex).__name__ == 'ServerError'):
                print('\nImagify.io hat aktuell einen Serverfehler!')
                input("Bitte mit der Eingabetaste bestätigen!")
                sys.exit()
            elif(type(ex).__name__ == 'OverQuotaError'):
                print('\nIhr Imagify.io Accountlimit wurde erreicht!')
                input("Bitte mit der Eingabetaste bestätigen!")
                sys.exit()
            elif(type(ex).__name__ == 'UnsupportedMediaType'):
                errorFiles.append(row)
            else:
                template = "An exception of type {0} occurred. Arguments:\n{1!r}"
                message = template.format(type(ex).__name__, ex.args)
                print(message)
    
# set variables
CONFIG_PATH     = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE     = 'config.ini'
CONFIG_FILEPATH = CONFIG_PATH + '/' + CONFIG_FILE
IS_ACTIVE       = False
KEEP_SOURCEFILE = True
SYSTEM_PATH     = ''
OPTIMIZATION    = None
API_KEY         = None

# get config file
if(not os.path.isfile(CONFIG_FILEPATH)):
    sys.exit('CONFIG NICHT GEFUNDEN!')

config = configparser.ConfigParser()
config.read(CONFIG_FILEPATH)

print('\nKonfigurations-Datei wird verarbeitet!')
time.sleep(1)

# set variables
if('SYSTEM' in config):
    if('is_active' in config['SYSTEM']):
        IS_ACTIVE = strToBool(config['SYSTEM']['is_active'])

    if('keep_sourcefile' in config['SYSTEM']):
        KEEP_SOURCEFILE = strToBool(config['SYSTEM']['keep_sourcefile'])

    if('system_path' in config['SYSTEM']):
        SYSTEM_PATH = str(config['SYSTEM']['system_path']).strip()

if('IMAGIFY' in config):
    if('optimization_algorithm' in config['IMAGIFY']):
        options = {1: 'aggressive', 2: 'ultra'}
        OPTIMIZATION = options.get(int(config['IMAGIFY']['optimization_algorithm']), 'normal')

    if('apiKey' in config['IMAGIFY']):
        API_KEY = str(config['IMAGIFY']['apiKey'])

if(not os.path.exists(SYSTEM_PATH)):
    sys.exit('PFAD NICHT GEFUNDEN: '+ SYSTEM_PATH)

# is it active?
if(IS_ACTIVE != True):
    sys.exit('Anwendung wurde deaktiviert!')

# check if settings are correct
print('\nEinstellungen werden überprüft:')
time.sleep(1)

print('\nIst der Pfad korrekt? '+ SYSTEM_PATH)
realPathPrompt = input('(j/n): ')
if(not realPathPrompt.lower().startswith('j')):
    sys.exit()

print('\nIst die richtige Komprimierung eingestellt? '+ OPTIMIZATION)
optimizationPrompt = input('(j/n): ')
if(not optimizationPrompt.lower().startswith('j')):
    sys.exit()

if(KEEP_SOURCEFILE == True):
    print('\nOriginaldatei soll als Kopie beibehalten werden, korrekt?')
else:
    print('\nOriginaldatei soll überschrieben werden, korrekt?')
sourcefilePrompt = input('(j/n): ')
if(not sourcefilePrompt.lower().startswith('j')):
    sys.exit()

# set imagify options
imagify = Imagify(API_KEY)
if(OPTIMIZATION == 'ultra'):
    param = dict(normal=False, aggressive=False, ultra=True)
elif(OPTIMIZATION == 'aggressive'):
    param = dict(normal=False, aggressive=True, ultra=False)
else:
    param = dict(normal=True, aggressive=False, ultra=False)

# start pre process
print('\nDateien werden durchsucht, einen Moment Geduld bitte! ')

getFiles(SYSTEM_PATH, ['.jpg', '.jpeg', '.JPEG', '.JPG', '.png', '.PNG', '.gif', '.GIF'])

if(len(filesToOptimize)==0):
    print('\nEs konnten leider keine unterstützten Formate gefunden werden!')
    time.sleep(3)
    sys.exit()
    
print('\nAnalyse erfolgreich abgeschlossen, es wurden %i unterstützte Dateien gefunden'% (len(filesToOptimize)))

# start process
print('\nOptimierung der Bilder wird gestartet!\n')
optimizeImages(param)

# start post process
print('\nAnzahl der optimierten Bilder: ' + str(len(successFiles)))
print('Anzahl der unoptimierten Bilder: ' + str(len(errorFiles)))

print('\nDateimenge:')
print('Vor der Optimierung: ' + humanbytes(fileSizeOriginal))
print('Nach der Optimierung: ' + humanbytes(fileSizeNew))

# close optimizer 
input("\nBitte Eingabetaste drücken, um das Programm zu beenden!")