import json
import os
import requests
from steam.webapi import WebAPI
from typing import List

from game import SteamGame

class SteamClient(object):
    def __init__(self, api_key: str, steamid: int, use_cache: bool) -> None:
        self.api_key = api_key
        self.steamid = steamid
        self.use_cache = use_cache
        self.client = None

    def get_owned_games(self) -> List[SteamGame]:
        if self.client is None:
            self.client = WebAPI(key=self.api_key)

        if self.use_cache and os.path.exists('games.json'):
            print('A games.json file exists; loading from local cache.')
            print('You can disable this behavior with --usecache=False.')
            with open('games.json', 'r') as f:
                games = list()
                data = json.loads(f.read())
                for entry in data:
                    game = SteamGame(
                        appid=entry['appid'],
                        name=entry['name'],
                        achievements_unlocked=entry['achievements_unlocked'],
                        achievements_total=entry['achievements_total'],
                    )
                    games.append(game)
                return games

        print(f'Retrieving games and achievements...')
        result = self.client.call(
            'IPlayerService.GetOwnedGames_v1',
            appids_filter=[],
            include_appinfo=True,
            include_extended_appinfo=False,
            include_free_sub=False,
            include_played_free_games=False,
            key=self.api_key,
            language='en-US',
            skip_unvetted_apps=True,
            steamid=self.steamid,
        )
        games = list()
        for game in result['response']['games']:
            g = SteamGame(name=game['name'], appid=game['appid'])
            acs = self.get_achievements_for_game(appid=game['appid'])
            (g.achievements_unlocked, g.achievements_total) = acs
            games.append(g)
        data = json.dumps(games, default=vars)
        with open('games.json', 'w') as f:
            f.write(data)
        return games

    def get_achievements_for_game(self, appid: int) -> tuple:
        if self.client is None:
            self.client = WebAPI(key=self.api_key)

        try:
            result = self.client.call(
                'ISteamUserStats.GetPlayerAchievements_v1',
                appid=appid,
                key=self.api_key,
                l='en-US',
                steamid=self.steamid,
            )
            if 'achievements' not in result['playerstats'].keys():
                return (0, 0)
            x = result['playerstats']['achievements']
            return (
                sum([a['achieved'] for a in result['playerstats']['achievements']]),
                len(result['playerstats']['achievements']),
            )
        except requests.exceptions.HTTPError as e:
            # Games with no achievements return HTTP/400 instead of 0.
            return (0, 0)

    # Average Game Completion Rate (AGCR) is defined as the average of game
    # completion percentage among games where at least 1 achievement has been
    # unlocked.
    def calculate_agcr(self, games: List[SteamGame]) -> float:
        pcts = list()
        for game in games:
            if game.achievements_unlocked < 1: continue
            pcts.append(game.achievements_unlocked / game.achievements_total)
        if len(pcts) == 0:
            print('Error: No games with achievements found.')
            return 0
        return sum(pcts) / len(pcts)

    # Highest gain is defined as the Game which provides the highest AGCR
    # increase on a per-achievement basis.
    def calculate_highest_gain(self, games: List[SteamGame]) -> str:
        result = None
        fewest_achievements = 2**63-1
        for game in games:
            if game.achievements_unlocked < 1: continue
            if game.achievements_unlocked == game.achievements_total: continue
            if game.achievements_total < fewest_achievements:
                result = game
                fewest_achievements = game.achievements_total
        if result is None:
            print('Error: Could not determine game with highest potential AGCR gain.')
            return ''
        return result.name
