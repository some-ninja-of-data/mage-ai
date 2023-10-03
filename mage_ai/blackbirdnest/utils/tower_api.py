import requests
import base64
import json
import datetime
from copy import deepcopy

TOWER_USER = "walmart_retail_link"
TOWER_API_HOST = "https://api.tower.thestable.com"
TOWER_PW = "patAhQ75r6sNRDg9cvZKkm5oS6RrT9PrCLjvQCJvlpCy4wx64A"
TOWER_SCOPE = "high_radius"

class Tower(object):   
    def __init__(self, **kwargs):
        self.username = kwargs.get('username', TOWER_USER)
        self.pw = kwargs.get('password', TOWER_PW)
        self.scope = kwargs.get('scope', TOWER_SCOPE)
        self.api_host = kwargs.get('api_host', TOWER_API_HOST)
        self.token_expires = datetime.datetime.strptime('1950-01-01','%Y-%m-%d')
        self.session = requests.Session()
        self.token = None
    def _get_token(self):
        if self.token_expires < datetime.datetime.now():
            url ='{}/oauth2/access_token'.format(self.api_host)
            data = {
                "client_id": self.username,
                "client_secret": self.pw,
                "scope": self.scope
            }
            token_response = self.session.post(url, json=data, verify=False)
            token_raw = token_response.json()
            self.token = token_raw['token']
            split_token = token_raw['token'].split('.')
            token_type_raw, token_issued_raw = [*split_token[0:2]]
            token_type = json.loads(base64.b64decode(token_type_raw))
            token_issued = json.loads(base64.b64decode(token_issued_raw))
            token_expires_dt = datetime.datetime.fromtimestamp(token_issued['exp'])
            self.token_expires = token_expires_dt
        return self.token
    
    def get_clients_for_service(self, **kwargs):
        """
        Example response=[
        {
            'id': '9f96bf8e-e069-4056-8242-f96f9f46ecbd',
            'service_name': 'high_radius',
            'site_url': None,
            'client_id': 593,
            'user_id': 'emma@ideavillage.com',
            'password': 'passwordasdfasdf23423',
            'vendor_ids': ['484720'],
            'change_notify_emails': [],
            'sales_rep_email': None,
            'password_auto_change': False,
            'is_reporting': False,
            'in_atlas': False,
            'twilio_phone_number': None,
            'expires_at': '2023-07-01T18:49:21.268Z',
            'password_updated_at': '2023-05-02T18:49:21.268Z',
            'is_active': True,
            'custom_params': None,
            'sourcefolderpathname': None,
            'rl_bot_token': None,
            'rl_bot_token_expires_at': None,
            'rl_bot_token_changed_at': None,
            'created_at': '2023-05-02T18:49:21.268Z',
            'updated_at': '2023-05-02T18:49:21.268Z',
            'deletedAt': None
            }
            ]
        """
        token = self._get_token()
        auth =  {
                "Authorization": f"Bearer {token}",
        }
        self.session.headers.update(auth)
        service_name = kwargs.get('service_name')
        active_bot_is_priority = kwargs.get('active_bot_is_priority', True)

        creds_response = self.session.get(f"https://api.tower.thestable.com/retail/{service_name}/all-passwords", verify=False)
        creds_json = creds_response.json()
        creds_active_only = []
        suppliers_dictionary = {}
        supplier_filters = kwargs.get('client_filters')
        for creds in creds_json:            
            failed_check = False
            if creds['is_active'] and (creds['is_reporting'] or creds['is_bot'] or creds['in_atlas']) and creds['sourcefolderpathname']:
                this_supplier = suppliers_dictionary.get(creds['sourcefolderpathname'],None)
                if supplier_filters:
                    for filter_key in list(supplier_filters.keys()):
                        if creds[filter_key] != supplier_filters[filter_key]:
                            failed_check=True
                            continue
                    if failed_check==True:
                        continue
                if this_supplier:
                    if active_bot_is_priority and this_supplier.get('bot-account',None):
                        continue
                    
                suppliers_dictionary[creds['sourcefolderpathname']] = {"bot-account": True, "creds_info": creds} if creds.get('rl_bot_token') else {"creds_info": creds}

                this_cred = {}
                this_cred = deepcopy(creds)
                this_cred.update({
                    'Supplier': creds['sourcefolderpathname'],
                    'User ID': creds['user_id'],
                    'Password': creds['password'],
                    'Twilio #': '1{}'.format(creds['twilio_phone_number'])
                    })
                suppliers_dictionary[creds['sourcefolderpathname']] = {"bot-account": True, "creds_info": this_cred} if creds.get('rl_bot_token') else {"creds_info": this_cred}
        for s in suppliers_dictionary:
            creds_active_only.append(suppliers_dictionary[s]['creds_info'])
        return creds_active_only

    def get_all_clients_for_service(self, **kwargs):
        """
        Example response=[
        {
            'id': '9f96bf8e-e069-4056-8242-f96f9f46ecbd',
            'service_name': 'high_radius',
            'site_url': None,
            'client_id': 593,
            'user_id': 'emma@ideavillage.com',
            'password': 'passwordasdfasdf23423',
            'vendor_ids': ['484720'],
            'change_notify_emails': [],
            'sales_rep_email': None,
            'password_auto_change': False,
            'is_reporting': False,
            'in_atlas': False,
            'twilio_phone_number': None,
            'expires_at': '2023-07-01T18:49:21.268Z',
            'password_updated_at': '2023-05-02T18:49:21.268Z',
            'is_active': True,
            'custom_params': None,
            'sourcefolderpathname': None,
            'rl_bot_token': None,
            'rl_bot_token_expires_at': None,
            'rl_bot_token_changed_at': None,
            'created_at': '2023-05-02T18:49:21.268Z',
            'updated_at': '2023-05-02T18:49:21.268Z',
            'deletedAt': None
            }
            ]
        """
        service_name = kwargs.get('service_name')
        creds_json = self.get_clients_for_service(service_name=service_name)
        return creds_json

    def update_client(self, **kwargs):
        token = self._get_token()
        auth =  {
                "Authorization": f"Bearer {token}",
        }
        self.session.headers.update(auth)
        
        update_params = kwargs.get('update_params')
        service_name = update_params.get('service_name')
        tower_id = update_params.get("tower_id")
        tower_client_id = update_params.get('client_id')
        new_client_info = {
            "client_id": tower_client_id,
            "rl_bot_token": update_params.get('rl_bot_token'),
            "service_name": service_name
        }
        print(new_client_info)
        update_url = f'https://api.tower.thestable.com/retail/{service_name}/password/{tower_id}'  
        print(update_url)      
        update_response = self.session.put(update_url, json=new_client_info, verify=False)
        return update_response.json()


