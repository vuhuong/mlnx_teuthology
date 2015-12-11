import utilities
import optparse
import settings
import sys
import teuthology
import pdb

class RunnerError(Exception):  pass
class TestFormatError(RunnerError):  pass
class RunfileError(RunnerError):  pass


class Runner:
    def __init__(self, targetfile=None, bat=None, set_number=None,
                 report_result=False, poweroff=False, debug=False, mail=False,
                 runlist=None, archive=False):
        self.targetfile = targetfile
        self.bat = bat
        self.set_number = set_number
        self.report_result = report_result
        self.no_poweroff = poweroff
        self.debug = debug
        self.mail = mail
        self.runlist = runlist
        self.archive = archive
        self.use_runlist = None
        self.log_dir_inuse  = None

        #from settings
        self.sendmails = settings.SEND_MAIL_LIST
        self.default_log_path_dict = settings.LOG_PATH_LOCAL
        self.default_runlist_dict = settings.DEFAULT_RUN_LIST
        self.bat_list = settings.RUN_TYPE


    @staticmethod
    def from_argv(argv=None):
        parser = optparse.OptionParser()
        parser.add_option("-t", dest="targetfile", type="string",
                          help="Target file containing host info")
        parser.add_option("-b", dest="bat", type="string",
                          help="bat = bvt, bst, fvt_inktank, fvt_storm")
        parser.add_option("-s", dest="set_number", type="int",
                          help="set_number = 1, 2, 3,...execution set number,"
                               " not mandatory for bvt ")
        parser.add_option("--report", dest="report_result", default=False,
                          action="store_true", help="Report result to testlink")
        parser.add_option("--no-poweroff", dest="poweroff", default=False,
                          action="store_true", help="Dont poweroff nodes")
        parser.add_option("-v", dest="debug", default=False,
                          action="store_true",
                          help="Enable debug (verbose) logging.")
        parser.add_option("-m", dest="mail", default=False, action="store_true",
                          help="Send email on completion.")
        parser.add_option("--no-archive", dest="archive", default=True,
                          action="store_false",
                          help="Do not archive test output.")
        parser.add_option("-r", dest="runlist", type="string",
                          help="Specify the runlist.")
        (options, args) = parser.parse_args(args=argv)
        return Runner(**vars(options))


    def default_runlist(self):
        try:
            self.use_runlist = self.default_runlist_dict[self.bat]
        except KeyError:
            raise  RunfileError("No runlist available for bat type:%s" %
                                (self.bat))

    def run(self):
        if self.runlist:
            self.use_runlist = self.runlist
        else:
            self.default_runlist()

        #check if  user provided runlist exsis or not
        if not utilities.is_file_valid(self.use_runlist):
            raise RunfileError("runlist %s does not exist" %
                               self.use_runlist)

        #check if targetfile exist or not
        if (not self.targetfile) or \
           (not utilities.is_file_valid(self.targetfile)):
            raise RunnerError("Target file %s is not passed or does not exist" % (self.targetfile))
        #create log folder if not existing
        if self.bat not in self.bat_list:
            raise RunnerError("Invalid bat type %s, provide bvt, bst, fvt_inktank or fvt_storm")
        #check if set_number is provided, not mendatory for bvt
        if self.bat != 'bvt':
            if not self.set_number:
                raise RunnerError("Please pass set_number with -s option")
        self.log_dir_inuse = self.default_log_path_dict.get(self.bat)
        if not utilities.is_path(self.log_dir_inuse):
            utilities.create_dir(self.log_dir_inuse)

        #start executing the test present in the runlist
        obj = teuthology.Teuthology(targetfile=self.targetfile,
                                    bat_type=self.bat,
                                    set_number=self.set_number,
                                    report_result=self.report_result,
                                    runlist_path=self.use_runlist,
                                    log_path=self.log_dir_inuse,
                                    nuke=self.debug,  mail=self.mail,
                                    no_poweroff=self.no_poweroff)
        obj.run()


if __name__ == "__main__":
    runner = Runner.from_argv()
    runner.run()
    sys.exit(0)
