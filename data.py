#!/usr/bin/env python
from os import listdir
from os import path
from datetime import datetime
import json
import re

# git clone https://github.com/openfootball/world-cup

start = 1986
max = 2014

def valid_result_line(l):
    return '@' in l

def extract_result_from_line(l, isHome=True):
    reg = re.search('(\d+-\d+)', l)
    result = reg.group(0).split('-')
    return int(result[0]) if isHome else int(result[1])


def extract_team_from_line(l, isHome=True):
    try:
        # Has time in date
        reg = re.search('\:(?s)(.*)@', l)
        result = reg.group(0).split()
        start, i = 1, 1
    except:
        # Has no time in date
        try:
            reg = re.search('\/(?s)(.*)@', l)
            result = reg.group(0).split()
            start, i = 1, 1
        except:
            # Has no time and date is in a different format
            # Just grab eerything after 4th word and pray
            result = l.split()[3:]
            start, i = 0, 0

    extracted = False
    home_team, away_team = '',''

    while (not extracted):
        # E.g. South Afirca 1-0 United States
        if '-' in result[i + 1]:
            home_team = ' '.join(result[start:i + 1])
            if 'a.e.t.' in result[i + 2]:
                away_team = ' '.join(result[i + 5:]).split('@')[0]
                extracted = True
            elif '(' in result[i + 2]:
                away_team = ' '.join(result[i + 3:]).split('@')[0]
                extracted = True
            elif 'pen.' in result[i + 2]:
                away_team = ' '.join(result[i + 7:]).split('@')[0]
                extracted = True
            else:
                away_team = ' '.join(result[i + 2:]).split('@')[0]
                extracted = True
        i += 1

    return home_team.strip() if isHome else away_team.strip()

def extract_date_from_line(l, year):
    try:
        d = '%s/%s' % (year, l.split()[2])
        dformat = '%Y/%b/%d'
        date = datetime.strptime(d, dformat)
        return date.isoformat()
    except:
        # Different data format
        d = '%s %s' % (year, ' '.join(l.split()[1:3]))
        dformat = '%Y %d %B'
        date = datetime.strptime(d, dformat)
        return date.isoformat()
    

def is_valid_entry(home_team, away_team, home_goals, away_goals):
    # Numbers in a team name suggests somethings bad about the data
    # Letters in the scores suggests somethings bad about the data
    if any(char.isdigit() for char in home_team) or \
       any(char.isdigit() for char in away_team) or \
       not isinstance(home_goals, int) or \
       not isinstance(away_goals, int):
        return False
 
    return True
    
def parse_result_line(l, year):
    home_team = extract_team_from_line(l)
    away_team = extract_team_from_line(l, False)
    home_goals = extract_result_from_line(l)
    away_goals = extract_result_from_line(l, False)
    date = extract_date_from_line(l, year)
    obj = {
        'home_team': home_team,
        'away_team': away_team,
        'home_goals': home_goals,
        'away_goals': away_goals,
        'date': date
    }

    if is_valid_entry(home_team, away_team, home_goals, away_goals):
        game_result = 'draw'
        home_diff = 0
        away_diff = 0

        if home_goals > away_goals:
            game_result = home_team
        if away_goals > home_goals:
            game_result = away_team

        home_diff = home_goals - away_goals
        away_diff = away_goals - home_diff

        obj['game_result'] = game_result
        obj['home_diff'] = home_diff
        obj['away_diff'] = away_diff

        print '%s v %s - (%d-%d)' % (home_team, away_team, home_goals, away_goals)
        return obj
    else:
        print('Ommitting due to error in passing.', l)
    return None

def extract(path, year):
    print 'Processing results from %s ' % path
    results = []
    with open(path) as f:
        for line in f:
            if valid_result_line(line):
                r = parse_result_line(line, year)
                if r:
                    results.append(r)
    return results
        
def get_year_from_dir(d):
    return d.split('/')[0].split('--')[0]
    
def extract_results_from_directory(d, year):
    return {
        'group': extract(path.join('', d, 'cup.txt'), year),
        'finals': extract(path.join('', d, 'cup_finals.txt'), year),
    }

def write_to_file(items):
    obj = {}
    with open('data.json' , 'w') as outfile:
        json.dump(items, outfile)
    
def extract_results_from_directories(dirs):
    obj = {}
    for d in dirs:
        year = get_year_from_dir(d)
        obj[year] = extract_results_from_directory(d, year)

    return obj

if __name__ == '__main__':
    # Walk over every folder, looking for valid folders
    dirs = [f for f in listdir('.') if path.isdir(path.join('', f))]
    datadirs = filter(lambda k: '--' in k, dirs)
    cutdirs = filter(lambda k:
                     int(k[:4]) >= start and
                     int(k[:4]) <= max, datadirs)
    write_to_file(extract_results_from_directories(cutdirs))
