# Go Game Now (GGN)

A Windows desktop application for playing the game of Go against a local AI opponent. No internet connection required — everything runs on your machine.

## Features

- Play on 9x9, 13x13, or 19x19 boards
- Choose your opponent's strength on the traditional kyu/dan rating scale, from 20 kyu up to 9 dan
- Full ruleset: captures, basic ko rule, area scoring, pass, resign
- Calm, original piano soundtrack

## The AI: Bloom

The opponent is powered by a single engine called **Bloom**.

Bloom is not a neural network. It is a hand-written engine that combines move-scoring heuristics with a shallow minimax search, and it is deliberately built this way: a single codebase whose *playing strength is a parameter*, not a separate model per level.

When you pick a rank in the menu (say, `7k` or `4d`), the game loads a preset for that rank that controls three things inside Bloom:

- **Randomness** — how often Bloom ignores its own analysis and plays a weaker, more human-like move. High at low kyu levels, close to zero at dan levels.
- **Precision** — how strictly Bloom sticks to its best-found move versus a good-enough one. Increases with rank.
- **Search depth** — at low ranks, Bloom only evaluates the immediate position (captures, atari, liberties, board influence). At higher ranks, it adds a limited-depth minimax look-ahead, narrowed to a small pool of promising candidate moves so it stays responsive even on a 19x19 board.

In short: there are not 29 different bots, there is one engine that gets more careful, more far-sighted, and less random as the selected rank increases.

Bloom's evaluation considers: capturing opponent groups, avoiding self-atari, extending groups that are low on liberties, pressuring opponent groups that are low on liberties, and area score (stones + surrounded territory) at deeper search levels.

Because Bloom is a heuristic/search engine rather than a trained model, its ranks are a relative difficulty scale within the game, not a certified equivalent to official Go rating federations.

## Installation

Download the installer from [Releases](../../releases) and run it.

## Running from source

```
pip install pygame
cd src
python main.py
```

## Project status

In development (MVP).

## Credits

Original soundtrack composed and performed on piano by Savva Poliakov.

## License

All rights reserved — see [LICENSE](LICENSE).
