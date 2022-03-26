###
# Copyright (c) 2022, cottongin
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions, and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions, and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the author of this software nor the name of
#     contributors to this software may be used to endorse or promote products
#     derived from this software without specific prior written consent.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

###

import random

# import pendulum
from sopel.formatting import bold, color, colors, underline
from sopel.plugin import commands, example
import sopel.tools as tools

# from supybot import utils, plugins, ircutils, callbacks
# from supybot.commands import *
# try:
#     from supybot.i18n import PluginInternationalization
#     _ = PluginInternationalization('AlbumPicker')
# except ImportError:
#     # Placeholder that allows to run the plugin on a bot
#     # without the i18n module
#     _ = lambda x: x


# def sanity(irc, msg, args, state):
#     # args[0] is the string/input being converted
#     date = args[0]
#     # one could create custom strings to parse, like 'yesterday', etc
#     valid = ['yesterday', 'tomorrow']
#     check = None
#     try:
#         if date.lower() in valid:
#             if date.lower() == 'yesterday':
#                 # note, thie format should be what you want to use in your plugin
#                 check = pendulum.yesterday().format('MM/DD/YYYY') 
#             else:
#                 # note, thie format should be what you want to use in your plugin
#                 check = pendulum.tomorrow().format('MM/DD/YYYY')
#         else:
#             # this is the magic, care of pendulum.parse and strict=False
#             # note, thie format should be what you want to use in your plugin
#             check = pendulum.parse(date, strict=False).format('MM/DD/YYYY')
#     except:
#         # we didn't get a valid date back
#         pass
#     if not check:
#         # this will cause the command to not even execute!! perfect, no more
#         # checking the date manually in the command
#         state.errorInvalid(_('date format'), str(date))
#     else:
#         # we have a valid date, let's append it 
#         state.args.append(check)
#         del args[0]
# # now we add it to the converter list
# addConverter('validDate', getValidDateFmt)


def setup(bot):
    bot.memory['discchanger_current_albums'] = {}

def shutdown(bot):
    bot.memory.pop('discchanger_current_albums', None)

# TODO sanity check input
@commands('loadchanger', 'loaddiscs', 'ldc', 'ldd')
def loadchanger(bot, trigger):
    """Load up the disc changer"""
    if bot.memory['discchanger_current_albums']:
        bot.reply("I already have some albums loaded!")
        return
    if not trigger.group(2):
        bot.reply("I need a list of albums (ex: 1t13 2t12t11)")
        return
    albums = trigger.group(2).lower()
    albums = albums.split()

    for playlist_idx, album in enumerate(albums, start=1):
        # [INDEX]t[NUMBER OF TRACKS]t[NUMBER OF TRACKS]
        tmp = {}
        for discnum, disc in enumerate(album.split("t")[1:], start=1):
            # create a temporary track list of each disc for tracking
            # whether the track has been played
            # tmp.append(list(range(1, int(disc)+1)))
            tmp[discnum] = list(range(1, int(disc)+1))
        bot.memory['discchanger_current_albums'][playlist_idx] = tmp

    bot.say("OK, loaded up")
    return

# TODO make this voice/op/admin only?
@commands('clearchanger', 'cleardiscs', 'clrc', 'clrd')
def clearchanger(bot, trigger):
    """clear the CD changer out"""
    bot.memory['discchanger_current_albums'] = {}
    return bot.say("OK, cleared")

@commands('pickasong', 'ps')
def pickasong(bot, trigger):
    """Pick an album, any album"""
    if not bot.memory['discchanger_current_albums']:
        bot.reply("No albums loaded in the changer!")
        return

    # # remove empties
    for alb in bot.memory['discchanger_current_albums']:
        bot.memory['discchanger_current_albums'][alb] = {k: v for k, v in bot.memory['discchanger_current_albums'][alb].items() if v}
    temp_albums = {*bot.memory['discchanger_current_albums']}
    for alb in temp_albums:
        try:
            if not bot.memory['discchanger_current_albums'][alb]:
                bot.memory['discchanger_current_albums'].pop(alb)
        except:
            continue
    # self.current_albums = list(filter(None, self.current_albums))

    if not bot.memory['discchanger_current_albums']:
        bot.reply("I've run out of songs, load some more")
        return

    # first pick an album
    album_index, album_choice = random.choice(list(filter(None, bot.memory['discchanger_current_albums'].items())))
    if not album_choice:
        bot.reply("Sorry, I couldn't pick an album")
        return

    # number_of_discs = len(self.current_albums[album_index])

    disc_index, disc_choice = random.choice(list(album_choice.items()))
    if not disc_choice:
        bot.reply("Sorry, I couldn't pick a song")
        return

    # now pick a song and pop it so it doesn't get picked again
    song_choice = bot.memory['discchanger_current_albums'][album_index][disc_index].pop(
        random.choice(range(len(disc_choice)))
    )

    reply_string = "{nick} picked {track} from {disc} on {album}"

    reply_string = reply_string.format(
        nick=trigger.nick,
        track=bold(underline("Track #{}".format(song_choice))), 
        disc=color(bold("Disc/Side {}".format(disc_index)), colors.BLUE),
        album=color(bold("Album #{}".format(album_index)), colors.GREEN),
    )

    bot.say(reply_string)
    # # remove empties
    # self.current_albums = {k: v for k, v in self.current_albums.items() if v}
    for alb in bot.memory['discchanger_current_albums']:
        bot.memory['discchanger_current_albums'][alb] = {k: v for k, v in bot.memory['discchanger_current_albums'][alb].items() if v}
    return


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
