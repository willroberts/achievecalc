# achievement-calc

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
client = SteamClient(api_key='abc', steamid=123) # Create an API client.
games = client.get_owned_games()                 # Fetch games and achievements from API.
client.calculate_agcr(games)                     # Compute Average Game Completion Rate.
client.calculate_highest_gain(games)             # Find highest per-achievement opportunity.
client.top_detractors(games, top=10)             # Find top AGCR detractors.
```

See `main.py` for a more complete example.
