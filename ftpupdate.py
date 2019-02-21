from ftplib import FTP, error_perm
import os
import json

with open('config.json') as f:
    content = f.read()
    content = content.replace('\\', '/')
    config = json.loads(content)

dest_path = config['dest_path']
source_path = config['source_path']
host = config['host']
user = config['user']
pwd = config['passwd']


def upload_dir(ftp, path):
    path = path
    for name in os.listdir(path):
        name = name
        localpath = os.path.join(path, name)
        if os.path.isfile(localpath):
            print('STOR', name, localpath)
            ftp.storbinary('STOR ' + name, open(localpath,'rb'))
        elif os.path.isdir(localpath):
            print('MKD', name)

            try:
                ftp.mkd(name)
            except error_perm as e:
                if not e.args[0].startswith('550'):
                    raise

            print('CWD', name)
            ftp.cwd(name)
            upload_dir(ftp, localpath)
            print('CWD', '..')
            ftp.cwd('..')


def remove_dir(path):

    try:
        path = path
        ftp.cwd(path)
        print('Working dir:', ftp.pwd())
        print('MLSD', path)
        content = ftp.mlsd('')
        files = []
        dirs = []
        for c in content:
            if c[1]['type'] == 'file':
                files.append(c)
            elif c[1]['type'] == 'dir':
                dirs.append(c)

        for f in files:
            print('Working dir:', ftp.pwd())
            print('Removing file:', f[0])
            ftp.delete(f[0])
        for d in dirs:
            remove_dir(d[0])

        ftp.cwd('..')
        print('Working dir:', ftp.pwd())
        print('Removing dir:', path)
        ftp.rmd(path)

    except error_perm as e:
        print('REMOVE ERROR')
        print(e)
        if not e.args[0].startswith('550'):
            raise


ftp = FTP(host, user, pwd)
ftp.encoding = 'utf-8'

try:
    ftp.login()
except error_perm:
    pass

print(dest_path)
dir_name = dest_path.split('/')[-1]

try:
    ftp.cwd(dest_path)
    print(dir_name)
    ftp.cwd('..')
    remove_dir(dir_name)
except error_perm as e:
    if not e.args[0].startswith('550'):
        raise

ftp.cwd('/')

print('Working dir:', ftp.pwd())

try:
    print('Make dir:', dest_path)
    ftp.mkd(dest_path)
except Exception as e:
    if not e.args[0].startswith('550'):
        raise

ftp.cwd(dest_path)
print('UPLOAD')
print('Working dir:', ftp.pwd())
upload_dir(ftp, source_path)

ftp.quit()
