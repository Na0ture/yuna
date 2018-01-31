import unittest
import logging
from ..core import sourceSingleton

log = logging.getLogger('test_aliyun')
logging.basicConfig(level=logging.DEBUG)


class TestAliyun(unittest.TestCase):

    def test_one(self):
        response = sourceSingleton._request_to_response("002614.SZ", ("20170601", "20180117"))
        a = sourceSingleton._json_to_dict(response)
        log.debug(a)