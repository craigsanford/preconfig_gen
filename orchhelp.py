import requests
import json
import base64

class OrchHelper:

    def __init__(self, ipaddress):
        self.ipaddress = ipaddress
        self.url_prefix = "https://" + ipaddress + ":443/gms/rest"
        self.session = requests.Session()
        self.data = {}
        self.user = "admin"
        self.password = "admin" 


    def post_preconfig(self, hostname, yaml_text):
        # convert from a string to base64,
        # then post that b64 output as a string to Orch
        yaml_upload = self.yaml_to_b64string(yaml_text)
        data = {}
        data['name'] = hostname 
        data['configData'] = yaml_upload
        data['autoApply'] = True
        data['tag'] = hostname
        r = self.post("/gms/appliance/preconfiguration/validate", data)
        if(r.status_code == 200):
                self.post("/gms/appliance/preconfiguration/", data)
                #print("Success")
        else:
                print("Problem with upload")
                print(r.text)


    def get_hostname(self, hostname):
        app = self.get("/appliance").json()
        for i in app:
                if (i['hostName']== hostname):
                        return i['nePk']

    def yaml_to_b64string(self, yaml):
        yaml_byte = yaml.encode('utf-8')
        yaml_b64 = base64.b64encode(yaml_byte)
        yaml_upload = str(yaml_b64)
        # take off the (b' ') portion
        yaml_upload = yaml_upload[2:-1]
        return yaml_upload

    def b64string_to_yaml(yaml_upload):
        yaml_byte = base64.b64decode(yaml_upload)
        yaml = yaml_byte.decode('utf-8')
        yaml = bytes(yaml, 'utf-8').decode("unicode_escape")
        return yaml

        
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
        


