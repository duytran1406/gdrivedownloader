# -*- coding: utf-8 -*-
from apiclient import errors
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

    store = file.Storage('token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('drive', 'v3', http=creds.authorize(Http()))
    print ('* Directory to save - by default it will be current directory')
    location = input("   - Path: ")
    while not location:
        location = raw_input("   - Path: ")
    type(location)
    print ('* Sub-directory: ')
    folder_name = input("   - Path: ")
    while not folder_name:
        folder_name = raw_input("   - Path: ")
    type(folder_name)
    print ('* GDrive Folder/File ID: ')
    folder_id = input("   - ID  : ")
    while not folder_id:
        folder_id = input("   - ID  : ")
    type(folder_id)

    #if len(sys.argv) > 2:
        #location = unicode(sys.argv[2], 'utf-8')
    if location[-1] != '/':
        location += '/'
    
    folder = service.files().list(
            q="name='{}' and mimeType='application/vnd.google-apps.folder'".format(folder_name),
            fields='files(id)').execute()
    folder_name = unicode(folder_name, 'utf-8')
    download_folder(service, folder_id, location, folder_name)

    

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
        print ('Folder is empty!')
        sys.exit()
    else:
        print ('START DOWNLOADING')
    current = 1
    for item in result:
        file_id = item[u'id']
        filename = no_accent_vietnamese(item[u'name'])
        mime_type = item[u'mimeType']
        #print '- ', filename, mime_type, '({}/{})'.format(current, total)
        if mime_type == 'application/vnd.google-apps.folder':
            download_folder(service, file_id, location, filename)
        elif not os.path.isfile('{}{}'.format(location, filename)):
            download_file(service, file_id, location, filename)
        else:
            remote_size = item[u'size']
            local_size = os.path.getsize('{}{}'.format(location, filename))
            if (str(remote_size) == str(local_size)):
                print ('File existed!')
            else:
                print ('Local File corrupted')
                os.remove('{}{}'.format(location, filename))
                download_file(service, file_id, location, filename)
        current += 1
        percent = float((current-1))/float(total)*100
        print ("%.2f percent completed!" % percent)


def download_file(service, file_id, location, filename):
    request = service.files().get_media(fileId=file_id)
    fh = io.FileIO('{}{}'.format(location, filename), 'wb')
    downloader = MediaIoBaseDownload(fh, request,chunksize=1024*1024)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        if status:
            #print '\rDownload {}%.'.format(int(status.progress() * 100)),
            print (int(status.progress() * 100)," percent complete         \r"),
            #sys.stdout.flush()
    print ("")
    print ('%s downloaded!' % filename)
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
