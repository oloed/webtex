# WebTeX Copyright (c) 2012, Iain McGinniss
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the <organization> nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from bottle import *
from bottle_sqlite import SQLitePlugin
# Include the Dropbox SDK libraries
from dropbox import client, rest, session
import sqlite3, cPickle, os
import zipfile, StringIO, time
from inmem import *

# Get your app key and secret from the Dropbox developer website
APP_KEY = os.environ['DROPBOX_APP_KEY']
APP_SECRET = os.environ['DROPBOX_SECRET_KEY']
COOKIE_KEY = os.environ['COOKIE_KEY']

# ACCESS_TYPE should be 'dropbox' or 'app_folder' as configured for your app
ACCESS_TYPE = 'app_folder'


sess = session.DropboxSession(APP_KEY, APP_SECRET, ACCESS_TYPE)

def user_info():
	token = request.get_cookie("access_token",secret=COOKIE_KEY)
	if token:
		sess.set_token(token.key,token.secret)
		cl = client.DropboxClient(sess)
		print cl.account_info()
		return cl.account_info()
	else:
		return None

def getDocs():
	token = request.get_cookie("access_token",secret=COOKIE_KEY)
	if token:
		sess.set_token(token.key,token.secret)
		cl = client.DropboxClient(sess)
		md = cl.metadata('/')
		print type(md)
		out = []
		contents = md['contents']
		for i in range(len(contents)):
			temp = contents[i]
			if temp['is_dir']:
				doc = get_doc(cl,temp)
				if not doc == None:
					out.append(doc)
		temp = str(out)
		return out

def get_doc(cl,temp):
	md = cl.metadata(temp['path'])
	contents = md['contents']
	out = []
	for i in range(len(contents)):
		t2 = contents[i]
		if not bool(t2['is_dir']):
			path = t2['path']
			dot = path.rfind('.')
			slash = path.rfind('/')
			doc_name = path[path.find('/')+1:slash]
			fname = path[slash:dot]
			ext = path[dot:]
			if fname == temp['path'] and ext == '.tex':
				return {'name':doc_name,'modified':t2['modified'], 'doc_id':doc_name}
	return None

def get_doc_content(doc_id):
	token = request.get_cookie("access_token",secret=COOKIE_KEY)
	if token:
		sess.set_token(token.key,token.secret)
		cl = client.DropboxClient(sess)
		f, md = cl.get_file_and_metadata('/' + doc_id + '/' + doc_id + '.tex')
		if not md:
			return None

		return f.read()

	return None

def get_doc_pdf(doc_id):
	token = request.get_cookie("access_token",secret=COOKIE_KEY)
	if token:
		sess.set_token(token.key,token.secret)
		cl = client.DropboxClient(sess)
		f, md = cl.get_file_and_metadata('/' + doc_id + '/' + doc_id + '.pdf')
		if not md:
			return '???'

		return f.read()

	return '???!?'

def make_doc(docname, template=None):
	token = request.get_cookie("access_token",secret=COOKIE_KEY)
	if token:
		sess.set_token(token.key,token.secret)
		cl = client.DropboxClient(sess)
		try:
			cl.file_create_folder(docname)
		except:
			pass
		f = open(str(docname)+'.tex','w')
		f.close()
		f = open(str(docname)+'.tex','r')
		cl.put_file('/'+docname+'/'+docname+'.tex', f,overwrite=True)
		f.close()
		os.remove(docname+'.tex')

def put_doc(path, content):
	print 'a'
	token = request.get_cookie("access_token",secret=COOKIE_KEY)
	print 'b'
	if token:
		print 'c'
		sess.set_token(token.key,token.secret)
		print 'd'
		cl = client.DropboxClient(sess)
		print 'e'
		#f = open(path,'w')
		#f.write(content)
		#f.close()
		#f = open(path,'r')
		cl.put_file(path,content,overwrite=True)
		print 'f'
		#f.close()
		#os.remove(path)

def zip_files(cl, zp, path):
	md = cl.metadata(path)
	contents = md['contents']
	for i in range(len(contents)):
		temp = contents[i]
		if bool(temp['is_dir']):
			zip_files(cl,zp,temp['path'])
		else:
			f = cl.get_file(temp['path'])
			pos = temp['path'].rfind('/')
			fname = temp['path'][pos+1:]
			print fname
			content = f.read()
			zp.append(fname,content)


def zip_doc(doc_id):
	token = request.get_cookie("access_token",secret=COOKIE_KEY)
	if token:
		sess.set_token(token.key,token.secret)
		cl = client.DropboxClient(sess)
		path = '/' + doc_id
		myzip = InMemoryFile()
		zip_files(cl,myzip,path)
		return myzip

	return None
	

def templateList():
	pass
