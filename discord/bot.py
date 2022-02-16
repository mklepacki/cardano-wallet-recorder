from discord.ext import commands
from discord.user import User
from discord.guild import Guild, Member, Role
from dislash import slash_commands
from dislash.interactions import *
import os
import psycopg2
import requests
from cardano_verify import verify_address

client = commands.Bot(command_prefix="!")
slash = slash_commands.SlashClient(client)

@slash.command(
    name="register-ergo",
    description="Register your address for the airdrop.",
    options=[Option("address","Your ergo wallet address",OptionType.STRING,required=True)]
    )
async def register-ergo(interaction: SlashInteraction, address: str):
    # ------------- get user & guild ------------------
    guild: Guild = interaction.guild
    member: Member = interaction.author
    user: User = interaction.author

    # ------------- get wallet info based on address ---------------
    r = requests.get(f'{os.environ.get("ERGO_NODE")}/utils/address/{address}')
    res = r.json()

    # -------------- if wallet is valid save it in the DB ------------------
    if res['isValid']:
        with psycopg2.connect(
            host=os.environ.get("POSTGRES_HOST"),
            port=os.environ.get("POSTGRES_PORT"),
            database=os.environ.get('POSTGRES_DB'),
            user=os.environ.get('POSTGRES_USER'),
            password=os.environ.get('POSTGRES_PASSWORD')
            ) as conn:
            with conn.cursor() as cur:
                cur.execute("""INSERT INTO discord_wallets 
                (guild_id,user_id,user_name,guild_join_date,wallet_address) 
                VALUES 
                (%s,%s,%s,%s,%s)
                ON CONFLICT ON CONSTRAINT "discord_wallets_GUILD_ID_USER_ID"
                DO UPDATE SET
                (user_name, wallet_address, wallet_update_ts)
                = (EXCLUDED.user_name, EXCLUDED.wallet_address, CURRENT_TIMESTAMP)""",(
                    guild.id,
                    user.id,
                    member.display_name,
                    member.joined_at,
                    address
                    ))
                conn.commit()
                # this seems redundant 
                # ---------------------------
                # cur.execute("""
                # SELECT count(*) from discord_wallets
                # where guild_id = '%s' and wallet_registration_ts <= (select wallet_registration_ts from discord_wallets where user_id = '%s' and guild_id = '%s')
                # """,(guild.id,user.id,guild.id))
                # count = cur.fetchone()[0]
                # ---------------------------
                extra = f"🦾 We'll keep this on hand for any future airdrops and events!😇"
                # if guild.id == 876475955701501962:
                    
                    # this seems redundant
                    # ---------------------------------------
                    # cur.execute("""
                    # SELECT count(*) from discord_users
                    # where guild_id = '%s' and join_date <= (select join_date from discord_users where user_id = '%s' and guild_id = '%s')
                    # """,(guild.id,user.id,guild.id))
                    # ogcount = cur.fetchone()[0]

                    # if ogcount > 0 and ogcount <= 1500:
                    #     extra = f"You were Discord member number {ogcount}, congratulations and thank you for being one of the first 1,500 Discord members to join our community. 😇 You are now successfully registered and will receive your airdrop soon!🥳🎉"
                    # ----------------------------------------
                    
                    # ---------- OG badge is no longer available -----------
                    # for r in guild.roles:
                    #     role: Role = r
                    #     if role.name == "OG":
                    #         await member.add_roles(role)
                    #  ---------------------------------------
                await interaction.reply(f"CONGRATULATIONS! 🎊 You successfully registered your Ergo Wallet address. {extra}")
    else:
        await interaction.reply("ERROR! Please re-enter a valid Ergo wallet address.")

@slash.command(
    name="register-cardano",
    description="Register your address to get LISO badge.",
    options=[Option("address","Your Cardano wallet address",OptionType.STRING,required=True)]
    )
async def register-ergo(interaction: SlashInteraction, address: str):
    # ------------- get user & guild ------------------
    guild: Guild = interaction.guild
    member: Member = interaction.author
    user: User = interaction.author

    # -------------- if wallet is valid save it in the DB ------------------
    # Important !!!!!!!
    # Add blockfrost_project_id
    if verify_address(address, os.environ.get('blockfrost_project_id')):
        with psycopg2.connect(
            host=os.environ.get("POSTGRES_HOST"),
            port=os.environ.get("POSTGRES_PORT"),
            database=os.environ.get('POSTGRES_DB'),
            user=os.environ.get('POSTGRES_USER'),
            password=os.environ.get('POSTGRES_PASSWORD')
            ) as conn:
            # Important !!!!
            # Create discord_cardano_wallets table that uses schema of discord_wallets tabel used for ERGO
            with conn.cursor() as cur:
                cur.execute("""INSERT INTO discord_cardano_wallets 
                (guild_id,user_id,user_name,guild_join_date,wallet_address) 
                VALUES 
                (%s,%s,%s,%s,%s)
                ON CONFLICT ON CONSTRAINT "discord_cardano_wallets_GUILD_ID_USER_ID"
                DO UPDATE SET
                (user_name, wallet_address, wallet_update_ts)
                = (EXCLUDED.user_name, EXCLUDED.wallet_address, CURRENT_TIMESTAMP)""",(
                    guild.id,
                    user.id,
                    member.display_name,
                    member.joined_at,
                    address
                    ))
                conn.commit()
                extra = f"🦾 We'll keep this on hand for any future airdrops and events!😇"
                if guild.id == 876475955701501962:
                    for r in guild.roles:
                        role: Role = r
                        if role.name == "LISO":
                            await member.add_roles(role)
                await interaction.reply(f"CONGRATULATIONS! 🎊 You successfully registered your Cardano Wallet address. {extra}")
    else:
        await interaction.reply("ERROR! Please re-enter a valid Cardano wallet address.")

client.run(os.environ.get("DISCORD_KEY"))