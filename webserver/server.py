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
from dropbox import client, rest, session
from login import *

from datetime import *
from docs import *
from urllib import quote_plus
import StringIO
import tempfile
import os

import browser_producer as bp
import browser_consumer as bc

@route('/')
def index():
	return template('index')


@route('/doclist')
def doclist():
	name = user_info()['display_name']
	template_list = ['LNCS', 'ACM', 'IEEE']
	doc_list = getDocs()
	
	docs_html = ''.join([template('docitem', name=doc['name'], link='/editor/' + doc['doc_id'], modified=doc['modified']) for doc in doc_list])

	templates_html = ''.join([template('templateitem', name=tmpl, tmpl_id=tmpl) for tmpl in template_list])

	return template('doclist', name=name, docs=docs_html, templates=templates_html)

@post('/newdoc')
def createNewDoc():
	req = request.json
	#print req
	print req['name']
	print req['template']
	make_doc(req['name'],req['template'])
	#redirect('/editor/'+req['name'])
	return { 'doc_id': req['name'] }

@route('/editor/<doc_id:path>')
def editor(doc_id):
	content = get_doc_content(doc_id)
	print content
	return template('editor', doc_name=doc_id, doc_content=content)

@get('/doc/<doc_id>/tex')
def get_document_tex(doc_id):
	response.content_type = 'application/x-latex'
	return get_doc_content(doc_id)

@get('/doc/<doc_id>/pdf')
def get_document_pdf(doc_id):
	response.content_type = 'application/pdf'
	return get_doc_pdf(doc_id)

@post('/doc/<doc_id>')
def update_document(doc_id):
	content = request.body
	# 1. push content to dropbox
	put_doc('/' + doc_id + '/' + doc_id + '.tex', content)
	# 2. get zip of document from dropbox
	zipped = zip_doc(doc_id)
	# 3. push zip to S3 & order build on cluster
	bp.main(zipped)
	return {
		'txid': 'banana'
	}

@post('/job/<doc_name>/<txid>')
def check_job(doc_name, txid):
	fff, path = tempfile.mkstemp(suffix='.pdf')
	if bc.main(fff):
		file_name = doc_name + '/' + doc_name + '.pdf'
		print 'storing updated pdf to ' + file_name
		put_doc(file_name, path)
                print 'done storing'
		os.fdopen(fff).close()
		os.remove(path)
		return { 'finished': True }

	os.fdopen(fff).close()
	os.remove(path)
	return { 'finished': False }


@route('/static/<path:path>')
def static(path):
	return static_file(path, root='static')


if __name__ == '__main__':
	run(host='localhost', port=8080, debug=True, reloader = True)
