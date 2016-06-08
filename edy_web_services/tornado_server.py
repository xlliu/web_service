# -*- coding: utf-8 -*-
import logging
import logging.config
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from edy_web_services import app
# abs_path = os.path.split(os.path.realpath(__file__))[0]

# 使用一个名字为fib的logger
logger = logging.getLogger('fib')
# 设置logger的level为DEBUG
logger.setLevel(logging.DEBUG)
# 创建一个输出日志到控制台的StreamHandler
hdr = logging.StreamHandler()
formatter = logging.Formatter('[%(asctime)s] %(name)s:%(levelname)s: %(message)s')
hdr.setFormatter(formatter)
# 给logger添加上handler
logger.addHandler(hdr)
if __name__ == '__main__':
    http_server = HTTPServer(WSGIContainer(app),xheaders=True)
    http_server.listen(5000)
    IOLoop.instance().start()
