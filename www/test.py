import logging
import asyncio
import orm
from models import User, Blog, Comment

logging.basicConfig(level=logging.INFO)

loop = asyncio.get_event_loop()

async def test():
     await orm.create_pool(loop=loop,user='www-data', password='www-data', db='awesome')
     u = User(name='Test4', email='test4@example.com', passwd='1234567890', image='about:blank')
     await u.save()
     await orm.destroy_pool()   


loop.run_until_complete(test())
loop.close()  

