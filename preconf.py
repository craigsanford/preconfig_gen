

# Helper file for preconfig generator

def extra_info(orch, nepk, hostname):
    yaml_text = "" 
#    info = orch.get("/appliance/extraInfo/" + nepk).json()
    info = orch.get("/appliance/extraInfo/" + nepk + "?source=context_menu_id").json()  
    yaml_text += "applianceInfo: \n"
    yaml_text += "  hostname: " + hostname + "\n"
    yaml_text += "  location:\n"
    yaml_text += "    address: " + info['location']['address'] + "\n"
    yaml_text += "    address2: " + info['location']['address2'] + "\n"
    yaml_text += "    city: " + info['location']['city'] + "\n"
    yaml_text += "    state: " + info['location']['state'] + "\n"
    yaml_text += "    zipCode: " + info['location']['zipCode'] + "\n"
    yaml_text += "    country: " + info['location']['country'] + "\n"
    yaml_text += "  contact:\n"
    yaml_text += "    name: " + info['contact']['name'] + "\n"
    yaml_text += "    email: " + info['contact']['email'] + "\n"
    yaml_text += "    phoneNumber: " + info['contact']['phoneNumber'] + "\n"
    return yaml_text

def deployment(orch, nepk, labels, zones):
    yaml_text = ""
    dhcp_yaml_text = ""
    dhcpInfo = False
    dep = orch.get("/appliance/rest/" + nepk + "/deployment").json()
    firewallMode = ["all", "harden", "stateful", "statefulsnat"]
    yaml_text += "\ndeploymentInfo: \n"
    yaml_text += "  deploymentMode: inline-router \n"
    yaml_text += "  totalOutboundBandwidth: " + str(dep['sysConfig']['maxBW']) + "\n"
    yaml_text += "  totalInboundBandwidth: " + str(dep['sysConfig']['maxInBW']) + "\n"
    yaml_text += "  shapeInboundTraffic: "
    if(dep['sysConfig']['maxInBWEnabled']):
            yaml_text += "true \n"
    else:
            yaml_text += "false \n"

    yaml_text += "\n  deploymentInterfaces: \n"
    for ifs in range(len(dep['modeIfs'])):
        for ips in range(len(dep['modeIfs'][ifs]['applianceIPs'])):
            
            ### Add an interface, check if it is tagged
            yaml_text += "\n    - interfaceName: " + dep['modeIfs'][ifs]['ifName']
            intName = dep['modeIfs'][ifs]['ifName']
            if("vlan" in dep['modeIfs'][ifs]['applianceIPs'][ips].keys()):
                yaml_text += "." + str(dep['modeIfs'][ifs]['applianceIPs'][ips]['vlan']) + " \n"
                intName += "." + str(dep['modeIfs'][ifs]['applianceIPs'][ips]['vlan'])
            else:
                yaml_text += " \n"
            
            yaml_text += "      interfaceComment: " + dep['modeIfs'][ifs]['applianceIPs'][ips]['comment'] + "\n"
            if(dep['modeIfs'][ifs]['applianceIPs'][ips]['zone']):
                yaml_text += "      zone: " + zones[str(dep['modeIfs'][ifs]['applianceIPs'][ips]['zone'])]['name'] + "\n"
            
            ### Check for dhcp address, else set IP address/mask/nh
            if(dep['modeIfs'][ifs]['applianceIPs'][ips]['dhcp']):
                yaml_text += "      ipAddressMask: \n"
            else:
                yaml_text += "      ipAddressMask: " + dep['modeIfs'][ifs]['applianceIPs'][ips]['ip'] + "/" + str(dep['modeIfs'][ifs]['applianceIPs'][ips]['mask']) + "\n"
                if(dep['modeIfs'][ifs]['applianceIPs'][ips]['wanNexthop'] != "0.0.0.0"):
                    yaml_text += "      nextHop: " + dep['modeIfs'][ifs]['applianceIPs'][ips]['wanNexthop'] + "\n"
            
    
            ### Check if this is wan/lan, add info accordingly
            if(dep['modeIfs'][ifs]['applianceIPs'][ips]['lanSide']):
                yaml_text += "      interfaceType: lan \n"
                if(dep['modeIfs'][ifs]['applianceIPs'][ips]['label']):
                    yaml_text += "      interfaceLabel:  " + labels['lan'][dep['modeIfs'][ifs]['applianceIPs'][ips]['label']]['name'] + "\n"

                #If lan side, check DHCP settings - this may add too many "dhcpInfo:" lines
                if(("dhcpd" in dep['modeIfs'][ifs]['applianceIPs'][ips].keys()) and (dep['modeIfs'][ifs]['applianceIPs'][ips]['dhcpd']['type'] == "server")):
                #if(dep['modeIfs'][ifs]['applianceIPs'][ips]['dhcpd']['type'] == "server"):
                    if(not dhcpInfo):
                        dhcp_yaml_text += "  dhcpInfo: \n"
                        dhcpInfo = True
                    dhcp_yaml_text += "    - dhcpInterfaceName: " + intName + "\n"
                    dhcp_yaml_text += "      dhcpType: server \n"
                    dhcp_yaml_text += "      dhcpAddressMask: " + dep['modeIfs'][ifs]['applianceIPs'][ips]['dhcpd']['server']['prefix'] + "\n"
                    dhcp_yaml_text += "      startIpAddress: " + dep['modeIfs'][ifs]['applianceIPs'][ips]['dhcpd']['server']['ipStart'] + "\n"
                    dhcp_yaml_text += "      endIpAddress: " + dep['modeIfs'][ifs]['applianceIPs'][ips]['dhcpd']['server']['ipEnd'] + "\n"
                    try:
                        dhcp_yaml_text += "      gatewayIpAddress: " + dep['modeIfs'][ifs]['applianceIPs'][ips]['dhcpd']['server']['gw'][0] + "\n"
                    except IndexError:
                        print("There is no gateway for this DHCP Scope.")
                    if(len(dep['modeIfs'][ifs]['applianceIPs'][ips]['dhcpd']['server']['dns'])):
                        dhcp_yaml_text += "      dnsServers: \n"
                        for i in range(len(dep['modeIfs'][ifs]['applianceIPs'][ips]['dhcpd']['server']['dns'])):
                            dhcp_yaml_text += "        - " + dep['modeIfs'][ifs]['applianceIPs'][ips]['dhcpd']['server']['dns'][i] + "\n"
                    if(len(dep['modeIfs'][ifs]['applianceIPs'][ips]['dhcpd']['server']['ntpd'])):
                        dhcp_yaml_text += "      ntpServers: \n"
                        for i in range(len(dep['modeIfs'][ifs]['applianceIPs'][ips]['dhcpd']['server']['ntpd'])):
                            dhcp_yaml_text += "        - " + dep['modeIfs'][ifs]['applianceIPs'][ips]['dhcpd']['server']['ntpd'][i] + "\n"
                    # dhcp_yaml_text += "      netbiosNameServers: \n"
                    # for(i in range(len(dep['modeIfs'][ifs]['applianceIPs'][ips]['dhcpd']['ntpd']):
                    # dhcp_yaml_text += "        - 192.168.0.0
                    # dhcp_yaml_text += "      netbiosNodeType: B
                    # dhcp_yaml_text += "      maximumLease: 24
                    # dhcp_yaml_text += "      defaultLease: 24
                    # dhcp_yaml_text += "      options:
                    # dhcp_yaml_text += "        - option: 1
                    # dhcp_yaml_text += "          value: 255.255.255.0
                    # dhcp_yaml_text += "      staticIpAssignments:
                    # dhcp_yaml_text += "        - hostname: google
                    # dhcp_yaml_text += "          macAddress: 00:25:96:FF:FE:12
                    # dhcp_yaml_text += "          ipAddress: 198.168.0.7


                elif(("dhcpd" in dep['modeIfs'][ifs]['applianceIPs'][ips].keys()) and (dep['modeIfs'][ifs]['applianceIPs'][ips]['dhcpd']['type'] == "relay")):
                    if(not dhcpInfo):
                        dhcp_yaml_text += "  dhcpInfo: \n"
                        dhcpInfo = True
                    dhcp_yaml_text += "    - dhcpInterfaceName: " + intName + "\n"
                    dhcp_yaml_text += "      dhcpType: relay \n"
                    dhcp_yaml_text += "      dhcpProxyServers: \n"
                    for i in range(len(dep['modeIfs'][ifs]['applianceIPs'][ips]['dhcpd']['relay']['dhcpserver'])):
                        dhcp_yaml_text += "        - " + dep['modeIfs'][ifs]['applianceIPs'][ips]['dhcpd']['relay']['dhcpserver'][i] + "\n"
                    if(dep['modeIfs'][ifs]['applianceIPs'][ips]['dhcpd']['relay']['option82']):
                        dhcp_yaml_text += "      enableOptions82: " + str(dep['modeIfs'][ifs]['applianceIPs'][ips]['dhcpd']['relay']['option82']) + "\n"
                        dhcp_yaml_text += "      options82Policy: " + dep['modeIfs'][ifs]['applianceIPs'][ips]['dhcpd']['relay']['option82_policy'] + "\n"

            else:
                if(dep['modeIfs'][ifs]['applianceIPs'][ips]['label']):
                    yaml_text += "      interfaceLabel:  " + labels['wan'][dep['modeIfs'][ifs]['applianceIPs'][ips]['label']]['name'] + "\n"
                yaml_text += "      interfaceType: wan \n"
                yaml_text += "      outboundMaxBandwidth: " + str(dep['modeIfs'][ifs]['applianceIPs'][ips]['maxBW']['outbound']) + "\n"
                yaml_text += "      inboundMaxBandwidth: " + str(dep['modeIfs'][ifs]['applianceIPs'][ips]['maxBW']['outbound']) + "\n"
                yaml_text += "      firewallMode: " + firewallMode[dep['modeIfs'][ifs]['applianceIPs'][ips]['harden']] + "\n"
                yaml_text += "      behindNat: " + dep['modeIfs'][ifs]['applianceIPs'][ips]['behindNAT'] + "\n"


    return yaml_text, dhcp_yaml_text

def routes(orch, nepk):
    yaml_text = "" 
    sys = orch.get("/appliance/rest/" + nepk + "/system").json()
    yaml_text += "\nlocalRoutes: \n" 
    yaml_text += "  useSharedSubnetInfo: " + str(sys['auto_subnet']['self']).lower() + "\n"
    yaml_text += "  advertiseLocalLanSubnets: " + str(sys['auto_subnet']['add_local_lan']).lower() + "\n"
    yaml_text += "  advertiseLocalWanSubnets: " + str(sys['auto_subnet']['add_local_wan']).lower() + "\n"
    yaml_text += "  localMetric: " + str(sys['auto_subnet']['add_local_metric']) + "\n"
    yaml_text += "  localCommunities: \n"

    try:
        sub3 = orch.get("/appliance/rest/" + nepk + "/subnets3/configured").json()
        if("prefix" in sub3.keys()):
            yaml_text += "\n  routes: \n"
            for i in sub3['prefix']:
                #Is there a better way to do the nhop manipulation? probably
                nhop = str(list(sub3['prefix'][i]['nhop']))[2:-2]
                int = str(list(sub3['prefix'][i]['nhop'][nhop]['interface']))[2:-2]
            
                yaml_text += "    - routeIpSubnet: " + i + "\n"
                yaml_text += "      nextHop: " + nhop + "\n"
        #        yaml_text += "      interfaceName: " + int + "\n"
                yaml_text += "      metric: " + str(sub3['prefix'][i]['nhop'][nhop]['interface'][int]['metric']) + "\n"
                yaml_text += "      advertise: " + str(sub3['prefix'][i]['advert']).lower() + "\n"
                yaml_text += "      advertiseToBgp: " + str(sub3['prefix'][i]['advert_bgp']).lower() + "\n"
                yaml_text += "      advertiseToOspf: " + str(sub3['prefix'][i]['advert_ospf']).lower() + "\n"
                yaml_text += "      tag: " + str(sub3['prefix'][i]['nhop'][nhop]['interface'][int]['dir']) + "\n"
                yaml_text += "      comment: " + str(sub3['prefix'][i]['nhop'][nhop]['interface'][int]['comment']) + "\n"
    except:
        print("Uhoh")

    return yaml_text

def loopback(orch, nepk, labels, zones):
    yaml_text = ""
    loopback = orch.get("/appliance/rest/" + nepk + "/virtualif/loopback").json()
    user_def_loopback = False
    loop_text = ""
    if(loopback):
        for int in loopback:
            if(not loopback[int]['gms_marked']):
                user_def_loopback = True
                loop_text += "    - interfaceId: " + int + "\n"
                loop_text += "      adminStatus: "
                if(loopback[int]['admin']):
                    loop_text += "Up\n"
                else:
                    loop_text += "Down\n"
                loop_text += "      ipAddressMask: " + loopback[int]['ipaddr'] + "/" + str(loopback[int]['nmask']) + "\n"
                if(loopback[int]['zone']):
                    loop_text += "      zone: " + zones[str(loopback[int]['zone'])]['name'] + "\n"
                loop_int = loopback[int]['label']
                if(loop_int):
                    loop_text += "      interfaceLabel: " + labels['lan'][loop_int]['name'] + "\n\n"

    if(user_def_loopback):
        yaml_text += "\nloopbackInterface:\n"
        yaml_text += "  loopbacks:\n"
        yaml_text += loop_text

    return yaml_text


def bgp(orch, nepk):
    yaml_text = ""
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


    return yaml_text


def templates(orch, nepk):
    yaml_text = ""
    templates = orch.get("/template/applianceAssociation/" + nepk).json()
    yaml_text += "\ntemplateGroups: \n"
    yaml_text += "  groups: \n"
    for i in range(len(templates['templateIds'])):
        yaml_text += "    - " + templates['templateIds'][i] + "\n"

    return yaml_text

def bio(orch, nepk):
    yaml_text = ""
    bio = orch.get("/gms/overlays/association").json()
    bio_config = orch.get("/gms/overlays/config").json()
    bio_dict = {}
    for i in range(len(bio_config)):
        bio_dict[str(bio_config[i]['id'])] = bio_config[i]['name']

    yaml_text += "\nbusinessIntentOverlays:\n"
    yaml_text += "  overlays:\n"
    for i in bio:
            if nepk in bio[i]:
                yaml_text += "    - " + bio_dict[i] + "\n"
    return yaml_text

def inbound_port_forwarding(orch, nepk):
    yaml_text = ""
    ipf = orch.get("/portForwarding/" + nepk).json()
    if(ipf):
        yaml_text += "\ninboundPortForwarding:\n"
        yaml_text += "  portForwardingRules:\n"

        for i in ipf:
            if(not i['gms_marked']):
                yaml_text += "    - sourceIpSubnet: " + i['srcSubnet'] + "\n"
                yaml_text += "      destinationIpSubnet: " + i['destSubnet'] + "\n"
                yaml_text += "      translate: true\n" #always true? Unsure of the different use cases
                yaml_text += "      destinationPortRange: " + i['destPort'] + "\n"
                yaml_text += "      destinationProtocol: " + i['protocol'] + "\n"
                yaml_text += "      translateIp: " + i['targetIp'] + "\n"
                yaml_text += "      translatePortRange: " + i['targetPort'] + "\n"
                yaml_text += "      comment: " + i['comment'] + "\n"


    return yaml_text







