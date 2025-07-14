#!/usr/bin/env python3
import os
from argparse import ArgumentParser

from client import SteamClient

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('steamid', type=int)
    parser.add_argument('--keyfile', type=str, default='.steam-api-key')
    parser.add_argument('--nocache', action='store_true')
    args = parser.parse_args()

    if not os.path.isfile(args.keyfile):
        print(f'Error: Steam Web API key not found at {args.keyfile}')
        exit(1)

    with open(args.keyfile, 'r') as f:
        key = f.read().strip()
    c = SteamClient(api_key=key, nocache=args.nocache)
    print(f'Connected to Steam Web API with Steam ID {args.steamid}.')

    games = c.get_owned_games(steam_id=args.steamid)
    agcr = c.calculate_agcr(games)
    print('----------')
    print(f'AGCR is {agcr}.')

    print('----------')
    print('Top AGCR opportunities:')
    for game in c.top_agcr_opportunities(games, top=5):
        print(f'{game.name}: {game.achievements_unlocked} out of {game.achievements_total}')

    print('----------')
    print('Top AGCR detractors:')
    for game in c.top_agcr_detractors(games, top=5):
        print(f'{game.name}: {game.achievements_unlocked} out of {game.achievements_total}')
