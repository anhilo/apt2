try:
    from yattag import Doc
except ImportError:
    raise ImportError('Missing Yattag, if you would like to enable report generation do: pip install yattag')
from core.actionModule import actionModule
from core.keystore import KeyStore as kb
from core.utils import Utils


class reportgen(actionModule):
    def __init__(self, config, display, lock):
        super(reportgen, self).__init__(config, display, lock)
        self.title = "Generate Report"
        self.shortName = "reportGen"
        self.description = "Gather scan information and generate HTML report"

        self.requirements = []
        self.triggers = ["allFinished"]

        self.safeLevel = 5

    def getTargets(self):
        # we are interested in all hosts
        self.targets = kb.get(['host'])

    def processTarget(self, t, port):
        # do nothing
        return

    def process(self):
        self.display.verbose(self.shortName + " - Writing report")
        doc, tag, text = Doc().tagtext()
        self.getTargets()
        #Calculate some numbers
        numhosts = len(self.targets)
        services = kb.get('service')
        numservices = 0
        numvulnerabilities = 0
        for s in services:
                #TODO: Could make this a dict and do counts by specific services/port
                numserv = len(kb.get('service/' + s + '/host'))
                numservices = numservices + numserv
        for t in self.targets:
            numvulnerabilities = numvulnerabilities + len(kb.get('host/' + t + '/vuln'))
        doc.asis('<!DOCTYPE html>')
        with tag('html'):
            with tag('head'):
                with tag('title'):
                    text('Generated Report')
                with tag('style'):
                    text("""div{ width: 100%; } 
                        html { margin: 0; padding: 10px; } 
                        body { font: 12px verdana, sans-serif;line-height: 1.88889; background: #CCC; margin: 5%; padding: 0; width: 90%; } 
                        p { margin-top: 5px; text-align: justify; } 
                        h3 { font: italic normal 1.4em georgia, sans-serif; letter-spacing: 1px; margin-bottom: 0; } 
                        div.hostsection{ border-top: 1px solid #555555; min-height: 30px; background: #AAA; padding: 0px;}
                        div.hostsection h3{ font: bold; width: 100%; float: left; background: #CCC; }
                        div.hostsection b{font: bold; width: 100%; float: left; background: #BBB;}
                        .sectiontitle{ font: bold; width: 100%; float: left; background: #BBB; }
                        .toc{ border-top: 2px solid #AAAAAA; }
                        .toctable{}
                        .bodysection{ width: 90%; border-top: 1px solid #555555; }
                        .bodysectiontext{}
                        a.vulnname{ font: 16px verdana; }
                        div.vulndescription{ border-top: 1px solid #000; min-height: 30px; background: #AAA; padding: 5px; } 
                        .vulndescriptiontitle{ font: bold; width: 100%; float: left; background: #BBB; }
                        .vulndescriptioncontents{}
                        a:link { font-weight: bold; text-decoration: none; } 
                        a:visited { font-weight: bold; text-decoration: none; } 
                        a:hover, a:focus, a:active { text-decoration: underline; }""")
            with tag('body'):
                with tag('div', klass='toc'):
                    with tag('h2', klass='sectiontitle'):
                        text('Table of Contents')
                    with tag('table', klass='toctable'):
                        with tag('tr'):
                            with tag('td'):
                                with tag('a', href='#Summary'):
                                    text('Summary')
                        with tag('tr'):
                            with tag('td'):
                                with tag('a', href='#Hosts'):
                                    text('Hosts')
                        with tag('tr'):
                            with tag('td'):
                                with tag('a', href='#Vulns'):
                                    text('Vulnerabilities and Findings')
                with tag('div', klass='bodysection'):
                    with tag('a', id='Summary'):
                        with tag('h2', klass='sectiontitle'):
                            text('Summary')
                    with tag('div', klass='bodysectiontext'):
                        text('This is a summary of everything')
                        with tag('ul'):
                            #NMAP Scan Arguments
                            #TODO: Update this to reflect an imported NMAP file, which doesn't modify these values
                            with tag('li'):
                                text('NMAP Scan')
                                with tag('ul'):
                                    with tag('li'):
                                        text('Scan Type: ' + self.config["scan_type"])
                                    with tag('li'):
                                        text('Scan Flags: ' + self.config["scan_flags"])
                                    with tag('li'):
                                        text('Port Range: ' + self.config["scan_port_range"])
                                    if self.config["scan_target"]:
                                        with tag('li'):
                                            text('Target: ' + self.config["scan_target"])
                                    elif self.config["scan_target_list"]:
                                        with tag('li'):
                                            text('Target: ' + self.config["scan_target_list"])
                            #Total Hosts Found
                            with tag('li'):
                                text('Hosts Found: ' + str(numhosts))
                            #Total Services Found
                            with tag('li'):
                                text('Services Found: ' + str(numservices))
                            #Total Vulnerabilities Found
                            with tag('li'):
                                text('Vulnerabilities Found: ' + str(numvulnerabilities))
                with tag('div', klass='bodysection'):
                    with tag('a', id='Hosts'):
                        with tag('h2', klass='sectiontitle'):
                            text('Hosts')
                    with tag('div', klass='bodysectiontext'):
                        text('This is a detailed breakdown of hosts')
                        #For each host
                        for t in self.targets:
                            with tag('div', klass='hostsection'):
                                with tag('h3'):
                                    #Output IP address - Known Hostname
                                    text(t)
                                #List Services
                                hostservices = kb.get('service/*/host/' + t)
                                if len(hostservices) > 0:
                                    with tag('b', klass='hostsection'):
                                        text('Services')
                                    with tag('ul'):
                                        for s in hostservices:
                                            tcpports = kb.get('service/' + s + '/host/' + t + '/tcpport')
                                            udpports = kb.get('service/' + s + '/host/' + t + '/udpport')
                                            ports = ""
                                            for p in tcpports:
                                                if (ports == ""):
                                                    ports = p + "/TCP"
                                                else:
                                                    ports = ports + ", " + p + "/TCP"
                                            for p in udpports:
                                                if (ports == ""):
                                                    ports = p + "/TCP"
                                                else:
                                                    ports = ports + ", " + p + "/TCP"
                                            with tag('li'):
                                                text(s + " - " + ports)
                                #List Domains
                                hostdomains = kb.get('domain/*/host/' + t)
                                if len(hostdomains) > 0:
                                    with tag('b', klass='hostsection'):
                                        text('Domains/Workgroups')
                                    with tag('ul'):
                                        for s in hostdomains:
                                            with tag('li'):
                                                text(s)
                                #List Users
                                hostusers = kb.get('host/' + t + '/user')
                                if len(hostusers) > 0:
                                    with tag('b', klass='hostsection'):
                                        text('Users')
                                    with tag('ul'):
                                        for s in hostusers:
                                            with tag('li'):
                                                text(s)
                                #List Shares
                                hostshares = kb.get('host/' + t + '/share')
                                if len(hostshares) > 0:
                                    with tag('b', klass='hostsection'):
                                        text('Shares')
                                    with tag('ul'):
                                        for s in hostshares:
                                            with tag('li'):
                                                text(s)
                                #Link to section in Vulnerabilities
                                hostvulns = kb.get('host/' + t + '/vuln')
                                if len(hostvulns) > 0:
                                    with tag('b', klass='hostsection'):
                                        text('Vulnerabilities')
                                    with tag('ul'):
                                        i = 0
                                        for s in hostvulns:
                                            with tag('li'):
                                                with tag('a', href='#vuln' + t.replace('.','') + str(i)):
                                                    i += 1
                                                    text(s)
                                #List Shares
                                hostfiles = kb.get('host/' + t + '/files')
                                if len(hostfiles) > 0:
                                    with tag('b', klass='hostsection'):
                                        text('Output Files')
                                    with tag('ul'):
                                        for s in hostfiles:
                                            files = kb.get('host/' + t + '/files/' + s)
                                            for f in files:
                                                with tag('li'):
                                                    url = "file://" + f.replace("%2F","/")
                                                    with tag('a', href=url):
                                                        text(s)
                with tag('div', klass='bodysection'):
                    with tag('a', id='Vulns'):
                        with tag('h2', klass='sectiontitle'):
                            text('Vulnerabilities and Findings')
                    with tag('div', klass='bodysectiontext'):
                        text('This is a detailed breakdown of vulnerabilities and findings')
                        #For each Host that has listed vulnerabilties
                        for t in self.targets:
                            #For each Vulnerability
                            hostvulns = kb.get('host/' + t + '/vuln')
                            if len(hostvulns) > 0:
                                with tag('h3', klass='hostsection'):
                                    #Output IP address - Known Hostname
                                    text(t)
                                i = 0
                                for s in hostvulns:
                                    with tag('div', klass='vulndescription'):
                                        #Generate anchor tag to link from host section can be made
                                        with tag('a', klass='vulnname', id='vuln' + t.replace('.','') + str(i)):
                                            i += 1
                                            #Title
                                            text(s) 
                                        #Associated Service, Port, IP Address
                                        #If there is a path (NMAP -> FTP Found -> Anonymoous Login) Put it here
                                        vulnDetails = kb.get("host/" + t + "/vuln/" + s)
                                        for d in vulnDetails:
                                            #Iterate through each section under this vuln (module, vector, message, port, etc.)
                                            if(d == "output"):
                                                outfile = kb.get("host/" + t + "/vuln/" + s + "/" + d)
                                                with tag('a', klass='vulndescriptiontitle', ):
                                                    text("Files:")
                                                with tag('ul'):
                                                    for f in outfile:
                                                        with tag('li'):
                                                            url = "file://" + f.replace("%2F","/")
                                                            with tag('a', klass='vulndescriptioncontents', href=url):
                                                                text(f.replace("%2F","/"))
                                            else:
                                            #TODO: Look into capitalizing first letter, maybe splitting at capitals for cases like communityString
                                                with tag('p', klass='vulndescriptiontitle'):
                                                    text(d)
                                                detailContents = kb.get("host/" + t + "/vuln/" + s + "/" + d)
                                                with tag('ul'):
                                                    for c in detailContents:
                                                        with tag('li', klass='vulndescriptioncontents'):
                                                            text(c)
        #TODO: Put report in folder, copy CSS and maybe JS files (if we want to make the report fancy)
        outfile = self.config["reportDir"] + self.shortName + "_" + Utils.getRandStr(10) + ".html"
        Utils.writeFile(doc.getvalue(), outfile)
        self.display.alert("Report file located at %s" % outfile)

        return
