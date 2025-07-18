# achievement-calc

Returns the top games in your Steam library which will contribute the most value
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
# Create an API client.
c = SteamClient(api_key='abc')

# Fetch games and achievements from API.
games = c.get_owned_games(steam_id=123)

# Compute Average Game Completion Rate.
c.calculate_agcr(games)

# Find top AGCR opportunities.
c.top_agcr_opportunities(games, top=10)

# Find top AGCR detractors.
c.top_agcr_detractors(games, top=10)
```

See `main.py` for a more complete example.
