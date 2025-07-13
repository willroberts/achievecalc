# achievecalc

Returns the top game in your Steam library which will contribute the most value
to Average Game Completion Rate (AGCR).

To use Achievement APIs, you must set the privacy settings for 'My Profile' and
'Game Details' to 'Public'. You must also uncheck 'Always keep my total
playtime private'.

## Dependencies

Built with `steam==1.4.4`.
```
virtualenv env
source env/bin/activate
pip install -r requirements.txt
```

## Usage

```python
>>> c = SteamClient(api_key='abcd1234', steamid=1234)
>>> games = c.get_owned_games() # cached locally at games.json
>>> c.calculate_agcr(games)
0.12345
>>> c.calculate_highest_gain(games)
Game(appid=234900, name='Anodyne', achievements_unlocked=1, achievements_total=6)
```

See `main.py` for a complete example.
