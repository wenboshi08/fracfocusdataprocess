# fracfocusdataprocess

## Download Source Data

### Fracfous
https://www.fracfocus.org/index.php?p=data-download
"Download CSV Data", then unzip the zip file to a folder "FracFocusData"

### USGS National Produced Waters Geochemical Database
https://www.sciencebase.gov/catalog/item/59d25d63e4b05fe04cc235f9, download "USGSPWDBv2.3n.csv"

### NGDS Well temperature data
http://geothermal.smu.edu/static/DownloadFilesButtonPage.htm, download "Aggregated Well Data" csv

## Create virtual environment
* create myenv virtual environment
```console
python3 -m venv myenv
```
* activate the virtual environment
```console
source myenv/bin/activate
```
* install dependencies
```console
pip install -r requirements.txt
```

## Run the program
```console
python datacleaning.py
```

## Final dataset
The final dataset should be 
**fullFracFocus_joined_correctedcas_addedmatchflag_chemcascorrected_addedwelldepth.csv**


