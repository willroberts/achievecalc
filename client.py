import json
import os
import requests
from dataclasses import dataclass
from steam.webapi import WebAPI

@dataclass
class SteamGame:
    app_id: int
    name: str
    achievements_unlocked: int = 0
    achievements_total: int = 0

class SteamClient(object):
    def __init__(self, api_key: str, steam_id: int, nocache: bool) -> None:
        self.api_key = api_key
        self.steam_id = steam_id
        self.cache_enabled = False if nocache else True
        self.client = None

    def initialize_client(self) -> None:
        self.client = WebAPI(key=self.api_key)

    def save_games_to_file(self, games) -> None:
        with open('games.json', 'w') as f:
            f.write(json.dumps(games, default=vars))

    def load_games_from_file(self) -> list[SteamGame]:
        games = list()
        if not os.path.exists('games.json'):
            return games
        print('A games.json file exists; loading from local cache.')
        print('You can disable this behavior with --nocache.')
        with open('games.json', 'r') as f:
            for game in json.loads(f.read()):
                games.append(SteamGame(
                    app_id=game['app_id'],
                    name=game['name'],
                    achievements_unlocked=game['achievements_unlocked'],
                    achievements_total=game['achievements_total'],
                ))
        return games

    def get_owned_games(self) -> list[SteamGame]:
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
            steamid=self.steam_id,
        )
        games = list()
        for game in resp.get('response', {}).get('games'):
            achievements = self.get_achievements_for_game(app_id=game['appid'])
            games.append(SteamGame(
                app_id=game['appid'],
                name=game['name'],
                achievements_unlocked=achievements[0],
                achievements_total=achievements[1],
            ))

        if self.cache_enabled:
            self.save_games_to_file(games)
        return games

    def get_achievements_for_game(self, app_id: int) -> tuple[int, int]:
        if self.client is None: self.initialize_client()

        try:
            resp = self.client.call(
                'ISteamUserStats.GetPlayerAchievements_v1',
                appid=app_id,
                key=self.api_key,
                l='en-US',
                steamid=self.steam_id,
            )
            achievements = resp.get('playerstats', {}).get('achievements')
            if achievements is None: return (0, 0)
            return (
                sum([a.get('achieved') for a in achievements]),
                len(achievements),
            )
        except requests.exceptions.HTTPError as e:
            reason = e.response.json().get('playerstats').get('error')
            if reason == 'Requested app has no stats': return (0, 0)
            raise Exception(f'HTTP Error {e.response.status_code}: {e.response.text}')

    # Average Game Completion Rate (AGCR) is defined as the average of game
    # completion percentage among games where at least 1 achievement has been
    # unlocked.
    def calculate_agcr(self, games: list[SteamGame]) -> float:
        pcts = list()
        for game in games:
            if game.achievements_unlocked < 1: continue
            pcts.append(game.achievements_unlocked / game.achievements_total)
        if len(pcts) == 0:
            raise Exception('No games with achievements found.')
        return sum(pcts) / len(pcts)

    # Highest gain is defined as the Game which provides the highest AGCR
    # increase on a per-achievement basis.
    def calculate_highest_gain(self, games: list[SteamGame]) -> str:
        highest_gain = None
        fewest_achievements = 2**63-1
        for game in games:
            if game.achievements_unlocked < 1: continue
            if game.achievements_unlocked == game.achievements_total: continue
            if game.achievements_total < fewest_achievements:
                highest_gain = game
                fewest_achievements = game.achievements_total
        if highest_gain is None:
            raise Exception('Could not determine game with highest potential AGCR gain.')
        return highest_gain.name
