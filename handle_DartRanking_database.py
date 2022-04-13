from audioop import tostereo
from calendar import SATURDAY
from http import server


import os
import sys

import urllib
import pandas as pd
from pkg_resources import parse_requirements
import numpy as np
import keyring
import pyodbc
from sqlalchemy import create_engine
from getpass import getpass

def set_credentials(service,username):
    password = getpass()
    keyring.set_password(service,username,password)
    
def connect_to_database():
    #Set 
    service = 'DartRankingDatabase'    
    server_name = '10.8.128.233'
    database_name = 'DartRanking'
    username = 'SA'
    
    #Get credential
    password = keyring.get_password(service,username)
    if password==None:
        set_credentials(service,username)
        password = keyring.get_password(service,username)

    #Set up pyodbc connection
    connection = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};'
                        f'Server={server_name};'
                        f'Database={database_name};'
                        f'UID={username};'
                        f'PWD={password};'
                        )
                        
    #Set up sqlalchemy engine
    dialect = 'mssql'
    driver='pyodbc'
    params = urllib.parse.quote_plus("DRIVER={ODBC Driver 17 for SQL Server};"
                                    f"SERVER={server_name};"
                                    f"DATABASE={database_name};"
                                    f"UID={username};"
                                    f"PWD={password}")
    
    sqlalchemy_database_url = "mssql+pyodbc:///?odbc_connect={}".format(params)
    
    sqlalchemy_engine = create_engine(sqlalchemy_database_url)
    return connection, sqlalchemy_engine

def calc_primary_key(table, column):
    cursor.execute(f'SELECT MAX({column}) FROM {table};')
    row = cursor.fetchone()
    if row[0] == None:
        primary_key=1
    else:
        primary_key=row[0]+1
    return primary_key

def is_data_in_database(table, column, data):
    """Checks if given set of data already is in the database. Given two lists a list of data and a respective list of colunns 
    the function returns True if all the data is present. 

    Args:
        table (String): Table in DartRanking database
        column (List): List of column names in table, to be checked
        data (List): List of data to be checked in corresponging column.

    Returns:
        None: 
    """
    where_clause = f' WHERE {column[0]} = \'{data[0]}\''
    for i in range(1,len(column)):
        where_clause += f' AND {column[i]} = \'{data[i]}\''
    where_clause+=';'
    cursor.execute(f'SELECT * FROM {table}'+where_clause)
    row=cursor.fetchone()
    return row!=None

def add_new_player_to_database(player_name,cursor, enigin):
    """This is a dunction that updates the DartRanking database with a new player.

    Args:
        player_df (_type_): _description_
        cursor (_type_): _description_
        enigin (_type_): _description_
    """
    if is_data_in_database('player',['player_name'],[player_name]):
        print('Player already exists')
        return   
    primary_key = calc_primary_key('player', 'player_id')
    data = {'player_id':[primary_key], 'player_name':[player_name]}
    df = pd.DataFrame(data)
    df.to_sql('player',engine, if_exists='append',index=False)

def calc_elo():
    return 0

def add_match_to_database(datetime, winner, participants):
    """The is a function that given a time, winner and participants of a dart updates the DartRanking database. 

    Args:
        datetime (String): Unique timestamp of the played match in the form YYYY-MM-DD hh:mm
        winner (String): Spacifies the name of the winner
        participants (list): List the names of all persons participating in the match

    Returns:
        None: 
    """
    
    ### Add to match table
    if is_data_in_database('match',['datum'],[datetime+':00']):
        print('Match already exists')
        return
    match_id = calc_primary_key('match', 'match_id')
    data = {'match_id':[match_id], 'datum':[datetime+':00']}
    df = pd.DataFrame(data)
    df.to_sql('match',engine, if_exists='append',index=False)

    ### Add participants to participants table
    for participant in participants:
        cursor.execute(f'SELECT player_id FROM player WHERE player_name = \'{participant}\';')
        player_id=cursor.fetchone()[0]
        if is_data_in_database('participant',['match_id','player_id'],[match_id, player_id]):
            print('Participant already exists')
            return
        participant_id = calc_primary_key('participant', 'participant_id')
        data = {'participant_id':[participant_id], 'match_id':[match_id],'player_id':[player_id]}
        df = pd.DataFrame(data)
        df.to_sql('participant',engine, if_exists='append',index=False)

    ### Add winner to winner table
    cursor.execute(f'SELECT participant_id FROM participant WHERE player_id =(SELECT player_id FROM player WHERE player_name=\'{winner}\') AND match_id = {match_id};')
    winner_participant_id = cursor.fetchone()[0]
    if is_data_in_database('winner',['participant_id'],[winner_participant_id]):
        print('Winner already exists')
        return
    winner_id = calc_primary_key('winner', 'winner_id')
    data = {'winner_id':[winner_id], 'participant_id':[winner_participant_id]}
    df = pd.DataFrame(data)
    df.to_sql('winner',engine, if_exists='append',index=False)
    
    ### Add elo update to elo table
    for participant in participants:
        cursor.execute(f'SELECT participant_id FROM participant WHERE match_id={match_id} AND player_id = (SELECT player_id FROM player WHERE player_name=\'{participant}\');')
        row = cursor.fetchone()
        participant_id = row[0]

        if is_data_in_database('elo',['participant_id'],[participant_id]):
            print('Elo already registred')
            return
        elo = calc_elo()
        elo_id = calc_primary_key('elo', 'elo_id')
        data = {'elo_id':[elo_id], 'participant_id':[participant_id],'elo':[elo]}
        df = pd.DataFrame(data)
        df.to_sql('elo',engine, if_exists='append',index=False)

conn, engine = connect_to_database()
cursor = conn.cursor()
