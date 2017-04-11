import logging
import asyncio
import orm
from models import User, Blog, Comment

logging.basicConfig(level=logging.INFO)

#创建一个event_loop
loop = asyncio.get_event_loop()

async def test():
     #创建进程池,这里使用的用户在schema.sql脚本中给与了权限
     await orm.create_pool(loop=loop,user='www-data', password='www-data', db='awesome')
     #此处将调用models中的User来创建一个用户
     u = User(name='Test4', email='test4@example.com', passwd='1234567890', image='about:blank')
     await u.save()#将该用户存放在数据库中
     await orm.destroy_pool()#销毁进程池

#等待运行完
loop.run_until_complete(test())
#关闭event_loop,在此之前要现销毁进程池
loop.close()  

