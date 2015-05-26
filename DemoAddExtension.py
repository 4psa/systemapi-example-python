"""
4PSA VoipNow SystemAPI Client for Python

Copyright (c) 2012, Rack-Soft (www.4psa.com). All rights reserved.
VoipNow is a Trademark of Rack-Soft, Inc
4PSA is a Registered Trademark of Rack-Soft, Inc.
All rights reserved.

This script adds an extension.
"""
import sys
import string
import random
import SOAPpy
from SOAPpy import SOAPProxy

# To view soap request/response set SOAPpy.Config.debug = 1
SOAPpy.Config.debug = 0

# Authentication data
ACCESS_TOKEN = "CHANGEME"

# Start constructing the Header
soapHeader = SOAPpy.Types.headerType()

#XML template for sending the authentication data
authenticationTemplate = """ <ns1:accessToken>%s</ns1:accessToken>"""
  				
# filling in the template above with our authentication data				
credentials = authenticationTemplate % (ACCESS_TOKEN)

soapHeader.userCredentials = SOAPpy.Types.headerType(credentials)

# the namespace for the user credentials
soapHeader.userCredentials._ns = "http://4psa.com/HeaderData.xsd/3.0.0"

soapHeader.userCredentials.userCredentials = SOAPpy.Types.untypedType(credentials)

# We need a parent user for the new extension, so we make a request to
# fetch all the users.

# Construct the Body
soapBody = SOAPpy.Types.untypedType("")
soapBody._name = "ns2:GetUsers" 

# Set namespaces
soapBody._setAttr("xmlns:ns2", "http://4psa.com/UserMessages.xsd/3.0.0")

# Set endpoint
endpoint = "https://voipnow2demo.4psa.com/soap2/user_agent.php"

# Set soapaction
soapaction = "http://4psa.com/User/3.0.0:getUsersIn"

# Set service connection
server = SOAPProxy(endpoint, noroot = 1, soapaction = soapaction, header = soapHeader)

#run our soap request
try:
	users = server._callWithBody(soapBody)
except SOAPpy.Types.faultType, error:
	# Catch exception, for situations when the users could not be fetched
	print "Error " + error[0] + ": " + error[1]
	sys.exit(1)

# Get the id of a random user
userID = None
if len(users) != 0:
	randUser = users[random.randint(0, len(users) - 1)]
	if hasattr(randUser, 'ID'):
		userID = randUser.ID
		if hasattr(randUser, 'name'):
			print "Using parent user " + randUser.name + "."
		else:
			print "Using parent user with id " + userID + "."

if userID == None:
	print "No users found on the server. Can not add an extension."
	sys.exit(1)

# Construct the Body
body = SOAPpy.Types.structType()

#XML template for sending the new extension data
bodyTemplate = """
      <ns3:label>%s</ns3:label>
      <ns3:password>%s</ns3:password>
	  <ns4:parentID>%s</ns4:parentID>"""

# Extension data
label = "ExtensionPython" + str(random.randint(1, 1000))
password = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(10))
parentID = userID

# Filling in the template above with the extension data
body = bodyTemplate % (label, password, parentID)
soapBody = SOAPpy.Types.untypedType(body)
soapBody._name = "ns2:AddExtension" 

# Set namespaces
soapBody._setAttr("xmlns:ns2", "http://4psa.com/ExtensionMessages.xsd/3.0.0")
soapBody._setAttr("xmlns:ns3", "http://4psa.com/ExtensionData.xsd/3.0.0")
soapBody._setAttr("xmlns:ns4", "http://4psa.com/AccountData.xsd/3.0.0")

# Set endpoint
endpoint = "https://voipnow2demo.4psa.com/soap2/extension_agent.php"

# Set soapaction
soapaction = "http://4psa.com/Extension/3.0.0:addExtensionIn"

# Set service connection
server = SOAPProxy(endpoint, noroot = 1, soapaction = soapaction, header = soapHeader)

#run our soap request
try:
	server._callWithBody(soapBody)
	print "Extension created successfully."
except SOAPpy.Types.faultType, error:
	# Catch exception, for situations when the extension could not be added
	print "Error " + error[0] + ": " + error[1]