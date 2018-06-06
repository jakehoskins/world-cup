#!/usr/bin/env python
import requests
import json
from datetime import datetime
from elasticsearch import Elasticsearch

def load_data_file(f):
    return json.loads(open(f).read())

def parse_for_es(d):
    clean = []
    for key in d:
        for item in d[key]['group']:
            item['@timestamp'] = '@' + item['date']
            item['type'] = 'group'
            clean.append(item)
        for item in d[key]['finals']:
            item['@timestamp'] = '@' + item['date']
            item['type'] = 'finals'
            clean.append(item)
    return clean

def publish_data(d, index):
    clean = parse_for_es(d)
    for item in clean:
        result = es.index(index='football', doc_type='result', body=item)
        print result

if __name__ == '__main__':
    es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
    data = load_data_file('data.json')
    publish_data(data, 'games')
