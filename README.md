# BLDB_download

Python script to programmatically download all protein sequences at [BLDB](http://www.bldb.eu/).

## Usage
```
usage: bldb_download.py [-h] [-u URL] [-r RETRIES] -o OUTPUT

Programmatic download of all protein sequences from BLDB.

options:
  -h, --help            show this help message and exit
  -u, --url             Parent URL of proteins. Modify in case it has changed. Default: http://www.bldb.eu/seq_prot/
  -r, --retries         Number of download retries if connection error. Default: 3
  -o, --output          Required. Final output directory
```

If you use BLDB please cite: Naas, T.; Oueslati, S.; Bonnin, R. A.; Dabos, M. L.; Zavala, A.; Dortet, L.; Retailleau, P.; Iorga, B. I., Beta-Lactamase DataBase (BLDB) – Structure and Function. J. Enzyme Inhib. Med. Chem. 2017, 32, 917-919. https://doi.org/10.1080/14756366.2017.1344235
