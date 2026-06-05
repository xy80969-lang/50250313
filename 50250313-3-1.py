import json
import subprocess

cmd = """
fio test.fio \
--output-format=json
"""

result = subprocess.check_output(
    cmd,
    shell=True
)

data = json.loads(result)

iops = data["jobs"][0]["read"]["iops"]

bw = data["jobs"][0]["read"]["bw"]

print("IOPS:", iops)
print("Bandwidth:", bw)