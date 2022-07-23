from flask import Flask

app = Flask(__name__, 
    static_url_path='/', 
    static_folder='wwwroot', 
    template_folder='html')

from oap.api import *
from oap.pages import *