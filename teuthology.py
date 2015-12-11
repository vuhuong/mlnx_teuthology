"""
Description
"""
import commands
import datetime
import mail
import utilities
import regular_expressions
import os
import pprint
import re
import runner
import sys
import settings
#import testlinklib
import time
import pdb

VIRTUAL_TEUTHOLOGY = 'teuthology/virtualenv/bin/teuthology'
VIRTUAL_TEUTHOLOGY_NUKE = 'teuthology/virtualenv/bin/teuthology-nuke'
CEPH_QA_SUITES = 'ceph-qa-suite/suites/'
CURRENT_DATE = datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
CURRENT_DATE_WITHOUT_SPACE = datetime.date.today().strftime("%d %B %Y")


class Teuthology():
    def __init__(self, targetfile, bat_type=None, set_number=None,
                 report_result=False, runlist_path=None, log_path=None,
                 nuke=False, mail=False, no_poweroff=False):
        self.targetfile = targetfile
        self.bat = bat_type
        self.set_number = set_number
        self.report_result = report_result
        self.runlist = runlist_path
        self.log_path = log_path
        self.nuke = nuke
        self.runlist_use = []
        self.result = None
        self.mail = mail
        self.no_poweroff = no_poweroff
        self.execution_time = 0
        #get all the targets from target files
        self.target_nodes = utilities.read_yaml(self.targetfile).get('targets')
        self.target_nodes = self.target_nodes.keys()
        self.ceph_version = None
        self.tls_obj = None

        if self.report_result:
            self.tls_obj = testlinklib.Testlink()

    def parse_runlist(self):
        if self.bat == 'fvt_inktank':
            self.parse_fvt_inktank()
        elif self.bat == 'fvt_storm':
            self.parse_bvt()
        elif self.bat == 'bvt':
            self.parse_bvt()


    def parse_fvt_inktank(self):
        patter_obj = re.compile('clusters')
        list_of_testcase = []
        list_of_testcase = self.read_eachline(self.runlist)
        for test in list_of_testcase:
            testcase = test.split('{')
            each_test = [CEPH_QA_SUITES + testcase[0] + x.rstrip('}')
                         for x in testcase[1].split(" ") if not patter_obj.search(x)]
            #each_test = [CEPH_QA_SUITES + testcase[0] + x.rstrip('}')
            #             for x in testcase[1].split(" ")]

            self.runlist_use.append((test, " ".join(each_test)))


    def parse_bvt(self):
        list_of_testcase = []
        list_of_testcase = self.read_eachline(self.runlist)
        for eachtest in list_of_testcase:
            test = [CEPH_QA_SUITES + x for x in eachtest.split(" ")]
            self.runlist_use.append(" ".join(test))


    def read_eachline(self,file_path):
        """
        Return each file
        """
        test_case_list = []
        patter = re.compile("#")
        with open(file_path,'r') as runlist_handle:
            for eachline in runlist_handle:
                if not patter.match(eachline):
                    test_case_list.append(eachline.strip())

        return test_case_list


    def run(self):
        self.parse_runlist()
        self.total_result = {}
        log_path = self.log_path + CURRENT_DATE
        self.result = log_path + '/' + 'result.log'
        if not utilities.is_path(log_path):
            utilities.create_dir(log_path)

        no_of_testcases = len(self.runlist_use)

        if no_of_testcases == 0:
            print "No testcases to run"
            sys.exit()
        count = 1
        #Execution started, start time
        start_time = time.time()
        for each_test in self.runlist_use:
            if self.set_number:
               set_no = "_%s" % self.set_number
               log_no = 'Log' + str(count) + set_no
            else:
               log_no = 'Log' + str(count)
            log_suffix = log_path + '/' + log_no
            if type(each_test) is tuple:
                each_name, each_test = each_test[0], each_test[1]
            status = self.run_teuthology(each_test, log_suffix)
            if self.tls_obj:
                testcase_IDList = self.get_testcaseID(log_suffix)
                if testcase_IDList:
                    for tcid in testcase_IDList:
                        try:
                            self.tls_obj.report_result(tcid, status,
                                                       self.ceph_version)
                        except Exception:
                            print ("Error while reporting Testcases: "
                                   "%s to testlink" % tcid)
            try:
                each_name
            except Exception:
                pass
            else:
                each_test = each_name

            if not status:
                self.total_result["%s. %s" %(count,each_test)] = 'Fail'
            else:
                self.total_result["%s. %s" %(count,each_test)] = 'Pass'
            count+=1
        #Exection completed, stop time

        stop_time = time.time()
        self.execution_time = int(stop_time - start_time)
        with open(self.result,'w')  as result_handle:
            result_handle.write(pprint.pformat(self.total_result))
        print pprint.pformat(self.total_result)
        #send mail
        if self.mail:
            self.sendmail()

        #stop all the nodes
        if not self.no_poweroff:
            self.poweroff_nodes()
        return


    def poweroff_nodes(self):
        """
        This function will poweroff the nodes
        """
        #stop all the nodes
        power_stop = "ssh %s 'sudo shutdown -P now'"
        for node in self.target_nodes:
            cmd = power_stop % node
            status, output = self._run_getstatusouput(cmd)


    def run_teuthology(self, testcase, log_path):
        #Nuke the target nodes
        cmd = "%s -t %s" % (VIRTUAL_TEUTHOLOGY_NUKE, self.targetfile)
        status_nuke = self._run_cmd(cmd)
        #Execute the yaml files
        cmd  = "%s %s %s -a %s -v" % (VIRTUAL_TEUTHOLOGY, self.targetfile,
                                   testcase, log_path)
        status1 = self._run_cmd(cmd)
        status2 = self.check_summary(log_path + '/' + 'summary.yaml')
        return all((status1, status2))


    def get_hostip(self):
        cmd = regular_expressions.GET_PRIMARY_IP_UNIX
        status, output = self._run_getstatusouput(cmd)
        return output


    def _run_cmd(self, cmd):
        status = True
        status_1 = os.system(cmd)
        if status_1 != 0:
            status = False
        return status


    def _run_getstatusouput(self, cmd):
        status, output = commands.getstatusoutput(cmd)
        return (status, output)


    def check_summary(self, file_summary):
        status = False
        if not utilities.is_file_valid(file_summary):
            print "File %s does not exist" %(file_summary)
        else:
            summary_dict = utilities.read_yaml(file_summary)
            #set ceph version
            if not self.ceph_version:
                self.ceph_version = summary_dict.get('version')

            if summary_dict.get('success'):
                status = True
        return status


    def get_testcaseID(self, file_name):
        try:
            file_config = "%s/orig.config.yaml" %file_name
            if not utilities.is_file_valid(file_config):
                print "File %s does not exist" %(file_config)
            else:
                config_dict = utilities.read_yaml(file_config)

            return config_dict.get('testcase_id')
        except Exception:
            print "Error reporting result"
            return None


    def sendmail(self):
        to_add_list = []
	if self.bat == 'bvt':
            bat = 'BVT'
        elif self.bat == 'bst':
            bat = 'BST'
	elif self.bat == 'fvt_inktank':
            bat = 'FVT Inktank'
        else:
            bat = 'FVT Storm'
        subject = "%s Execution %s" % ( bat, CURRENT_DATE_WITHOUT_SPACE)
        from_addr = 'vu@mellanox.com'
	patter = re.compile('#')
        to_add_list = [x for x in settings.SEND_MAIL_LIST if not patter.match(x)]
        msg = "%s Summary %s\n\n" % (bat, CURRENT_DATE_WITHOUT_SPACE)
        msg+='Build Version: %s '% self.ceph_version
        msg+="Total Exection time in seconds: %s\n\n" % self.execution_time
        msg+="Log Path: %s " %("%s:%s" % (self.get_hostip(), self.log_path + CURRENT_DATE))
        msg+="Total Testcases: %s  Total Pass: %s  Total: Fail: %s\n\n"%(len(self.total_result.keys()),
                                                                    len([x for x in self.total_result.values() if x == 'Pass']),
                                                                    len([x for x in self.total_result.values() if x == 'Fail']))
        x = utilities.prettytable(20, self.total_result ,["Testcase", "Result"])
        msg+="%s" % x
        if settings.SMPT_SERVER:
            mail.sendmail(from_addr, to_add_list, subject, msg, settings.SMPT_SERVER)
        else:
            mail.sendmail(from_addr, to_add_list, subject, msg)
	return
