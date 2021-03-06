import pandas as pd
import numpy as np
import PySimpleGUI as sg
import os

root_path = os.path.dirname(os.path.realpath(__file__))
matches_path = os.path.join(root_path, "MatchHistory")
elos_path_pot = os.path.join(root_path, "ElosPot")
elos_path_chess = os.path.join(root_path, "ElosChess")

start_score_pot = 301.
start_score_chess = 1200.
# data_dict = {'MatchHistory': (['datetime','winner','opponents'], None),
#              'Elos': (['Christofer'], {'Christofer':start_score_pot})}
# row_dict = {}
# for key, (cols, rows) in data_dict.items():
#     try:
#         data = pd.read_csv(root_path + key)
#     except FileNotFoundError:
#         data = pd.DataFrame(columns=cols)
#         if not rows is None:
#             data = data.append(rows, ignore_index=True)
#         data.to_csv(root_path + key, index=False)
        
        
def Add_result_and_update_elo(datetime, outcomes, players):
    i = outcomes.index('Win')
    winner = players[i]
    opponents = players[:i] + players[i+1:]
    Add_match_to_match_history(datetime, winner, opponents)
    Add_match_to_elos_history(winner, opponents)
    
def Add_match_to_match_history(datetime, winner, opponents):
    matches = pd.read_csv(matches_path)
    match = {'datetime':datetime, 'winner':winner,'opponents':opponents}
    matches = matches.append(match, ignore_index=True)
    matches.to_csv(matches_path, index=False)

def Add_match_to_elos_history(winner, opponents):
    elos_pot = pd.read_csv(elos_path_pot)
    elos_chess = pd.read_csv(elos_path_chess)
    players = [winner] + opponents
    for player in players:
        if not player in elos_pot.columns:
            elos_pot[player] = [start_score_pot]*len(elos_pot.index)

        if not player in elos_chess.columns:
            elos_chess[player] = [start_score_chess]*len(elos_chess.index)


    last_elos_chess = elos_chess.iloc[-1]
    mult_factor = 32
    scores = {player:int(player==winner) for player in players}
    exp_elos = {player: 10**(last_elos_chess[player]/400) for player in players}
    tot_exp_elos = sum(exp_elos.values())
    new_elos_chess = last_elos_chess.copy()
    for player in players:
        new_elos_chess[player] = last_elos_chess[player] + mult_factor*(scores[player] - exp_elos[player]/tot_exp_elos)

    elos_chess = elos_chess.append(new_elos_chess, ignore_index=True)
    elos_chess.to_csv(elos_path_chess, index=False)
    
    last_elos_pot = elos_pot.iloc[-1]
    pot_factor = 0.01
    pot_size = pot_factor*np.sum([last_elos_pot[player] for player in players])
    new_elos_pot = last_elos_pot.copy()
    for player in players:
        new_elos_pot[player] =  np.round((1.-pot_factor)*last_elos_pot[player] + pot_size*float(player==winner), 6)
    
    elos_pot = elos_pot.append(new_elos_pot, ignore_index=True)
    elos_pot.to_csv(elos_path_pot, index=False)
    pass

def Delete_game_by_index(index):
    index = index
    matches = pd.read_csv(matches_path)
    matches = matches.drop(index)
    matches.to_csv(matches_path, index=False)
    elos = pd.read_csv(elos_path_pot)
    elos = elos.drop(index+1)
    elos.to_csv(elos_path_pot, index=False)
    pass

def Create_strings_input_values(values):
    players = []
    outcomes = []
    for key in values:
        if key % 2 == 0:
            players.append(values[key])
        else:
            outcomes.append(values[key])
    datetime = players.pop(-1)
    return players, outcomes, datetime
        
def Create_and_launch_gui():
    sg.theme('DarkAmber')   # Add a touch of color
    # All the stuff inside your window. 10 rows because too much effort to make window dynamic.
    layout = [  [sg.Text('Enter the names of the players and the outcome for every player as either Win or Loss and enter \nthe apprximate time for the game. Press Ok to record the game.')],
                [sg.Text('To show the match history, press "Show match history".')],
                [sg.Text('To show a player\'s elo history enter the name of the player on the first row and press "Show player elos history".')],
                [sg.Text('To delete a game by index, enter the index of the game (starting on 0) and press \'Delete game by index\'.')],
                [sg.Text('Name of player                                                        '), sg.Text('Outcome')],
                [sg.InputText(),sg.Combo(['Win','Loss'], size = 10, readonly=True)],
                [sg.InputText(),sg.Combo(['Win','Loss'], size = 10, readonly=True)],
                [sg.InputText(),sg.Combo(['Win','Loss'], size = 10, readonly=True)],
                [sg.InputText(),sg.Combo(['Win','Loss'], size = 10, readonly=True)],
                [sg.InputText(),sg.Combo(['Win','Loss'], size = 10, readonly=True)],
                [sg.InputText(),sg.Combo(['Win','Loss'], size = 10, readonly=True)],
                [sg.InputText(),sg.Combo(['Win','Loss'], size = 10, readonly=True)],
                [sg.InputText(),sg.Combo(['Win','Loss'], size = 10, readonly=True)],
                [sg.InputText(),sg.Combo(['Win','Loss'], size = 10, readonly=True),               sg.Text('Date and approximate time for match hh:mm dd-mm-yyyy')],
                [sg.InputText(),sg.Combo(['Win','Loss'], size = 10, readonly=True), sg.InputText()],
                [sg.Button('Record game'), sg.Button('Show match history'), 
                 sg.Button('Show player elos history'), sg.Button('Delete game by index'), 
                 sg.Button('Cancel')] ]

    # Create the Window
    window = sg.Window('Syntronic R&D Dart score tracker', layout)
    # Event Loop to process "events" and get the "values" of the inputs
    while True:
        event, values = window.read()
        short_values = {k: v for k, v in values.items() if v}
        
        if event == sg.WIN_CLOSED or event == 'Cancel': # if user closes window or clicks cancel
            break


        if event == 'Show match history':
            history = str(pd.read_csv(matches_path))
            sg.Print(history, do_not_reroute_stdout=False)
            continue
            
        try:
            if not short_values:
                sg.Print('No values received.', do_not_reroute_stdout=False)
                continue

            if event == 'Show player elos history':
                history = str(pd.read_csv(elos_path_pot)[short_values[0]])
                sg.Print(history, do_not_reroute_stdout=False)
                continue
            
            if event == 'Record game':
                players, outcomes, datetime = Create_strings_input_values(short_values)
                
                if len(players) != len(outcomes):
                    sg.Print('Number of players must match number of recorded results.', do_not_reroute_stdout=False)
                    continue
                    
                if outcomes.count('Win') != 1:
                    sg.Print('One and only one player must be recorded as winner.', do_not_reroute_stdout=False)
                    continue
                    
                Add_result_and_update_elo(datetime, outcomes, players)
                sg.Print('Game has been recorded.', do_not_reroute_stdout=False)

                
            if event == 'Delete game by index':
                index = short_values[0]
                Delete_game_by_index(int(index))
                outp_string = 'Game with index ' + str(index) + ' has been deleted.'
                sg.Print(outp_string, do_not_reroute_stdout=False)
                continue
                
        except Exception as e:
            sg.Print(e, do_not_reroute_stdout=False)
    window.close()
    pass


if __name__ == '__main__':
    Create_and_launch_gui()