# This will go to an orchestrator and pull the current config from the specified appliance.  It will then 
# create a preconfig file with the configuration information of that appliance. 

# 2020.06.30 - Begin modularization project
# 2020.06.13 - Add Loopbacks
# 2020.02.24 - BGP disabled for now 
# 2020.02.20 - Last Tested on 8.8.5
# 2020.02.04 - Local Communities is now required
#

# Known Limitations:
# * Python 3.X only
# * No Software Version
# * No HA
# * Incomplete DHCP
#   - No Options
#   - No NetBios
#   - No Static IPs
# * Limited Routing
# * No Licensing
# * BGP must be enabled for configuration to be pulled
# * No BGP Password 
# * No BGP redistribute (to Silver Peak and route map rules)
# * Inbound Port Forwarding - must translate
# * No Group
# * No networkRole




from orchhelp import OrchHelper
import getpass
import preconf

gms_url = input("Orch IP/Hostname?")
gms_user = input("username?")
gms_password = getpass.getpass("Password?: ")

yaml_text = ""
dhcp_yaml_text = ""
post_input = input("Post preconfiguration file back to Orchestrator? Any input will post, hit <Enter> for False: ")
if(post_input):
    post = True
else:
    post = False 
#dhcpInfo = False

orch = OrchHelper(gms_url, gms_user, gms_password)
#orch.post("/authentication/loginToken", {"user": orch.user, "password":orch.password, "TempCode":False})
#token = input("Input Token: ")
#orch.post("/authentication/login", {"user":orch.user, "password":orch.password, "token":token})
orch.login()

hostname = input("What Appliance? (Hit <Enter> to see the list): ")
while(not hostname):
    app_list = orch.get_appliances()
    for i in app_list:
        print(i['hostName'])
    hostname = input("What Appliance?")
nepk = orch.get_hostname(hostname)
#Build Out useful info
#firewallMode = ["all", "harden", "stateful", "statefulsnat"]
#Labels and zones are needed in Deployment and Loopback
labels = orch.get("/gms/interfaceLabels").json()
#zones = orch.get("/zones").json()
zones = orch.get("/zones?source=menu_firewall_zones_id").json()
#NOW THAT WE HAVE NEPK, GRAB INFO

#appliance extra info
yaml_text += preconf.extra_info(orch, nepk, hostname) 

#deployment
dep_text, dhcp_yaml_text = preconf.deployment(orch, nepk, labels, zones)
yaml_text += dep_text
yaml_text += dhcp_yaml_text

#system - have to for routes info
#yaml_text += preconf.routes(orch, nepk)
yaml_text += preconf.loopback(orch, nepk, labels, zones)
yaml_text += preconf.bgp(orch, nepk)
yaml_text += preconf.templates(orch, nepk)
yaml_text += preconf.bio(orch, nepk)
yaml_text += preconf.inbound_port_forwarding(orch, nepk)

if(post):
    orch.post_preconfig( hostname, yaml_text)
else: 
    print(yaml_text)
orch.logout()

write_to_file = input("File name to write to in local directory, hit enter to skip: ")
if(write_to_file):
    with open(write_to_file, "a+") as f:
        f.write(yaml_text)





