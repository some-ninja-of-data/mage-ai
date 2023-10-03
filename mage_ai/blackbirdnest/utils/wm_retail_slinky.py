import requests
import json
import logging, sys
logging.basicConfig(stream=sys.stderr, level=logging.INFO)

logger = logging.getLogger(__name__)

class RetailLink():
    def __init__(self,**kwargs):
        self.username = kwargs.get('username')
        self.password = kwargs.get('password')
        self.bot_token = kwargs.get('rl_bot_token')
        self.requests_session = requests.Session()
    
    def login(self):
        login_info = {"username": self.username,"password": self.password,"language": "en"}

        headers = {"content-type": "application/json", "cookie": "lang=en","x-bot-token": self.bot_token,"referer": "https://retaillink.login.wal-mart.com"}

        # to_reset_id = 'dukecannon-wmt-bb1@outlook.com'

        rl = self.requests_session.post('https://retaillink.login.wal-mart.com/api/login', headers=headers,data=json.dumps(login_info),verify=False)
        return rl.json()
    def reset_bot_token(self):
        """
        example response:
        # resp.json = {
        # 'success': True,
        # 'payload': {'token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJsb2dpbklkIjoiZHVrZWNhbm5vbi13bXQtYmIxQG91dGxvb2suY29tIiwiaXNzIjoia3Jha2VuIiwiZXhwIjoxNjk5NjQ1OTMyLCJpYXQiOjE2OTQ0NjE5MzIsImp0aSI6IjdiZTY1Zjk4LTY3N2UtNDU0Mi1iMmMyLWIxOTNjMTU1ZWY0YyJ9.C0N8XbXwEhJN4fsJ3swyY3IbgXo8wsrRsgkmseRILDDvZt_HrI-eCKpwre3m3z4Sw9gdLHxNDEhtDQd33qnDABOhhK_XCUslvDlWr_bhDOr74-IC9rNSIqueZ2K4sSliW8gAG8ApKz2SJO8SjE-cixbIaCJF-lQTpitig98avrMN64al5FzkzKgTxMiVncu7gnsJBIE8_Gke2Kr1-RXViQc2mbREMtaAme30MpLszz1y5_5PdUrRrWAI4JSz8TgW1FIsyZ8QAUntKmg5cKUDywDInIVbobTMGb4BKF7tbufXVA3gJ0_pp3urkA50voZJ8eCwIuopfc95ddspF-Z2ng',
        #  'expiryDate': '2023-11-10 19:52:12.000',
        #  'generationDate': '2023-09-11 19:52:12.000'}
        # }
        """
        resp = self.requests_session.get(f'https://retaillink.supplier.wal-mart.com/api/generateToken/{self.username}',verify=False)
        logger.debug(self.username,resp.json()['payload']['token'])
        return resp.json()