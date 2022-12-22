# fm-tactic-downloader
Scripts for downloading tactics from FMBase's Tactic tester.

## Requirements

` pip install selenium pandas requests `

Our selenium script uses a Firefox browser, so make sure to have it installed.

## Usage
First, we scrape the given page from FMBase:
```
python get_tactic_links.py --link 'https://beta.fm-base.co.uk/tactics' --output './tactics/current_version/tactics.txt'
```

This will create a ``tactics.txt`` text file with links to all tactics listed. Next, we obtain the metadata file ``metadata.csv`` via
```
 python get_tactic_metadata.py --input './tactics/current_version/tactics.txt' --output './tactics/current_version/metadata.csv'
```
While creating the metadata, the selenium script visits each tactic page sequentially, so it is very slow (~30 minutes on my PC). Moreover, the scripts above might break if the FMBase website layout changes. As a result, we provide the metadata files in the ``tactics`` folder of this repo.

Once the metadata is created, it is enough to execute
```
  python download_tactics.py --input './tactics/current_version/metadata.csv'--output './tactics/current_version'
```
This script runs faster because it makes up to 40 download requests in parallel. Downloads will be saved in ``` './tactics/current_version/downloads' ``` in this case.
