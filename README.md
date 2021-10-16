#Discord bot
### Developed for LU gaming discord

-------------------------

Based on discord.py package

##Dependencies
>python 3.x

Packages:
``` 
pip install discord.py dislash.py asyncio
```

------------------

When updating database, it is recommended to make updates both in DB.migrate_db() and 
all of DB.__drop_tables(), DB.__create_tables() and DB.__seed_tables()