import requests
from bs4 import BeautifulSoup
import json
import logging, sys
logging.basicConfig(stream=sys.stderr, level=logging.INFO)

logger = logging.getLogger(__name__)

class Atlas():
    def __init__(self, **kwargs):
        self.username = kwargs.get('username')
        self.password = kwargs.get('password')
        self.requests_session = requests.Session()
        self.requests_session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36 Edg/117.0.2045.31"
                }
            )
        self.fingerprint = self.requests_session.get('https://atlasdsr.okta.com/auth/services/devicefingerprint')
        self.nonce_info = self.requests_session.post('https://atlasdsr.okta.com/api/v1/internal/device/nonce')
    
    def login(self, **kwargs):
        self.username = self.username if self.username else kwargs.get('username')
        self.password = self.password if self.password else kwargs.get('password')
        return_val = 'failed'
        try:
            login_info = {
                "password": self.password,
                "username": self.username,
                "options": {
                    "warnBeforePasswordExpired":True,
                    "multiOptionalFactorEnroll":True
                    }
                }
            loginpg = self.requests_session.post('https://atlasdsr.okta.com/api/v1/authn',json=login_info)
            login_json = loginpg.json()
            authtoken = login_json['sessionToken']
            logger.debug(f"{self.username} - {authtoken}")
            self.logintoken = f"{self.username} - {authtoken}"
            logger.debug(self.logintoken)
            b = self.requests_session.get(f"https://atlasdsr.okta.com/login/sessionCookieRedirect?checkAccountSetupComplete=true&token={authtoken}&redirectUrl=https%3A%2F%2Fatlasdsr.okta.com%2Fuser%2Fnotifications", verify=False)
            soup = BeautifulSoup(b.content, 'html.parser')
            # bcontent = b.content.decode('utf-8')
            # xsrf_token = bcontent.split('_xsrfToken">')[1].split("<")[0]
            xsrf_token = soup.find(id="_xsrfToken").get_text()
            logger.debug(f"{xsrf_token}")
            self.xsrf_token = f"{xsrf_token}"
            xheaders={
                "X-Okta-User-Agent-Extended": "okta-auth-js/6.3.0 @okta/okta-react/6.4.3",
                "X-Okta-Xsrftoken": xsrf_token,
            }
            okta = self.requests_session.get('https://atlasdsr.okta.com/.well-known/openid-configuration',headers=xheaders, verify=False)
            okta_id = okta.headers['X-Okta-Request-Id']
            c=self.requests_session.get('https://accounts.atlasdsr.com/RetailerPortal',verify=False)
            soup = BeautifulSoup(c.content, 'html.parser')
            oidc_form = soup.find(id="appForm")
            oidc_state = oidc_form.find(attrs={"name":"state"}).get('value')
            oidc_code = oidc_form.find(attrs={"name":"code"}).get('value')
            xheaders.update({
                    "content-type": "application/x-www-form-urlencoded",
                    "Dnt": "1",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7"
                    })
            bb = self.requests_session.post(f"https://id.atlasdsr.com/signin-oidc",headers=xheaders,data={"state": oidc_state,"code": oidc_code},verify=False)
            
            soup = BeautifulSoup(bb.content, 'html.parser')
            # to_reset_id = 'dukecannon-wmt-bb1@outlook.com'
            oid_token = soup.find(attrs={"name": "id_token"}).get('value')
            logger.debug(f"oid token {oid_token}")
            oid_session_state = soup.find(attrs={"name": "session_state"}).get('value')
            logger.debug(f"{oid_token}\n{oid_session_state}")
            logger.debug(f"{oid_token}\n{oid_session_state}")
            thedata = {
                "id_token": oid_token,
                "scope": "openid profile atlasid",
                "session_state": oid_session_state

            }
            cb = self.requests_session.post('https://accounts.atlasdsr.com/Account/LoginCallback',data=thedata,verify=False )
            soup = BeautifulSoup(cb.content, 'html.parser')
            page_title = soup.title.string
            if page_title.strip().lower() == 'home - atlas dsr':
                logger.info(f"User {self.username} logged in")
                return_val = "success"
            else:
                logger.error(f"User {self.username} could not logged in")
                return_val = 'failed'
        except Exception as failed_e:
            logger.error(failed_e)
            return_val = failed_e

        return return_val

    def _get_client_list(self, default_db='4L8ppYO8mN', tenant_id='521'):
        headers = {
            "Accept": "application/json",
            "AtlasDatabaseid": default_db,
            "withCredentials": "true"
            }
        logger.debug(default_db,tenant_id)
        client_list_url = f"https://atlas.atlasdsr.com/api/retailer-portal/login-for-customers/{default_db}/{tenant_id}"
        clients_list = self.requests_session.get(client_list_url,headers=headers, verify=False)
        returning = clients_list.json()

        return returning

    def get_clients(self, default_db=None, tenant_id=None, client_type='Retail Link', **kwargs):
        client_filters = kwargs.get('client_filters',{})
        logger.debug(client_filters)
        client_filters['type'] = client_type
        client_filter_list = list(client_filters.keys())
        conn_info = {}
        if default_db:
            conn_info["default_db"] = default_db
        if tenant_id:
            conn_info["tenant_id"] = tenant_id
        client_list = self._get_client_list(**conn_info)
        logger.debug(client_list)
        filtered_clients = []

        for client_info in client_list:
            failed_check = False
            for client_filter in client_filter_list:
                if client_filter in list(client_info.keys()):
                    if not client_filters[client_filter] == client_info[client_filter]:
                        failed_check=True
                        continue
            if failed_check==True:
                continue
            filtered_clients.append(client_info)

        return filtered_clients


        

    def _update_bot_token(self, default_db=None, client_info_id=None, new_retail_link_pw=None, new_token_value=None, new_token_expiration=None):
        """
        example response:
        # resp.json = {
        # 'success': True,
        # 'payload': {'token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJsb2dpbklkIjoiZHVrZWNhbm5vbi13bXQtYmIxQG91dGxvb2suY29tIiwiaXNzIjoia3Jha2VuIiwiZXhwIjoxNjk5NjQ1OTMyLCJpYXQiOjE2OTQ0NjE5MzIsImp0aSI6IjdiZTY1Zjk4LTY3N2UtNDU0Mi1iMmMyLWIxOTNjMTU1ZWY0YyJ9.C0N8XbXwEhJN4fsJ3swyY3IbgXo8wsrRsgkmseRILDDvZt_HrI-eCKpwre3m3z4Sw9gdLHxNDEhtDQd33qnDABOhhK_XCUslvDlWr_bhDOr74-IC9rNSIqueZ2K4sSliW8gAG8ApKz2SJO8SjE-cixbIaCJF-lQTpitig98avrMN64al5FzkzKgTxMiVncu7gnsJBIE8_Gke2Kr1-RXViQc2mbREMtaAme30MpLszz1y5_5PdUrRrWAI4JSz8TgW1FIsyZ8QAUntKmg5cKUDywDInIVbobTMGb4BKF7tbufXVA3gJ0_pp3urkA50voZJ8eCwIuopfc95ddspF-Z2ng',
        #  'expiryDate': '2023-11-10 19:52:12.000',
        #  'generationDate': '2023-09-11 19:52:12.000'}
        # }
        """
        # "tokenExpirationDate":"2023-08-05T05:00:00.000Z"
        
        token_reset_payload = {
            "newPassword":new_retail_link_pw,
            "botTokenModel": {
                "botToken": new_token_value,
                "tokenExpirationDate": new_token_expiration
            }
        }

        resp = self.requests_session.post(f'https://atlas.atlasdsr.com/api/retailer-portal/password/{default_db}/{client_info_id}',json=token_reset_payload,verify=False)
        updated_response = resp.content.decode('utf-8')
        print(updated_response)
        return updated_response