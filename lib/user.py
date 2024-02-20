from iclass import SSO
import asyncio
from functools import wraps
import aiohttp


class User:
    def __init__(self, std_id=None, passwd=None):
        self.std_id = std_id
        self.passwd = passwd
        self.session = None
    
    def async_event_caller(func):
        if asyncio.iscoroutinefunction(func):
            @wraps(func)
            async def wrapper(self, *args, **kwargs):
                task = [asyncio.create_task(func(self, *args, **kwargs))]
                result = await asyncio.gather(*task)
                return result[0]
        else:
            def wrapper(*args, **kwargs):
                print('this is not async function')
    
    @async_event_caller
    async def login(self):
        if not self.is_login:
            client = SSO(self.std_id, self.passwd, self.session)
            cookies, self.is_login = await client.login()
            if cookies is not None:
                self.set_session(cookies)
                return True
            else:
                return False
        return True
    
    