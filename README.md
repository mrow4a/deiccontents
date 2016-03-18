#Work in progress.. 

DONE:

* Read normal files from the webdav server.
* Read the directory structure of webdav directory contents Notebooks/ - after running Jupyter, directory structure is being read directly from webdav. 
* Prepared class in order to easily add new components and features.
* Proper commenting structure to ease teamwork in order to understand the way the notebook works.

TODO:

[for the development purposes, Jupyter server directory and webdav server is synced with normal owncloudcmd client, so that jupyter server works without most of the features]

* Save notebook in webdav
* Read notebook from webdav
* Save file in webdav
* Create directory
* Implementation of checkpoints (save file dynamicaly in webdav)
* Upload file to webdav via Jupyter

#WebDav deiccontents (will work with all owncloud installations)

Script deiccontents/deicmanager.py is overwriting functions from FileContentsManager of Jupyter, in order to have a notebook files being read from ownCloud webdav server and not from computing node filesystem. 

Script deiccontents/utils.py is set of utilities for deicmanager

#Instalation

Change this lines:

``
self.oc = owncloud.Client("https://YOUR.SERVER/")
self.oc.login("YOUR_USER", "YOUR_PASSWORD") could be ("","") for passwordless login
``

Recommended installation:

``https://www.continuum.io/downloads``

Be sure you are accepting prepending .bashrc during installation.

``conda install pip``

``pip install pyocclient``

temporarily, for development purposes, install owncloud ``https://software.opensuse.org/download/package?project=isv:ownCloud:desktop&package=owncloud-client``

Now, to run default notebook server ``jupyter notebook``

Installation:

``http://jupyter.readthedocs.org/en/latest/install.html``

Additionaly:

create folder at e.g. ``~/Notebooks``. It will be the location at which at this development stage Notebook files will be stored. Later on, the file list will be read/written/updated directly from webdav ownCloud server and there won't be a need of ``cd`` to any folder. Notebooks server could be started from any location on the DeIC Computing Node.

To start up notebook server from ``Notebooks`` folder use:

``jupyter notebook --ip={server ip address e.g. from ipconfig eth0} --no-browser --config={path to your dir with content manager}/deiccontents/deiccontents.py --notebook-dir={path to your dir with Notebooks}/Notebooks``

#Installing new notebooks
e.g.
``conda create -n r r r-essentials anaconda``

``source activate r``

``echo "Y" | conda install notebook ipykernel``

``ipython kernelspec install-self --user``

# Security concerns
In the development stage it is not recommended to publish notebook server port in the internet, and work only on localhost or closed environment. If needed, one can set the firewall rules.  

``sudo iptables -A INPUT -p tcp --dport 8888 -j DROP``

``sudo iptables -A INPUT -p tcp --dport 8888 -s (trusted address) -j ACCEPT``
