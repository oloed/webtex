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

import StringIO, zipfile

class InMemoryFile(object):
   def __init__(self):
       # Create the in-memory file-like object
       self.in_memory_zip = StringIO.StringIO()
      
   def append(self, filename_in_zip, file_contents):
       '''Appends a file with name filename_in_zip and contents of
          file_contents to the in-memory zip.'''
       # Get a handle to the in-memory zip in append mode
       zf = zipfile.ZipFile(self.in_memory_zip, "a", zipfile.ZIP_DEFLATED)
      
       # Write the file to the in-memory zip
       zf.writestr(filename_in_zip, file_contents)
      
       # Mark the files as having been created on Windows so that
       # Unix permissions are not inferred as 0000
       for zfile in zf.filelist:
           zfile.create_system = 0       
      
       return self
      
   def read(self):
       '''Returns a string with the contents of the in-memory zip.'''
       self.in_memory_zip.seek(0)
       return self.in_memory_zip.getvalue()
  
   def writetofile(self, filename):
       '''Writes the in-memory zip to a file.'''
       f = file(filename, "wb")
       f.write(self.read())
       f.close()
