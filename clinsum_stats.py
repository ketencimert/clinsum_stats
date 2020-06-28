# -*- coding: utf-8 -*-
"""
Created on Sat Jun 27 20:55:32 2020

@author: Mert Ketenci
"""
import collections
from collections import defaultdict
import csv
import os
from multiprocessing import Pool
from pathlib import Path

from bs4 import BeautifulSoup
import re
from tqdm import tqdm

from medcat.cat import CAT
from medcat.utils.vocab import Vocab
from medcat.cdb import CDB 

from utils import *

path_medcat = os.path.join(Path(os.path.dirname(__file__)))
path_mrns = os.path.join(Path(os.path.dirname(__file__)).parent) + '/notes_by_mrn'

def calculate_statistics(mrn_path):
    
    source_target_dict = defaultdict(list)
    stats_dict = {}
    error_log = []

    try:
        mrn_number = int(mrn_path.split('/')[-1])
        with open(mrn_path + '/data.source', 'r') as source:
            source = source.read()
            
        with open(mrn_path + '/data.target', 'r') as target:
            target = target.read()
    except:
        mrn_number = mrn_path.split('/')[-1]
        error_log.append('Error: source/target missing mrn: {}'.format(mrn_number))
        return stats_dict, error_log
    
    soup = BeautifulSoup(source)
    examples = [str(x) for x in soup.findAll("e")]
    for example in examples:
        account_number = int(re.search(r'<e account=(.*? )', example)[1].split('"')[1])
        source_target_dict[account_number].append(set([x['cui'] for x in cat.get_entities(remove_html_tags(example))]))

    soup = BeautifulSoup(target)
    examples = [str(x) for x in soup.findAll("e")]
    for example in examples:
        account_number = int(re.search(r'<e account=(.*? )', example)[1].split('"')[1])
        
        if len(source_target_dict[account_number]) != 0:
            source_target_dict[account_number].append(set([x['cui'] for x in cat.get_entities(remove_html_tags(example))]))
        else:
            error_log.append('Error: source example missing mrn: {} account: {}'.format(mrn_number, account_number))
            
    for account_number in source_target_dict.keys():
        try:
            source = source_target_dict[account_number][0]
            target = source_target_dict[account_number][1]
        except:
            error_log.append('Error: target example missing mrn: {} account: {}'.format(mrn_number, account_number))
            continue
        
        intersection_space = len(source.intersection(target))
        target_space = len(target)
        
        stats_dict[(mrn_number, account_number)] = intersection_space / target_space
 
    return stats_dict, error_log

if __name__ == '__main__':
    
    print('Loading the vocabulary...')
    try:
        vocab = Vocab()
        vocab.load_dict(path_medcat + '/vocab.dat')
    except:
        raise ImportError('vocab and script should be in same directory')

    print('Loading the weights. This will take time...')
    try:
        cdb = CDB()
        cdb.load_dict(path_medcat + '/umls_base_wlink_fixed_x_avg_2m_mimic.dat') 
    except:
        raise ImportError('weights and script should be in same directory')
    
    print('Building the model...')
    cat = CAT(cdb=cdb, vocab=vocab)
    
    print('Building mrn directories...')
    mrns = [path_mrns + '/' + x for x in os.listdir(path_mrns)]
    total = len(mrns)
    
    print('{} available mrns \n'.format(total))
    stats_dicts = {}
    error_logs = []
    
    for mrn in tqdm(mrns, total = total):
        stats, errs = calculate_statistics(mrn)
        stats_dicts.update(stats)
        if len(errs) != 0:
            error_logs.append(errs)
            
    print('Saving stats and error log...')
    w = csv.writer(open(path_medcat + "/stats.csv", "w", newline=''))
    for key, val in stats_dicts.items():
        w.writerow([key, val])
    
    w = csv.writer(open(path_medcat + "/err_log.csv", "w", newline=''))
    for errs in error_logs:
        w.writerow(errs)

    

