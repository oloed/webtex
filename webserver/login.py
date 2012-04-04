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
import sqlite3, cPickle

conn = sqlite3.connect('/tmp/example')
c = conn.cursor()


install(SQLitePlugin(dbfile = '/tmp/example.db'))

# Get your app key and secret from the Dropbox developer website
APP_KEY = 'gkucvfe9xptshud'
APP_SECRET = '08nvepsv953j8b9'

# ACCESS_TYPE should be 'dropbox' or 'app_folder' as configured for your app
ACCESS_TYPE = 'app_folder'


sess = session.DropboxSession(APP_KEY, APP_SECRET, ACCESS_TYPE)

@route('/login')
def login(db):
	request_token = sess.obtain_request_token()
	print request_token

	p = cPickle.dumps(request_token, cPickle.HIGHEST_PROTOCOL)
	
	db.execute('create table if not exists login (oauth text, token blob)')
	db.execute('insert into login values (?,?)',[request_token.key,sqlite3.Binary(p)])

	url = sess.build_authorize_url(request_token, 'http://localhost:8080/success')


	redirect(url)

@route('/success')
def success(db):
	tok = str(request.query.oauth_token)
	row = db.execute('select token from login where oauth = ?',[tok]).fetchone()
	if row:
		token = cPickle.loads(str(row['token']))
		access_token = sess.obtain_access_token(token)
		print dir(access_token)
		cl = client.DropboxClient(sess)
		response.set_cookie('access_token',access_token,secret = 'secretkey')
		redirect('/doclist')
	else:	
		return 'Something went wrong'
