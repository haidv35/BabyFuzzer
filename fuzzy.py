import requests, sys, os, json, optparse, subprocess, re
from http import cookies
from urllib.parse import urlparse, urlencode, quote_plus
from requests.utils import requote_uri
import urllib.request, sys, os, optparse
from ast import literal_eval

OKBLUE='\033[94m'
OKRED='\033[91m'
OKGREEN='\033[92m'
OKORANGE='\033[93m'
OKMAGENTA = '\u001b[35m'
OKCYAN = '\u001b[36m'
OKWHITE = '\u001b[37m'
OKBLACK = '\u001b[30m'
COLOR1='\033[95m'
COLOR2='\033[96m'

BGWHITE = '\u001b[47m'
BGRED = '\u001b[41m'
BGGREEN = '\u001b[42m'
BGBLUE = '\u001b[44m'

RESET='\x1b[0m'

def greeting():
    print('''
██████╗  █████╗ ██████╗ ██╗   ██╗    ███████╗██╗   ██╗███████╗███████╗██╗   ██╗
██╔══██╗██╔══██╗██╔══██╗╚██╗ ██╔╝    ██╔════╝██║   ██║╚══███╔╝╚══███╔╝╚██╗ ██╔╝
██████╔╝███████║██████╔╝ ╚████╔╝     █████╗  ██║   ██║  ███╔╝   ███╔╝  ╚████╔╝ 
██╔══██╗██╔══██║██╔══██╗  ╚██╔╝      ██╔══╝  ██║   ██║ ███╔╝   ███╔╝    ╚██╔╝  
██████╔╝██║  ██║██████╔╝   ██║       ██║     ╚██████╔╝███████╗███████╗   ██║   
╚═════╝ ╚═╝  ╚═╝╚═════╝    ╚═╝       ╚═╝      ╚═════╝ ╚══════╝╚══════╝   ╚═╝   
                                                                               
    ''')


def readJson(filename):
    #read victim file
    f = open(filename,)
    jsonData = json.load(f)
    f.close()
    return jsonData


def defaultFuzz(url):
    request = urllib.request.Request(url)
    request.add_header('User-Agent', 'Mozilla/5.0')

    http_request = urllib.request.urlopen(request)
    http_response = str(http_request.read())
    http_length = len(http_response)
    return http_length


def normalFuzz(base_url, fileName):
    command = ['ffuf/./ffuf', '-w', fileName, '-u', base_url]
    p = subprocess.run(command, stdout=subprocess.PIPE)
    text = p.stdout.decode('utf-8')
    return text

def fuzzingDirsAndFiles(host, fileName):
    command = 'ffuf/./ffuf -w ' + fileName + ' -u ' + host + ' -mc 200,204,301,302'
    p = subprocess.Popen(command, stdout=subprocess.PIPE, shell = True)
    while True:
        line = p.stdout.readline().decode('utf-8').strip()
        if not line: 
            break
        if ("301" in line) or ("302" in line):
            print(OKORANGE + line + RESET)
        else:
            print(OKGREEN + line + RESET)

def regexFuzz(base_url, keyword):
    request = urllib.request.Request(base_url)
    request.add_header('User-Agent', 'Mozilla/5.0')
    http_request = urllib.request.urlopen(request)
    http_response = str(http_request.read())
    if keyword in http_response:
        return True
    else:
        return False

def fuzz(full_url, vulnerability):
    print("")
    print(BGRED + OKWHITE + "=> Scanning " + vulnerability + "..." + RESET)
    check = 0
    if(vulnerability == "SQLI"):
        command = 'python3 SQLI/sqlmap.py -u ' + full_url
        p = subprocess.Popen(command, stdout=subprocess.PIPE, shell = True)
        while True:
            line = p.stdout.readline().decode('utf-8')
            if not line: 
                break
            keyword = ["Parameter:", "Type:", "Title:", "Payload:"]
            for key in keyword:
                if key in line:
                    if(key == "Type:"):
                        check += 1
                        print(OKGREEN + line + RESET)
                    else:
                        check += 1
                        print(OKGREEN + line.strip() + RESET)
    if(vulnerability == "XSS"):
        command = 'python3 XSS/xsstrike.py -u ' + full_url + " --fuzzer"
        p = subprocess.Popen(command, stdout=subprocess.PIPE, shell = True)
        while True:
            line = p.stdout.readline().decode('utf-8').strip()
            if not line: 
                break
            if "passed" in line:
                print(OKGREEN + line + RESET)
            if "filtered" in line:
                print(OKRED + line + RESET)


    if(vulnerability == "LFI"):
        command = 'LFI/./dotdotpwn.pl -m http-url -u ' + full_url + ' -k "root:" -r log.txt'
        p = subprocess.Popen(command, stdout=subprocess.PIPE, shell = True)
        while True:
            line = p.stdout.readline().decode('utf-8')
            if not line: 
                break
            print(OKWHITE + line.strip() + RESET)

            

def scanVulners(full_url, dynamic_url):
    #XSS
    fuzz(full_url, "XSS")
    
    #SQLI
    fuzz(full_url, "SQLI")

def fuzz2(all_param, all_url, vulnerability):
    payload = "TRAVERSAL"
    param_list = all_param['param_list']
    param_vals = all_param['param_vals']
    param_length = all_param['param_length']
    full_url = all_url['full_url']
    dynamic_url = all_url['dynamic_url']
    all_url['base_url'] = base_url = str(full_url[:dynamic_url + 1])

    active_fuzz = 1
    i = 1
    while i <= param_length and active_fuzz <= param_length:
        if (i < param_length and i == active_fuzz):
            print(COLOR2 + ">> Parameter: " + param_list[i-1][:-1] + RESET)
            base_url += param_list[i-1] + payload + "&"
            i = i+1
        elif (i == param_length and i == active_fuzz):
            print(COLOR2 + ">> Parameter: " + param_list[i-1][:-1] + RESET)
            base_url += param_list[i-1] + payload
            active_fuzz = active_fuzz+1
            i = i+1
            print(base_url)
            fuzz(base_url, vulnerability)
            base_url = str(full_url[:dynamic_url + 1])
        elif (i == param_length and i != active_fuzz):
            base_url += param_list[i-1] + param_vals[i-1]
            active_fuzz = active_fuzz+1
            i = 1
            print(base_url)
            fuzz(base_url, vulnerability)
            base_url = str(full_url[:dynamic_url + 1])
        elif (i == param_length):
            base_url += param_list[i-1] + param_vals[i-1]
            active_fuzz = active_fuzz+1
            i = 1
            print(base_url)
            fuzz(base_url, vulnerability)
            base_url = str(full_url[:dynamic_url + 1])
        else:
            base_url += param_list[i-1] + param_vals[i-1] + "&"
            i = i+1

def parseURL(all_url):
    full_url = all_url['full_url']

    parsed = urllib.request.urlparse(full_url)

    all_url['host'] = parsed.scheme + "://" + parsed.netloc + "/"

    params = urllib.parse.parse_qsl(parsed.query)
    param_list = []
    param_vals = []
    param_length = 0
    for x,y in params:
        param_list.extend([str(x + "=")])
        param_vals.extend([str(urllib.parse.quote_plus(y))])
        param_length = param_length + 1
    dynamic_url = full_url.find("?")
    all_url['dynamic_url'] = dynamic_url

    all_param = {
        "param_list": param_list, 
        "param_vals": param_vals, 
        "param_length": param_length
    }
    return all_param, all_url

def mainProcess(jsonData):
    for data in jsonData:
        full_url = data['url']

        all_url = {}
        all_url['full_url'] = full_url
        all_param, all_url = parseURL(all_url)
        print(all_url['host'] + "FUZZ")

        #Scan dir
        print("")
        print(COLOR1 + "> FUZZING DIRECTORIES AND FILES !!!" + RESET)
        fuzzingDirsAndFiles(all_url['host'] + "FUZZ", "wordlist.txt")

        #Scan vulnerability
        print("")
        print(COLOR1 + "> FUZZING PARAMS AND FIND VULNERABILITIES !!!" + RESET)
        print("=" * 50)
        scanVulners(full_url, all_url['dynamic_url'])

        #LFI & Path traversal
        fuzz2(all_param, all_url, "LFI")
        
        break
#----------------------------------------------------------------------------------------------------#
payload = "FUZZ"
greeting()

# if len(sys.argv) < 2:
#     print("You need to specify a URL to scan. Use --help for all options.")
#     quit()
# else:
#     parser = optparse.OptionParser()
#     parser.add_option('-u', '--url', action="store", dest="url", help="Full URL to scan", default="")
#     options,args = parser.parse_args()
#     target = str(options.url)

json_data = readJson("data.json")
mainProcess(json_data)


    
