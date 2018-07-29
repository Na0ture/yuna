import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("sources")
from . import aliyun, windpy
