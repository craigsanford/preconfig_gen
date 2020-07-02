import requests
import json
import base64

class OrchHelper:
    def __init__(self, url, user, password):
        self.url = url
        self.user = user
        self.password = password
        self.url_prefix = "https://" + url + "/gms/rest"
        self.session = requests.Session()
        self.headers = {}

    def login(self):
        response = self.post("/authentication/login", {"user": self.user, "password": self.password})
        if response.status_code == 200:
            print("{0}: Orchestrator login success".format(self.url))
            # get and set X-XSRF-TOKEN
            for cookie in response.cookies:
                if cookie.name == "orchCsrfToken":
                    self.headers["X-XSRF-TOKEN"] = cookie.value
        else:
            print("{0}: Orchestrator login failed: {1}".format(self.url, response.text))

    def logout(self):
        r = self.get("/authentication/logout")
        if r.status_code == 200:
            print("{0}: Orchestrator logout success".format(self.url))
        else:
            print("{0}: Orchestrator logout failed: {1}".format(self.url, r.text))

    def post(self, url, data):
        requests.packages.urllib3.disable_warnings()
        return self.session.post(self.url_prefix + url, json=data, verify=False, timeout=120, headers=self.headers)

    def get(self, url):
        requests.packages.urllib3.disable_warnings()
        return self.session.get(self.url_prefix + url, verify=False, timeout=120, headers=self.headers)

    def delete(self, url):
        requests.packages.urllib3.disable_warnings()
        return self.session.delete(self.url_prefix + url, verify=False, timeout=120, headers=self.headers)

    def put(self, url, data):
        requests.packages.urllib3.disable_warnings()
        return self.session.put(self.url_prefix + url, json=data, verify=False, timeout=120, headers=self.headers)

    def get_appliances(self):
        r = self.get("/appliance")
        if r.status_code == 200:
            return r.json()
        else:
            print("{0}: unable to get appliance list: {1}".format(self.url, r.text))
            return []   

    def empty_post(self, url):
        requests.packages.urllib3.disable_warnings()
        response = self.session.post(self.url_prefix + url, timeout=120, verify=False, headers=self.headers)
        return response

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

        


