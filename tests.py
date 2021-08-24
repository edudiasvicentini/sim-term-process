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
