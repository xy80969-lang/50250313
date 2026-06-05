import subprocess
import json
import csv
import time
from datetime import datetime

OUTPUT_FILE = "ceph_metrics.csv"


def run_cmd(cmd):
    try:
        result = subprocess.check_output(
            cmd,
            shell=True,
            stderr=subprocess.STDOUT
        )
        return result.decode("utf-8")
    except Exception as e:
        return str(e)


def get_cluster_status():
    output = run_cmd("ceph -s --format json")

    try:
        data = json.loads(output)

        health = data["health"]["status"]

        pg_total = data["pgmap"]["num_pgs"]

        osd_up = data["osdmap"]["num_up_osds"]

        osd_in = data["osdmap"]["num_in_osds"]

        return {
            "health": health,
            "pg_total": pg_total,
            "osd_up": osd_up,
            "osd_in": osd_in
        }

    except:
        return None


def get_iops_latency():

    output = run_cmd("ceph osd perf --format json")

    try:
        data = json.loads(output)

        commit_latency = []
        apply_latency = []

        for item in data["osd_perf_infos"]:
            commit_latency.append(float(item["perf_stats"]["commit_latency_ms"]))
            apply_latency.append(float(item["perf_stats"]["apply_latency_ms"]))

        avg_commit = sum(commit_latency) / len(commit_latency)

        avg_apply = sum(apply_latency) / len(apply_latency)

        return avg_commit, avg_apply

    except:
        return 0, 0


def get_recovery_status():

    output = run_cmd("ceph pg stat")

    return output.strip()


def collect_data():

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cluster = get_cluster_status()

    if cluster is None:
        return

    commit_latency, apply_latency = get_iops_latency()

    recovery_status = get_recovery_status()

    row = [
        timestamp,
        cluster["health"],
        cluster["pg_total"],
        cluster["osd_up"],
        cluster["osd_in"],
        round(commit_latency, 2),
        round(apply_latency, 2),
        recovery_status
    ]

    with open(
            OUTPUT_FILE,
            "a",
            newline="",
            encoding="utf-8"
    ) as f:

        writer = csv.writer(f)

        writer.writerow(row)

    print("Collected:", timestamp)


if __name__ == "__main__":

    with open(
            OUTPUT_FILE,
            "w",
            newline="",
            encoding="utf-8"
    ) as f:

        writer = csv.writer(f)

        writer.writerow([
            "Timestamp",
            "Health",
            "PG_Count",
            "OSD_Up",
            "OSD_In",
            "Commit_Latency(ms)",
            "Apply_Latency(ms)",
            "Recovery_Status"
        ])

    while True:
        collect_data()
        time.sleep(60)