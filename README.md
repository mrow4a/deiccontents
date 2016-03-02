# deiccontents
Work in progress..

Script deiccontents/deicmanager.py is overwriting functions from FileContentsManager of Jupyter, in order to have a notebook files being read from ownCloud webdav server and not from computing node filesystem. 

Script deiccontents/utils.py is set of utilities for deicmanager

Installation:

``http://jupyter.readthedocs.org/en/latest/install.html``

To start up notebook server use:

``jupyter notebook --ip=(server ip addressm e.g. from ipconfig eth0) --no-browser --config=/home/origo/deiccontents/deiccontents.py ``

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
