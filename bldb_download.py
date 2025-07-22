# %%
import argparse
import requests
from bs4 import BeautifulSoup
from pathlib import Path
import time
import warnings
import sys
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

# %%
ERROR_DELAY = 5

# %%
def parse_args():
    parser = argparse.ArgumentParser(
        prog = 'bldb_download.py',
        description='Parse BLDB from site web. Downloads tables and protein sequences.')

    parser.add_argument(
        '-u', '--url', default='http://www.bldb.eu/',
        type=str,
        help="Parent URL of proteins. Default: http://www.bldb.eu/"
    )

    parser.add_argument(
        '-r', '--retries', default=3,
        type=int,
        help="Number of download retries if connection error"
    )

    parser.add_argument(
        '-d', '--delay', default=0,
        type=float,
        help="Seconds of delay between downloads. Default: 0"
    )

    parser.add_argument(
        '-o', '--output', required=True,
        type=Path,
        help='Required. Final output directory'
    )

    return parser.parse_args()

# %%
def read_html(url):
    """
    Read HTML from a given URL and return a BeautifulSoup object.
    """
    r = requests.get(url)
    if r.status_code != 200:
        raise ValueError(f"Failed to retrieve data from {url}. Status code: {r.status_code}")
    return BeautifulSoup(r.text, 'lxml')

# %%
def retrieve_table(soup):
    """
    Retrieve a table from the given URL.
    """
    basic_columns = ["Ambler class", "Protein name", "Alternative protein names", "Subfamily", "GenPeptID", "GenBankID", "PubMedID (DOI)", "Sequence", "Number of PDB structures", "Mutants", "Phenotype", "Functional information", "Natural (N) or Acquired (A)"]	
    full_columns = []
    drop_cols = ['Ambler class_link', 'Protein name_link', 'Alternative protein names_link', 'Phenotype_link', 'Natural (N) or Acquired (A)_link']

    for col in basic_columns:
        full_columns.extend([col, f'{col}_link'])

    d_df = {}
    for table in soup.find_all('table'):
        for row in table.find_all('tr'):
            if any(a.get('href', '').endswith('.fasta') for a in row.find_all('a')):
                new_row = '@'.join([
                    td.text.strip() + '@' + ','.join(a.get('href') for a in td.find_all('a'))
                    for td in row.find_all('td')
                ]).split('@')
                d_df[new_row[2]] = new_row

    final_df = pd.DataFrame(d_df).T.reset_index(drop=True)
    final_df.columns = full_columns
    final_df.drop(columns=drop_cols, inplace=True, errors='ignore')

    return final_df

# %%
def download_single_fasta(fasta, base_url, output_dir, retries, delay):
    """
    Download a single FASTA file using streaming requests.
    """
    url = f"{base_url}{fasta}"
    dest = output_dir / Path(fasta)

    for attempt in range(retries):
        try:
            with requests.get(url, stream=True, timeout=30) as r:
                r.raise_for_status()
                with open(dest, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
            time.sleep(delay)
            return fasta, True
        except Exception as e:
            warnings.warn(f"Retry {attempt+1} for {fasta} failed: {e}")
            time.sleep(delay)
    return fasta, False

# %%
def download_fasta_parallel(soup, url, output_dir, retries=3, delay=0.5, max_workers=8):
    """
    Parallel FASTA downloader with streaming and progress bar.
    """
    list_fastas = [link.get('href') for link in soup.find_all('a') if link.get('href').endswith('.fasta')]
    n_list = len(list_fastas)
    print(f"Downloading {n_list} protein sequences with {max_workers} threads:")

    error_list = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(download_single_fasta, fasta, url, output_dir, retries, delay): fasta
            for fasta in list_fastas
        }

        with tqdm(total=n_list, desc="Overall Progress", unit="file") as bar:
            for future in as_completed(futures):
                fasta, success = future.result()
                if not success:
                    error_list.append(fasta.replace(".fasta", ""))
                bar.update(1)

    print(f"{n_list - len(error_list)} successful downloads")
    if error_list:
        print(f"{len(error_list)} unsuccessful downloads:")
        print(','.join(error_list))

# %%
def main():
    args = parse_args()
    output_dir = args.output
    output_dir.mkdir(parents=True, exist_ok=True)

    # Download tables
    d_df = {}
    for bl_class in ['A', 'B1', 'B2', 'B3', 'C', 'D']:
        soup = read_html(f'{args.url}BLDB.php?prot={bl_class}')
        d_df[bl_class] = retrieve_table(soup)
        print(f'Class {bl_class}: {len(d_df[bl_class])} entries found')
    # Concat dataframes
    final_df = pd.concat(d_df.values(), ignore_index=True)

    # Save the final DataFrame to a CSV file
    output_file = output_dir / 'bldb_table.csv'
    final_df.to_csv(output_file, index=False)
    print(f"Table saved to {output_file}")

    # Download protein sequences
    soup = read_html(f'{args.url}seq_prot/')
    download_fasta_parallel(soup, f'{args.url}seq_prot/', output_dir, args.retries, args.delay)

    print("Download ended.")
    
# %%
if __name__ == "__main__":
    main()


