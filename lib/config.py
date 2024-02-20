

class Url:
    # SSO URL
    SSO_BASE_URL = 'https://sso.tku.edu.tw'
    SSO_LOGIN_URL = f'{SSO_BASE_URL}/NEAI/login2.do?action=EAI'
    SSO_VERICODE_URL = f'{SSO_BASE_URL}/NEAI/ImageValidate'
    SSO_ICLASS_LOGIN_PAGE_URL = f'{SSO_BASE_URL}/NEAI/loginrwd.jsp?myurl=https://sso.tku.edu.tw/iclass/api/cas-login'

class Headers:
    USER_AGENT = 'Mozilla/5.0 (Linux; Android 7.1.2; SM-G9810 Build/QP1A.190711.020; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/92.0.4515.131 Mobile Safari/537.36;webank/h5face;webank/1.0;netType:NETWORK_WIFI;appVersion:18340;packageName:com.wisdomgarden.trpc'
    SSO_HEADERS = {
        'User-Agent': USER_AGENT,
        'Referer': 'https://sso.tku.edu.tw/NEAI/loginrwd.jsp?myurl=https://sso.tku.edu.tw/iclass/api/cas-login'
    }
    
    
    # Tonclass Headers
    TRONCLASS_SESSION_HEADERS = {
        'Host': 'iclass.tku.edu.tw',
        'Connection': 'keep-alive',
        'Accept': 'application/json, text/plain, */*',
        'X-Requested-With': 'XMLHttpRequest',
        'Accept-Language': 'zh-Hant',
        'User-Agent': USER_AGENT,
        'Origin': 'http://localhost',
        'Sec-Fetch-Site': 'cross-site',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Referer': 'http://localhost/',
        'Accept-Encoding': 'gzip, deflate',
        'X-SESSION-ID': ''
    }
    
    


class DataPayload:

    SSO_ICLASS_LOGIN_PAYLOAD = {
        'myurl': 'https://sso.tku.edu.tw/iclass/api/cas-login?ln=zh_TW',
        'ln': 'zh_TW',
        'embed': 'No',
        'vkb': 'No',
        'logintype': 'loginrwd',
        'username': '',
        'password': '',
        'vidcode': ''
    }
