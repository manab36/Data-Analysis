import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import tqdm
from pandas.errors import SettingWithCopyWarning
import warnings
warnings.simplefilter(action="ignore", category=SettingWithCopyWarning)





def get_players_details_numberfire():
    url_player_rating= "https://www.numberfire.com/nba/players/power-rankings"
    bs4_req = requests.get(url_player_rating)

    bs4_html = BeautifulSoup(bs4_req.text, 'html.parser')
    bs4_player_names= bs4_html.find('table', class_="projection-table projection-table--fixed")
    bs4_players_full_name= []
    bs4_players_rank= []
    for row in bs4_player_names.tbody.find_all('td'):
        temp_1= row.find("span", class_="full")
        temp_2= row.find("span", class_="abbrev")

        if'#' in row.get_text():
            bs4_players_rank.append(row.get_text().replace('#', ''))
            
        if temp_1 is not None:
            bs4_players_full_name.append(temp_1.get_text())

    #Efficiency
    nerd= []
    nf_eff= []
    fantasy= []

    #Statistics
    mpg= []
    ppg= []
    rpg= []
    apg= []

    bs4_player_ratings= bs4_html.find('table', class_="projection-table no-fix")
    for row in bs4_player_ratings.tbody.find_all('td'):
        # print(row["class"])
        if "nerd" in row["class"]:
            nerd.append(row.get_text())

        if "nf_eff" in row["class"]:
            nf_eff.append(row.get_text())

        if "fantasy" in row["class"]:
            fantasy.append(row.get_text())

        if "mpg" in row["class"]:
            mpg.append(row.get_text())

        if "ppg" in row["class"]:
            ppg.append(row.get_text())

        if "rpg" in row["class"]:
            rpg.append(row.get_text())

        if "apg" in row["class"]:
            apg.append(row.get_text())

    cols= (
        ('player', 'name'),
        ('player', 'rank'),
        ('efficiency', 'nerd'),
        ('efficiency', 'nf_eff'),
        ('efficiency', 'fantasy'),
        ('statistics', 'mpg'),
        ('statistics', 'ppg'),
        ('statistics', 'rpg'),
        ('statistics', 'apg'),
    )

    rating_data_df= pd.DataFrame(columns=cols)
    rating_data_df

    rating_data_df[('player','name')]= bs4_players_full_name
    rating_data_df[('player', 'rank')]= bs4_players_rank

    rating_data_df[('efficiency', 'nerd')]= nerd
    rating_data_df[('efficiency', 'nf_eff')]= nf_eff
    rating_data_df[('efficiency', 'fantasy')]= fantasy

    rating_data_df[('statistics', 'mpg')]= mpg
    rating_data_df[('statistics', 'ppg')]= ppg
    rating_data_df[('statistics', 'rpg')]= rpg
    rating_data_df[('statistics', 'apg')]= apg

    return rating_data_df


def get_players_details_by_list_name(player_names):
    player_details= []

    counter_limit= 99
    time_limit= 58 #in sec
    counter= 1
    start_time= time.time()
    for player_name in tqdm.tqdm(player_names):
        now_time= time.time()
        time_dif= now_time-start_time

        #get the details:
        url= f"https://www.thesportsdb.com/api/v1/json/3/searchplayers.php?p={player_name.replace(' ', '%20')}"
        player_detail_req= requests.get(url)
        if player_detail_req.status_code != 200 or player_detail_req.json()['player'] is None: #or len(player_detail_req.json()['player']) != 1:
            continue

        
        player_details.append(player_detail_req.json()['player'][0])

        #reset the time and pause
        if counter>= counter_limit and time_dif <= time_limit:
            print('..')
            time.sleep(time_limit- time_dif)
            counter= 0
            start_time= time.time()
        counter+=1
    return pd.DataFrame(player_details)


def clean_player_details_data(player_details_df):
    player_details_df= player_details_df[["strPlayer", "strTeam", "strSport", "dateBorn", "strBirthLocation", "strStatus", "strGender", "strHeight", "strWeight"]]

    player_details_df.columns= player_details_df.columns.str.replace('str', '')
    player_details_df.columns= player_details_df.columns.str.lower()

    player_details_df["status"]= player_details_df["status"].apply(lambda x: True if x=='Active' else False )
    player_details_df["gender"]= player_details_df["gender"].apply(lambda x: 'M' if x=='Male' else 'F' )

    player_details_df["weight"]= player_details_df["weight"].str.replace('\xa0', ' ').str.split('(').apply(lambda x: x[0])
    player_details_df["weight"]= player_details_df["weight"].apply(lambda x: 
                                                                round(int(x.split(' ')[0])*2.20462,0 )
                                                                if 'kg' in x 
                                                                else  float(x.split(' ')[0]) 
                                                                if 'lb' in x
                                                                else None
                                                                )

    player_details_df["height"]= player_details_df["height"].str.replace('\xa0', ' ').str.replace(" \'", ' ft ').str.replace('"', ' ').str.split('(').apply(lambda x: x[-1])
    player_details_df["height"]= player_details_df["height"].apply(lambda x: 
                                        float(x.split(' ')[-2])
                                        if 'cm' in x
                                        else float(x.split(' ')[0])* 100
                                        if 'm' in x
                                        else round(((int(x.split(' ')[0])*12)+ int(x.split(' ')[2]))* 2.54, 2)
                                        if 'ft' in x
                                        else None
                                    )

    player_details_df.columns= ['player_name',
        'team',
        'sport',
        'birth_date',
        'birth_location',
        'active_status',
        'gender',
        'height_in_cm',
        'weight_in_lb'
    ]

    return player_details_df


def get_team_details_numberfire():
    url_team_rating= "https://www.numberfire.com/nba/teams"
    bs4_req = requests.get(url_team_rating)
    bs4_html = BeautifulSoup(bs4_req.text, 'html.parser')

    list_of_team= []
    for first_div in bs4_html.find_all('div', class_= "all-teams__row"):
        conference_name= first_div.find("h2").get_text().strip()
        for snd_div in first_div.find_all('div', class_= "all-teams__column"):
            division_name= snd_div.find("span", class_="all-teams__column__title").get_text().strip()
            for table_row in snd_div.find_all("li"):
                rows= [row.strip() for row in table_row.get_text().strip().split("\n")]
                team_name= rows[0]
                power_rank= rows[-1].split("#")[-1]

                list_of_team.append({
                    "team": team_name,
                    "team_rank": power_rank,
                    "conference": conference_name,
                    "division": division_name
                })

    team_perforance_df= pd.DataFrame(list_of_team)
    return team_perforance_df



if __name__ == "__main__":
    players_details_df= get_players_details_numberfire()
    # players_details_df
    players_details_df.columns = [i+'_'+v for i,v in players_details_df.columns.tolist()]
    # players_details_df
    players_details_2_df= get_players_details_by_list_name(players_details_df['player_name'])
    clean_player_details_df= clean_player_details_data(players_details_2_df)
    # clean_player_details_df
    team_details_df= get_team_details_numberfire()
    # team_details_df
    merge_df= clean_player_details_df.merge(team_details_df, on='team', how= 'left', indicator=True)
    merge_df= merge_df[merge_df["_merge"]== "both"].drop(columns= "_merge")
    # merge_df
    merge_df_2= merge_df.merge(players_details_df, on='player_name', how= 'left', indicator=True)
    merge_df_2= merge_df_2[merge_df_2["_merge"]== "both"].drop(columns= "_merge")
    # merge_df_2

    print(players_details_df)
    print(clean_player_details_df)
    print(team_details_df)
    print(merge_df_2)
    merge_df_2.to_csv(R"..\dataset\basketball_players.csv")
