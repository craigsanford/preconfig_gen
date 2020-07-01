

# Helper file for preconfig generator

def extra_info(orch, nepk, hostname):
    yaml_text = "" 
    info = orch.get("/appliance/extraInfo/" + nepk).json()
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

