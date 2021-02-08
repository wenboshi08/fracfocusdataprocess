import pandas as pd
import numpy as np
from sqlalchemy import create_engine

# connect to local sqllite Database
# connect engine input format https://docs.sqlalchemy.org/en/14/core/engines.html
username = "****"
password = "****"
# RDS host address can be used to be looked up at our aws account
host = "djangodatabase.ckgqvtxdjqra.us-east-1.rds.amazonaws.com"
port = "3306"
databasename = "djangodatabase"
mysql_instance = "mysql://" + username + ":" + password + "@" + host + ":" + port + "/" + databasename
engine = create_engine(mysql_instance)
conn = engine.connect()

dir = ''
file = 'fullFracFocus_joined_correctedcas_addedmatchflag_chemcascorrected_addedwelldepth.csv'

df = pd.read_csv(dir + file)
df = df.replace({np.nan: None})
df = df.drop(columns=['ID'])
print(df.columns)
df.columns = ["upload_key",
            "job_start_date",
            "job_end_date",
            "api_number",
            "state_number",
            "county_number",
            "operator_name",
            "well_name",
            "latitude",
            "longitude",
            "projection",
            "tvd",
            "total_base_water_volume",
            "total_base_nonwater_volume",
            "state_name",
            "county_name",
            "ff_version",
            "federal_well",
            "indian_well",
            "source",
            "dtmod",
            "purpose_key",
            "trade_name",
            "supplier",
            "purpose",
            "system_approach",
            "is_water",
            "purpose_percent_hf_job",
            "purpose_ingredient_msds",
            "ingredient_key",
            "ingredient_name",
            "cas_number",
            "percent_high_additive",
            "percent_hf_job",
            "ingredient_comment",
            "ingredient_msds",
            "mass_ingredient",
            "claimant_company",
            "disclosure_key",
            "basin",
            "chloride_mean",
            "chloride_std",
            "pH_mean",
            "pH_std",
            "bromide_mean",
            "bromide_std",
            "iodide_mean",
            "iodide_std",
            "temperature_mean",
            "temperature_std",
            "cas_number_corrected",
            "cas_chem_match",
            "chem_cas_corrected",
            "well_depth"]
n = df.size
# here can write to sql partially or entirely by changing the input of range()
for i in range(1):
    print(i)
    cur_df = df[n//1000*i: n//1000*(i+1)]
    # # write the dataframe to SQL
    cur_df.to_sql('disclosure_disclosure', conn, index=False, if_exists='append')
    print('done')
    # print(engine.execute("SELECT COUNT(*) FROM disclosure_disclosure ").fetchall())