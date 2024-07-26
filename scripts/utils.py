import yaml
import numpy as np
import pandas as pd
import seaborn as sns


def load_config():
    with open("config.yml", "r") as ymlfile:
        cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)

    sns.set(**cfg["general_plotting"])
    return cfg


def load_tom_data(filename: str):
     df =  pd.read_csv(filename, sep=";", encoding="unicode_escape").dropna(axis=1)
     return df


def filter_data_tom_flask(df: pd.DataFrame, flask: str, offset: float = 0.0):
    
    df_out = df[df.columns[df.columns.str.contains(flask)]]
    df_out["Time [h]"] = None
    df_out["Time [h]"] = df[df.columns[0]] + offset
    
    df_out.columns = [str(col).replace(flask, "") for col in df_out.columns]
    df_out.columns = [str(col).replace("(", "[") for col in df_out.columns]
    df_out.columns = [str(col).replace(")", "]") for col in df_out.columns]
    
    return df_out

def filter_values(x: np.array, min_distance: float):
    delta = x[1:] - x[:-1]
    return np.concatenate([x[0:1], x[1:][delta >= min_distance]])


def convert_slope_to_CTR(slope, v_molar=25.45, v_liquid=50, v_headspace=530):
    """ 
    Assumes that
    -v_molar is in L/mol
    -v_liquid is in mL
    -v_headspace is in mL
    -slope is in %CO2/h
    """
    
    slope_in_fraction = slope / 100   # convert %CO2 into mole fraction of CO2
    
    return slope_in_fraction * (1 /v_molar) * (v_headspace/v_liquid) * 1000