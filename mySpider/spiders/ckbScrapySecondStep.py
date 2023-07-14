import scrapy
import pandas as pd
import numpy as np
import datetime
import re
import math
import pymongo
from ..items import GeneVarientsItems, CATEGORY_VARIANTSItems, MOLECULAR_PROFILESItems, GENE_LEVEL_EVIDENCEItems, CLINICAL_TRIALSItems
from ..settings import MONGO_URI,MONGO_DATABASE

def get_gene_variant_name(variant):
    variant = variant.replace('\n','')
    match = re.match(r'.*data-filter="(.*?)" class.*',variant)
    if match:
        value = match.group(1)
    else:
        match = re.match(r'<td>(.*?)</td>',variant)
        value = match.group(1)
    return value

def get_molecular_profiles_name(variant):
    variant = variant.replace('\n','')
    variant = f'<td>{variant}'
    match = re.match(r'.*btn-wrap">(.*?)</a>.*',variant)
    if match:
        value = match.group(1).strip()
    else:
        match = re.match(r'<td>(.*?)</td>',variant)
        value = match.group(1).strip()
    return value

def get_gene_level_evidence_name(variant):
    variant = variant.replace('\n','')
    match = re.match(r'.*btn-wrap">(.*?)</a>.*',variant)
    if match:
        value = match.group(1).strip()
    else:
        match = re.match(r'.*class="sorting_1">(.*?)</td>',variant)
        if match:
            value = match.group(1)
        else:
            match = re.match(r'.*btn-reference">\s*(\S*\s\S*).*',variant)
            if match:
                value = match.group(1).strip('\n').strip()
            else:
                match = re.match(r'<td>(.*?)</td>',variant)
                if match:
                    value = match.group(1).strip('\n').strip()
                else:
                    print(variant)
                    value = 'Match Error'
    return value

def get_clinical_trials_name(variant):
    variant = variant.replace('\n','')
    match = re.match(r'.*clinical-trial">(.*?)</a>.*',variant)
    if match:
        value = match.group(1).strip()
    else:
        match = re.match(r'.*btn-wrap">(.*?)</a>.*',variant)
        if match:
            value = match.group(1)
        else:
            match = re.match(r'class="sorting_1">(.*?)</td>.*',variant)
            if match:
                value = match.group(1).strip('\n').strip()
            else:
                match = re.match(r'<td.*>(.*?)</td>',variant)
                if match:
                    value = match.group(1).strip('\n').strip()
                else:
                    print(variant)
                    value = 'aa'
    return value

def get_gene_variants(response, gene_map):
    t = response.xpath('//*[(@id = "DataTables_Table_0")]//td | //*[contains(concat( " ", @class, " " ), concat( " ", "sorting", " " ))]/text()').getall()
    df = pd.DataFrame(np.array(t).reshape(-1,5),)
    df.columns = ['variant', 'impact', 'protein_effect', 'variant_description','associated_with_drug_resistance']
    df = df.drop(df.index[0])
    df = df.applymap(get_gene_variant_name)
    df['origin_url'] = response.url
    df['type'] = 'GENE_VARIANTS'
    geneid = re.match(r'.*geneId=(.*?)&tabType=.*',response.url).group(1)
    df['gene'] = gene_map[geneid]
    df['date'] = datetime.datetime.now()
    df['status'] = 'suceess'
    return df.to_dict(orient='index')

def get_category_variants(response, gene_map):
    t = response.xpath('//*[(@id = "DataTables_Table_0")]//td | //*[contains(concat( " ", @class, " " ), concat( " ", "sorting", " " ))]/text()').getall()
    df = pd.DataFrame(np.array(t).reshape(-1,5),)
    df.columns = ['variant', 'impact', 'protein_effect', 'variant_description','associated_with_drug_resistance']
    df = df.drop(df.index[0])
    df = df.applymap(get_gene_variant_name)
    df['origin_url'] = response.url
    df['type'] = 'CATEGORY_VARIANTS'
    geneid = re.match(r'.*geneId=(.*?)&tabType=.*',response.url).group(1)
    df['gene'] = gene_map[geneid]
    df['date'] = datetime.datetime.now()
    df['status'] = 'suceess'
    return df.to_dict(orient='index')


def get_molecular_profiles(response, gene_map):
    g = response.xpath('//table').getall()[2]
    t = [list(filter(None, m.replace('\n','').strip().split('<td>'))) for m in g.split('<tr')]
    t.pop(0) #删除第一行title
    t.pop(0) #删除第一行title
    df = pd.DataFrame(t)
    df.columns = ['Molecular_Profile', 'Protein_Effect', 'Treatment_Approaches']
    df = df.applymap(get_molecular_profiles_name)
    df['origin_url'] = response.url
    df['type'] = 'MOLECULAR_PROFILES'
    geneid = re.match(r'.*geneId=(.*?)&tabType=.*',response.url).group(1)
    df['gene'] = gene_map[geneid]
    df['date'] = datetime.datetime.now()
    df['status'] = 'suceess'
    return df.to_dict(orient='index')

def get_gene_level_evidence(response, gene_map):
    t = response.xpath('//*[(@id = "DataTables_Table_0")]//td | //*[contains(concat( " ", @class, " " ), concat( " ", "sorting", " " ))]/text()').getall()
    df = pd.DataFrame(np.array(t).reshape(-1,8),)
    df.columns = ['Molecular_Profile', 'Indication_or_Tumor_Type', 'Response_Type', 'Therapy_Name', 'Approval_Status', 'Evidence_Type', 'Efficacy_Evidence', 'References']
    df = df.drop(df.index[0])
    df = df.applymap(get_gene_level_evidence_name)
    df['origin_url'] = response.url
    df['type'] = 'GENE_LEVEL_EVIDENCE'
    geneid = re.match(r'.*geneId=(.*?)&tabType=.*',response.url).group(1)
    df['gene'] = gene_map[geneid]
    df['date'] = datetime.datetime.now()
    df['status'] = 'suceess'
    return df.to_dict(orient='index')

def get_clinical_trials(response, gene_map):
    t = response.xpath('//*[(@id = "DataTables_Table_0")]//td | //*[contains(concat( " ", @class, " " ), concat( " ", "sorting", " " ))]/text()').getall()
    df = pd.DataFrame(np.array(t).reshape(-1,7),)
    df.columns = ['Clinical_Trial', 'Phase', 'Therapies', 'Title', 'Recruitment_Status', 'Covered_Countries', 'Other_Countries']
    df = df.drop(df.index[0])
    df = df.applymap(get_clinical_trials_name)
    df['origin_url'] = response.url
    df['type'] = 'CLINICAL_TRIALS'
    geneid = re.match(r'.*geneId=(.*?)&tabType=.*',response.url).group(1)
    df['gene'] = gene_map[geneid]
    df['date'] = datetime.datetime.now()
    df['status'] = 'suceess'
    return df.to_dict(orient='index')


class CKBScrapySecondStepSpider(scrapy.Spider):
    name = 'ckbScrapySecondStep'

    allowed_domains = ['pubmed.ncbi.nlm.nih.gov','nature.com','science.org','cell.com','ahajournals.org','ckb.jax.org']
    
    def __init__(self, name='ckbScrapySecondStep', **kwargs):
        super().__init__(name, **kwargs)
        client = pymongo.MongoClient(MONGO_URI)
        db = client[MONGO_DATABASE]
        all_urls = []
        gene_map = {}
        # all_urls = db['PageItem'].find({'status':'score','type':'Circulation'},{'url':1})
        # all_urls = db['FirstPageItem'].find({'status':'score'},{'type_url':1})
        all_score = db['FirstPageItem'].find({'status':'score'},{'type_url':1, 'gene':1})
        for single_score in all_score:
            all_urls.append(single_score['type_url'])
            geneid = re.match(r'.*geneId=(.*?)&tabType=.*',single_score['type_url']).group(1)
            if geneid not in gene_map.keys():
                gene_map[geneid] = single_score['gene']
        self.start_urls = all_urls
        self.gene_map  = gene_map


    def parse(self, response):

        url = response.url
        if 'GENE_VARIANTS' in url:
            return_item = GeneVarientsItems()
            items = get_gene_variants(response, self.gene_map)
            for item in items.values():
                for key,value in item.items():
                    return_item[key] = value
                yield return_item
        
        if 'CATEGORY_VARIANTS' in url:
            return_item = CATEGORY_VARIANTSItems()
            items = get_category_variants(response, self.gene_map)
            for item in items.values():
                for key,value in item.items():
                    return_item[key] = value
                yield return_item
        
        if 'MOLECULAR_PROFILES' in url:
            return_item = MOLECULAR_PROFILESItems()
            items = get_molecular_profiles(response, self.gene_map)
            for item in items.values():
                for key,value in item.items():
                    return_item[key] = value
                yield return_item
        
        if 'GENE_LEVEL_EVIDENCE' in url:
            return_item = GENE_LEVEL_EVIDENCEItems()
            items = get_gene_level_evidence(response, self.gene_map)
            for item in items.values():
                for key,value in item.items():
                    return_item[key] = value
                yield return_item
        
        if 'CLINICAL_TRIALS' in url:
            return_item = CLINICAL_TRIALSItems()
            items = get_clinical_trials(response, self.gene_map)
            for item in items.values():
                for key,value in item.items():
                    return_item[key] = value
                yield return_item


