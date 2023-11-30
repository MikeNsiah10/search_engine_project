import sys
import os

os.chdir("/home/user123/search_engine_project")
sys.path.append("/home/user123/search_engine_project")

from app import app

application = app
