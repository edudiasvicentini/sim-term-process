import csv
import pandas as pd
import re
import os
from io import FileIO
import copy
from logging.handlers import RotatingFileHandler
import logging
import sys
from seaborn import light_palette
from weasyprint import HTML
from itertools import product
import numpy as np


abs_path = "C:/iot_sim_proc"


def to_pdf(file_name: str, html: str) -> str:
    """Recebe um nome de arquivo e uma representação em html
    para escrever um arquivo pdfi."""

    return HTML(string=html).write_pdf(file_name)


#def heatmap(df: pd.DataFrame, background_color: str, 
#        text_color: str, vmax: float, threshold: float, 
#        subset: list | None=None, axis: int | None=0) -> str:
#    """Recebe um DataFrame e retorna a representação em html
#    do background como um gradiente de cor"""
#
#    cm = sns.light_palette(background_color, as_cmap=True)
#    return df.style.background_gradient(cmap=cm, axis=axis, 
#            subset=subset, vmax=vmax).applymap(
#                    lambda x: f'background-color:green; color:{text_color};' 
#                    if x>threshold else None).render()

def color_header(df: pd.DataFrame, color: str) -> pd.DataFrame:
    """Recebe um dataframe e muda o style para ter css 
    com cabçalho colorido"""

    return df.style.set_table_styles(
            [{'selector': 'th',
                'props': [('background-color', color)]}]
            )
    

# ARQUIVOS

def get_key_ad(file_name: str) -> str:
    """Retorna a chave e adsortnacia dependendo do nome do arquivo."""
    
    rs = ['1R', '5R']
    ss = ['SS', 'CS']

    comb = product(rs, ss)

    r = [item for item in rs if item in file_name][0]
    s = [item for item in ss if item in file_name][0]
    adsorts = [0.3, 0.5, 0.7, 0.8, 0.9]
    for adsort in adsorts:
        adsort = str(adsort)
        if adsort in file_name: 
            return r+s, adsort


def get_file_names_dict(file_names: list) -> dict:
    """Retorna um dicionário com o nome dos arquivos e seu uso."""

    files_dict = dict()

    for each_file in file_names:
        key, adsort = get_key_ad(each_file)
        try:
            files_dict[key][adsort] = each_file
        except KeyError:
            files_dict[key] = dict()
            files_dict[key][adsort] = each_file

    return files_dict

def read_csv_to_dict_dfs(file_names_dict: dict, path: str = '') -> dict:
    """Recebe a lista de nomes e opcionalmete um caminho e le os arquivos
    csv para um dicionario de DataFrame."""

    dfs = dict()
    for adsort in file_names_dict:
        dfs[adsort] = pd.read_csv(os.path.join(path, file_names_dict[adsort]))
    
    return dfs

def get_rooms_cols(df: pd.DataFrame) -> list:
    """Recebe um DataFrame e retorna as colunas que são de comodos"""
   
    if isinstance(df.columns[0], tuple):
        return [header for header in df.columns if "Date/Time" 
            not in header[0] and "Drybulb" not in header[0]]
   
    return [header for header in df.columns if "Date/Time" 
            not in header and "Drybulb" not in header]

def create_df_agg(dict_dfs: dict, rooms_cols: list) -> pd.DataFrame:
    """Recebe o dicionário com todos os dataframes por adsortância
    e a lista de cols que se referem a cômodos. Retorna o dataframe
    agregando por comodo, todas as adsortâncias."""
    
    agg_dict = dict()
    for adsort in dict_dfs:
        cols = {room: (room, adsort) for room in rooms_cols}
        cols.update({col: (col, "SEASON") for col in dict_dfs[adsort] 
            if col not in rooms_cols})
        agg_dict.update(dict_dfs[adsort].rename(columns=cols).to_dict())
    
    return pd.DataFrame(agg_dict)


def get_temp_col(df: pd.DataFrame) -> pd.DataFrame:
    """Recebe dataframe e retorna coluna da temperatura
    pela keyword Drybulb"""

    for col in df.columns:
        if isinstance(col, tuple):
            for item in col:
                if 'drybulb' in item.lower():
                    return col
        elif "drybulb" in col.lower():
            return col

def get_time_col(df: pd.DataFrame) -> pd.DataFrame:
    """Recebe dataframe e retorna coluna da temperatura
    pela keyword Date/Time"""

    for col in df.columns:
        if isinstance(col, tuple):
            for item in col:
                if 'date/time' in item.lower():
                    return col
        elif "date/time" in col.lower():
            return col


def get_max_temp(df: pd.DataFrame) -> float:
    """Recebe um dataframe e retorna a temperatura maxima
    dele"""

    temp_col = get_temp_col(df)
    return float(df[temp_col].max())


def get_min_temp(df: pd.DataFrame) -> float:
    """Recebe um dataframe e retorna a temperatura minima
    dele"""

    temp_col = get_temp_col(df)
    return float(df[temp_col].min())


def get_df_seasons(df: pd.DataFrame) -> pd.DataFrame:
    """Recebe um dataframe e retorna dois dataframes, um para o verão
    e outro para o inverno."""
    
    size = int(len(df.index) / 2)
    df1 = df[:size].reset_index(drop=True)
    df2 = df[size:].reset_index(drop=True)

    df1_max = get_max_temp(df1)
    df2_max = get_max_temp(df2)
   
    if df1_max >= df2_max:
        df_ver = df1
        df_inv = df2
    else:
        df_ver = df2
        df_inv = df1

    return df_ver, df_inv

def replace_header_season(df: pd.DataFrame, season: str) -> pd.DataFrame:
    """Recebe um dataframe e uma string e substitui essa
    string em cabeçalhos que tiver 'season' no nome"""
    
    cols = {col[1]: season for col in df.columns 
            if 'SEASON' in col}
    
    return df.rename(columns=cols, level=1)


def drop_irrelevant_cols(df: pd.DataFrame, season: str) -> pd.DataFrame:
    """Recebe um dataframe e uma string e dropa as colunas 
    irrelevantes"""

    ver_cols = [col for col in df.columns if '_VER_' in col[0]]
    inv_cols = [col for col in df.columns if '_INV_' in col[0]]

    if season == 'Verão':
        return df.drop(inv_cols, axis=1)
    else:
        return df.drop(ver_cols, axis=1)


def replace_drop_header_dfs(df_ver: pd.DataFrame, df_inv: pd.DataFrame) -> pd.DataFrame:
    """Recebe os dois dataframes de verão e inverno e retorna
    a aplicação da fonte replace_header_season neles"""

    return (drop_irrelevant_cols(
                replace_header_season(df_ver, 'Verão'),
                'Verão'), 
            drop_irrelevant_cols( 
                replace_header_season(df_inv, 'Inverno'),
                'Inverno')
            )

def test_temp(temp: float, temp_obj: float, func_obj) -> bool: 
    """Recebe um valor e um valor objetivo e uma função de 
    comparação(min ou max).
    Se o valor retornado pela função for igual ao valor passado
    retorna True. Se não, retorna False."""
    return (temp == func_obj(temp, temp_obj) or 
            np.isnan(temp))
    

def fail_temps(df: pd.DataFrame, season="Verão") -> dict:
    """Recebe um dataframe agregado das adsortâncias e a estação
    e retorna um dicionario dos comodos e adsortâncias, como
    chave, e, como valor, o horário."""
   
    if season == "Verão":
        obj_temp = get_max_temp(df)
        obj_func = min
    else:
        obj_temp = get_min_temp(df) + 3
        obj_func = max
    
    time_col = get_time_col(df)
    room_cols = get_rooms_cols(df)
    fail_cols = dict()

    for header in room_cols:
        for i in df[header].index:
            if not test_temp(df[header][i], obj_temp, obj_func):
                fail_cols[header] = df[time_col][i]
   
    return fail_cols

