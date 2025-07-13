from dataclasses import dataclass

@dataclass
class SteamGame:
    appid: int
    name: str
    achievements_unlocked: int = 0
    achievements_total: int = 0
