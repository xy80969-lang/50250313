import shutil
from datetime import datetime

log_file = "/var/log/ceph/ceph-osd.0.log"

backup_name = f"osd_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

shutil.copy(
    log_file,
    f"./logs/{backup_name}"
)