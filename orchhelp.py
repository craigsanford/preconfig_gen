import requests
import json

class OrchHelper:

    def __init__(self, ipaddress):
        self.ipaddress = ipaddress
        self.url_prefix = "https://" + ipaddress + ":443/gms/rest"
        self.session = requests.Session()
        self.data = {}
        self.user = "admin"
        self.password = "admin" 
        
    def login(self):
        try:
            response = self.post("/authentication/login", {"user": self.user, "password": self.password})
            if response.status_code == 200:
                print("{0}: Orch login success".format(self.ipaddress))
                return True
            else:
                print("{0}: Orch login failed: {1}".format(self.ipaddress, response.text))
                return False
        except:
            print("{0}: Unable to connect to Orch appliance".format(self.ipaddress))
            return False

    def logout(self):
        response = self.get("/authentication/logout")
        if response.status_code == 200:
            print("{0}: Orch logout success".format(self.ipaddress))
        else:
            print("{0}: Orch logout failed: {1}".format(self.ipaddress, response.text))
        pass
        
    def post(self, url, data):
        requests.packages.urllib3.disable_warnings()
        response = self.session.post(self.url_prefix + url, json=data, timeout=120, verify=False)
        #print(response.text)
        return response
        
    def empty_post(self, url):
        requests.packages.urllib3.disable_warnings()
        response = self.session.post(self.url_prefix + url, timeout=120, verify=False)
        return response
        
    def put(self, url, data):
        requests.packages.urllib3.disable_warnings()
        response = self.session.put(self.url_prefix + url, json=data, timeout=120, verify=False)
        return response

    def get(self, url):
        requests.packages.urllib3.disable_warnings()
        response = self.session.get(self.url_prefix + url, timeout=120, verify=False)
        return response

    def delete(self, url):
        requests.packages.urllib3.disable_warnings()
        response = self.session.delete(self.url_prefix + url, timeout=120, verify=False)
        return response
        


