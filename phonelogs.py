#######################################
# Collect Phone Logs from a phone
# 
#Requires:
#pip install urllib3.request
#pip install wget
#
# Version 1.0
#######################################

#Backwards compatibility
from __future__ import print_function, unicode_literals, division

import os, re, urllib3.request, wget, subprocess

#Collect the Phone's IP Address
print("\n")
print("="*56)
print("Enter the IP Address for the phone")
print("="*56)
strIP = input("IP: ")
print("\n")

#Validate User Input is IP Address
#Validated Dotted Decimal notation
strRegEx = '\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}'
matIP = re.search(strRegEx, strIP)

#If Dotted Decimal checks out Validate the Octets are correct
if matIP:
     strIP = matIP.group()
     strTestIP = strIP.split(".")
     i = 0
     #Loop through the Octets
     for ip in strTestIP:
          intOctet = int(ip)
          #If i = 0 We're looking at the first Octet
          if i == 0:
               #If we are not Class A, B or C Terminate
               if (intOctet == 0) or (intOctet > 223):
                    print("Invalid IP - Terminating")
                    exit()
          #If we have more than 4 octets the IP was wrong
          elif i > 3:
               print("Invalid IP - Terminating")
               exit()
          #The remaining Octets can be between 0 and 255
          else:
               if intOctet > 255:
                    print("Invalid IP - Terminating")
                    exit()
          i = i + 1

else:
     print("Invalid IP")
     exit()


##Test connection to phone
print("="*56)
print("Testing Connectivity to the Phone")
print("="*56)
if os.name == 'nt':
     #strPingTest = os.system("ping -n 1 " + strIP + " | find \"TTL=\"")
     procPingTest = subprocess.Popen(["ping", "-n", "1", strIP])
     procPingTest.wait()
     if not procPingTest.poll() == 0:
          print("\n")
          print("*"*56)
          print("Ping Test to Phone failed.\n\nPlease Test Connectivity or IP and try again")
          print("*"*56)
          exit()
else:
     intPingTest = os.system("ping -c 1 " + strIP)
     if not intPingTest == 0:
          print("\n")
          print("*"*56)
          print("Ping Test to Phone failed.\n\nPlease Test Connectivity or IP and try again")
          print("*"*56)
          exit()


#Collect current path
strLclPath = os.getcwd()
if os.name == 'nt':
     strDownLoadDir = strLclPath + "\\" + strIP
else:
     strDownLoadDir = strLclPath + "/" + strIP

#Check if path exists
if not os.path.exists(strDownLoadDir):
    os.mkdir(strDownLoadDir)
else:
     strSuffixFail = ""
     for i in range(1, 5):
          if i == 4:
               print("\n")
               print("*"*56)
               print("Too many failed attempts.\n")
               print("Please check paths and try script again.")
               print("Terminating Script.")
               exit()
          print("\n")
          print("="*56)
          print("That Path already exists.\n")
          print("Cannot Create:\n" + strDownLoadDir + strSuffixFail + "\n")
          print("Please enter a directory Suffix to append")
          print("="*56)
          strSuffix = input("Suffix: ")
          if not os.path.exists(strDownLoadDir + strSuffix):
               os.mkdir(strDownLoadDir + strSuffix)
               strDownLoadDir = strDownLoadDir + strSuffix
               break
          else:
               strSuffixFail = strSuffix
               strSuffix = ""

print("\n")
print("="*56)
print("Downloaded logfiles will be saved to:\n" + strDownLoadDir)
print("="*56)

#Go out to the Phone and get the HTML
strURL = "http://" + strIP + "/CGI/Java/Serviceability?adapter=device.statistics.consolelog"

#Get the HTML Data from the Phone
try:
     objHttp = urllib3.PoolManager()
     objHttpResponse = objHttp.request('GET', strURL)
     strHtmlData = str(objHttpResponse.data)
except:
     print("\n")
     print("="*56)
     print("Something went wrong, we cannot connect to the phone.\n")
     print("Check to make sure that the WebUI on the phone is enabled.\n")
     print("Terminating script")
     print("="*56)
     exit()

#Split the HTML on the href Tag so we have this as the start
#of the line.  href will be removedfrom the resultant string
strHtmlData = strHtmlData.split('href')

#Loop through the results of the split html and look for strings
#that start with /FS and end in gz, messages, messages.<num or log
print("\n")
print("="*56)
print("Collecting Files from phone.\n")
print("="*56)
print("\n")
for enum in enumerate(strHtmlData):
     strLine = str(enum)
     strRegEx = '(\/FS.*gz"|\/FS.*messages"|\/FS.*messages\.\d"|\/FS.*log")'
     matPhonePath = re.search(strRegEx, strLine)
     #If we find the string we're looking for, download the file
     if matPhonePath:
           strPhonePath = matPhonePath.group()
           print("Collecting File: " + strPhonePath[:-1])
           url = "http://" + strIP + strPhonePath[:-1]
           wget.download(url, strDownLoadDir)
           print("\n")

exit()

