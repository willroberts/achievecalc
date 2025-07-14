import json
import os
import requests
from dataclasses import dataclass
from steam.webapi import WebAPI

@dataclass
class SteamGame:
    '''
    SteamGame encapsulates achievement metadata for a game.
    '''
    app_id: int
    name: str
    achievements_unlocked: int
    achievements_total: int

class SteamClient(object):
    '''
    SteamClient provides methods for fetching game and achievement metadata,
    and computing various values related to Average Game Completion Rate (AGCR).
    '''
    def __init__(self, api_key: str, nocache: bool) -> None:
        self.api_key = api_key
        self.cache_enabled = False if nocache else True
        self.client = None

    def initialize_client(self) -> None:
        '''
        Instantiates a Steam Web API client and retrieves supported methods.
        '''
        self.client = WebAPI(key=self.api_key)

    def save_games_to_file(self, games) -> None:
        '''
        Caches game metadata to a local file.
        '''
        with open('games.json', 'w') as f:
            f.write(json.dumps(games, default=vars))

    def load_games_from_file(self) -> list[SteamGame]:
        '''
        Loads game metadata from local cache to reduce API request volume.
        '''
        games = list()
        if not os.path.exists('games.json'):
            return games
        print('A games.json file exists; loading from local cache.')
        with open('games.json', 'r') as f:
            for game in json.loads(f.read()):
                games.append(SteamGame(
                    app_id=game['app_id'],
                    name=game['name'],
                    achievements_unlocked=game['achievements_unlocked'],
                    achievements_total=game['achievements_total'],
                ))
        return games

    def get_owned_games(self, steam_id: int) -> list[SteamGame]:
        '''
        Retrieves metadata for all games in a user's library.
        '''
        if self.client is None: self.initialize_client()

        if self.cache_enabled:
            games = self.load_games_from_file()
            if len(games) > 0: return games

        print(f'Retrieving games and achievements...')
        resp = self.client.call(
            'IPlayerService.GetOwnedGames_v1',
            appids_filter=[],
            include_appinfo=True,
            include_extended_appinfo=False,
            include_free_sub=False,
            include_played_free_games=False,
            key=self.api_key,
            language='en-US',
            skip_unvetted_apps=True,
            steamid=steam_id,
        )
        games = list()
        for game in resp.get('response', {}).get('games'):
            achievements = self.get_achievements_for_game(
                app_id=game['appid'],
                steam_id=steam_id,
            )
            games.append(SteamGame(
                app_id=game['appid'],
                name=game['name'],
                achievements_unlocked=achievements[0],
                achievements_total=achievements[1],
            ))

        if self.cache_enabled:
            self.save_games_to_file(games)
        return games

    def get_achievements_for_game(self, app_id: int, steam_id: int) -> tuple[int, int]:
        '''
        Returns the number of unlocked achievements and total achievements for
        the given game.
        '''
        if self.client is None: self.initialize_client()

        try:
            resp = self.client.call(
                'ISteamUserStats.GetPlayerAchievements_v1',
                appid=app_id,
                key=self.api_key,
                l='en-US',
                steamid=steam_id,
            )
        except requests.exceptions.HTTPError as e:
            reason = e.response.json().get('playerstats').get('error')
            if reason == 'Requested app has no stats': return (0, 0)
            raise Exception(f'HTTP Error {e.response.status_code}: {e.response.text}')

        achievements = resp.get('playerstats', {}).get('achievements')
        if achievements is None: return (0, 0)
        return (
            sum([a.get('achieved') for a in achievements]),
            len(achievements),
        )

    def calculate_agcr(self, games: list[SteamGame]) -> float:
        '''
        Average Game Completion Rate (AGCR) is defined as the average of game
        completion percentages, among games where at least 1 achievement has
        been unlocked.
        '''
        pcts = [g.achievements_unlocked / g.achievements_total for g in games if g.achievements_unlocked > 0]
        if len(pcts) == 0:
            raise Exception('No games with achievements found.')
        return sum(pcts) / len(pcts)

    def top_agcr_opportunities(self, games: list[SteamGame], top: int = 10) -> str:
        '''
        AGCR opportunities are games with the highest per-achievement AGCR increase.
        '''
        games = [g for g in games if g.achievements_unlocked > 0 and g.achievements_unlocked != g.achievements_total]
        return sorted(games, key=lambda g: g.achievements_total)[:top]

    def top_agcr_detractors(self, games: list[SteamGame], top: int = 10) -> list[SteamGame]:
        '''
        AGCR detractors are games with the lowest percent completion.
        '''
        games = [g for g in games if g.achievements_unlocked > 0 and g.achievements_unlocked != g.achievements_total]
        if top >= len(games):
            return games
        return sorted(games, key=lambda g: g.achievements_unlocked / g.achievements_total)[:top]
