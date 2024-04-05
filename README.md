** This branch is no longer used because i started to rewrite the bot **
-> see 'rewrite'-branch for more


# PUG BOT
This Discord Bot manages the PUG Night for the [Munich eSports Discord](https://discord.com/invite/muc)

## A comprehensive list of features:

- [x] Fully automatic queue system
- [x] Teambalancing through FACEIT Elo
- [x] Random captains as well as captains vote
- [x] JSON configuration files for server and privileged roles
- [x] Support for RCON through Discord
- [x] Fully functional webinterface with automatic demo uploads and backend api
- [x] Alot more stuff that i am too lazy to put here since markdown is annoying

## My Todo list:
- [ ] Make map pool votable (technically implemented already, but no logic for it is written)
- [ ] Clean up database design (it is really aweful and convoluted for what could be two tables)
- [ ] Clean up alot of code - sometimes i wonder what i was cooking, sometimes it is just bad ¯\\\_(ツ)_/¯
- [ ] Seasonal leaderboards and "Hall of Fame" on the webinterface - I hate html so that might take a while...
- [ ] Finish this readme
---
### Commands:
|Command|Description|
|-------|-----------|
|/help|Shows more or less this same thing|
|/whoami|Shows information about the steam account you have linked|
|/steam {url}|Link your steam account to your discord account|
|Require privileged role:||
|/pug|Starts a new queue|
|/rcon {mode} {server}|Send a predefined RCON command to a certain server|

### Host it yourself:
To be honest, you really shouldnt use this bot for you personal projects, since most things are currently hardcoded either to my test server or the Munich eSports Discord,
but if you are knowledgeable with discord.py and python in general you could probably make it work.
Once this project is at a stage where i feel comfortable with it i will release a public version
