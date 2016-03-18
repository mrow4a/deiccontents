from notebook.services.contents.filemanager import FileContentsManager
from notebook.services.contents.fileio import FileManagerMixin
import os,sys
from tornado import web
from .utils import *
import owncloud
import mimetypes

def tmp_sync_with_oc():
    """"TMP TO HAVE BOTH NODES UP TO DATE 
    After development, it should be deleted 
    and no files should be residing on VM filesystem
    """
    import subprocess
    cmd = "owncloudcmd --trust --non-interactive ~/Notebooks https://test1:dummy@test.data.deic.dk/remote.php/webdav/Notebooks"
    process = subprocess.Popen(cmd, shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    process.communicate()
    ####

class DeICContentsManager(FileContentsManager):
    def __init__(self, *args, **kwargs):
        print "---->init DeICContentsManager"

        self.notebook_path = os.path.join('Notebooks')
        self.oc = owncloud.Client('https://YOUR.SERVER/')
        self.oc.login('YOUR_USER', 'YOUR_PASSWORD') #could be ('','') for passwordless login
        
        super(DeICContentsManager, self).__init__(*args, **kwargs)
        #print super(DeICContentsManager,self).parent.notebook_dir
        
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
        
        if path=='':
            """this is a temporary solution in order to make development
            easier by having webdav and jupyter up to date"""
            
            print "---->###REFRESH### sync with oc"
            tmp_sync_with_oc()
        
        path = path.strip('/')
        oc_path = os.path.join(self.notebook_path,path)
        
        print "-->",time_now(),"GET oc_path:%s, path:%s, content:%s, type:%s, format:%s"%(oc_path,path,content,type,format)
        
        file_info = self.oc_exists(oc_path)
        if file_info==False:
            raise web.HTTPError(404, u'No such file or directory: %s' % path)

        if file_info.is_dir():
            """DIR MODEL DONE"""
            if type not in (None, 'directory'):
                raise web.HTTPError(400,
                                u'%s is a directory, not a %s' % (path, type), reason='bad type')
            model = self._dir_model(path,file_info, content=content)
            """ """
        elif type == 'notebook' or (type is None and path.endswith('.ipynb')):
            """TODO"""
            model = super(DeICContentsManager, self)._notebook_model(path, content=content)
            """ """
        else:
            """FILE Model done"""
            if type == 'directory':
                raise web.HTTPError(400,
                                u'%s is not a directory' % path, reason='bad type')
            model = self._file_model(path, file_info, content=content, format=format)
            """ """       
        return model
   
    def is_hidden(self, path):
        """run custom is_hidden function from deiccontents utils"""
        return is_hidden(path)
    
    def file_exists(self, path):
        path = path.strip('/')
        path = os.path.join(self.notebook_path,path)  
        print "--->in file_exists:",self.notebook_path,path
        
        file_info = self.oc_exists(path)
        
        if (file_info!=False and (not file_info.is_dir())):
            return True
        
        print "oc file does not exist!",path 
        return False
    
    def oc_exists(self,path):
        try:
            file_info = self.oc.file_info(path)
            if file_info==None:
                return False
            return file_info
        except:
            return False
    
    def dir_exists(self, path):
        """ensure that the remote owncloud dir exists
        using self.oc client class
        """
        
        path = path.strip('/')
        path = os.path.join(self.notebook_path,path)  
        
        print "--->in dir_exists:",path
        
        file_info = self.oc_exists(path)
        
        if (file_info!=False and file_info.is_dir()):
            return True
        
        print "oc folder does not exist!",path 
        return False   
    
    def _oc_base_model(self,path, file_info):
        """Build the common base of a contents dir model
        This model is owncloud base model"""
        # Create the base model.
        
        print "->base model", path
        
        model = {}
        model['name'] = file_info.get_name()
        model['path'] = path
        model['last_modified'] = file_info.get_last_modified()
        model['created'] = None
        model['content'] = None
        model['format'] = None
        model['mimetype'] = None
        model['writable'] = check_perm(file_info.attributes['{http://owncloud.org/ns}permissions'] \
            ,"WCK")
        
        return model  

    def get_file_contents(self,oc_path):
        try:
            file = self.oc.get_file_contents(oc_path)
            if (file==False):
                return None
            return file
        except:
            return None
        
    def _read_file(self, oc_path, format):
        """Read a non-notebook file.
        os_path: The path to be read.
        format:
        If 'text', the contents will be decoded as UTF-8.
        If 'base64', the raw bytes contents will be encoded as base64.
        If not specified, try to decode as UTF-8, and fall back to base64
        """
        
        bcontent = self.get_file_contents(oc_path)
        
        if bcontent is None:
            raise web.HTTPError(400, "Cannot read non-file %s" % oc_path)
    
        if format is None or format == 'text':
            # Try to interpret as unicode if format is unknown or if unicode
            # was explicitly requested.
            try:
                return bcontent.decode('utf8'), 'text'
            except UnicodeError:
                if format == 'text':
                    raise HTTPError(
                        400,
                        "%s is not UTF-8 encoded" % os_path,
                        reason='bad format',
                    )
        return encodebytes(bcontent).decode('ascii'), 'base64'   
                 
    def _file_model(self, path, dir_info, content=True, format=None):
        """Build a model for a file
        if content is requested, include the file contents.
        format:
          If 'text', the contents will be decoded as UTF-8.
          If 'base64', the raw bytes contents will be encoded as base64.
          If not specified, try to decode as UTF-8, and fall back to base64
        """
        
        oc_path = os.path.join(self.notebook_path,path)
               
        model = self._oc_base_model(path,dir_info)
        model['type'] = 'file'
        
        model['mimetype'] = mimetypes.guess_type(oc_path)[0]

        if content:
            content, format = self._read_file(dir_info.path, format)
            if model['mimetype'] is None:
                default_mime = {
                    'text': 'text/plain',
                    'base64': 'application/octet-stream'
                }[format]
                model['mimetype'] = default_mime

            model.update(
                content=content,
                format=format,
            )

        return model
    
    def _dir_model(self, path, dir_info, content=True):
        """Build a model for a directory
        if content is requested, will include a listing of the directory
        """
        oc_path = dir_info.path
        four_o_four = u'directory does not exist: %r' % oc_path
        
        if is_hidden(oc_path, self.notebook_path):
            super(DeICContentsManager, self).log.info("Refusing to serve hidden directory %r, via 404 Error",
                oc_path
            )
            raise web.HTTPError(404, four_o_four)

        model = self._oc_base_model(path,dir_info)
        model['type'] = 'directory'
        if content:
            model['content'] = contents = []
            oc_list = self.oc.list(oc_path)
            
            for file_info in oc_list:
                name = file_info.get_name()
                file_path = os.path.join(oc_path, name)
                
                if file_info==None:
                    super(DeICContentsManager, self).log.debug("%s not a regular file"\
                        , file_path)
                if super(DeICContentsManager, self).should_list(name) \
                 and not is_hidden(file_path, self.notebook_path):
                    contents.append(self.get(
                        path='%s/%s' % (path, name),
                        content=False)
                    )

            model['format'] = 'json'

        return model
    
    
    
