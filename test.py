

URL = 'https://sandboxapicdc.cisco.com'
LOGIN = 'admin'
PASSWORD = 'ciscopsdt'

import cobra.mit.session
import cobra.mit.access
import cobra.mit.request
import requests
requests.packages.urllib3.disable_warnings()

auth = cobra.mit.session.LoginSession(URL, LOGIN, PASSWORD)
session = cobra.mit.access.MoDirectory(auth)
session.login()

tenant_query = cobra.mit.request.DnQuery("uni/tn-Heroes")
heroes_tenant = session.query(tenant_query)
heroes = heroes_tenant[0]
print(dir(heroes))