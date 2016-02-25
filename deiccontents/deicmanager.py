from notebook.services.contents.filemanager import FileContentsManager
from notebook.services.contents.fileio import FileManagerMixin
import os,sys
from tornado import web
import time
from .utils import (
    is_hidden,
    to_api_path,
)

import owncloud

def tmp_sync_with_oc():
    #TMP TO HAVE BOTH NODES UP TO DATE
    import subprocess
    cmd = "owncloudcmd --trust --non-interactive ~/Notebooks https://data.deic.dk/remote.php/webdav/Notebooks"
    process = subprocess.Popen(cmd, shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    process.communicate()
    ####

class DeICContentsManager(FileContentsManager):
    def __init__(self, *args, **kwargs):
        print "init DeICContentsManager"
        self.notebook_path = os.path.join('Notebooks')

        self.oc = owncloud.Client('https://data.deic.dk/')
        self.oc.login('', '')
        #self.oc.__webdav_url = self.oc.__webdav_url + 'Notebooks'
        super(DeICContentsManager, self).__init__(*args, **kwargs)

    def get(self, path, content=True, type=None, format=None):
        """ Takes a path for an entity and returns its model
        Parameters
        ----------
        path : str
            the API path that describes the relative path for the target
        content : bool
            Whether to include the contents in the reply
        type : str, optional
            The requested type - 'file', 'notebook', or 'directory'.
            Will raise HTTPError 400 if the content doesn't match.
        format : str, optional
            The requested format for file contents. 'text' or 'base64'.
            Ignored if this returns a notebook or directory model.
        Returns
        -------
        model : dict
            the contents model. If content=True, returns the contents
            of the file or directory as well.
        """
        print str(time.time()),"GET path:%s, content:%s, type:%s, format:%s"%(path,content,type,format)
        if path=='':
            print "sync with oc"
            tmp_sync_with_oc()
        path = path.strip('/')

        if not self.exists(path):
            raise web.HTTPError(404, u'No such file or directory: %s' % path)

        os_path = super(DeICContentsManager, self)._get_os_path(path)
        if os.path.isdir(os_path):
            if type not in (None, 'directory'):
                raise web.HTTPError(400,
                                u'%s is a directory, not a %s' % (path, type), reason='bad type')
            model = self._dir_model(path, content=content)
        elif type == 'notebook' or (type is None and path.endswith('.ipynb')):
            model = super(DeICContentsManager, self)._notebook_model(path, content=content)
        else:
            if type == 'directory':
                raise web.HTTPError(400,
                                u'%s is not a directory' % path, reason='bad type')
            model = super(DeICContentsManager, self)._file_model(path, content=content, format=format)
        return model
   
    def is_hidden(self, path):
        return is_hidden(path)
    
    def file_exists(self, path):
        print "in file_exists:",path
        return super(DeICContentsManager, self).file_exists(path)
    
    def tmp_exists(self,path):
        try:
            self.oc.file_info(path)
            return True
        except:
            return False
        
    def is_dir(self,path):
        if (self.oc.file_info(path)).file_type == 'dir':  
            return True
        return False

    def dir_exists(self, path):
        print "in dir_exists:",path
        path = os.path.join(self.notebook_path,path)  
        if self.tmp_exists(path):
            if self.is_dir(path):
                return True
            return False
        elif path=='':
            if not self.is_dir(path):
                self.oc.delete(self.notebook_path)
            self.oc.mkdir(self.notebook_path)
            return True
        else:   
            return False
    
    def _dir_model(self, path, content=True):
        """Build a model for a directory
        if content is requested, will include a listing of the directory
        """
        os_path = super(DeICContentsManager, self)._get_os_path(path)
        four_o_four = u'directory does not exist: %r' % path

        if not os.path.isdir(os_path):
            raise web.HTTPError(404, four_o_four)
        elif is_hidden(os_path, super(DeICContentsManager, self).root_dir):
            super(DeICContentsManager, self).log.info("Refusing to serve hidden directory %r, via 404 Error",
                os_path
            )
            raise web.HTTPError(404, four_o_four)

        model = super(DeICContentsManager, self)._base_model(path)
        model['type'] = 'directory'
        if content:
            model['content'] = contents = []
            os_dir = super(DeICContentsManager, self)._get_os_path(path)
            for name in os.listdir(os_dir):
                try:
                    os_path = os.path.join(os_dir, name)
                except UnicodeDecodeError as e:
                    super(DeICContentsManager, self).log.warn(
                        "failed to decode filename '%s': %s", name, e)
                    continue
                # skip over broken symlinks in listing
                if not os.path.exists(os_path):
                    super(DeICContentsManager, self).log.warn("%s doesn't exist", os_path)
                    continue
                elif not os.path.isfile(os_path) and not os.path.isdir(os_path):
                    super(DeICContentsManager, self).log.debug("%s not a regular file", os_path)
                    continue
                if super(DeICContentsManager, self).should_list(name) and not is_hidden(os_path, self.root_dir):
                    contents.append(self.get(
                        path='%s/%s' % (path, name),
                        content=False)
                    )

            model['format'] = 'json'

        return model
    
    
    
