
import os
import pwd
import grp
from shutil import rmtree


class Configuration(object):
  
   
    def __init__(self):
        """ Constructor """

        # filenames
        self.filename = "fallRiskEvaluation.conf"
        self.log_filename = "fallRiskEvaluation.log"
        # paths
        self.path = "/etc/sysconfig/fallRiskEvaluation/"
        self.log_path = "/var/log/fallRiskEvaluation/"
        
        self.pathname = os.path.abspath(os.path.join(self.path, self.filename))


        try:


            # Delete folder included files
            if os.path.isdir(self.path):
                rmtree(self.path) 

            # create folder
            os.makedirs(self.path)
            uid = pwd.getpwnam("orion2sql").pw_uid
            gid = grp.getgrnam("orion2sql").gr_gid            
            os.chown(self.path, uid, gid)

            # Generate logging path
            if os.path.exists(self.log_path) == False:
                os.makedirs(self.log_path)
                os.chown(self.log_path, uid, gid)

            # VM
            config = '[vm]\nPUBLIC_IP=127.0.0.1\n\n'
            # orion            
            config += '[orion]\nHOST=localhost\nPORT=1026\n\n'
            # MySQL database
            config += '[mysql]\nUSER=takis\nPASSWORD=t@k!s\nDATABASE_NAME=test\nHOST=localhost\n\n'
            # Restful web services
            config += '[services]\nHOST=localhost\nPORT=5000\n\n'
            # orion-to-mysql app
            config += '[orion2mysql]\nHOST=localhost\nPORT=5999\n\n'
            # Logs
            config += '[logs]\nPATH=' + self.log_path + self.log_filename + '\nLOG_FILES_NUMBER=5\nLOGS_FILE_SIZE=8192\n\n'
            # notifier
            config += '[notifications]\nEMAIL=my_gmail_account@gmail.com\nPASSWORD=my_gmail_password\n\n'

            # Generate a .conf file 
            with open(self.pathname, 'w') as file:
                file.write(config)

        except:
            import traceback
            traceback.print_exc()



if __name__ == '__main__':

    # create a new object
    obj = Configuration()

    

    
