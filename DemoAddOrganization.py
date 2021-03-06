"""
4PSA VoipNow SystemAPI Client for Python

Copyright (c) 2012, Rack-Soft (www.4psa.com). All rights reserved.
VoipNow is a Trademark of Rack-Soft, Inc
4PSA is a Registered Trademark of Rack-Soft, Inc.
All rights reserved.

This script adds an organization.
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

# We need a parent service provider for the new organization, so we make a request to
# fetch all the service providers.

# Construct the Body
soapBody = SOAPpy.Types.untypedType("")
soapBody._name = "ns2:GetServiceProviders" 

# Set namespaces
soapBody._setAttr("xmlns:ns2", "http://4psa.com/ServiceProviderMessages.xsd/" + version)

# Set endpoint
endpoint = "https://" + str(sys.argv[1]) + "/soap2/sp_agent.php"

# Set soapaction
soapaction = "http://4psa.com/ServiceProvider/" + version + ":getServiceProvidersIn"

# Set service connection
server = SOAPProxy(endpoint, noroot = 1, soapaction = soapaction, header = soapHeader)

#run our soap request
try:
	serviceProviders = server._callWithBody(soapBody)
except SOAPpy.Types.faultType, error:
	# Catch exception, for situations when the service providers could not be fetched
	print "Error " + error[0] + ": " + error[1]
	sys.exit(1)

# Get the id of a random service provider
serviceProviderID = None
if len(serviceProviders) != 0:
	randServiceProvider = serviceProviders[random.randint(0, len(serviceProviders) - 1)]
	if hasattr(randServiceProvider, 'ID'):
		serviceProviderID = randServiceProvider.ID
		if hasattr(randServiceProvider, 'name'):
			print "Using parent service provider " + randServiceProvider.name + "."
		else:
			print "Using parent service provider with id " + serviceProviderID + "."

if serviceProviderID == None:
	print "No service providers found on the server. Can not add an organization."
	sys.exit(1)
		
# We need a charging plan for the new account, so we make a request to
# fetch all the charging plans of the parent service provider and then 
# pick a random one from the response list.

# Construct the Body
body = SOAPpy.Types.structType()

#XML template for sending the charging plans data
bodyTemplate = """
	  <ns3:userID>%s</ns3:userID>"""

# Request data
userID = serviceProviderID

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
soapaction = "http://4psa.com/Billing/" + version + ":getChargingPlansIn"

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

#XML template for sending the new organization data
bodyTemplate = """
      <ns3:name>%s</ns3:name>
      <ns3:login>%s</ns3:login>
      <ns3:firstName>%s</ns3:firstName>
      <ns3:lastName>%s</ns3:lastName>
      <ns3:email>%s</ns3:email>
      <ns3:password>%s</ns3:password>
      <ns3:country>%s</ns3:country>
      <ns3:parentID>%s</ns3:parentID>
      <ns3:company>%s</ns3:company>"""

if chargingPlanID != None:
	bodyTemplate += """
		  <ns3:chargingPlanID>%s</ns3:chargingPlanID>"""

# Organization data
name = "OrgPython" + str(random.randint(1, 1000))
login = "OrgPython" + str(random.randint(1, 1000))
firstname = "FirstnamePython" + str(random.randint(1, 1000))
lastname = "LastnamePython" + str(random.randint(1, 1000))
email = "Email" + str(random.randint(1, 1000)) + "@example.com"
password = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(10))
country = "us"
parentID = serviceProviderID
company = "test_company"

# Filling in the template above with the organization data
if chargingPlanID != None:
	body = bodyTemplate % (name, login, firstname, lastname, email, password, country, parentID, company, chargingPlanID)
else:
	body = bodyTemplate % (name, login, firstname, lastname, email, password, country, parentID, company)
soapBody = SOAPpy.Types.untypedType(body)
soapBody._name = "ns2:AddOrganization" 

# Set namespaces
soapBody._setAttr("xmlns:ns2", "http://4psa.com/OrganizationMessages.xsd/" + version)
soapBody._setAttr("xmlns:ns3", "http://4psa.com/OrganizationData.xsd/" + version)

# Set endpoint
endpoint = "https://" + str(sys.argv[1]) + "/soap2/organization_agent.php"

# Set soapaction
soapaction = "http://4psa.com/Organization/" + version + ":addOrganizationIn"

# Set service connection
server = SOAPProxy(endpoint, noroot = 1, soapaction = soapaction, header = soapHeader)

#run our soap request
try:
	server._callWithBody(soapBody)
	print "Organization created successfully."
except SOAPpy.Types.faultType, error:
	# Catch exception, for situations when the organization could not be added
	print "Error " + error[0] + ": " + error[1]
