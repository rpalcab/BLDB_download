#!/usr/bin/env python3

"""
Script to programmatically download all 
protein sequences from BLDB.
"""

# %%
import argparse
import requests
from bs4 import BeautifulSoup
import urllib.request
from pathlib import Path
import time
import warnings

# %%
def get_args():

    parser = argparse.ArgumentParser(
        prog = 'bldb_download.py',
        description = 'Programmatic download of all protein sequences from BLDB.'
    )

    parser.add_argument(
        '-u', '--url', default='http://www.bldb.eu/seq_prot/',
        type=str,
        help="Parent URL of proteins. Modify in case it has changed"
    )

    parser.add_argument(
        '-r', '--retries', default=3,
        type=int,
        help="Number of download retries if connection error"
    )

    parser.add_argument(
        '-o', '--output', required=True,
        type=Path,
        help='Required. Final output directory'
    )

    return parser.parse_args()

# %%
STD_DELAY = 0.35
ERROR_DELAY = 5

# %%
def main():
    args = get_args()

    print(f'Reading {args.url}')
    r = requests.get(args.url)
    soup = BeautifulSoup(r.text, 'lxml')

    list_fastas = [link.get('href') for link in soup.find_all('a') if link.get('href').endswith('.fasta')]
    n_list = len(list_fastas)
    print(f"Downloading {n_list} sequences: ")

    for i, fasta in enumerate(list_fastas):
        update_status = int(i // n_list )
        print("[%-50s] %d%% %s (%d/%d)" % ('=' * (update_status // 2), update_status, fasta, i, n_list), end = '\r')
        success = False
        for n in range(args.retries):
            try:
                url = f"{args.url}{fasta}"
                dest = args.output / Path(fasta)
                urllib.request.urlretrieve(url, dest)
                success = True
                time.sleep(STD_DELAY)
                break
            except Exception as e:
                warnings.warn(f"Retry {n+1} for {fasta} failed: {e}")
                time.sleep(ERROR_DELAY)
        if not success:
            warnings.warn(f"Failed to download {fasta} after {args.retries} retries.")

# %%
if __name__ == "__main__":
    main()