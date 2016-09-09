"""
4PSA VoipNow SystemAPI Client for Python

Copyright (c) 2012, Rack-Soft (www.4psa.com). All rights reserved.
VoipNow is a Trademark of Rack-Soft, Inc
4PSA is a Registered Trademark of Rack-Soft, Inc.
All rights reserved.

This script adds a user.
"""
import sys
import string
import random
import SOAPpy
from SOAPpy import SOAPProxy

# To view soap request/response set SOAPpy.Config.debug = 1
SOAPpy.Config.debug = 0 
version = "3.5.0"

if len(sys.argv) < 3:
    print "Usage: python <executable_name> <serverIP> \"<accessToken>\""
    print "example: python DemoAddServiceProvider.py 192.168.0.2 \"1|V_pmPvEm25-HrqAzERx_nvJbBvNs~q3F|1|v-gntT4GFH-UCUX0EM2_r9XTVDrw~qCF\""
    sys.exit(1)

# Authentication data
ACCESS_TOKEN = sys.argv[2]

# Start constructing the Header
soapHeader = SOAPpy.Types.headerType()

#XML template for sending the authentication data
authenticationTemplate = """ <ns1:accessToken>%s</ns1:accessToken>"""
  				
# filling in the template above with our authentication data				
credentials = authenticationTemplate % (ACCESS_TOKEN)

soapHeader.userCredentials = SOAPpy.Types.headerType(credentials)

# the namespace for the user credentials
soapHeader.userCredentials._ns = "http://4psa.com/HeaderData.xsd/" + version

soapHeader.userCredentials.userCredentials = SOAPpy.Types.untypedType(credentials)

# We need a parent organization for the new user, so we make a request to
# fetch all the organizations.

# Construct the Body
soapBody = SOAPpy.Types.untypedType("")
soapBody._name = "ns2:GetOrganizations" 

# Set namespaces
soapBody._setAttr("xmlns:ns2", "http://4psa.com/OrganizationMessages.xsd/" + version)

# Set endpoint
endpoint = "https://" + str(sys.argv[1]) + "/soap2/organization_agent.php"

# Set soapaction
soapaction = "http://4psa.com/Organization/" + version +":getOrganizationsIn"

# Set service connection
server = SOAPProxy(endpoint, noroot = 1, soapaction = soapaction, header = soapHeader)

#run our soap request
try:
	organizations = server._callWithBody(soapBody)
except SOAPpy.Types.faultType, error:
	# Catch exception, for situations when the organizations could not be fetched
	print "Error " + error[0] + ": " + error[1]
	sys.exit(1)

# Get the id of a random organization
organizationID = None
if len(organizations) != 0:
	randOrganization = organizations[random.randint(0, len(organizations) - 1)]
	if hasattr(randOrganization, 'ID'):
		organizationID = randOrganization.ID
		if hasattr(randOrganization, 'name'):
			print "Using parent organization " + randOrganization.name + "."
		else:
			print "Using parent organization with id " + organizationID + "."

if organizationID == None:
	print "No organizations found on the server. Can not add an user."
	sys.exit(1)
		
# We need a charging plan for the new account, so we make a request to
# fetch all the charging plans of the parent organization and then 
# pick a random one from the response list.

# Construct the Body
body = SOAPpy.Types.structType()

#XML template for sending the charging plans data
bodyTemplate = """
	  <ns3:userID>%s</ns3:userID>"""

# Request data
userID = organizationID

# Filling in the template above with the request data
body = bodyTemplate % (userID)
soapBody = SOAPpy.Types.untypedType(body)
soapBody._name = "ns2:GetChargingPlans" 

# Set namespaces
soapBody._setAttr("xmlns:ns2", "http://4psa.com/BillingMessages.xsd/" + version)
soapBody._setAttr("xmlns:ns3", "http://4psa.com/Common.xsd/" + version)

# Set endpoint
endpoint = "https://" + str(sys.argv[1]) + "/soap2/billing_agent.php"

# Set soapaction
soapaction = "http://4psa.com/Billing/" + version +":getChargingPlansIn"

# Set service connection
server = SOAPProxy(endpoint, noroot = 1, soapaction = soapaction, header = soapHeader)

#run our soap request
try:
	chargingPlans = server._callWithBody(soapBody)
except SOAPpy.Types.faultType, error:
	# Catch exception, for situations when the charging plans could not be fetched
	print "Error " + error[0] + ": " + error[1]
	sys.exit(1)

# Get the id of a random charging plan
chargingPlanID = None
if len(chargingPlans) != 0:
	randChargingPlan = chargingPlans[random.randint(0, len(chargingPlans) - 1)]
	if hasattr(randChargingPlan, 'ID'):
		chargingPlanID = randChargingPlan.ID
		if hasattr(randChargingPlan, 'name'):
			print "Using charging plan " + randChargingPlan.name + "."
		else:
			print "Using charging plan with id " + chargingPlanID + "."

# Construct the Body
body = SOAPpy.Types.structType()

#XML template for sending the new user data
bodyTemplate = """
      <ns3:name>%s</ns3:name>
      <ns3:login>%s</ns3:login>
      <ns3:firstName>%s</ns3:firstName>
      <ns3:lastName>%s</ns3:lastName>
      <ns3:email>%s</ns3:email>
      <ns3:password>%s</ns3:password>
      <ns3:country>%s</ns3:country>
	  <ns3:parentID>%s</ns3:parentID>"""

# User data
name = "UserPython" + str(random.randint(1, 1000))
login = "UserPython" + str(random.randint(1, 1000))
firstname = "FirstnamePython" + str(random.randint(1, 1000))
lastname = "LastnamePython" + str(random.randint(1, 1000))
email = "Email" + str(random.randint(1, 1000)) + "@example.com"
password = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(10))
country = "us"
parentID = organizationID

# Filling in the template above with the user data
if chargingPlanID != None:
	body = bodyTemplate % (name, login, firstname, lastname, email, password, country, parentID, chargingPlanID)
else:
	body = bodyTemplate % (name, login, firstname, lastname, email, password, country, parentID)
soapBody = SOAPpy.Types.untypedType(body)
soapBody._name = "ns2:AddUser" 

# Set namespaces
soapBody._setAttr("xmlns:ns2", "http://4psa.com/UserMessages.xsd/" + version)
soapBody._setAttr("xmlns:ns3", "http://4psa.com/OrganizationData.xsd/" + version)

# Set endpoint
endpoint = "https://" + str(sys.argv[1]) + "/soap2/user_agent.php"

# Set soapaction
soapaction = "http://4psa.com/User/" + version + ":addUserIn"

# Set service connection
server = SOAPProxy(endpoint, noroot = 1, soapaction = soapaction, header = soapHeader)

#run our soap request
try:
	server._callWithBody(soapBody)
	print "User created successfully."
except SOAPpy.Types.faultType, error:
	# Catch exception, for situations when the user could not be added
	print "Error " + error[0] + ": " + error[1]
