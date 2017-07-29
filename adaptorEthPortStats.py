"""
Author: kriswans@cisco.com

Program Description:
1. Authenticates and grabs cookie
2. Pulls list of servers in UCSM domain
3. Polls all adaptorEthPortStats over specified interval and writes to a csv file
"""

import requests
from xml.etree import ElementTree
import pprint
import sys
import getpass
import time

def adaptorEthPortStats(ucsm_ip,runs,interv,user,passw):

    if ucsm_ip == None:
        ucsm_ip=input("Enter the IP or Name of the UCSM that you will connect to: ")
    if runs == None:
        runs=int(input("\nEnter the number of polling iterations: "))
    if interv == None:
        interv=int(input("\nEnter the polling interval: "))
    if user == None:
        user=input("\nEnter the username to connect to UCSM: ")
    if passw == None:
        passw=getpass.getpass(prompt='\nEnter UCSM Password: ')


    url = "http://{ucsm_ip}/nuova".format(ucsm_ip=ucsm_ip)

    payload = "<aaaLogin inName=\"{user}\" inPassword=\"{passw}\" />".format(user=user,passw=passw)
    headers = {
        'content-type': "text/xml",
        'cache-control': "no-cache",
        'postman-token': "a1a32551-e587-c4e0-cf3b-24eb78f6b713"
        }

    response = requests.request("POST", url, data=payload, headers=headers)

    root = ElementTree.fromstring(response.content)


    for child in root.iter('aaaLogin'):
        aaaLogin=child.attrib

    outCookie=aaaLogin['outCookie']

    payload = "<configFindDnsByClassId \r\n    classId=\"computeItem\" \r\n    cookie=\"{outCookie}\" />".format(outCookie=outCookie)
    headers = {
        'content-type': "text/xml",
        'cache-control': "no-cache",
        'postman-token': "79a0aa4a-8af7-fff2-5225-c5f85320cf5b"
        }

    response2 = requests.request("POST", url, data=payload, headers=headers)

    root2 = ElementTree.fromstring(response2.content)

    compute_list=[]
    for child in root2.iter('dn'):
         compute_list.append(child.attrib['value'])

    statsfile=open('adaptorEthPortStats.csv','w')
    i=0
    while i < runs :
        print("\nRunning {i} of {runs} runs.".format(i=str(i+1),runs=str(runs)))
        for svr in compute_list:

            payload = "<configScope \r\n    cookie=\"{outCookie}\" \r\n    inHierarchical=\"true\" \r\n    dn=\"{svr}\"\r\n    inClass=\"adaptorEthPortStats\" />".format(outCookie=outCookie,svr=svr)
            headers = {
                'content-type': "text/xml",
                'cache-control': "no-cache",
                'postman-token': "c280bf42-4d04-42b5-f2ab-ba2ca95683ac"
                }

            response3 = requests.request("POST", url, data=payload, headers=headers)

            root3 = ElementTree.fromstring(response3.content)

            for child in root3.iter('adaptorEthPortStats'):
                stat=(child.attrib)
                server=(child.attrib['dn'])
                statsfile.write(str(server))
                statsfile.write(" :\n\n")
                del stat['dn']
                statsfile.close()

                f=open('adaptorEthPortStats.csv','a')
                orig_stdout = sys.stdout
                sys.stdout = f
                pprint.pprint(stat)
                sys.stdout = orig_stdout
                f.close()
                statsfile=open('adaptorEthPortStats.csv','a')
                statsfile.write(2*'\n'+50*'#'+2*'\n')
        i+=1
        print("\nWaiting {interv} seconds.".format(interv=str(interv)))
        time.sleep(interv)


    statsfile.close()
    print("\nDone!")

if __name__=="__main__":
    adaptorEthPortStats(None,None,None,None,None)
