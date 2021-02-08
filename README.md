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

## Post dataset to MySQL in AWS

### Clean the old table in database
Before post new dataset to database, please make sure the corresponding table in the database is fully wiped out. 
This can be operated with the help of django **dbshell** tools.
In the following commnand:
replace <table-name> with _disclosure_disclosure_
replace <app-name> with _disclosure_

drop the old table in database
```console
python manage.py dbshell
drop table <table-name>
```
recreate an empty table through django, note the following command is not in the dbshell
```console
rm -r <app-name>/migrations/ 
python manage.py makemigrations <app-name> 
python manage.py sqlmigrate <app-name> 0001_initial
```
Copy the command in the terminal, restart the dbshell if was closed in previous step
```console
python manage.py dbshell
```
Past the command to recreate the table in database

### Post processed csv file to the target table in database
In postBydftoSQL.py file, fill in with correct username and password

```console
python postBydftoSQL.py
```

