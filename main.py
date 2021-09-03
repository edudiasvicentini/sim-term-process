import pandas as pd
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
import matplotlib.pyplot as plt
from scipy import interpolate

abs_path = "C:/iot_sim_proc"
out_path = 'output'


def write_df(df: pd.DataFrame, file_name: str, writer: pd.ExcelWriter, sr_type: str, nrows: int) -> int:
    """Escreve os dataframes para um excel"""

    nome = pd.DataFrame([{'nome': sr_type}])
    nome.to_excel(writer, header=False, startrow=nrows, index=False)
    nrows += 1
    df.columns.to_frame().transpose().to_excel(writer, startrow=nrows)
    nrows += 1
    df.to_excel(writer,header=False,startrow=nrows)

    return len(df.index) + nrows + 2

def write_df_fails(df: pd.DataFrame, file_name: str, writer: pd.ExcelWriter, sr_type: str, nrows: int) -> int:
    
    nome = pd.DataFrame([{'nome': sr_type}])
    nome.to_excel(writer, header=False, startrow=nrows, index=False)
    nrows += 1
    df.columns.to_frame().transpose().to_excel(writer, startrow=nrows, header=False, index=False)
    nrows += 1
    df.to_excel(writer,header=False,startrow=nrows, index=False)

    return len(df.index) + nrows + 1

def to_pdf(file_name: str, html: str) -> str:
    """Recebe um nome de arquivo e uma representação em html
    para escrever um arquivo pdfi."""

    return HTML(string=html).write_pdf(file_name)


def heatmap(df: pd.DataFrame, background_color: str, 
        text_color: str, vmax: float, threshold: float, 
        subset: list, axis: int) -> str:
    """Recebe um DataFrame e retorna a representação em html
    do background como um gradiente de cor"""

    cm = sns.light_palette(background_color, as_cmap=True)
    return df.style.background_gradient(cmap=cm, axis=axis, 
            subset=subset, vmax=vmax).applymap(
                    lambda x: f'background-color:red; color:{text_color};' 
                    if x>threshold else None).render()

def color_header(df: pd.DataFrame, color: str) -> pd.DataFrame:
    """Recebe um dataframe e muda o style para ter css 
    com cabçalho colorido"""

    return df.style.set_table_styles(
            [{'selector': 'th',
                'props': [('background-color', color)]}]
            )

# Plot

#def plot_df(df: pd.DataFrame) -> plt.Figure
    

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
        cols = {room: (room.split(':')[0], adsort) for room in rooms_cols}
        cols.update({col: (col, "SEASON") for col in dict_dfs[adsort] 
            if col not in rooms_cols})
        agg_dict.update(dict_dfs[adsort].rename(columns=cols).to_dict())
   
    sorted_dict = sorted(agg_dict.items())
    
    return pd.DataFrame(dict(sorted_dict))


def get_temp_col(df: pd.DataFrame) -> pd.DataFrame:
    """Recebe dataframe e retorna coluna da temperatura
    pela keyword Drybulb"""
    
    room_cols = get_rooms_cols(df)
    possible_cols = [col for col in df.columns if col not in room_cols]
    for col in possible_cols:
        if isinstance(col, tuple):
            for item in col:
                if 'drybulb' in item.lower():
                    return col
        elif "drybulb" in col.lower():
            return col

def get_time_col(df: pd.DataFrame) -> pd.DataFrame:
    """Recebe dataframe e retorna coluna da temperatura
    pela keyword Date/Time"""

    room_cols = get_rooms_cols(df)
    possible_cols = [col for col in df.columns if col not in room_cols]
    for col in possible_cols:
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

def get_dfs_replaced_droped(df: pd.DataFrame) -> pd.DataFrame:
    """Recebe um dataframe e retorna os dois dataframes por
    season."""

    df_ver, df_inv = get_df_seasons(df)
    return replace_drop_header_dfs(df_ver, df_inv)


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
                try:
                    fail_cols[header].append(df[time_col][i])
                    fail_cols[header] = sorted(fail_cols[header])
                except KeyError:
                    fail_cols[header] = [df[time_col][i]]
    
    return fail_cols


def process_fail_temps(fail_cols: dict) -> pd.DataFrame:
    """Recebe o dicionários com as temperaturas falhas e
    retorna o data_frame dos problemas"""
   
    fail_cols_procs = list()
    hours = set()

    for header in fail_cols:
        hours.update(fail_cols[header])
    
    hours = sorted(hours)
    for hour in hours:
        fail_cols_proc = dict()
        fail_cols_proc['horario'] = hour
        fail_cols_procs.append(copy.deepcopy(fail_cols_proc))
    
    for header in fail_cols:
        for hour in fail_cols[header]:
            for dictionary in fail_cols_procs:
                if hour == dictionary['horario']:
                    try:
                        dictionary[header[0]] += f", {header[1]}"
                    except KeyError:
                        dictionary[header[0]] = f"{header[1]}"
   
    return pd.DataFrame(fail_cols_procs)


def set_logging(logs_path: str):
    logFormatter = logging.Formatter(
        "%(asctime)s [%(levelname)-5.5s]  %(message)s")

    rootLogger = logging.getLogger()

    fileHandler = logging.FileHandler(logs_path)
    fileHandler.setFormatter(logFormatter)
    rootLogger.addHandler(fileHandler)

    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    rootLogger.addHandler(consoleHandler)
    rootLogger.setLevel(logging.INFO)
    
    size_log = os.path.getsize(logs_path)
    if size_log < 50*1024:
        sys.stderr = open(logs_path, 'a')
    else:
        sys.stderr = open(logs_path, 'w')
    


def main():  
    path_sim_folder = os.path.join(abs_path, "sim")
    
    logs_path = os.path.join(abs_path, 'sim_term.log')
    set_logging(logs_path)

    try:
        file_names_list = os.listdir(path_sim_folder)
    except FileNotFoundError:
        raise FileNotFoundError(f"A pasta {path_sim_folder} não foi encontrada.\
            Você precisa criar ela e subir os 6 csv da simulação em uma subpasta com nome de sim")
    

    file_names_dict = get_file_names_dict(file_names_list)
    

    writer_ver = pd.ExcelWriter(os.path.join(abs_path, out_path, "sim_ver.xlsx")
            , engine='xlsxwriter')
    writer_inv = pd.ExcelWriter(os.path.join(abs_path, out_path, "sim_inv.xlsx")
            , engine='xlsxwriter')
    writer_ver_fails = pd.ExcelWriter(os.path.join(abs_path, out_path, "fails_ver.xlsx")
            , engine='xlsxwriter')
    writer_inv_fails = pd.ExcelWriter(os.path.join(abs_path, out_path, "fails_inv.xlsx")
            , engine='xlsxwriter')
    nrows_ver = 0
    nrows_inv = 0
    nrows_ver_fails = 0
    nrows_inv_fails = 0
    for sr_type in file_names_dict:
        logging.info(f"Lendo {sr_type}")

        dict_dfs = read_csv_to_dict_dfs(file_names_dict[sr_type], path_sim_folder)
        rooms_cols = get_rooms_cols(dict_dfs[list(dict_dfs.keys())[0]])
        df_agg = create_df_agg(dict_dfs, rooms_cols)
        df_ver, df_inv = get_dfs_replaced_droped(df_agg)

        nrows_ver = write_df(df_ver, 'sim_ver', writer_ver, sr_type, nrows_ver)
        nrows_inv = write_df(df_inv, 'sim_inv', writer_inv, sr_type, nrows_inv)
       
        fail_cols_ver = fail_temps(df_ver, season="Verão")
        fail_cols_inv = fail_temps(df_inv, season="Inverno")
        df_ver_fails = process_fail_temps(fail_cols_ver)
        df_inv_fails = process_fail_temps(fail_cols_inv)
        nrows_ver_fails = write_df_fails(df_ver_fails, 'fails_ver', writer_ver_fails, sr_type, nrows_ver_fails)
        nrows_inv_fails = write_df_fails(df_inv_fails, 'fails_inv', writer_inv_fails, sr_type, nrows_inv_fails)
        #df_ver.to_excel(os.path.join(abs_path, out_path, f'{sr_type}_ver.xlsx'), merge_cells=True)
        #df_inv.to_excel(os.path.join(abs_path, out_path, f'{sr_type}_inv.xlsx'))
        #to_pdf(os.path.join(abs_path, out_path, f'sr_type_ver.pdf'), df_ver.to_html())
        
        temp_col = get_temp_col(df_ver)
        df_ver.index += 1
        for col in df_ver.columns:
            x = range(1, 25)
            x_interp = np.arange(1, 25, 0.1)
            
            for ad in df_ver[col[0]].columns: 
                y = df_ver[col[0]][ad].values
                tck = interpolate.splrep(x, y, s=0)
                y_interp = interpolate.splev(x_interp, tck, der=0)
                plt.plot(x, y, 'o', x_interp, y_interp, label=f"{ad}")

            #df_ver[col[0]].plot(legend=True)
            y = df_ver[temp_col].values
            tck = interpolate.splrep(x, y, s=0)
            y_interp = interpolate.splev(x_interp, tck, der=0)
            plt.plot(x, y, 'o', x_interp, y_interp, label="Drybulb")

            #df_ver[temp_col].plot(legend=True, label='Drybulb')
            
            max_temp = get_max_temp(df_ver)
            plt.plot(range(1, 25), [max_temp]*24, label="Max Temp")
            
            plt.ylabel("Temperatura (ºC)")
            plt.xlabel("Hora")
            plt.title(f"{sr_type} {col[0]} verão")
            plt.show()
            break
        break

        


    writer_ver.save()
    writer_ver.close()
    writer_inv.save()
    writer_inv.close()
    writer_ver_fails.save()
    writer_ver_fails.close()
    writer_inv_fails.save()
    writer_inv_fails.close()
    sys.stderr.close()
    logging.info("Fim")



if __name__ == '__main__':
    main()
