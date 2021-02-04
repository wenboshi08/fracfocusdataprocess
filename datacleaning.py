import pandas as pd
import numpy as np
from scipy.spatial import cKDTree
import statistics
import re
import json

def combine_facfoucs():
    filepaths = ['FracFocusData/FracFocusRegistry_' + str(i) + '.csv' for i in range(1, 21)]
    df = pd.concat(map(pd.read_csv, filepaths))
    df.to_csv('fullFracFocus.csv', index=False)
    return df

def get_distinct_well(full_frac):
    FF1 = full_frac
    FF2 = FF1[pd.notnull(FF1['CASNumber'])]
    FF3 = FF2[FF2['IngredientName'].str.len() > 2]
    FF4 = FF3[FF3['Latitude'].apply(lambda x: 25 < x < 49) & FF3['Longitude'].apply(lambda x: -125 < x < -67)]
    FF5 = FF4[['UploadKey', 'Latitude', 'Longitude', 'JobStartDate', 'JobEndDate',
               'WellName', 'Projection', 'TotalBaseWaterVolume', 'StateName',
               'CountyName', 'OperatorName']].drop_duplicates()
    wells = FF5.reset_index(drop=True)
    wells.to_csv('distinct_wells.csv', index=False)
    return wells

def get_usgs(filename):
    usgs = pd.read_csv(filename)
    usgs = usgs[['LATITUDE', 'LONGITUDE', 'BASIN', 'Cl', 'PH', 'Br', 'I']]
    usgs.columns = ['Latitude', 'Longitude', 'Basin', 'Cl', 'pH', 'Br', 'I']
    usgs = usgs[pd.notnull(usgs['Latitude']) & pd.notnull(usgs['Longitude'])]
    return usgs.reset_index(drop=True)

def get_ngds(filename):
    ngds = pd.read_csv(filename)
    ngds = ngds[['latitude', 'longitude', 'bht']]
    ngds = ngds[pd.notnull(ngds['bht'])]
    ngds.columns = ['Latitude', 'Longitude', 'T']
    return ngds.reset_index(drop=True)

def ckdnearest(wells, geodata, new_columns, k):
    nA = np.array(list(zip(wells.Latitude, wells.Longitude)))
    nB = np.array(list(zip(wells.Latitude, geodata.Longitude)))
    for new_c in new_columns:
        if new_c == 'Basin':
            wells[new_c] = None
        else:
            wells[new_c + '_mean'] = None
            wells[new_c + '_std'] = None
    btree = cKDTree(nB)
    dist, idx = btree.query(nA, k)
    for i in range(len(nA)):
        row_list_b = idx[i]
        for new_c in new_columns:
            if new_c == 'Basin':
                options = [geodata[new_c].loc[x] for x in row_list_b]
                wells[new_c].loc[i] = statistics.mode(options)
            else:
                wells[new_c + '_mean'].loc[i] = np.nanmean([geodata[new_c].loc[x] for x in row_list_b])
                wells[new_c + '_std'].loc[i] = np.nanstd([geodata[new_c].loc[x] for x in row_list_b])
        if i % 10000 == 0:
            print(i)
    return wells

def add_basin_cl(wells, usgs):
    result = ckdnearest(wells, usgs, ['Basin', 'Cl'], 10)
    result.to_csv('added_Basin_Cl.csv', index=False)
    return result

def add_ph(wells, usgs):
    result = ckdnearest(wells, usgs, ['pH'], 20)
    result.to_csv('added_Basin_Cl_pH.csv', index=False)
    return result

def add_Br_I(wells, usgs):
    basin = usgs.groupby(['Basin']).agg({'Basin': 'size',
                                         'Cl': [np.nanmean, np.nanstd],
                                         'pH': [np.nanmean, np.nanstd],
                                         'Br': [np.nanmean, np.nanstd],
                                         'I': [np.nanmean, np.nanstd]})
    basin.columns = ['_'.join(tup).rstrip('_') for tup in basin.columns.values]
    new_columns = ['Br_mean', 'Br_std', 'I_mean', 'I_std']
    for new_c in new_columns:
        wells[new_c] = None
    total_rows = len(wells)
    for i in range(total_rows):
        current_basin = wells['Basin'].loc[i]
        wells['Br_mean'].loc[i] = basin['Br_nanmean'].loc[current_basin]
        wells['Br_std'].loc[i] = basin['Br_nanstd'].loc[current_basin]
        wells['I_mean'].loc[i] = basin['I_nanmean'].loc[current_basin]
        wells['I_std'].loc[i] = basin['I_nanstd'].loc[current_basin]
        if pd.isnull(wells['Cl_mean'].loc[i]):
            wells['Cl_mean'].loc[i] = basin['Cl_nanmean'].loc[current_basin]
            wells['Cl_std'].loc[i] = basin['Cl_nanmean'].loc[current_basin]
        if pd.isnull(wells['pH_mean'].loc[i]):
            wells['pH_mean'].loc[i] = basin['pH_nanmean'].loc[current_basin]
            wells['pH_std'].loc[i] = basin['pH_nanstd'].loc[current_basin]
        if i % 1000 == 0:
            print(i)
    wells.to_csv('added_Basin_Cl_pH_Br_I.csv', index=False)
    return wells

def add_T(wells, ngds):
    result = ckdnearest(wells, ngds, ['T'], 10)
    result.to_csv('added_Basin_Cl_pH_Br_I_T.csv', index=False)
    return result


def join_frac_well():
    frac = pd.read_csv('fullFracFocus.csv')
    well = pd.read_csv('added_Basin_Cl_pH_Br_I_T.csv')
    frac = frac[pd.notnull(frac['CASNumber'])]
    frac = frac[frac['IngredientName'].str.len() > 2]
    frac = frac[frac['CASNumber'].apply(lambda x: bool(re.match('\d{2,7}-\d{2}-\d', x)))]
    joined = pd.merge(frac, well, on=['UploadKey', 'Latitude', 'Longitude', 'JobStartDate', 'JobEndDate',
                                      'WellName', 'Projection', 'TotalBaseWaterVolume', 'StateName',
                                      'CountyName', 'OperatorName'], how='left')
    joined = joined.reset_index(drop=True)
    joined.insert(0, 'ID', range(0, len(joined)))
    for i in joined.columns:
        joined[i] = joined[i].astype(str)
    joined.to_csv('fullFracFocus_joined.csv', index=False)

def correct_cas():
    df = pd.read_csv('fullFracFocus_joined.csv')
    def remove_zero(x):
        parts = x.split('-')
        head = parts[0]
        new_head = head[:-1].lstrip('0') + head[-1]
        parts[0] = new_head
        tail = parts[-1]
        new_tail = tail.rstrip()
        parts[-1] = new_tail
        return '-'.join(parts)

    df["CASNumber_corrected"] = df["CASNumber"].apply(lambda x: remove_zero(x))
    df.to_csv('fullFracFocus_joined_correctedcas.csv', index=False)

def add_match():
    with open('casListToChem.json') as f:
        casListToChem = json.load(f)

    # change the value from a list to set
    # speed the look up time
    casListToChemSet = {}
    for key, value in casListToChem.items():
        casListToChemSet[key] = set(value)

    df = pd.read_csv('fullFracFocus_joined_correctedcas.csv')
    # preset the new column to False
    df['Cas_Chem_Match'] = False

    # iterate the rows in dataframe and check if valid or not
    for index, row in df.iterrows():
        cas = row['CASNumber_corrected']
        chem_name = row['IngredientName']
        if cas in casListToChemSet:
            if chem_name in casListToChemSet[cas]:
                df.at[index, 'Cas_Chem_Match'] = True
        # if index % 10000 == 0:
        #     print(index)
    df.to_csv('fullFracFocus_joined_correctedcas_addedmatchflag.csv', index=False)

def add_chemcascorrected():
    df = pd.read_csv('fullFracFocus_joined_correctedcas_addedmatchflag.csv')

    with open('chemToCas.json') as f:
        ChemToCas = json.load(f)

    df['Chem_Cas_Corrected'] = False

    # iterate the rows in dataframe and check if valid or not
    for index, row in df.iterrows():
        cas = row['CASNumber_corrected']
        chem_name = row['IngredientName']
        if chem_name in ChemToCas:
            if cas != ChemToCas[chem_name]:
                df.at[index, 'CASNumber_corrected'] = ChemToCas[chem_name]
                df.at[index, 'Chem_Cas_Corrected'] = True
        # if index % 10000 == 0:
        #     print(index)

    df.to_csv('fullFracFocus_joined_correctedcas_addedmatchflag_chemcascorrected.csv', index=False)

def add_depth():
    wells_df = pd.read_csv('core.surface_site_county_state_materialized_view.csv')
    wells_depth_df = wells_df[['api', 'depth']].dropna()
    wells_depth_df.columns = ['APINumber', 'WellDepth']
    wells_depth_df['APINumber'] = wells_depth_df['APINumber'].astype(str)
    df = pd.read_csv('fullFracFocus_joined_correctedcas_addedmatchflag_chemcascorrected.csv')
    df['APINumber'] = df['APINumber'].astype(str)
    joined_df = df.join(wells_depth_df.set_index('APINumber'), on='APINumber')
    joined_df.to_csv('fullFracFocus_joined_correctedcas_addedmatchflag_chemcascorrected_addedwelldepth.csv',
                     index=False)

def run():
    full_frac = combine_facfoucs()
    wells = get_distinct_well(full_frac)
    usgs = get_usgs('USGSPWDBv2.3n.csv')
    ngds = get_ngds('core.surface_site_county_state_materialized_view.csv')
    wells = add_basin_cl(wells, usgs)
    wells = add_ph(wells, usgs)
    wells = add_Br_I(wells, usgs)
    wells = add_T(wells, ngds)
    join_frac_well()
    correct_cas()
    add_match()
    add_chemcascorrected()
    add_depth()

if __name__ == "__main__":
    run()
