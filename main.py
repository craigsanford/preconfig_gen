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
post = False 
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

#hostname = input("What Appliance?")
hostname = "Baltimore-Sanford"

nepk = orch.get_hostname(hostname)
#Build Out useful info
#firewallMode = ["all", "harden", "stateful", "statefulsnat"]
#Labels is needed in Deployment and Loopback
labels = orch.get("/gms/interfaceLabels").json()
#zones = orch.get("/zones").json()

#NOW THAT WE HAVE NEPK, GRAB INFO

#appliance extra info
yaml_text += preconf.extra_info(orch, nepk, hostname) 

#deployment
dep_text, dhcp_yaml_text = preconf.deployment(orch, nepk, labels)
yaml_text += dep_text
yaml_text += dhcp_yaml_text

#system - have to for routes info
yaml_text += preconf.routes(orch, nepk)
yaml_text += preconf.loopback(orch, nepk, labels)
#*********
bgp = orch.get("/appliance/rest/" + nepk + "/bgp/config/system").json()
bgp_neigh = orch.get("/appliance/rest/" + nepk + "/bgp/config/neighbor").json()
if(bgp['enable']):
    yaml_text += "\nbgpSystemConfig: \n"
    yaml_text += "  enable: true \n"
    yaml_text += "  asn: " + str(bgp['asn']) + "\n"
    yaml_text += "  routerId: " + bgp['rtr_id'] + "\n"
    yaml_text += "  enableGracefulRestart: " + str(bgp['graceful_restart_en']).lower() + "\n"
    yaml_text += "  maxRestartTime: " + str(bgp['max_restart_time']) + "\n"
    yaml_text += "  maxStalePathTime: " + str(bgp['stale_path_time']) + "\n"
    #yaml_text += "  redistToSilverPeak: false" + bgp['asn'] + "\n"
    yaml_text += "  propagateAsPath: " + str(bgp['remote_as_path_advertise']).lower() + "\n"
    yaml_text += "  redistOspfToBgp: " + str(bgp['redist_ospf']).lower() + "\n"
    yaml_text += "  filterTag: " + str(bgp['redist_ospf_filter']) + "\n"

    # if(bgp_neigh):
        # yaml_text += "  neighbors: \n"
        # for i in range(len(list(bgp_neigh))):
        
            # yaml_text += "    - peerIpAddress: " + list(bgp_neigh)[i] + "\n"
            # yaml_text += "      enableImports: " + str(bgp_neigh[list(bgp_neigh)[i]]['import_rtes']).lower() + "\n"
            # yaml_text += "      peerAsn: " + str(bgp_neigh[list(bgp_neigh)[i]]['remote_as']) + "\n"
            # #yaml_text += "      peerType: " + bgp_neigh[list(bgp_neigh)[i]]['type'] + "\n"
            # yaml_text += "      enableNeighbor: " + str(bgp_neigh[list(bgp_neigh)[i]]['enable']).lower() + "\n"
            # #yaml_text += "      localPreference: " + str(bgp_neigh[list(bgp_neigh)[i]]['loc_pref']) + "\n"
            # yaml_text += "      med: " + str(bgp_neigh[list(bgp_neigh)[i]]['med']) + "\n"
            # yaml_text += "      asPrependCount: " + str(bgp_neigh[list(bgp_neigh)[i]]['as_prepend']) + "\n"
            # yaml_text += "      nextHopSelf: " + str(bgp_neigh[list(bgp_neigh)[i]]['next_hop_self']).lower() + "\n"
            # if("lcl_interface" in bgp_neigh[list(bgp_neigh)[i]].keys()):
                # yaml_text += "      sourceIpInterface: " + bgp_neigh[list(bgp_neigh)[i]]['lcl_interface'] + "\n"
            # yaml_text += "      inputMetric: " + str(bgp_neigh[list(bgp_neigh)[i]]['in_med']) + "\n" #???
            # yaml_text += "      keepAlive: " + str(bgp_neigh[list(bgp_neigh)[i]]['ka']) + "\n"
            # yaml_text += "      holdTime: " + str(bgp_neigh[list(bgp_neigh)[i]]['hold']) + "\n"
            #yaml_text += "      password:
            #yaml_text +=      localConfigured: true
            # yaml_text +=      learnViaSubnetSharing: true
            # yaml_text +=      learnFromBgpBranch: true
            # yaml_text +=      learnFromBgpBranchTransit: true
            # yaml_text +=      learnFromBgpPeRouter: true
            # yaml_text +=      remoteBgp: true
            # yaml_text +=      remoteBgpBranchTransit: true
            # yaml_text +=      learnFromLocalOspf: true
            # yaml_text +=      learnFromRemoteOspf: true

#*********
yaml_text += preconf.templates(orch, nepk)
yaml_text += preconf.bio(orch, nepk)
yaml_text += preconf.inbound_port_forwarding(orch, nepk)

if(post):
    orch.post_preconfig( hostname, yaml_text)
else: 
    print(yaml_text)
orch.logout()
