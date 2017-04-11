#!/usr/bin/env python3
# -*- coding: utf-8 -*-

0:本设计文件的目的提供数据访问的函数,即对数据库进行封装
对象-关系映射(OBJECT/RELATIONALMAPPING,简称ORM),是随着面向对象的软件开发方法发展而产生的。
用来把对象模型表示的对象映射到基于SQL的关系模型数据库结构中去。
这样，我们在具体的操作实体对象的时候，就不需要再去和复杂的SQL语句打交道，只需简单的操作实体对象的属性和方法。
ORM技术是在对象和关系之间提供了一条桥梁，前台的对象型数据和数据库中的关系型的数据通过这个桥梁来相互转化。
////////////////////////////////////////

////////////////////////////////////////
1:引入设计所需的库
import asyncio, logging
import aiomysql
////////////////////////////////////////

////////////////////////////////////////
2:打印SQL信息
def log(sql, args=()):
    logging.info('SQL: %s' % sql)
////////////////////////////////////////

////////////////////////////////////////
3:创建连接池
为了简化并更好地标识异步IO，从Python 3.5开始引入了新的语法async和await，可以让coroutine的代码更简洁易读。
1.把@asyncio.coroutine替换为async；
2.把yield from替换为await。
我们需要创建一个全局的连接池，每个HTTP请求都可以从连接池中直接获取数据库连接。
使用连接池的好处是不必频繁地打开和关闭数据库连接，而是能复用就尽量复用。

aiomsql.create_pool:
关于create_pool函数的说明
参考:https://aiomysql.readthedocs.io/en/latest/pool.html

开始的host等参数与connection相关:

https://aiomysql.readthedocs.io/en/latest/connection.html#connection
//Connection
str host:host where the database server is located, default: localhost.
int port:MySQL port to use, default is usually OK.
str user:username to log in as.
str password:password to use.
str db:database to use, None to not use a particular one.
str charset:charset you want to use, for example ‘utf8’.
autocommit:Autocommit mode. None means use server default. (default: False)
//Pool
minsize (int) – minimum sizes of the pool.
maxsize (int) – maximum sizes of the pool.
loop – is an optional event loop instance, asyncio.get_event_loop() is used if loop is not specified.


async def create_pool(loop, **kw):
    logging.info('create database connection pool...')
    global __pool
    __pool = await aiomysql.create_pool(
        host=kw.get('host', 'localhost'),
        port=kw.get('port', 3306),
        user=kw['user'],
        password=kw['password'],
        db=kw['db'],
        charset=kw.get('charset', 'utf8'),
        autocommit=kw.get('autocommit', True),
        maxsize=kw.get('maxsize', 10),
        minsize=kw.get('minsize', 1),
        loop=loop
    )
////////////////////////////////////////

////////////////////////////////////////
4:实现SELECT语句
cursor,记录访问数据库信息的一个游标
游标（cursor）
　　游标是系统为用户开设的一个数据缓冲区，存放SQL语句的执行结果
https://aiomysql.readthedocs.io/en/latest/cursors.html

DictCursor:
A cursor which returns results as a dictionary. All methods and arguments same as Cursor


execute(query, args=None):
  Coroutine, executes the given operation substituting any markers with the given parameters.
    For example, getting all rows where id is 5:
    yield from cursor.execute("SELECT * FROM t1 WHERE id=%s", (5,))
    Parameters:	
        query (str) – sql statement
        args (list) – tuple or list of arguments for sql query
    Returns int: number of rows that has been produced of affected

如果传入size参数，就通过fetchmany()获取最多指定数量的记录，否则，通过fetchall()获取所有记录。
async def select(sql, args, size=None):
    log(sql, args)
    global __pool
    async with __pool.get() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(sql.replace('?', '%s'), args or ())
            if size:
                rs = await cur.fetchmany(size)
            else:
                rs = await cur.fetchall()
        logging.info('rows returned: %s' % len(rs))
        return rs
////////////////////////////////////////

////////////////////////////////////////
5:执行函数
模仿修改数据库的过程.
https://aiomysql.readthedocs.io/en/latest/connection.html?highlight=pool commit
async def execute(sql, args, autocommit=True):
    log(sql)
    async with __pool.get() as conn:
        if not autocommit:
            await conn.begin()
        try:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute(sql.replace('?', '%s'), args)
                affected = cur.rowcount
            if not autocommit:
                await conn.commit()
        except BaseException as e:
            if not autocommit:
                await conn.rollback()
            raise
        return affected
////////////////////////////////////////

////////////////////////////////////////
6:添加问号
参考str类默认函数
https://docs.python.org/3/library/stdtypes.html?highlight=join#str.join

def create_args_string(num):
    L = []
    for n in range(num):
        L.append('?')
    return ', '.join(L)
////////////////////////////////////////

////////////////////////////////////////
7:创建了一个包含4个属性的类,后续都是继承Field.
class Field(object):

    def __init__(self, name, column_type, primary_key, default):
        self.name = name
        self.column_type = column_type
        self.primary_key = primary_key
        self.default = default

    def __str__(self):
        return '<%s, %s:%s>' % (self.__class__.__name__, self.column_type, self.name)

class StringField(Field):

    def __init__(self, name=None, primary_key=False, default=None, ddl='varchar(100)'):
        super().__init__(name, ddl, primary_key, default)

class BooleanField(Field):

    def __init__(self, name=None, default=False):
        super().__init__(name, 'boolean', False, default)

class IntegerField(Field):

    def __init__(self, name=None, primary_key=False, default=0):
        super().__init__(name, 'bigint', primary_key, default)

class FloatField(Field):

    def __init__(self, name=None, primary_key=False, default=0.0):
        super().__init__(name, 'real', primary_key, default)

class TextField(Field):

    def __init__(self, name=None, default=None):
        super().__init__(name, 'text', False, default)
////////////////////////////////////////

////////////////////////////////////////
8:原类的使用
www.liaoxuefeng.com/wiki/0014316089557264a6b348958f449949df42a6d3a2e542c000/0014319106919344c4ef8b1e04c48778bb45796e0335839000

主关键字(primary key)是表中的一个或多个字段，它的值用于唯一地标识表中的某一条记录。在两个表的关系中，主关键字用来在一个表中引用来自于另一个表中的特定记录。主关键字是一种唯一关键字，表定义的一部分。一个表的主键可以由多个关键字共同组成，并且主关键字的列不能包含空值。主关键字是可选的，并且可在 CREATE TABLE 或 ALTER TABLE 语句中定义。

当我们传入关键字参数metaclass时，魔术就生效了，它指示Python解释器在创建MyList时，要通过ListMetaclass.__new__()来创建，在此，我们可以修改类的定义，比如，加上新的方法，然后，返回修改后的定义。

__new__()方法接收到的参数依次是：
 1当前准备创建的类的对象；
 2类的名字；
 3类继承的父类集合；
 4类的方法集合。

class ModelMetaclass(type):

    def __new__(cls, name, bases, attrs):
        if name=='Model':
            return type.__new__(cls, name, bases, attrs)
        tableName = attrs.get('__table__', None) or name
        logging.info('found model: %s (table: %s)' % (name, tableName))
        mappings = dict()
        fields = []
        primaryKey = None
        for k, v in attrs.items():
            if isinstance(v, Field): #判断是否属于Field类
                logging.info('  found mapping: %s ==> %s' % (k, v))
                mappings[k] = v
                if v.primary_key:
                    # 找到主键:
                    if primaryKey:
                        raise StandardError('Duplicate primary key for field: %s' % k)
                    primaryKey = k
                else:
                    fields.append(k)
        if not primaryKey:
            raise StandardError('Primary key not found.')
        for k in mappings.keys():
            attrs.pop(k)  #这里要删除原有的类
        escaped_fields = list(map(lambda f: '`%s`' % f, fields))
        attrs['__mappings__'] = mappings # 保存属性和列的映射关系
        attrs['__table__'] = tableName
        attrs['__primary_key__'] = primaryKey # 主键属性名
        attrs['__fields__'] = fields # 除主键外的属性名
        attrs['__select__'] = 'select `%s`, %s from `%s`' % (primaryKey, ', '.join(escaped_fields), tableName)
        attrs['__insert__'] = 'insert into `%s` (%s, `%s`) values (%s)' % (tableName, ', '.join(escaped_fields), primaryKey, create_args_string(len(escaped_fields) + 1))
        attrs['__update__'] = 'update `%s` set %s where `%s`=?' % (tableName, ', '.join(map(lambda f: '`%s`=?' % (mappings.get(f).name or f), fields)), primaryKey)
        attrs['__delete__'] = 'delete from `%s` where `%s`=?' % (tableName, primaryKey)
        return type.__new__(cls, name, bases, attrs)
////////////////////////////////////////

////////////////////////////////////////
此处涉及到定制类的概念
http://www.liaoxuefeng.com/wiki/
0014316089557264a6b348958f449949df42a6d3a2e542c000/
0014319098638265527beb24f7840aa97de564ccc7f20f6000

class Model(dict, metaclass=ModelMetaclass):

    def __init__(self, **kw):
        super(Model, self).__init__(**kw)

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(r"'Model' object has no attribute '%s'" % key)

    def __setattr__(self, key, value):
        self[key] = value

    def getValue(self, key):
        return getattr(self, key, None)

    def getValueOrDefault(self, key):

        value = getattr(self, key, None)
        if value is None:
            field = self.__mappings__[key]
            if field.default is not None:
                value = field.default() if callable(field.default) else field.default
                logging.debug('using default value for %s: %s' % (key, str(value)))
                setattr(self, key, value)
        return value

    @classmethod
    async def findAll(cls, where=None, args=None, **kw):
        ' find objects by where clause. '
        sql = [cls.__select__]
        if where:
            sql.append('where')
            sql.append(where)
        if args is None:
            args = []
        orderBy = kw.get('orderBy', None)
        if orderBy:
            sql.append('order by')
            sql.append(orderBy)
        limit = kw.get('limit', None)
        if limit is not None:
            sql.append('limit')
            if isinstance(limit, int):
                sql.append('?')
                args.append(limit)
            elif isinstance(limit, tuple) and len(limit) == 2:
                sql.append('?, ?')
                args.extend(limit)
            else:
                raise ValueError('Invalid limit value: %s' % str(limit))
        rs = await select(' '.join(sql), args)
        return [cls(**r) for r in rs]

    @classmethod
    async def findNumber(cls, selectField, where=None, args=None):
        ' find number by select and where. '
        sql = ['select %s _num_ from `%s`' % (selectField, cls.__table__)]
        if where:
            sql.append('where')
            sql.append(where)
        rs = await select(' '.join(sql), args, 1)
        if len(rs) == 0:
            return None
        return rs[0]['_num_']

    @classmethod
    async def find(cls, pk):
        ' find object by primary key. '
        rs = await select('%s where `%s`=?' % (cls.__select__, cls.__primary_key__), [pk], 1)
        if len(rs) == 0:
            return None
        return cls(**rs[0])

    async def save(self):
        args = list(map(self.getValueOrDefault, self.__fields__))
        args.append(self.getValueOrDefault(self.__primary_key__))
        rows = await execute(self.__insert__, args)
        if rows != 1:
            logging.warn('failed to insert record: affected rows: %s' % rows)

    async def update(self):
        args = list(map(self.getValue, self.__fields__))
        args.append(self.getValue(self.__primary_key__))
        rows = await execute(self.__update__, args)
        if rows != 1:
            logging.warn('failed to update by primary key: affected rows: %s' % rows)

    async def remove(self):
        args = [self.getValue(self.__primary_key__)]
        rows = await execute(self.__delete__, args)
        if rows != 1:
           logging.warn('failed to remove by primary key: affected rows: %s' % rows)
////////////////////////////////////////

////////////////////////////////////////
