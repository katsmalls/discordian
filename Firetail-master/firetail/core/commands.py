import asyncio
import json
import os

import aiohttp
import discord
from discord.ext import commands

from firetail.core import checks
from firetail import utils


class Core:
    """General bot functions."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="shutdown", aliases=["exit"])
    @checks.is_owner()
    async def _shutdown(self, ctx):
        """Shuts down the bot"""
        embed = utils.make_embed(
            title='Shutting down.',
            msg_colour='red',
            icon="https://i.imgur.com/uBYS8DR.png")
        try:
            await ctx.send(embed=embed)
        except discord.HTTPException:
            pass
        await ctx.bot.shutdown()

    @commands.command(name="break")
    @checks.is_owner()
    async def _break(self, ctx):
        """Simulates a sudden disconnection."""
        embed = utils.make_embed(msg_type='warning',
                                 title='Faking a crash...')
        try:
            await ctx.send(embed=embed)
        except discord.HTTPException:
            pass
        await ctx.bot.logout()

    @commands.command(name="restart")
    @checks.is_owner()
    async def _restart(self, ctx):
        """Restarts the bot"""
        embed = utils.make_embed(
            title='Restarting.',
            msg_colour='red',
            icon="https://i.imgur.com/uBYS8DR.png")
        try:
            await ctx.send(embed=embed)
        except discord.HTTPException:
            pass
        await ctx.bot.shutdown(restart=True)

    @commands.group(name="set")
    @checks.is_co_owner()
    async def _set(self, ctx):
        """Changes bot settings"""
        if ctx.invoked_subcommand is None:
            await ctx.bot.send_cmd_help(ctx)

    @_set.command(name="game")
    @checks.is_co_owner()
    @commands.guild_only()
    async def _game(self, ctx, *, game: str):
        """Sets bot game status"""
        status = ctx.me.status
        game = discord.Game(name=game)
        await ctx.bot.change_presence(status=status, game=game)
        embed = utils.make_embed(msg_type='success',
                                 title='Game set.')
        await ctx.send(embed=embed)

    @_set.command(name="status")
    @checks.is_co_owner()
    @commands.guild_only()
    async def status(self, ctx, *, status: str):
        """Sets bot status
        Available statuses:
            online
            idle
            dnd
        """

        statuses = {
            "online"    : discord.Status.online,
            "idle"      : discord.Status.idle,
            "dnd"       : discord.Status.dnd,
            "invisible" : discord.Status.invisible
            }

        game = ctx.me.game

        try:
            status = statuses[status.lower()]
        except KeyError:
            await ctx.bot.send_cmd_help(ctx)
        else:
            await ctx.bot.change_presence(status=status,
                                          game=game)
            embed = utils.make_embed(
                msg_type='success',
                title="Status changed to {}.".format(status))
            await ctx.send(embed=embed)

    @_set.command(name="username", aliases=["name"])
    @checks.is_co_owner()
    async def _username(self, ctx, *, username: str):
        """Sets bot username"""
        try:
            await ctx.bot.user.edit(username=username)
        except discord.HTTPException:
            embed = utils.make_embed(
                msg_type='error',
                title="Failed to change name",
                content=("Remember that you can only do it up to 2 times an "
                         "hour. Use nicknames if you need frequent changes. "
                         "**{}set nickname**").format(ctx.prefix))
            await ctx.send(embed=embed)
        else:
            embed = utils.make_embed(
                msg_type='success',
                title="Username set.")
            await ctx.send(embed=embed)

    @_set.command(name="avatar")
    @checks.is_co_owner()
    async def _avatar(self, ctx, *, avatar_url: str):
        """Sets bot avatar"""
        session = aiohttp.ClientSession()
        async with session.get(avatar_url) as req:
            data = await req.read()
        await session.close()
        try:
            await ctx.bot.user.edit(avatar=data)
        except discord.HTTPException:
            embed = utils.make_embed(
                msg_type='error',
                title="Failed to set avatar",
                content=("Remember that you can only do it up to 2 "
                         "times an hour. URL must be a direct link to "
                         "a JPG / PNG."))
            await ctx.send(embed=embed)
        else:
            embed = utils.make_embed(
                msg_type='success',
                title="Avatar set.")
            await ctx.send(embed=embed)

    @_set.command(name="nickname")
    @checks.admin()
    @commands.guild_only()
    async def _nickname(self, ctx, *, nickname: str):
        """Sets bot nickname"""
        try:
            await ctx.guild.me.edit(nick=nickname)
        except discord.Forbidden:
            embed = utils.make_embed(
                msg_type='success',
                title="Failed to set nickname",
                content=("I'm missing permissions to change my nickname. "
                         "Use **{}get guildperms** to check permissions."
                         "").format(ctx.prefix))
            await ctx.send()
        else:
            embed = utils.make_embed(
                msg_type='success',
                title="Nickname set.")
            await ctx.send(embed=embed)

    @commands.command(name="uptime")
    async def _uptime(self, ctx):
        """Shows bot uptime"""
        uptime_str = ctx.bot.uptime_str
        embed = utils.make_embed(
            title='Uptime',
            content=uptime_str,
            msg_colour='blue',
            icon="https://i.imgur.com/82Cqf1x.png")
        try:
            await ctx.send(embed=embed)
        except discord.errors.Forbidden:
            await ctx.send("Uptime: {}".format(uptime_str))

    @commands.command(name="botinvite")
    async def _bot_invite(self, ctx, plain_url: bool = False):
        """Shows bot invite url"""
        invite_url = ctx.bot.invite_url
        if plain_url:
            await ctx.send("Invite URL: <{}>".format(invite_url))
            return
        else:
            embed = utils.make_embed(
                title='Click to invite me to your server!',
                title_url=invite_url,
                msg_colour='blue',
                icon="https://i.imgur.com/DtPWJPG.png")
        try:
            await ctx.send(embed=embed)
        except discord.errors.Forbidden:
            await ctx.send("Invite URL: <{}>".format(invite_url))

    @commands.command(name="about")
    async def _about(self, ctx):
        """Shows info about Firetail"""
        bot = ctx.bot
        author_repo = "https://github.com/shibdib"
        bot_repo = author_repo + "/Firetail"
        server_url = "https://discord.gg/ZWmzTP3"
        owner = await bot.get_user_info(ctx.bot.owner)
        uptime_str = bot.uptime_str
        invite_str = ("[Click to invite me to your server!]({})"
                      "").format(bot.invite_url)

        about = (
            "I'm a Discord bot to help organise and coordinate EVE Online "
            "communities!\n\n"
            "To learn about what I do either use the `!help` command, or "
            "check the [documentation here]({bot_repo}).\n\n"
            "[Join our support server]({server_invite}) if you have any "
            "questions or feedback.\n\n"
            "").format(bot_repo=bot_repo, server_invite=server_url)

        member_count = 0
        server_count = 0
        for guild in bot.guilds:
            server_count += 1
            member_count += len(guild.members)

        embed = utils.make_embed(
            msg_type='info', title="About Firetail", content=about)
        embed.set_thumbnail(url=bot.user.avatar_url_as(format='png'))
        embed.add_field(name="Owner", value=owner)
        embed.add_field(name="Uptime", value=uptime_str)
        embed.add_field(name="Servers", value=server_count)
        embed.add_field(name="Members", value=member_count)
        embed.add_field(name="Commands Used", value=bot.command_count)
        embed.add_field(name="Messages Read", value=bot.message_count)
        embed.add_field(name="Invite Link", value=invite_str)
        footer_txt = ("For support, contact us on our Discord server. "
                      "Invite Code: ZWmzTP3")
        embed.set_footer(text=footer_txt)

        try:
            await ctx.send(embed=embed)
        except discord.HTTPException:
            await ctx.send("I need the `Embed links` permission to send this")

    @commands.group(name="get")
    @checks.is_co_owner()
    async def _get(self, ctx):
        """Gets bot settings"""
        if ctx.invoked_subcommand is None:
            await ctx.bot.send_cmd_help(ctx)

    @_get.command(name="guildperms")
    @checks.is_co_owner()
    async def guildperms(self, ctx):
        """Gets bot permissions for the current guild."""
        guild_perms = ctx.guild.me.guild_permissions
        req_perms = ctx.bot.req_perms
        perms_compare = guild_perms >= req_perms
        core_dir = ctx.bot.core_dir
        data_dir = os.path.join(core_dir, '..', 'data')
        data_file = 'permissions.json'
        msg = "Guild Permissions: {}\n".format(guild_perms.value)
        msg += "Met Minimum Permissions: {}\n\n".format(str(perms_compare))

        with open(os.path.join(data_dir, data_file), "r") as perm_json:
            perm_dict = json.load(perm_json)

        for perm, bitshift in perm_dict.items():
            if bool((req_perms.value >> bitshift) & 1):
                if bool((guild_perms.value >> bitshift) & 1):
                    msg += ":white_small_square:  {}\n".format(perm)
                else:
                    msg += ":black_small_square:  {}\n".format(perm)

        try:
            if guild_perms.embed_links:
                embed = utils.make_embed(
                    msg_type='info',
                    title='Guild Permissions',
                    content=msg)
                await ctx.send(embed=embed)
            else:
                await ctx.send(msg)
        except discord.errors.Forbidden:
            embed = utils.make_embed(
                msg_type='info',
                title='Guild Permissions',
                content=msg)
            await ctx.author.send(embed=embed)

    @_get.command(name="channelperms")
    @checks.is_co_owner()
    async def channelperms(self, ctx):
        """Gets bot permissions for the current channel."""
        chan_perms = ctx.channel.permissions_for(ctx.guild.me)
        req_perms = ctx.bot.req_perms
        perms_compare = chan_perms >= req_perms
        core_dir = ctx.bot.core_dir
        data_dir = os.path.join(core_dir, '..', 'data')
        data_file = 'permissions.json'
        msg = "Channel Permissions: {}\n".format(chan_perms.value)
        msg += "Met Minimum Permissions: {}\n\n".format(str(perms_compare))

        with open(os.path.join(data_dir, data_file), "r") as perm_json:
            perm_dict = json.load(perm_json)

        for perm, bitshift in perm_dict.items():
            if bool((req_perms.value >> bitshift) & 1):
                if bool((chan_perms.value >> bitshift) & 1):
                    msg += ":white_small_square:  {perm}\n".format(perm)
                else:
                    msg += ":black_small_square:  {perm}\n".format(perm)
        try:
            if chan_perms.embed_links:
                embed = utils.make_embed(
                    msg_type='info',
                    title='Channel Permissions',
                    content=msg)
                await ctx.send(embed=embed)
            else:
                await ctx.send(msg)
        except discord.errors.Forbidden:
            embed = utils.make_embed(
                msg_type='info',
                title='Channel Permissions',
                content=msg)
            await ctx.author.send(embed=embed)

    @_get.command(name="sessions_resumed")
    async def _sessions_resumed(self, ctx):
        """Gets the number of websocket reconnections."""
        r_c = ctx.bot.resumed_count
        embed = utils.make_embed(
            msg_type='info',
            title="Connections Resumed: {}".format(r_c))
        await ctx.send(embed=embed)

    @commands.command(name="ping")
    async def _ping(self, ctx):
        """Gets the discord server response time."""
        msg = ("{0:.2f} ms").format(ctx.bot.ws.latency * 1000)
        embed = utils.make_embed(
            msg_type='info',
            title='Bot Latency: {}'.format(msg))
        await ctx.send(embed=embed)

    @commands.command(name="purge")
    @checks.is_co_owner()
    async def purge(self, ctx, msg_number: int = 10):
        """Delete a number of messages from the channel.
        Default is 10. Max 100."""
        if msg_number > 100:
            embed = utils.make_embed(
                msg_type='info',
                title="ERROR",
                content="No more than 100 messages can be purged at a time.",
                guild=ctx.guild)
            await ctx.send(embed=embed)
            return
        deleted = await ctx.channel.purge(limit=msg_number)
        embed = utils.make_embed()
        result_msg = await ctx.send('Deleted {} message{}'.format(
            len(deleted), "s" if len(deleted) > 1 else ""))
        await asyncio.sleep(3)
        await result_msg.delete()

    @commands.command(name="reload_em")
    @checks.is_co_owner()
    async def reload_em(self, ctx):
        """Reload Extension Manager."""
        bot = ctx.bot
        try:
            bot.unload_extension('firetail.core.extension_manager')
            bot.load_extension('firetail.core.extension_manager')
            embed = utils.make_embed(msg_type='success',
                                     title='Extension Manager reloaded.')
            await ctx.send(embed=embed)
        except Exception as e:
            msg = "{}: {}".format(type(e).__name__, e)
            embed = utils.make_embed(msg_type='error',
                                     title='Error loading Extension Manager',
                                     content=msg)
            await ctx.send(embed=embed)

    @commands.command(name="prefix")
    async def _prefix(self, ctx, *, new_prefix: str = None):
        """Get and set server prefix.
        Use the argument 'reset' to reset the guild prefix to default.
        """
        bot = ctx.bot
        default_prefix = bot.default_prefix
        if ctx.guild:
            if new_prefix:
                await bot.data.guild(ctx.guild.id).prefix(new_prefix)
                if new_prefix.lower() == 'reset':
                    new_prefix = bot.default_prefix
                embed = utils.make_embed(
                    msg_type='success', title="Prefix set to {}".format(new_prefix))
                await ctx.send(embed=embed)
            else:
                guild_prefix = await bot.data.guild(ctx.guild).prefix()
                prefix = guild_prefix if guild_prefix else default_prefix
                if len(prefix) > 1:
                    prefix = ', '.join(default_prefix)
                else:
                    prefix = prefix[0]
                embed = utils.make_embed(
                    msg_type='info', title="Prefix is {}".format(prefix))
                await ctx.send(embed=embed)
        else:
            if len(default_prefix) > 1:
                prefix = ', '.join(default_prefix)
            else:
                prefix = default_prefix[0]
            embed = utils.make_embed(
                msg_type='info', title="Prefix is {}".format(prefix))
            await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Core(bot))
