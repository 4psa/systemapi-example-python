"""
4PSA VoipNow SystemAPI Client for Python

Copyright (c) 2012, Rack-Soft (www.4psa.com). All rights reserved.
VoipNow is a Trademark of Rack-Soft, Inc
4PSA is a Registered Trademark of Rack-Soft, Inc.
All rights reserved.

This script fetches the call costs of an extension.
"""
import sys
import random
import datetime
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

# We need an extension to check its call costs, so we make a request to
# fetch all the extensions.

# Construct the Body
soapBody = SOAPpy.Types.untypedType("")
soapBody._name = "ns2:GetExtensions" 

# Set namespaces
soapBody._setAttr("xmlns:ns2", "http://4psa.com/ExtensionMessages.xsd/3.0.0")

# Set endpoint
endpoint = "https://voipnow2demo.4psa.com/soap2/extension_agent.php"

# Set soapaction
soapaction = "http://4psa.com/User/3.0.0:getExtensionsIn"

# Set service connection
server = SOAPProxy(endpoint, noroot = 1, soapaction = soapaction, header = soapHeader)

#run our soap request
try:
	extensions = server._callWithBody(soapBody)
except SOAPpy.Types.faultType, error:
	# Catch exception, for situations when the extensions could not be fetched
	print "Error " + error[0] + ": " + error[1]
	sys.exit(1)

# Get the identifier of a random extension
extensionIdentifier = None
if len(extensions) != 0:
	randExtension = extensions[random.randint(0, len(extensions) - 1)]
	if hasattr(randExtension, 'identifier'):
		extensionIdentifier = randExtension.identifier
		if hasattr(randExtension, 'name'):
			print "Fetching call costs for extension " + randExtension.name + "."
		else:
			print "Fetching call costs for extension with identifier " + extensionIdentifier + "."

if extensionIdentifier == None:
	print "No extensions found on the server. Can not make the call costs request."
	sys.exit(1)

# Construct the Body
body = SOAPpy.Types.structType()

#XML template for sending the new request data
bodyTemplate = """
      <userIdentifier>%s</userIdentifier>
	  <interval>
			<startDate>%s</startDate>
			<endDate>%s</endDate>
	  </interval>"""

# The current date, used for the request data
now = datetime.datetime.now()
	  
# Request data
userIdentifier = extensionIdentifier
startDate = "2012-01-01"
endDate = now.strftime("%Y-%m-%d")

# Filling in the template above with the request data
body = bodyTemplate % (userIdentifier, startDate, endDate)
soapBody = SOAPpy.Types.untypedType(body)
soapBody._name = "ns2:CallCosts" 

# Set namespaces
soapBody._setAttr("xmlns:ns2", "http://4psa.com/ReportMessages.xsd/3.0.0")

# Set endpoint
endpoint = "https://voipnow2demo.4psa.com/soap2/report_agent.php"

# Set soapaction
soapaction = "http://4psa.com/Report/3.0.0:CallCostsIn"

# Set service connection
server = SOAPProxy(endpoint, noroot = 1, soapaction = soapaction, header = soapHeader)

#run our soap request
try:
	callCosts = server._callWithBody(soapBody)
	# Display the result
	print callCosts.totalCalls + " calls have been made between " + startDate + " and " + endDate + " with a total cost of " + callCosts.cost + " " + callCosts.currency
except SOAPpy.Types.faultType, error:
	# Catch exception, for situations when the call costs could not be fetched
	print "Error " + error[0] + ": " + error[1]
	sys.exit(1)