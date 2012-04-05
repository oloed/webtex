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

from settings import *

from bottle import *
# Include the Dropbox SDK libraries
from dropbox import client, rest, session
import oauth

import boto
from boto import dynamodb

import os


def connect_dropbox():
	return session.DropboxSession(
		DROPBOX_APP_KEY, 
		DROPBOX_APP_SECRET, 
		'app_folder')


@route('/login')
def login(db):
	request_token = sess.obtain_request_token()
	print request_token
	
	sess = connect_dropbox()
	db = dynamodb.connect_to_region(DYNAMODB_REGION)
	table = db.get_table(DROPBOX_REQ_TOKENS_TABLE)
	token_attrs = { 'key': request_token.key, 'secret': request_token.secret }
	token = table.new_item(attrs=token_attrs)
	token.put()


	url = sess.build_authorize_url(request_token, get_url('/success'))
	redirect(url)


@route('/success')
def success(db):
	sess = connect_dropbox()
	tok = str(request.query.oauth_token)

	db = dynamodb.connect_to_region(DYNAMODB_REGION)
	table = db.get_table(DROPBOX_REQ_TOKENS_TABLE)
	item = table.get_item(tok)

	if item:
		token = oauth.OAuthToken(item.attrs.key, item.attrs.secret)
		access_token = sess.obtain_access_token(token)
		cl = client.DropboxClient(sess)
		response.set_cookie('access_token', access_token, secret=COOKIE_KEY)
		redirect('/doclist')
	else:
		return 'Something went wrong'
