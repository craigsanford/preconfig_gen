import b64yaml


def post(orch, hostname, yaml_text):
	# convert from a string to base64,
	# then post that b64 output as a string to Orch
	yaml_upload = b64yaml.yaml_to_b64string(yaml_text)
	data = {}
	data['name'] = hostname 
	data['configData'] = yaml_upload
	data['autoApply'] = True
	data['tag'] = hostname
	r = orch.post("/gms/appliance/preconfiguration/validate", data)
	if(r.status_code == 200):
		orch.post("/gms/appliance/preconfiguration/", data)
		#print("Success")
	else:
		print("Problem with upload")
		print(r.text)