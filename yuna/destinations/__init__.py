import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("destinations")
from . import mysql
