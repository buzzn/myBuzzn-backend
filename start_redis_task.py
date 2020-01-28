activate_this = '/var/www/mybuzzn-backend.buzzn.net/mybuzznbackend/env/bin/activate_this.py'
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

import setup_environment
    
import util.task
util.task.run()

