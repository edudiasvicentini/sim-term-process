import unittest
import os
import pandas as pd
import main as target


class ListaArquivosTestCase(unittest.TestCase):
    
    def setUp(self):
        self.file_names = [
        'Morumbi R12-0.3 1R CS.csv',
        'Morumbi R12-0.3 1R SS.csv',
        'Morumbi R12-0.3 5R CS.csv',
        'Morumbi R12-0.3 5R SS.csv',
        'Morumbi R12-0.5 1R CS.csv',
        'Morumbi R12-0.5 1R SS.csv',
        'Morumbi R12-0.5 5R CS.csv',
        'Morumbi R12-0.5 5R SS.csv',
        'Morumbi R12-0.7 1R CS.csv',
        'Morumbi R12-0.7 1R SS.csv',
        'Morumbi R12-0.7 5R CS.csv',
        'Morumbi R12-0.7 5R SS.csv',
        'Morumbi R12-0.8 1R CS.csv',
        'Morumbi R12-0.8 1R SS.csv',
        'Morumbi R12-0.8 5R CS.csv',
        'Morumbi R12-0.8 5R SS.csv',
        'Morumbi R12-0.9 1R CS.csv',
        'Morumbi R12-0.9 1R SS.csv',
        'Morumbi R12-0.9 5R CS.csv',
        'Morumbi R12-0.9 5R SS.csv'
        ]


    def test_get_key_07_1R_CS(self):
        key, adsort = target.get_key_ad("Teste r0.7 1R CS.csv")
        self.assertEqual(adsort, "0.7")
        self.assertEqual(key, '1RCS')

    def test_get_file_names_dict(self):
        file_names_dict = target.get_file_names_dict(self.file_names)['1RSS'] 
        test_files = {
                '0.3': 'Morumbi R12-0.3 1R SS.csv', '0.5': 'Morumbi R12-0.5 1R SS.csv',
                '0.7': 'Morumbi R12-0.7 1R SS.csv', '0.8': 'Morumbi R12-0.8 1R SS.csv', 
                '0.9': 'Morumbi R12-0.9 1R SS.csv',
                }
        self.assertEqual(file_names_dict, test_files)

class LeArquivosTestCase(unittest.TestCase):
    
    def setUp(self):
        self.file_path = os.path.join(os.path.dirname(__file__), 'test_files', 'Outputs Sim')
        self.file_names_dict = {
                '0.3': 'Morumbi R12-0.3 1R SS.csv', '0.5': 'Morumbi R12-0.5 1R SS.csv',
                '0.7': 'Morumbi R12-0.7 1R SS.csv', '0.8': 'Morumbi R12-0.8 1R SS.csv', 
                '0.9': 'Morumbi R12-0.9 1R SS.csv',
                }

    def test_read_csv_to_dict_dfs(self):
        dfs_dict = target.read_csv_to_dict_dfs(self.file_names_dict, self.file_path)
        df_dict_03 = pd.read_csv(os.path.join(self.file_path, 'Morumbi R12-0.3 1R CS.csv'))
        pd.testing.assert_frame_equal(df_dict_03, dfs_dict['0.3'])

class CriaDataFrameUnicoTestCase(unittest.TestCase):

    def setUp(self):
        self.df = pd.DataFrame([
            {"Date/Time": "01/01  01:00:00" ,"Drybulb temp":20.0, "T2_P2_AP1_QUARTO 1": 30.0},
            {"Date/Time": "01/01  02:00:00" ,"Drybulb temp":30.1, "T2_P2_AP1_SALA 1": 21.0},
            {"Date/Time": "01/01  03:00:00" ,"Drybulb temp":23.28, "T2_P2_AP1_QUARTO 2": 22.0},
            {"Date/Time": "01/01  04:00:00" ,"Drybulb temp":21.1, "T2_P2_AP2_QUARTO 1": 20.0},
            {"Date/Time": "01/01  05:00:00" ,"Drybulb temp":22.1, "T2_P2_AP2_QUARTO 2": 30.0},
            {"Date/Time": "01/01  06:00:00" ,"Drybulb temp":23.1, "T2_P2_AP2_SALA 1": 26.0},
            ])

        self.df_agg = pd.DataFrame(pd.DataFrame([{('T2_P2', 0.3): 1}]).to_dict())
        self.df_des = pd.DataFrame([{"T2_P2": 1}])

    def test_get_rooms_cols(self):
        test_cols = ["T2_P2_AP1_QUARTO 1",
                "T2_P2_AP1_SALA 1", "T2_P2_AP1_QUARTO 2",
                "T2_P2_AP2_SALA 1", "T2_P2_AP2_QUARTO 1",
                "T2_P2_AP2_QUARTO 2"]

        cols = target.get_rooms_cols(self.df)
        self.assertCountEqual(test_cols, cols)

    def test_create_df_agg(self):
        df_agg_t = target.create_df_agg({0.3: self.df_des}, ["T2_P2"])
        pd.testing.assert_frame_equal(df_agg_t, self.df_agg)

    def test_create_df_agg_complex(self):
        headers = [('Date/Time', 'SEASON'), 
                ('Drybulb temp', 'SEASON'), 
                ('T2_P2_AP1_QUARTO 1', 0.3), 
                ('T2_P2_AP1_SALA 1', 0.3), 
                ('T2_P2_AP1_QUARTO 2', 0.3), 
                ('T2_P2_AP2_QUARTO 1', 0.3), 
                ('T2_P2_AP2_QUARTO 2', 0.3), 
                ('T2_P2_AP2_SALA 1', 0.3), 
                ('T2_P2_AP1_QUARTO 1', 0.5), 
                ('T2_P2_AP1_SALA 1', 0.5), 
                ('T2_P2_AP1_QUARTO 2', 0.5), 
                ('T2_P2_AP2_QUARTO 1', 0.5), 
                ('T2_P2_AP2_QUARTO 2', 0.5), 
                ('T2_P2_AP2_SALA 1', 0.5)]
        df_agg_t = target.create_df_agg({0.3: self.df,
            0.5: self.df}, target.get_rooms_cols(self.df))
        self.assertCountEqual([i for i in df_agg_t.columns], headers)

class DivideDataFramesPorEstacaoTestCase(unittest.TestCase):

    def setUp(self):
        self.file_path = os.path.join(os.path.dirname(__file__), 'test_files', 'Outputs Sim')

        self.df = pd.DataFrame([
            {"Date/Time": "01/01  01:00:00" ,"Drybulb temp":20.0, "AP1_INV_QUARTO 1": 30.0, "AP1_INV_SALA 1": 22.0},
            {"Date/Time": "01/01  02:00:00" ,"Drybulb temp":30.1, "AP1_INV_QUARTO 1": 30.0, "AP1_INV_SALA 1": 21.0},
            {"Date/Time": "01/01  03:00:00" ,"Drybulb temp":23.28,"AP1_INV_QUARTO 1": 22.0, "AP1_INV_SALA 1": 22.0},
            {"Date/Time": "01/01  04:00:00" ,"Drybulb temp":21.1, "AP1_VER_QUARTO 1": 10.0, "AP1_VER_SALA 1": 21.0},
            {"Date/Time": "01/01  05:00:00" ,"Drybulb temp":22.1, "AP1_VER_QUARTO 1": 12.0, "AP1_VER_SALA 1": 22.0},
            {"Date/Time": "01/01  06:00:00" ,"Drybulb temp":23.1, "AP1_VER_QUARTO 1": 16.0, "AP1_VER_SALA 1": 21.0},
            ])

        self.df_dict = {0.3:self.df, 0.5:self.df}
        self.df_agg = target.create_df_agg(self.df_dict, target.get_rooms_cols(self.df))

        self.df_csv = pd.read_csv(os.path.join(self.file_path, 'Morumbi R12-0.3 1R CS.csv'))

    def test_get_temp_col(self):
        col = "Drybulb temp"
        col_t = target.get_temp_col(self.df)
        self.assertEqual(col, col_t)

    def test_get_max_temp(self):
        temp = 30.1
        temp_t = target.get_max_temp(self.df)
        self.assertEqual(temp, temp_t)

    def test_divide_df_by_season(self):
        df_ver, df_inv = target.get_df_seasons(self.df_agg)
        pd.testing.assert_frame_equal(df_ver, self.df_agg[0:3])
        self.assertCountEqual([i for i in df_inv.columns],
                [i for i in self.df_agg.columns])

    def test_divide_df_by_season_reverse(self):
        df_agg = self.df_agg.iloc[::-1].reset_index(drop=True)
        df_ver, df_inv = target.get_df_seasons(df_agg)
        pd.testing.assert_frame_equal(df_ver, df_agg[3:].reset_index(drop=True))
        self.assertCountEqual(df_ver["Drybulb temp"], self.df_agg[0:3]["Drybulb temp"])

    def test_replace_header_season_ver(self):
        headers = [
                ('Date/Time', 'Verão'), 
                ('Drybulb temp', 'Verão'), 
                ('AP1_INV_QUARTO 1', 0.3), 
                ('AP1_VER_QUARTO 1', 0.3), 
                ('AP1_INV_SALA 1', 0.3), 
                ('AP1_VER_SALA 1', 0.3), 
                ('AP1_INV_QUARTO 1', 0.5), 
                ('AP1_VER_QUARTO 1', 0.5), 
                ('AP1_INV_SALA 1', 0.5), 
                ('AP1_VER_SALA 1', 0.5), 
                ]
        df_ver, df_inv = target.get_df_seasons(self.df_agg)
        df_t = target.replace_header_season(df_ver, 'Verão')
        headers_t = df_t.columns.to_list()
        self.assertCountEqual(headers, headers_t)


    def test_replace_header_season_inv(self):
        headers = [
                ('Date/Time', 'Inverno'), 
                ('Drybulb temp', 'Inverno'), 
                ('AP1_INV_QUARTO 1', 0.3), 
                ('AP1_VER_QUARTO 1', 0.3), 
                ('AP1_INV_SALA 1', 0.3), 
                ('AP1_VER_SALA 1', 0.3), 
                ('AP1_INV_QUARTO 1', 0.5), 
                ('AP1_VER_QUARTO 1', 0.5), 
                ('AP1_INV_SALA 1', 0.5), 
                ('AP1_VER_SALA 1', 0.5), 
                ]
        df_ver, df_inv = target.get_df_seasons(self.df_agg)
        df_t = target.replace_header_season(df_inv, 'Inverno')
        headers_t = df_t.columns.to_list()
        self.assertCountEqual(headers, headers_t)
    

    def test_drop_irrelevant_cols(self):
        headers = [
                ('Date/Time', 'Inverno'), 
                ('Drybulb temp', 'Inverno'), 
                ('AP1_INV_QUARTO 1', 0.3), 
                ('AP1_INV_SALA 1', 0.3), 
                ('AP1_INV_QUARTO 1', 0.5), 
                ('AP1_INV_SALA 1', 0.5), 
                ]
        df_ver, df_inv = target.get_df_seasons(self.df_agg)
        df_r = target.replace_header_season(df_inv, 'Inverno')
        df_t = target.drop_irrelevant_cols(df_r, 'Inverno')
        headers_t = df_t.columns.to_list()
        self.assertCountEqual(headers, headers_t)
        

    def test_replace_drop_header_dfs(self):
        headers = [
                ('Date/Time', 'Inverno'), 
                ('Drybulb temp', 'Inverno'), 
                ('AP1_INV_QUARTO 1', 0.3), 
                ('AP1_INV_SALA 1', 0.3), 
                ('AP1_INV_QUARTO 1', 0.5), 
                ('AP1_INV_SALA 1', 0.5), 
                ]
        df_ver, df_inv = target.get_df_seasons(self.df_agg)
        df_ver_t, df_inv_t = target.replace_drop_header_dfs(df_ver, df_inv)
        headers_t = df_inv_t.columns.to_list()
        self.assertCountEqual(headers, headers_t)
        
