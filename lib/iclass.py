from config import *


class SSO:
    def __init__(self, std_id, passwd, aiohttp_client_session):
        self.reqs = aiohttp_client_session
        self.std_id = std_id
        self.passwd = passwd
        
    async def login(self):
        async with self.reqs.get(Url.SSO_ICLASS_LOGIN_PAGE_URL, headers=Headers.SSO_LOGIN_PAGE_HEADERS) as resp:
            await resp.text()
        
        async with self.reqs.get(Url.SSO_ICLASS_LOGIN_PAGE_URL, headers=Headers.SSO_LOGIN_PAGE_HEADERS) as resp:
            await resp.text()

        async with self.reqs.get(Url.SSO_VERICODE_URL, headers=Headers.SSO_HEADERS) as resp:
            await resp.read()

        async with self.reqs.post(Url.SSO_VERICODE_URL, data={'outType': 2}, headers=Headers.SSO_HEADERS) as resp:
            text = await resp.text()
            vidcode = text.replace('\r\n', '')
            print(vidcode)
        login_payload = self.set_login_payload(vidcode)
        async with self.reqs.post(Url.SSO_LOGIN_URL, headers=Headers.SSO_HEADERS, data=login_payload) as resp:
            try:
                result = await resp.json()
                if resp.headers.get('Set-Cookie') != None:
                    print(result)
                    print("Login!!")
                    return(resp.headers.get('Set-Cookie'), True)
                else:
                    print("ERROR!! Can't login!!")
                    return(None, False)
            except:
                return (None, False)
            
        
    def set_login_payload(self, vidcode):
        login_payload = DataPayload.SSO_ICLASS_LOGIN_PAYLOAD
        login_payload['username'] = self.std_id
        login_payload['password'] = self.passwd
        login_payload['vidcode']  = vidcode
        return login_payload
        