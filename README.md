# BLDB_download

Python script to programmatically download all protein sequences and tables at [BLDB](http://www.bldb.eu/).

## Usage
```
usage: bldb_download.py [-h] [-u URL] [-r RETRIES] [-d DELAY] -o OUTPUT

Programmatic download of all protein sequences from BLDB.

options:
  -h, --help            show this help message and exit
  -u URL, --url URL     Parent URL of proteins. Default: http://www.bldb.eu/
  -r RETRIES, --retries RETRIES
                        Number of download retries if connection error
  -d DELAY, --delay DELAY
                        Seconds of delay between downloads. Default: 0
  -o OUTPUT, --output OUTPUT
                        Required. Final output directory

```

If you use BLDB please cite: Naas, T.; Oueslati, S.; Bonnin, R. A.; Dabos, M. L.; Zavala, A.; Dortet, L.; Retailleau, P.; Iorga, B. I., Beta-Lactamase DataBase (BLDB) – Structure and Function. J. Enzyme Inhib. Med. Chem. 2017, 32, 917-919. https://doi.org/10.1080/14756366.2017.1344235
