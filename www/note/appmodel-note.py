////////////////////////////////////////////
1:标准注释:表示.py文件本身使用标准UTF-8编码
# -*- coding: utf-8 -*-
////////////////////////////////////////////

////////////////////////////////////////////
2:包含logging模块,logging.basicConfig函数各参数:
filename: 指定日志文件名
filemode: 和file函数意义相同，指定日志文件的打开模式，'w'或'a'
format: 指定输出的格式和内容，format可以输出很多有用信息，如上例所示:
 %(levelno)s: 打印日志级别的数值
 %(levelname)s: 打印日志级别名称
 %(pathname)s: 打印当前执行程序的路径，其实就是sys.argv[0]
 %(filename)s: 打印当前执行程序名
 %(funcName)s: 打印日志的当前函数
 %(lineno)d: 打印日志的当前行号
 %(asctime)s: 打印日志的时间
 %(thread)d: 打印线程ID
 %(threadName)s: 打印线程名称
 %(process)d: 打印进程ID
 %(message)s: 打印日志信息
datefmt: 指定时间格式，同time.strftime()
level: 设置日志级别，默认为logging.WARNING
默认情况下，logging将日志打印到屏幕，日志级别为WARNING；日志级别大小关系为：CRITICAL > ERROR >WARNING > INFO > DEBUG > NOTSET，当然也可以自己定义日志级别。
stream: 指定将日志的输出流，可以指定输出到sys.stderr,sys.stdout或者文件，默认输出到sys.stderr，当stream和filename同时指定时，stream被忽略
此处设置的日志级别为INFO.
import logging; logging.basicConfig(level=logging.INFO)
////////////////////////////////////////////

////////////////////////////////////////////
3:包含 asyncio,os,json,time等模块
import asyncio, os, json, time
////////////////////////////////////////////

////////////////////////////////////////////
4:datetime是Python处理日期和时间的标准库。
注意到datetime是模块，datetime模块还包含一个datetime类，
通过from datetime import datetime导入的才是datetime这个类。
如果仅导入import datetime，则必须引用全名datetime.datetime。
此处为导入datetime类
from datetime import datetime
////////////////////////////////////////////


////////////////////////////////////////////
5:aiohttp则是基于asyncio实现的HTTP框架。说白了就是一个给予asyncio的模块
此处从aiohttp引入了web类
from aiohttp import web
////////////////////////////////////////////

////////////////////////////////////////////
6:定义了一个index函数,用来产生一个回复
此处使用的是一个类,该类的实现代码可参考
https://aiohttp.readthedocs.io/en/stable/_modules/aiohttp/web_response.html#Response
可以发现都是使用Python实现的

此处是参数详细的说明
https://aiohttp.readthedocs.io/en/stable/_modules/aiohttp/web_response.html#Response

此处直接给出了body,其实就是一个包含body简单的html文件
def index(request):
    return web.Response(body=b'<h1>Awesome</h1>')
////////////////////////////////////////////

////////////////////////////////////////////
7:把一个generator标记为coroutine类型，然后，我们就把这个coroutine扔到EventLoop中执行。
@asyncio.coroutine
////////////////////////////////////////////

////////////////////////////////////////////
8:定义了一个init函数
#web.Application参考
https://aiohttp.readthedocs.io/en/stable/web_reference.html#aiohttp.web.Application
说明:
Application contains a router instance and a list of callbacks that will be called during application finishing.


#router.add_route参考
https://aiohttp.readthedocs.io/en/stable/web_reference.html?highlight=router.add_route#aiohttp.web.UrlDispatcher
说明:Append handler to the end of route table.

#make_handler参考
https://aiohttp.readthedocs.io/en/stable/web_reference.html?highlight=router.add_route#aiohttp.web.Application.make_handler
说明:
    Creates HTTP protocol factory for handling requests.

#coroutine AbstractEventLoop.create_server参考
https://docs.python.org/dev/library/asyncio-eventloop.html?highlight=crea#asyncio.AbstractEventLoop.create_server
说明:
Create a TCP server (socket type SOCK_STREAM) bound to host and port.
Return a Server object, its sockets attribute contains created sockets. Use the Server.close() method to stop the server: close listening sockets.
def init(loop):
    app = web.Application(loop=loop)
    app.router.add_route('GET', '/', index)
    srv = yield from loop.create_server(app.make_handler(),'127.0.0.1',9000)
    logging.info('server started at http://127.0.0.1:9000...')#单纯的打印消息
    return srv
////////////////////////////////////////////

loop = asyncio.get_event_loop()
loop.run_until_complete(init(loop))
loop.run_forever()
