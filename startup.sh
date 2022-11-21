#!/bin/bash

screen -dmS LU_gaming_bot bash -c 'exec bash'
screen -r LU_gaming_bot -X stuff "mamba activate LU_BOT \n"
screen -r LU_gaming_bot -X stuff "python3.9 '/mnt/data/LU_BOT/bot.py' \n"