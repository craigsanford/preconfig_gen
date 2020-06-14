# Receive hostname, return nepk

def standard(orch, hostname):
	app = orch.get("/appliance").json()
	for i in app:
		if (i['hostName']== hostname):
			return i['nePk']
    
