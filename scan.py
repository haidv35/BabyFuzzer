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

def scanDir(host, fileName):
    # command = ['ffuf/./ffuf', '-w', fileName, '-u', host + "FUZZ", '-recursion', '-recursion-depth', '3', '-mc', '200,204']
    command = 'ffuf/./ffuf -w ' + fileName + ' -u ' + host + ' -mc 200,204,301,302'
    p = subprocess.Popen(command, stdout=subprocess.PIPE, shell = True)
    while True:
        line = p.stdout.readline().decode('utf-8')
        if not line: 
            break
        print(OKGREEN + line + RESET)
    # text = p.stdout.decode('utf-8')
    # return text

def regexFuzz(base_url, keyword):
    request = urllib.request.Request(base_url)
    request.add_header('User-Agent', 'Mozilla/5.0')
    http_request = urllib.request.urlopen(request)
    http_response = str(http_request.read())
    # http_status = http_request.getcode()
    # http_length = len(http_response)

    if keyword in http_response:
        return True
    else:
        return False

# def inject(base_url, payload, keyword):
#     status, http = regexFuzz(base_url.replace("FUZZ", payload), keyword)
#     return status, http


# def XSS(base_url):
#     check = 0

#     payload = "<script>alert(1)</script>"
#     status, http = inject(base_url, payload, payload)
#     if(status == 1) and (http_status == 200):
#         check += 1

#     payload = "%3Cscript%3Ealert(1)%3C%2Fscript%3E"
#     status, http = inject(base_url, payload, payload)
#     if(status == 1) and (http['http_status'] == 200):
#         check += 1

#     payload = '"><iframe/onload=alert(1)>'
#     status, http = inject(base_url, payload, payload)
#     if(status == 1) and (http['http_status'] == 200):
#         check += 1

#     payload = '"><script>alert(1)</script>'
#     status, http = inject(base_url, payload, payload)
#     if(status == 1) and (http['http_status'] == 200):
#         check += 1

#     if(check > 0):
#         return check
#     return 0

# def SQLI(base_url):
#     check = 0

#     payload = "\\"
#     status, http = inject(base_url, payload, 'SQL')
#     if(http['http_status'] == 500) or (http['http_status'] == 503) or status == 1:
#         check += 1


#     payload = "\\\\"
#     status, http = inject(base_url, payload, 'SQL')
#     if(http['http_status'] == 500) or (http['http_status'] == 503) or status == 1:
#         check += 1

#     if(check > 0):
#         return check
#     return 0


# def LFI(base_url):
#     check = 0

#     payload = "/etc/passwd"
#     status, http = inject(base_url, payload, 'root:')
#     if(http['http_status'] == 200) and (status == 1) and (http['http_length'] > 0):
#         check += 1

#     payload = "/etc/passwd%00"
#     status, http = inject(base_url, payload, 'root:')
#     if(http['http_status'] == 200) and (status == 1) and (http['http_length'] > 0):
#         check += 1

#     payload = "pHp://FilTer/convert.base64-encode/resource=..././index"
#     status, http = inject(base_url, payload, payload)

#     if(http['http_status'] == 200) and (status == 0) and (http['http_length'] > 0):
#         check += 1

#     if(check > 0):
#         return check
#     return 0

# def SSTI(base_url):

def fuzz(base_url, full_url, vulner, fileName):
    print("")
    print(BGRED + OKWHITE + "=> Scanning " + vulner + "..." + RESET)

    defaultSize = defaultFuzz(full_url)
    text = normalFuzz(base_url, fileName)
    #Get ffuf response


    check = 0

    if(vulner == "SQLI"):
        command = 'python3 sqlmap/sqlmap.py -u ' + full_url
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
    if(vulner == "XSS"):
        command = 'python3 XSStrike/xsstrike.py -u ' + full_url + " --fuzzer"
        p = subprocess.Popen(command, stdout=subprocess.PIPE, shell = True)
        while True:
            line = p.stdout.readline().decode('utf-8').strip()
            if not line: 
                break
            print(line)


    
            # keyword = ["Parameter:", "Type:", "Title:", "Payload:"]
            # for key in keyword:
            #     if key in line:
            #         if(key == "Type:"):
            #             check += 1
            #             print(OKGREEN + line + RESET)
            #         else:
            #             check += 1
            #             print(OKGREEN + line.strip() + RESET)

    # for line in text.splitlines():
    #     if line:
    #         m = re.compile(r'(.*)(\s\[.*)')
    #         g = re.search(m, line)
    #         fuzzPayload = g.group(1).strip()
    #         #Da fix loi ki tu dac biet

    #         fuzzPayload = fuzzPayload[4:]
    #         fuzzPayload = requote_uri(fuzzPayload)
    #         fuzzResponse = g.group(2).strip()

    #         m = re.compile(r'Status:\s(\d+).+Size:\s(\d+).+Words:\s(\d+).+Lines:\s(\d+)')
    #         g = re.search(m, fuzzResponse)
    #         status = int(g.group(1).strip())
    #         size = int(g.group(2).strip())
    #         word = int(g.group(3).strip())

    #         # print(OKGREEN + line + RESET)

    #         #Reflected and DOM XSS
    #         if(vulner == "XSS") and (status == 200):
    #             checkRes = regexFuzz(base_url.replace("FUZZ", fuzzPayload), fuzzPayload)
    #             #kiem tra status = 200
    #             #kiem tra payload co trong response ko
    #             #kiem tra kich thuoc respones > 0
    #             if (checkRes is True) and (size > 0):
    #                 check += 1
    #                 print(OKGREEN + line + RESET)
            

    #         if(vulner == "LFI") and (status == 200):
    #             checkRes = regexFuzz(base_url.replace("FUZZ", fuzzPayload), fuzzPayload)
    #             #kiem tra status = 200
    #             #kiem tra size response > 0
    #             #kiem tra size response != size mac dinh
    #             #kiem tra payload khong nam trong response

    #             if (size > 0) and (checkRes is False):
    #                 #TH include cac trang con
    #                 if (size >= defaultSize):
    #                     check += 1
    #                     print(OKGREEN + line + RESET)
    #                 #TH /etc/passwd, C:\\boot.ini
    #                 else:
    #                     keyword = ['root:', 'boot loader', '16-bit']
    #                     for val in keyword:
    #                         checkRes = regexFuzz(base_url.replace("FUZZ", fuzzPayload), val)
    #                         if(checkRes == 1):
    #                             check += 1
    #                             print(OKGREEN + line + RESET)
            
    if (check == 0):
        print(OKORANGE + "NOT FOUND !!!" + RESET)
        

def scan(base_url,full_url):
    
    #XSS
    fuzz(base_url, full_url, "XSS", "XSS.txt")
    #LFI
    # fuzz(base_url, full_url, "LFI", "LFI.txt")
    #SQLI
    fuzz(base_url, full_url, "SQLI", "SQLI.txt")


def process(all_param, all_url):
    param_list = all_param['param_list']
    param_vals = all_param['param_vals']
    param_length = all_param['param_length']
    full_url = all_url['full_url']
    dynamic_url = all_url['dynamic_url']
    all_url['base_url'] = base_url = base_url = str(full_url[:dynamic_url + 1])

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
            scan(base_url, full_url)
            base_url = str(full_url[:dynamic_url + 1])
        elif (i == param_length and i != active_fuzz):
            base_url += param_list[i-1] + param_vals[i-1]
            active_fuzz = active_fuzz+1
            i = 1
            print(base_url)
            scan(base_url, full_url)
            base_url = str(full_url[:dynamic_url + 1])
        elif (i == param_length):
            base_url += param_list[i-1] + param_vals[i-1]
            active_fuzz = active_fuzz+1
            i = 1
            print(base_url)
            scan(base_url, full_url)
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
        # print("")
        # print(COLOR1 + "> FUZZING DIRECTORIES AND FILES !!!" + RESET)
        # scanDir(all_url['host'] + "FUZZ", "wordlist.txt")

        #Scan vulnerability
        print("")
        print(COLOR1 + "> FUZZING PARAMS AND FIND VULNERABILITIES !!!" + RESET)
        print("=" * 50)
        process(all_param, all_url)
        
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


    
