# PUG BOT
This Discord Bot manages the PUG Night for the [Munich eSports Discord](https://discord.com/invite/muc)



[changelog (for rewrite)](change_log.md)




# Roadmap

## Basics

- [x] .env and appsettings.json config files for various api tokens, cs2 servers and other settings
- [x] database for users and matches
- [x] running bot

## Implement all necessary commands

- [x] implement /profile
- [x] implement /pug
- [x] implement /rcon
- [ ] implement /help

## Bot sided Match Logic

- [x] pug interface
- [x] support for custom map pools
- [x] support for BO1/BO3/BO5
- [x] map voting
- [ ] pushing matches onto a free server

## Webinterface

- [ ] setup webinterface
- [ ] setup api
- [ ] leaderboards

## Far Future - Nice to haves

- [ ] ...
- [ ] ...
- [ ] ...


# To Do list

- [todo.md](todo.md)


---
### Current Commands:
|Command|Description|
|-------|-----------|
|/profile|Manage ur bot "profile"|
|Require privileged role:||
|/pug {map_pool} {bo1/bo3/bo5}|Starts a new queue|
|/rcon {mode} {server}|Send a predefined RCON command to a certain server|

### Host it yourself:
To be honest, you really shouldnt use this bot for you personal projects, altho basically nothing is hardcoded anymore, its far from usable,
but if you are knowledgeable with discord.py and python in general you could probably make it work.
Once this project is at a stage where i feel comfortable with it i will release a public version