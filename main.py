#!/usr/bin/env python3
import os
from argparse import ArgumentParser

from client import SteamClient

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('steamid', type=int)
    parser.add_argument('--keyfile', type=str, default='.steam-api-key')
    parser.add_argument('--nocache', action='store_true')
    parser.add_argument
    args = parser.parse_args()

    if not os.path.isfile(args.keyfile):
        print(f'Error: Steam Web API key not found at {args.keyfile}')
        exit(1)

    with open(args.keyfile, 'r') as f:
        key = f.read().strip()
    c = SteamClient(api_key=key, steam_id=args.steamid, nocache=args.nocache)
    print(f'Connected to Steam Web API with Steam ID {args.steamid}.')

    games = c.get_owned_games()
    agcr = c.calculate_agcr(games)
    print(f'AGCR is {agcr}.')

    highest_gain = c.calculate_highest_gain(games)
    print(f'Game {highest_gain} will provide the most AGCR increase.')
