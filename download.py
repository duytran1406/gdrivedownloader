# -*- coding: utf-8 -*-
from apiclient import errors
from colorama import init,Fore,Back,Style
from termcolor import colored
from apiclient.http import MediaIoBaseDownload
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import io
import os
import sys
import re

# If modifying these scopes, delete the file token.json.
SCOPES = 'https://www.googleapis.com/auth/drive'

def main():
    """
    Download folder content from google dirve without zipping.
    """

    # use Colorama to make Termcolor work on Windows too
    init()
    # now, to clear the screen
    cls()

    print colored(' _______  _______  _______  _______  ___      _______    ______   ______    ___   __   __  _______ ', 'red')
    print colored('|       ||       ||       ||       ||   |    |       |  |      | |    _ |  |   | |  | |  ||       |', 'red')
    print colored('|    ___||   _   ||   _   ||    ___||   |    |    ___|  |  _    ||   | ||  |   | |  |_|  ||    ___|', 'red')
    print colored('|   | __ |  | |  ||  | |  ||   | __ |   |    |   |___   | | |   ||   |_||_ |   | |       ||   |___ ', 'yellow')
    print colored('|   ||  ||  |_|  ||  |_|  ||   ||  ||   |___ |    ___|  | |_|   ||    __  ||   | |       ||    ___|', 'yellow')
    print colored('|   |_| ||       ||       ||   |_| ||       ||   |___   |       ||   |  | ||   |  |     | |   |___ ', 'green')
    print colored('|_______||_______||_______||_______||_______||_______|  |______| |___|  |_||___|   |___|  |_______|', 'green')
    print colored('     ______   _______  _     _  __    _  ___      _______  _______  ______   _______  ______       ', 'blue')
    print colored('    |      | |       || | _ | ||  |  | ||   |    |       ||   _   ||      | |       ||    _ |      ', 'blue')
    print colored('    |  _    ||   _   || || || ||   |_| ||   |    |   _   ||  |_|  ||  _    ||    ___||   | ||      ', 'magenta')
    print colored('    | | |   ||  | |  ||       ||       ||   |    |  | |  ||       || | |   ||   |___ |   |_||_     ', 'magenta')
    print colored('    | |_|   ||  |_|  ||       ||  _    ||   |___ |  |_|  ||       || |_|   ||    ___||    __  |    ', 'cyan')
    print colored('    |       ||       ||   _   || | |   ||       ||       ||   _   ||       ||   |___ |   |  | |    ', 'cyan')
    print colored('    |______| |_______||__| |__||_|  |__||_______||_______||__| |__||______| |_______||___|  |_|    ', 'cyan')
    print colored('===================================================================================================', 'white')
    print colored('                                         Version: ', 'yellow'), (1.0)
    print colored('                                         Author : ', 'yellow'), ('Blavk')
    print colored('                                         Github : ', 'yellow'), ('https://github.com/duytran1406/gdrivedownloader')
    store = file.Storage('token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('drive', 'v3', http=creds.authorize(Http()))
    print colored('* Directory to save - by default it will be current directory', 'blue')
    location = raw_input("   - Path: ")
    while not location:
        location = raw_input("   - Path: ")
    type(location)
    print colored('* Sub-directory: ', 'blue')
    folder_name = raw_input("   - Path: ")
    while not folder_name:
        folder_name = raw_input("   - Path: ")
    type(folder_name)
    print colored('* GDrive Folder/File ID: ','blue')
    folder_id = raw_input("   - ID  : ")
    while not folder_id:
        folder_id = raw_input("   - ID  : ")
    type(folder_id)

    #if len(sys.argv) > 2:
        #location = unicode(sys.argv[2], 'utf-8')
    if location[-1] != '/':
        location += '/'
    try:
        folder = service.files().list(
                q="name='{}' and mimeType='application/vnd.google-apps.folder'".format(folder_name),
                fields='files(id)').execute()
        folder_name = unicode(folder_name, 'utf-8')
        download_folder(service, folder_id, location, folder_name)

    except errors.HttpError, error:
        print 'An error occurred: {}'.format(error)

def download_folder(service, folder_id, location, folder_name):
    if not os.path.exists(location + folder_name):
        os.makedirs(location + folder_name)
    location += folder_name + '/'

    result = []
    files = service.files().list(
            q="'{}' in parents".format(folder_id),
            fields='files(id, name, mimeType, size)').execute()
    result.extend(files['files'])
    result = sorted(result, key=lambda k: k[u'name'])

    total = len(result)
    if total == 0:
        print colored('Folder is empty!', 'red')
        sys.exit()
    else:
        print colored('START DOWNLOADING', 'yellow')
    current = 1
    for item in result:
        file_id = item[u'id']
        filename = no_accent_vietnamese(item[u'name'])
        mime_type = item[u'mimeType']
        print '- ', colored(filename, 'cyan'), colored(mime_type, 'cyan'), '({}/{})'.format(current, total)
        if mime_type == 'application/vnd.google-apps.folder':
            download_folder(service, file_id, location, filename)
        elif not os.path.isfile('{}{}'.format(location, filename)):
            download_file(service, file_id, location, filename)
        else:
            remote_size = item[u'size']
            local_size = os.path.getsize('{}{}'.format(location, filename))
            if (str(remote_size) == str(local_size)):
                print colored('File existed!', 'magenta')
            else:
                print colored('Local File corrupted', 'red')
                os.remove('{}{}'.format(location, filename))
                download_file(service, file_id, location, filename)
        current += 1
        percent = float((current-1))/float(total)*100
        print colored("%.2f percent completed!" % percent,'green')


def download_file(service, file_id, location, filename):
    request = service.files().get_media(fileId=file_id)
    fh = io.FileIO('{}{}'.format(location, filename), 'wb')
    downloader = MediaIoBaseDownload(fh, request,chunksize=1024*1024)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        if status:
            #print '\rDownload {}%.'.format(int(status.progress() * 100)),
            print int(status.progress() * 100)," percent complete         \r",
            #sys.stdout.flush()
    print ""
    print colored(('%s downloaded!' % filename), 'green')
def cls():
    os.system('cls' if os.name=='nt' else 'clear')
def no_accent_vietnamese(s):
    #s = s.decode('utf-8', errors='ignore')
    s = re.sub(u'[àáạảãâầấậẩẫăằắặẳẵ]', 'a', s)
    s = re.sub(u'[ÀÁẠẢÃĂẰẮẶẲẴÂẦẤẬẨẪ]', 'A', s)
    s = re.sub(u'[èéẹẻẽêềếệểễ]', 'e', s)
    s = re.sub(u'[ÈÉẸẺẼÊỀẾỆỂỄ]', 'E', s)
    s = re.sub(u'[òóọỏõôồốộổỗơờớợởỡ]', 'o', s)
    s = re.sub(u'[ÒÓỌỎÕÔỒỐỘỔỖƠỜỚỢỞỠ]', 'O', s)
    s = re.sub(u'[ìíịỉĩ]', 'i', s)
    s = re.sub(u'[ÌÍỊỈĨ]', 'I', s)
    s = re.sub(u'[ùúụủũưừứựửữ]', 'u', s)
    s = re.sub(u'[ƯỪỨỰỬỮÙÚỤỦŨ]', 'U', s)
    s = re.sub(u'[ỳýỵỷỹ]', 'y', s)
    s = re.sub(u'[ỲÝỴỶỸ]', 'Y', s)
    s = re.sub(u'[Đ]', 'D', s)
    s = re.sub(u'[đ]', 'd', s)
    return s.encode('utf-8')

if __name__ == '__main__':
    main()
