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


