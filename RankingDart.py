import pandas as pd
import numpy as np
import PySimpleGUI as sg

def Load_player(name):
    path = r'\\rubin\\users$\\agfrxa\\dart\\' + name
    history = pd.read_csv(path)
    return history

def Create_player(name):
    player = ['outcome', 'elo', 'opponents']
    match = pd.DataFrame(columns=player)
    score = {'outcome':'N/A', 'elo':1000, 'opponents':'N/A'}
    match = match.append(score, ignore_index=True)
    path = r'\\rubin\\users$\\agfrxa\\dart\\' + name
    match.to_csv(path, index=False)
    pass

def Update_score(name, win_loss, opponents):
    path = r'\\rubin\\users$\\agfrxa\\dart\\' + name
    score = {'outcome':win_loss, 'elo':0, 'opponents':opponents}
    history = Load_player(name)
    history = history.append(score, ignore_index=True)
    history.to_csv(path, index=False)
    pass
    
def Update_elo(name, win_loss, opponents):
    no_players = len(opponents)
    path = r'\\rubin\\users$\\agfrxa\\dart\\' + name
    win_score = no_players/(no_players-0.8)
    loss_score = 0
    score_dict = {'Win':win_score, 'Loss':0}
    history = Load_player(name)
    player_elo = np.array(history['elo'])[-2]
    total_elo = 0
    
    
    for temp_name in opponents:
        temp_path = 'C:\\Users\\agfrxa\\Python\\dart\\' + temp_name
        temp_history = pd.read_csv(temp_path)
        total_elo += np.array(temp_history['elo'])[-2]
        
    mean_elo = total_elo/no_players
    expected_outcome = player_elo / (total_elo)
    outcome = score_dict[win_loss]
    mult_factor = 32
    row = history[history['elo']==0].index.values
    new_elo = player_elo + mult_factor * (outcome - expected_outcome)
    history.at[row, 'elo'] = new_elo
    history.to_csv(path, index=False)
    pass
    
def Add_result_and_update_elo(outcomes, players):
    for i, (outcome, name) in enumerate(zip(outcomes, players)):
        opponents = players.copy()
        opponents.pop(i)
        Update_score(name, outcome, opponents)
        
    for i, (outcome, name) in enumerate(zip(outcomes, players)):
        opponents = players.copy()
        opponents.pop(i)
        Update_elo(name, outcome, opponents)
    pass

        
def Delete_latest_game(names):
    for name in names:
        history_player = Load_player(name)
        latest_game_ind = len(history_player)-1
        history_player = history_player.drop(latest_game_ind)
        path = r'\\rubin\\users$\\agfrxa\\dart\\' + name
        history_player.to_csv(path, index=False)
    pass

def Create_strings_input_values(values):
    players = []
    outcomes = []
    for key in values:
        if key % 2 == 0:
            players.append(values[key])
        else:
            outcomes.append(values[key])
    return players, outcomes

        
def Create_and_launch_gui():
    sg.theme('DarkAmber')   # Add a touch of color
    # All the stuff inside your window. 10 rows because too much effort to make window dynamic.
    layout = [  [sg.Text('Enter the names of the players and the outcome for every player as either Win or Loss.\nPress Ok to record the game.')],
                [sg.Text('To create a new player, enter their name in the first row and press "Create player".')],
                [sg.Text('To show a player\'s history, enter their name in the first row and press "Show player match history".')],
                [sg.Text('To delete the latest game from one or more players history, enter their names and press "Delete latest game".')],
                [sg.Text('Name of player                                                        '), sg.Text('Outcome')],
                [sg.InputText(),sg.Combo(['Win','Loss'], size = 10, readonly=True)],
                [sg.InputText(),sg.Combo(['Win','Loss'], size = 10, readonly=True)],
                [sg.InputText(),sg.Combo(['Win','Loss'], size = 10, readonly=True)],
                [sg.InputText(),sg.Combo(['Win','Loss'], size = 10, readonly=True)],
                [sg.InputText(),sg.Combo(['Win','Loss'], size = 10, readonly=True)],
                [sg.InputText(),sg.Combo(['Win','Loss'], size = 10, readonly=True)],
                [sg.InputText(),sg.Combo(['Win','Loss'], size = 10, readonly=True)],
                [sg.InputText(),sg.Combo(['Win','Loss'], size = 10, readonly=True)],
                [sg.InputText(),sg.Combo(['Win','Loss'], size = 10, readonly=True)],
                [sg.InputText(),sg.Combo(['Win','Loss'], size = 10, readonly=True)],
                [sg.Button('Record game'), sg.Button('Create player'), 
                 sg.Button('Show player match history'), sg.Button('Delete latest game'), 
                 sg.Button('Cancel')] ]

    # Create the Window
    window = sg.Window('Syntronic R&D Dart score tracker', layout)
    # Event Loop to process "events" and get the "values" of the inputs
    while True:
        event, values = window.read()
        short_values = {k: v for k, v in values.items() if v}
        
        if event == sg.WIN_CLOSED or event == 'Cancel': # if user closes window or clicks cancel
            break
        
        try:
            if not short_values:
                sg.Print('No values recieved', do_not_reroute_stdout=False)
                continue
            
            if event == 'Record game':
                players, outcomes = Create_strings_input_values(short_values)
                
                if len(players) != len(outcomes):
                    sg.Print('Number of players must match number of recorded results.', do_not_reroute_stdout=False)
                    continue
                    
                if outcomes.count('Win') != 1:
                    sg.Print('One and only one player must be recorded as winner.', do_not_reroute_stdout=False)
                    continue
                    
                Add_result_and_update_elo(outcomes, players)
                sg.Print('Game has been recorded.', do_not_reroute_stdout=False)
                
            if event == 'Create player':
                Create_player(short_values[0])
                creation_string = 'Player' +  str(short_values[0]) + 'created'
                sg.Print('Player',  short_values[0], 'created', do_not_reroute_stdout=False)
                continue
                
            if event == 'Show player match history':
                history = str(short_values[0]) + '\n' + str(Load_player(short_values[0]))
                sg.Print(history, do_not_reroute_stdout=False)
                continue
                
            if event == 'Delete latest game':
                players, outcomes = Create_strings_input_values(short_values)
                Delete_latest_game(players)
                outp_string = 'Latest game for ' + ', '.join(players) + ' has been deleted.'
                sg.Print(outp_string, do_not_reroute_stdout=False)
                continue
                
        except Exception as e:
            sg.Print(e, do_not_reroute_stdout=False)
    window.close()
    pass


if __name__ == '__main__':
    Create_and_launch_gui()