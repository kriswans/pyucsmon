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

class Get_net_stats:

    def __init__(self, connectvars, outCookie, compute_list):
        self.connectvars = connectvars
        self.outCookie = outCookie
        self.compute_list = compute_list

    def findUCSMCredfile():
        '''find credential file for UCSM login'''


    def acquireConnectVars():
        '''aquire user login, connection, and polling variables for a ucs system. Return a dictionary containing the variables'''
        ucsm_ip=input("Enter the IP or Name of the UCSM that you will connect to: ")
        runs=int(input("\nEnter the number of polling iterations: "))
        interv=int(input("\nEnter the polling interval: "))
        user=input("\nEnter the username to connect to UCSM: ")
        passw=getpass.getpass(prompt='\nEnter UCSM Password: ')
        url = "http://{ucsm_ip}/nuova".format(ucsm_ip=ucsm_ip)
        connectvars={'ucsm_ip':ucsm_ip,'runs':runs,'interv':interv,'user':user,'passw':passw,'url':url}

        return connectvars

    def acquireCookie(connectvars):
        '''acquire and return login cookie to be used in place of user credentials'''

        url =connectvars['url']

        payload = "<aaaLogin inName=\"{user}\" inPassword=\"{passw}\" />".format(user=connectvars['user'],passw=connectvars['passw'])
        headers = {
            'content-type': "text/xml",
            'cache-control': "no-cache",
            }

        response = requests.request("POST", url, data=payload, headers=headers)

        root = ElementTree.fromstring(response.content)


        for child in root.iter('aaaLogin'):
            aaaLogin=child.attrib

        outCookie=aaaLogin['outCookie']

        return outCookie

    def findCompute(outCookie):
        '''find active servers in UCS domain, i.e. servers that have a Service Prifile associated.
        Return a list of active servers'''
        payload = "<configFindDnsByClassId \r\n    classId=\"computeItem\" \r\n    cookie=\"{outCookie}\" />".format(outCookie=outCookie)
        headers = {
            'content-type': "text/xml",
            'cache-control': "no-cache",
            }

        url =connectvars['url']

        response2 = requests.request("POST", url, data=payload, headers=headers)

        root2 = ElementTree.fromstring(response2.content)

        compute_list=[]
        for child in root2.iter('dn'):
             compute_list.append(child.attrib['value'])

        return compute_list

    def adaptorEthPortStats(outCookie, compute_list, connectvars):
        ''' polls the ethernet stats on the blades that have a service profile associated'''
        statsfile=open('adaptorEthPortStats.csv','w')
        i=0
        runs=connectvars['runs']
        interv=connectvars['interv']
        while i < runs :
            print("\nRunning {i} of {runs} runs.".format(i=str(i+1),runs=str(runs)))
            for svr in compute_list:

                payload = "<configScope \r\n    cookie=\"{outCookie}\" \r\n    inHierarchical=\"true\" \r\n    dn=\"{svr}\"\r\n    inClass=\"adaptorEthPortStats\" />".format(outCookie=outCookie,svr=svr)
                headers = {
                    'content-type': "text/xml",
                    'cache-control': "no-cache",
                    }

                url =connectvars['url']

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


if __name__ == '__main__':
    Get_net_stats.findUCSMCredfile()
    connectvars=Get_net_stats.acquireConnectVars()
    outCookie=Get_net_stats.acquireCookie(connectvars)
    compute_list=Get_net_stats.findCompute(outCookie)
    Get_net_stats.adaptorEthPortStats(outCookie, compute_list, connectvars)
