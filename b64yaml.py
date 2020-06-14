# This is to convert a yaml file to a base64 formatted string, and back

import base64

def yaml_to_b64string(yaml):
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
	
