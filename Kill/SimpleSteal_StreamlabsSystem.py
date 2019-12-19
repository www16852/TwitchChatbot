#!/usr/bin/python
# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
"""Simple Steal command, replica of the textbased version."""
# ---------------------------------------
# Libraries and references
# ---------------------------------------
import codecs
import json
import os
import winsound
import ctypes
import random

# ---------------------------------------
# [Required] Script information
# ---------------------------------------
ScriptName = "Kill"
Website = "https://www.twitch.tv/www16852"
Creator = "www16852"
Version = "1"
Description = "Simple Kill command"
# ---------------------------------------
# Versions
# ---------------------------------------
""" Releases (open README.txt for full release notes)
1.1 - Fixed cooldowns, added mixer & youtube support
1.0 - Initial Release
"""
# ---------------------------------------
# Variables
# ---------------------------------------
settingsFile = os.path.join(os.path.dirname(__file__), "settings.json")


# ---------------------------------------
# Classes
# ---------------------------------------
class Settings:
    """" Loads settings from file if file is found if not uses default values"""

    # The 'default' variable names need to match UI_Config
    def __init__(self, settingsFile=None):
        if settingsFile and os.path.isfile(settingsFile):
            with codecs.open(settingsFile, encoding='utf-8-sig', mode='r') as f:
                self.__dict__ = json.load(f, encoding='utf-8-sig')
        #正常不會跑else 不過放著這樣看參數比較方便
        #><
        else:
            self.Command = "!kill"
            self.Cost = 10
            self.DeadTime = 10
            self.UseCD = True
            self.Cooldown = 5
            self.OnCooldown = "{0} the command is still on cooldown for {1} seconds!"
            self.UserCooldown = 10
            self.OnUserCooldown = "{0} the command is still on user cooldown for {1} seconds!"
            self.NotEnoughResponse = "{0} you don't have enough {1} to attempt this!"
            self.KillSucessResponse = "{0} Kill {1} pay {2}"

    # Reload settings on save through UI
    def ReloadSettings(self, data):
        """Reload settings on save through UI"""
        self.__dict__ = json.loads(data, encoding='utf-8-sig')
        return

    # Save settings to files (json and js)
    def SaveSettings(self, settingsFile):
        """Save settings to files (json and js)"""
        with codecs.open(settingsFile, encoding='utf-8-sig', mode='w+') as f:
            json.dump(self.__dict__, f, encoding='utf-8-sig')
        with codecs.open(settingsFile.replace("json", "js"), encoding='utf-8-sig', mode='w+') as f:
            f.write("var settings = {0};".format(json.dumps(self.__dict__, encoding='utf-8-sig', ensure_ascii=False)))
        return


# ---------------------------------------
# [OPTIONAL] Settings functions
# ---------------------------------------
def SetDefaults():
    """Set default settings function"""

    # play windows sound
    winsound.MessageBeep()

    # open messagebox with a security check
    MessageBox = ctypes.windll.user32.MessageBoxW
    returnValue = MessageBox(0, u"You are about to reset the settings, "
                                "are you sure you want to contine?"
                             , u"Reset settings file?", 4)

    # if user press "yes"
    if returnValue == 6:
        # Save defaults back to file
        Settings.SaveSettings(MySet, settingsFile)

        # show messagebox that it was complete
        MessageBox = ctypes.windll.user32.MessageBoxW
        returnValue = MessageBox(0, u"Settings successfully restored to default values"
                                 , u"Reset complete!", 0)


# ---------------------------------------
# [Required] functions
# ---------------------------------------
def Init():
    """data on Load, required function"""
    global MySet
    MySet = Settings(settingsFile)


def Execute(data):
    if data.IsChatMessage() and data.GetParam(0) == MySet.Command:
        if IsOnCooldown(data):
            return

        if Parent.RemovePoints(data.User, data.UserName, MySet.Cost):
            user_name = data.GetParam(1)
            SendResp(data, "/timeout {0} {1}".format(user_name, MySet.DeadTime))
            message = MySet.KillSucessResponse.format(data.UserName, user_name, MySet.Cost)
            SendResp(data, message)
            AddCooldown(data)
            return
        else:
            message = MySet.NotEnoughResponse.format(data.UserName, Parent.GetCurrencyName())
            SendResp(data, message)

def Tick():
    """Required tick function"""
    pass


# ---------------------------------------
# [Optional] Functions for usage handling
# ---------------------------------------
def SendResp(data, sendMessage):
    """Sends message to Stream or discord chat depending on settings"""

    if not data.IsFromDiscord() and not data.IsWhisper():
        Parent.SendStreamMessage(sendMessage)

    if not data.IsFromDiscord() and data.IsWhisper():
        Parent.SendStreamWhisper(data.User, sendMessage)

    if data.IsFromDiscord() and not data.IsWhisper():
        Parent.SendDiscordMessage(sendMessage)

    if data.IsFromDiscord() and data.IsWhisper():
        Parent.SendDiscordDM(data.User, sendMessage)


def CheckUsage(data, rUsage):
    """Return true or false depending on the message is sent from
    a source that's in the usage setting or not"""

    if not data.IsFromDiscord():
        l = ["Stream Chat", "Chat Both", "All", "Stream Both"]
        if not data.IsWhisper() and (rUsage in l):
            return True

        l = ["Stream Whisper", "Whisper Both", "All", "Stream Both"]
        if data.IsWhisper() and (rUsage in l):
            return True

    if data.IsFromDiscord():
        l = ["Discord Chat", "Chat Both", "All", "Discord Both"]
        if not data.IsWhisper() and (rUsage in l):
            return True

        l = ["Discord Whisper", "Whisper Both", "All", "Discord Both"]
        if data.IsWhisper() and (rUsage in l):
            return True

    return False

def IsOnCooldown(data):
    """Return true if command is on cooldown and send cooldown message if enabled"""
    cooldown = Parent.IsOnCooldown(ScriptName, MySet.Command)
    userCooldown = Parent.IsOnUserCooldown(ScriptName, MySet.Command, data.User)
    # SendResp(data, "cooldown {0} userCooldown {1}".format(cooldown, userCooldown))
    if (cooldown or userCooldown):

        if MySet.UseCD:
            cooldownDuration = Parent.GetCooldownDuration(ScriptName, MySet.Command)
            userCDD = Parent.GetUserCooldownDuration(ScriptName, MySet.Command, data.User)

            if cooldownDuration > userCDD:
                m_CooldownRemaining = cooldownDuration

                message = MySet.OnCooldown.format(data.UserName, m_CooldownRemaining)
                SendResp(data, message)

            else:
                m_CooldownRemaining = userCDD

                message = MySet.OnUserCooldown.format(data.UserName, m_CooldownRemaining)
                SendResp(data, message)
        return True
    return False

def AddCooldown(data):
    """add cooldowns"""
    Parent.AddUserCooldown(ScriptName, MySet.Command, data.User, MySet.UserCooldown)
    Parent.AddCooldown(ScriptName, MySet.Command, MySet.Cooldown)
        
