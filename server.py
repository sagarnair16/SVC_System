import os
from flask import Flask, request, make_response, redirect, render_template, url_for, flash, session
from flask import send_from_directory
import json
from cloudant.client import Cloudant
import hashlib
from datetime import datetime
import mysql.connector


# Initializing flask app
app = Flask(__name__)
app.secret_key = 'You shall never know'

# Bluemix VCAP services
#PORT = int(os.getenv('VCAP_APP_PORT', 8000))



def listOfFiles():
    client = conn()
    fileList = []
    my_database = client['sagar']
    for document in my_database:
        fileList.append(document)

    disconn(client)
    return fileList



@app.route('/')
def index():
    return render_template('home.html')

@app.route('/send', methods=['GET', 'POST'])
def send():
    uname=request.form['uname']
    psw=request.form['psw']
    cnx=auth()
    cursor = cnx.cursor()
    cursor.execute("select password from authentication where username=%s", [uname])
    res=cursor.fetchone()
    if res[0]==psw:
        session['user']=uname
        fileList = listOfFiles()
        return render_template("index.html",name=session['user'],fileList=fileList)
    else:
        return render_template("home.html",name="Incorrect username and password")

def auth():
     cnx = mysql.connector.connect(user='DB username', password='your pass',
                              host='Your connection url',
                              database='database name')
     return cnx


def conn():
    cl_username = "your DB usrname"
    cl_password = "Db password"
    url = "your connection url"
    client = Cloudant(cl_username, cl_password, url=url)
    client.connect()
    return client


def disconn(client):
    client.disconnect()


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    client = conn()
    my_database = client['sagar']
    # print 'My Database - ' + my_database
    fileUploaded = request.files['file']
    fcontent = fileUploaded.read()
    flength = len(fcontent)
    file_name = fileUploaded.filename
    file_hash = hashlib.md5(fcontent).hexdigest()

    listofmatchingfiles = []
    for document in my_database:
        if file_name == document['fileName']:
            listofmatchingfiles.append(document)

    version_max = 0
    if len(listofmatchingfiles) == 0:
        print 'list of matching files is empty'
        fileJSON = {
            'fileName': file_name,  # Setting _id is optional
            # 'fileContent': fcontent,
            'fileSize': flength,
            'fileHash': hashlib.md5(fcontent).hexdigest(),
            'fileVersion': 1,
            'lastModified': str(datetime.now()),
            'author': session['user']
        }
        # Create a document using the Database API
        my_document = my_database.create_document(fileJSON)
        my_document.put_attachment(file_name, "text/plain", fcontent, headers=None)

    else:
        print 'list of matching files not empty'
        hash_check = True
        for k in listofmatchingfiles:
            if k['fileVersion'] > version_max:
                version_max = k['fileVersion']
            if k['fileHash'] == file_hash:
                print 'file with same contents exists'
                hash_check = False
                break

        if hash_check:
            new_version = version_max + 1
            fileJSONUpdate = {
                'fileName': file_name,  # Setting _id is optional
                # 'fileContent': fcontent,
                'fileSize': flength,
                'fileHash': hashlib.md5(fcontent).hexdigest(),
                'fileVersion': new_version,
                'lastModified': str(datetime.now()),
                'author':session['user']
            }
            # Create a document using the Database API
            my_document = my_database.create_document(fileJSONUpdate)
            my_document.put_attachment(file_name, "text/plain", fcontent, headers=None)

    disconn(client)
    fileList = listOfFiles()
    return render_template('index.html', name=session['user'], fileList=fileList)




@app.route('/deleteFile', methods=['GET', 'POST'])
def deleteFile():
    client = conn()
    my_database = client['sagar']
    filename = request.form['filename']
    file_name = filename.strip()
    fileversion = request.form['fileversion']
    file_version = fileversion.strip()

    for document in my_database:
        if file_name == document['fileName'] and file_version == str(document['fileVersion']):
            document.delete_attachment(file_name, headers=None)
            document.delete()

    fileList = listOfFiles()
    return render_template('index.html', name=session['user'],fileList=fileList)


@app.route('/downloadFile', methods=['GET', 'POST'])
def downloadFile():
    client = conn()
    my_database = client['sagar']
    filename = request.form['filename']
    file_name = filename.strip()
    fileversion = request.form['fileversion']
    file_version = fileversion.strip()

    for document in my_database:
        if file_name == document['fileName'] and file_version == str(document['fileVersion']):
            f = document.get_attachment(file_name, headers=None, write_to=None, attachment_type='text')
            response = make_response(f)
            response.headers["Content-Disposition"] = "attachment; filename=" + file_name
            disconn(client)
            return response

    fileList = listOfFiles()
    return render_template('index.html',name=session['user'], fileList=fileList)

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session['user']=None
    return render_template("home.html")

# start flask app
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000)
