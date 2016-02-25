import sys,os
sys.path.append(os.path.dirname(os.path.realpath(__file__)))
from deiccontents import DeICContentsManager
c = get_config()

c.NotebookApp.contents_manager_class = DeICContentsManager
