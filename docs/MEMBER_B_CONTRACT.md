# Member B contract: lab data (Network C)

This file defines what Member B's Ubuntu lab must produce so Member A's pipeline can use it.
Both members must agree on it in Sprint 1. Changes need both members' sign-off.

## 1. CICFlowMeter version
Pin the exact version here, and use it on both machines: **CICFlowMeter version = ________**

## 2. CSV format
- One or more CSV files in `lab/output/`. UTF-8, LF line endings, comma-separated.
- Exactly one header row.
- The header must match the CIC-IDS2017 CICFlowMeter header, same names and same order.
  Member A commits the reference header as `docs/feature_header.txt` in Sprint 1.
- The label column is named exactly `Label`.

## 3. Label names (use these exact strings)
| Lab activity | Write this in Label |
|---|---|
| Normal browsing, apt updates, normal SSH logins | BENIGN |
| hydra SSH brute force | SSH-Patator |
| hydra FTP brute force | FTP-Patator |
| slowloris | DoS slowloris |
| DVWA brute-force page (web) | Web Attack - Brute Force |
| sqlmap on DVWA | Web Attack - Sql Injection |
| nmap scans | PortScan (dropped by design, still label it) |

Label flows by attacker IP and by the attack time window in `lab/output/run_log.csv`.
The run log has these columns: start_time, end_time, attack, tool, attacker_ip, victim_ip, notes.

## 4. Scope and safety
- Attacks only against our own VMs on the private VMware network. Nothing leaves the laptop.
- Every attack run must have a row in run_log.csv.

## 5. Sanity checks before handing over
- Row count per class is written in `lab/output/class_counts.txt`.
- No rows with the wrong column count (open the CSV in a text editor, or run
  `awk -F, '{print NF}' file.csv | sort | uniq -c` and confirm one value).
- Member A runs `python scripts/01_clean.py` on the lab data. It fails loudly if the schema is wrong.

## 6. How to transfer
- Preferred: commit the scripts to Git. Send the CSVs via Google Drive or Kaggle. Do not put CSVs in Git.
- The CSVs go in `data/raw/lab/`. Add that folder to the cleaning script when Member A is ready.
