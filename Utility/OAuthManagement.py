import os
import sys
import threading
import traceback
import webbrowser
from enum import Enum

import httplib2
from apiclient import discovery
from oauth2client import client

from model_Json import DataSource2

SCOPES = ('https://www.googleapis.com/auth/gmail.send',
          'https://www.googleapis.com/auth/userinfo.email')
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Gmail API Python Send Email'


class AuthExecutor:
    def requestOauthCredentials(self):
        flow = None
        if os.name == 'nt':
            appdata_path = os.getenv("APPDATA")
            tmp_client_path = appdata_path + "\\" + ".tmpClient"
        elif os.name == 'posix':
            appdata_path = '/tmp'
            tmp_client_path = appdata_path + "/" + ".tmpClient"
        else:
            appdata_path = '/tmp'
            tmp_client_path = appdata_path + "/" + ".tmpClient"


        try:
            f = open(tmp_client_path, "w")
            f.write(
                "{\"installed\":{\"client_id\":\"182659479681-721n498ifo1i3r36qvamsqaoo9htc0o6.apps.googleusercontent.com\",\"project_id\":\"powerpanel-248406\",\"auth_uri\":\"https://accounts.google.com/o/oauth2/auth\",\"token_uri\":\"https://accounts.google.com/o/oauth2/token\",\"auth_provider_x509_cert_url\":\"https://www.googleapis.com/oauth2/v1/certs\",\"client_secret\":\"o7qgdzZnS1pw5lZNx2s2Zc1v\",\"redirect_uris\":[\"urn:ietf:wg:oauth:2.0:oob\",\"http://localhost\"]}}")
            f.flush()
            f.close()

            flow = client.flow_from_clientsecrets(f.name, SCOPES, redirect_uri='urn:ietf:wg:oauth:2.0:oob')
            auth_uri = flow.step1_get_authorize_url()
            webbrowser.open(auth_uri)
            flow.user_agent = APPLICATION_NAME
        except Exception:
            traceback.print_exc(file=sys.stdout)
        finally:
            if f:
                try:
                    os.remove(f.name)
                except Exception:
                    traceback.print_exc(file=sys.stdout)

    def requestExchange(self, code, callback):
        try:
            requestThread = DoExchangedThread(code, callback)
            requestThread.start()
        except Exception:
            traceback.print_exc(file=sys.stdout)


class DoExchangedThread(threading.Thread):
    # ERROR_CODE
    SUCCESS = 0
    ERROR = 1

    def __init__(self, code, callback):
        super(DoExchangedThread, self).__init__(None)
        self.code = code
        self.callback = callback

    def run(self):
        try:
            f = open(".forExchangCodeOnServerClientId", "w")
            f.write(
                "{\"installed\":{\"client_id\":\"182659479681-721n498ifo1i3r36qvamsqaoo9htc0o6.apps.googleusercontent.com\",\"project_id\":\"powerpanel-248406\",\"auth_uri\":\"https://accounts.google.com/o/oauth2/auth\",\"token_uri\":\"https://accounts.google.com/o/oauth2/token\",\"auth_provider_x509_cert_url\":\"https://www.googleapis.com/oauth2/v1/certs\",\"client_secret\":\"o7qgdzZnS1pw5lZNx2s2Zc1v\",\"redirect_uris\":[\"urn:ietf:wg:oauth:2.0:oob\",\"http://localhost\"]}}")
            f.flush()
            f.close()
            flow = client.flow_from_clientsecrets(f.name, SCOPES, redirect_uri='urn:ietf:wg:oauth:2.0:oob')
            credentials = flow.step2_exchange(self.code)

            if credentials and not credentials.invalid:
                oauthCredentials = DataSource2.OAuthCredentials()
                oauthCredentials.clientId = credentials.client_id
                oauthCredentials.clientSecret = credentials.client_secret
                oauthCredentials.accessToken = credentials.access_token
                oauthCredentials.refreshToken = credentials.refresh_token
                oauthCredentials.tokenUri = credentials.token_uri
                oauthCredentials.tokenExpiry = credentials.token_expiry

            http = credentials.authorize(httplib2.Http())
            service = discovery.build('gmail', 'v1', http=http, cache_discovery=False)
            user_info_service = discovery.build(serviceName='oauth2', version='v2', http=http, cache_discovery=False)
            user_info = None
            try:
                user_info = user_info_service.userinfo().get().execute()
                if user_info and user_info.get('email'):
                    oauthCredentials.oauthUserEmail = user_info.get('email')
                    self.callback(self.SUCCESS, oauthCredentials)
                else:
                    pass
            except Exception:
                pass

        except Exception:
            print("exchange failed")
            traceback.print_exc(file=sys.stdout)
            self.callback(self.ERROR, None)
        finally:
            if f:
                try:
                    os.remove(f.name)
                except Exception:
                    traceback.print_exc(file=sys.stdout)


class OAuthErrorCode(Enum):
    SUCCESS = 0
    ERROR = 1
