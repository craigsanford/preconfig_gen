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

gms_url = "seteam-orchestrator.silverpeak.cloud"
#gms_url = input("Orch IP/Hostname?")
gms_user = "craigsanford"
#gms_password = "admin"
yaml_text = ""
dhcp_yaml_text = ""
post = True 
dhcpInfo = False
#
orch = OrchHelper(gms_url)
orch.user = gms_user
#orch.user = input("Username? ")
#orch.password = gms_password
orch.password = getpass.getpass("Password?: ")
#orch.post("/authentication/loginToken", {"user": orch.user, "password":orch.password, "TempCode":False})
#token = input("Input Token: ")
#orch.post("/authentication/login", {"user":orch.user, "password":orch.password, "token":token})
orch.login()

hostname = "Baltimore-Sanford"
#hostname = input("What Appliance?")

nepk = orch.get_hostname(hostname)
#Build Out useful info
#firewallMode = ["all", "harden", "stateful", "statefulsnat"]
#Labels and zones are needed in Deployment and Loopback
labels = orch.get("/gms/interfaceLabels").json()
zones = orch.get("/zones").json()

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
