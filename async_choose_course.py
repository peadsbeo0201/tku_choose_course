import requests
import functools
from parsel import Selector
import re
from bs4 import BeautifulSoup
import json
import time
import aiohttp
import asyncio
from functools import wraps

class TKUCourseAssistant:
    captcha_pattern = re.compile('^\[("[0-9a-z]{40}",?){6}\]$')
    
    CHAPTCHA_MAP = {
        'b6589fc6ab0dc82cf12099d1c2d40ab994e8410c': '0',
        '356a192b7913b04c54574d18c28d46e6395428ab': '1',
        'da4b9237bacccdf19c0760cab7aec4a8359010b0': '2',
        '77de68daecd823babbb58edb1c8e14d7106e83bb': '3',
        '1b6453892473a467d07372d45eb05abc2031647a': '4',
        'ac3478d69a3c81fa62e60f5c3696165a4e5e6ac4': '5',
        'c1dfd96eea8cc2b62785275bca38ac261256e278': '6',
        '902ba3cda1883801594b6e1b452790cc53948fda': '7',
        'fe5dbbcea5ce7e2988b8c69bcfdfde8904aabc1f': '8',
        '0ade7c2cf97f75d009975f4d720d1fa6c19f4897': '9'
    }
    
    class_code = open('code.txt', 'r')

    def __init__(self) -> None:
        self.reqs = requests.session()
        self.reqs.request = functools.partial(self.reqs.request, timeout=30)
        self.reqs.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36'
        self.prev_page = None
        self.my_course_info = MyCourseInformation()
        
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
            
        return wrapper

    @staticmethod
    def show_course_id_list():
        for code in __class__.class_code:
            if code.startswith("a,"):
                print("加選: {}".format(code.split(",")[1]))
            elif code.startswith("d,"):
                print("退選: {}".format(code.split(",")[1]))
                
    @staticmethod
    def get_class_code_list():
        return [code for code in __class__.class_code]
    
    @staticmethod
    def get_captcha_code(text: str):
        assert __class__.captcha_pattern.match(text) is not None, "captcha not match!"
        return ''.join(map(__class__.CHAPTCHA_MAP.get, eval(text)))

    @staticmethod
    def get_hidden_arg(html: str):
        sel = Selector(html)
        return {
            prop: sel.css(f'#{prop}::attr("value")').get()
            for prop in ('__VIEWSTATE', '__VIEWSTATEGENERATOR', '__EVENTVALIDATION')
        }

    @async_event_caller
    async def login(self, std_id: str, passwd: str) -> requests.Response:
        async with self.session.get('https://www.ais.tku.edu.tw/EleCos/login.aspx?ReturnUrl=%2felecos%2f') as resp:
            login_page = await resp.text()
            
        async with self.session.post(
            'https://www.ais.tku.edu.tw/EleCos/Handler1.ashx') as resp:
            captcha_page = await resp.text()
            
        post_data = self.get_hidden_arg(login_page)
        post_data.update({
            '__EVENTTARGET': 'btnLogin',
            'txtCONFM': self.get_captcha_code(captcha_page),
            'txtStuNo': std_id,
            'txtPSWD': passwd
        })
        
        async with self.session.post(
            'https://www.ais.tku.edu.tw/EleCos/login.aspx?ReturnUrl=%2felecos%2f', data=post_data) as resp:
            login_resp_text = await resp.text()
            login_resp = resp


        soup = BeautifulSoup(login_resp_text, 'html.parser')
        msg = soup.find('td', attrs={'style': 'font-family: 細明體; color: blue'})
        if 'E999' in str(msg):
            error_msg = str(msg).split('<br/>')[1].split('<')[0]
        assert login_resp.history and login_resp.history[0].status == 302, f'{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())} Login failed {error_msg}'
        self.prev_page = login_resp_text
        return login_resp

    def show_course_list(self, html):
        self.my_course_info.get_courses(html)

    @async_event_caller
    async def _action(self, course_id: str, action: str) -> requests.Response:

        post_data = self.get_hidden_arg(self.prev_page)
        post_data.update({
            '__EVENTTARGET': action,
            'txtCosEleSeq': course_id
        })
        
        async with self.session.post(
            'https://www.ais.tku.edu.tw/EleCos/action.aspx', data=post_data) as resp:
            self.prev_page = await resp.text()
        soup = BeautifulSoup(self.prev_page, 'html.parser')
        status = soup.find('td', attrs={'style': 'font-family: 細明體;  width: 600px; color: blue;', 'align': 'left', 'valign': 'top'})
        status = str(status).replace(' ', '').replace('\n', '').replace('\r', '')
        status_code = str(status).split('<br/>')[0].split('>')[1].split('<')[0]
        reason_code = str(status).split('<br/>')[1].split('<')[0]
        assert 'I000' in status_code, f"action({action}) failed!, reason code: {reason_code[:4]}"
        return self.prev_page

    @async_event_caller
    async def course_info(self, course_id: str):
        try:
            await self._action(course_id, 'btnOffer')
        except Exception as e:
            print(e)

    @async_event_caller
    async def add_course(self, course_id: str):
        try:
            await self._action(course_id, 'btnAdd')
        except Exception as e:
            print(e)

    @async_event_caller
    async def del_course(self, course_id: str):
        try:
            await self._action(course_id, 'btnDel')
        except Exception as e:
            print(e)
    
    
    def run(self):
        loop = asyncio.new_event_loop()
        loop.run_until_complete(self.main())
    
    async def main(self):
        self.session = aiohttp.ClientSession()
        class_list = __class__.get_class_code_list()
        account = json.load(open("account.json",))
        while class_list!= []:
            try:
                await self.login(account["std_id"], account["passwd"])
                print(f'{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())} login success')
            except Exception as e:
                print(e)
                continue
            tasks = []
            
            while True:
                for code in class_list:
                    if len(tasks) < 100:
                        if code.split(',')[0] == 'a':
                            tasks.append(asyncio.create_task(self.add_course(code.split(',')[1])))
                        elif code.split(',')[0] == 'd':
                            tasks.append(asyncio.create_task(self.del_course(code.split(',')[1])))
                    else:
                        break
                else:
                    continue
                break
            
            t0 = time.time()
            await asyncio.gather(*tasks)
            t1 = time.time()
            print(t1-t0)
                    
        print('所有課程已加退選成功')
        
class MyCourseInformation:
    def __init__(self) -> None:
        pass

    def get_courses(self, html) -> list:
        soup = BeautifulSoup(html, 'html.parser')
        trs = soup.find_all('tr', attrs={'style': 'color:#330099;background-color:White;'})
        for tr in trs:
            for td in tr.find_all('td'):
                course_info_dict = {
                    'course_id': td[0].text,
                    'dept_type': td[1].text,
                    'grade': td[2].text,
                    'subject_id': td[3].text,
                    'subject_name': td[4].text,
                    'professional': td[5].text,
                    'semester': td[6].text,
                    'class_': td[7].text,
                    'group': td[8].text,
                    'option': td[9].text,
                    'credit': td[10].text,
                    'discipline_cluster': td[11].text,
                    'professor': td[12].text,
                    'form': td[13].text,
                    'conflict': td[14].text,
                    'remark': td[15].text
                }
                print(course_info_dict)


if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    client = TKUCourseAssistant()
    client.run()