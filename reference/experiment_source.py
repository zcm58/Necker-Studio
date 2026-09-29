#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This experiment was created using PsychoPy3 Experiment Builder (v2026.2.3),
    on September 29, 2026, at 16:15
If you publish work using this script the most relevant publication is:

    Peirce J, Gray JR, Simpson S, MacAskill M, Höchenberger R, Sogo H, Kastman E, Lindeløv JK. (2019) 
        PsychoPy2: Experiments in behavior made easy Behav Res 51: 195. 
        https://doi.org/10.3758/s13428-018-01193-y

"""

# --- Import packages ---
from psychopy import locale_setup
from psychopy import prefs
from psychopy import plugins
plugins.activatePlugins()
from psychopy import sound, gui, visual, core, data, event, logging, clock, colors, layout, hardware
from psychopy.tools import environmenttools
from psychopy.constants import (
    NOT_STARTED, STARTED, PLAYING, PAUSED, STOPPED, STOPPING, FINISHED, PRESSED, 
    RELEASED, FOREVER, priority
)

import numpy as np  # whole numpy lib is available, prepend 'np.'
from numpy import (sin, cos, tan, log, log10, pi, average,
                   sqrt, std, deg2rad, rad2deg, linspace, asarray)
from numpy.random import random, randint, normal, shuffle, choice as randchoice
import os  # handy system and path functions
import sys  # to get file system encoding

import psychopy.iohub as io
from psychopy.hardware import keyboard
import psychopy.hardware.speaker

# set audio backend
sound.Sound.backend = prefs.hardware['audioLib']
hardware.speaker.SpeakerDevice.backend = prefs.hardware['audioLib']
# --- Setup global variables (available in all functions) ---
# create a device manager to handle hardware (keyboards, mice, mirophones, speakers, etc.)
deviceManager = hardware.DeviceManager()
# ensure that relative paths start from the same directory as this script
_thisDir = os.path.dirname(os.path.abspath(__file__))
# store info about the experiment session
psychopyVersion = '2026.2.3'
expName = 'Necker_with_sound_conditioning2'  # from the Builder filename that created this script
expVersion = ''
# a list of functions to run when the experiment ends (starts off blank)
runAtExit = []
# information about this experiment
expInfo = {
    'participant_ID': '',
    'age': '',
    'sex': '',
    'handedness (left or right)': '',
    'date|hid': data.getDateStr(),
    'expName|hid': expName,
    'expVersion|hid': expVersion,
    'psychopyVersion|hid': psychopyVersion,
}

# --- Define some variables which will change depending on pilot mode ---
'''
To run in pilot mode, either use the run/pilot toggle in Builder, Coder and Runner, 
or run the experiment with `--pilot` as an argument. To change what pilot 
#mode does, check out the 'Pilot mode' tab in preferences.
'''
# work out from system args whether we are running in pilot mode
PILOTING = core.setPilotModeFromArgs()
# start off with values from experiment settings
_fullScr = True
_winSize = [1920, 1080]
# if in pilot mode, apply overrides according to preferences
if PILOTING:
    # force windowed mode
    if prefs.piloting['forceWindowed']:
        _fullScr = False
        # set window size
        _winSize = prefs.piloting['forcedWindowSize']

def showExpInfoDlg(expInfo):
    """
    Show participant info dialog.
    Parameters
    ==========
    expInfo : dict
        Information about this experiment.
    
    Returns
    ==========
    dict
        Information about this experiment.
    """
    # show participant info dialog
    dlg = gui.DlgFromDict(
        dictionary=expInfo, sortKeys=False, title=expName, alwaysOnTop=True
    )
    if dlg.OK == False:
        core.quit()  # user pressed cancel
    # return expInfo
    return expInfo


def setupData(expInfo, dataDir=None):
    """
    Make an ExperimentHandler to handle trials and saving.
    
    Parameters
    ==========
    expInfo : dict
        Information about this experiment, created by the `setupExpInfo` function.
    dataDir : Path, str or None
        Folder to save the data to, leave as None to create a folder in the current directory.    
    Returns
    ==========
    psychopy.data.ExperimentHandler
        Handler object for this experiment, contains the data to save and information about 
        where to save it to.
    """
    # remove dialog-specific syntax from expInfo
    for key, val in expInfo.copy().items():
        newKey, _ = data.utils.parsePipeSyntax(key)
        expInfo[newKey] = expInfo.pop(key)
    
    # data file name stem = absolute path + name; later add .psyexp, .csv, .log, etc
    if dataDir is None:
        dataDir = _thisDir
    filename = u'data/%s_%s_%s' % (expInfo['participant_ID'], expName, expInfo['date'])
    # make sure filename is relative to dataDir
    if os.path.isabs(filename):
        dataDir = os.path.commonprefix([dataDir, filename])
        filename = os.path.relpath(filename, dataDir)
    
    # an ExperimentHandler isn't essential but helps with data saving
    thisExp = data.ExperimentHandler(
        name=expName, version=expVersion,
        extraInfo=expInfo, runtimeInfo=None,
        originPath='C:\\Users\\djv92\\OneDrive - Mississippi State University\\NERD\\1 - Experiments\\Necker\\__NEW_NECKER_lastrun.py',
        savePickle=True, saveWideText=True,
        dataFileName=dataDir + os.sep + filename, sortColumns='time'
    )
    # store pilot mode in data file
    thisExp.addData('piloting', PILOTING, priority=priority.LOW)
    thisExp.setPriority('thisRow.t', priority.CRITICAL)
    thisExp.setPriority('expName', priority.LOW)
    # return experiment handler
    return thisExp


def setupLogging(filename):
    """
    Setup a log file and tell it what level to log at.
    
    Parameters
    ==========
    filename : str or pathlib.Path
        Filename to save log file and data files as, doesn't need an extension.
    
    Returns
    ==========
    psychopy.logging.LogFile
        Text stream to receive inputs from the logging system.
    """
    # set how much information should be printed to the console / app
    if PILOTING:
        logging.console.setLevel(
            prefs.piloting['pilotConsoleLoggingLevel']
        )
    else:
        logging.console.setLevel('warning')
    # save a log file for detail verbose info
    logFile = logging.LogFile(filename+'.log')
    if PILOTING:
        logFile.setLevel(
            prefs.piloting['pilotLoggingLevel']
        )
    else:
        logFile.setLevel(
            logging.getLevel('exp')
        )
    
    return logFile


def setupWindow(expInfo=None, win=None):
    """
    Setup the Window
    
    Parameters
    ==========
    expInfo : dict
        Information about this experiment, created by the `setupExpInfo` function.
    win : psychopy.visual.Window
        Window to setup - leave as None to create a new window.
    
    Returns
    ==========
    psychopy.visual.Window
        Window in which to run this experiment.
    """
    if PILOTING:
        logging.debug('Fullscreen settings ignored as running in pilot mode.')
    
    if win is None:
        # if not given a window to setup, make one
        win = visual.Window(
            size=_winSize, fullscr=_fullScr, screen=0,
            winType='pyglet', allowGUI=False, allowStencil=False,
            monitor='testMonitor', color=[0.0039, 0.0039, 0.0039], colorSpace='rgb',
            backgroundImage='', backgroundFit='none',
            blendMode='avg', useFBO=True,
            units='height',
            checkTiming=False  # we're going to do this ourselves in a moment
        )
    else:
        # if we have a window, just set the attributes which are safe to set
        win.color = [0.0039, 0.0039, 0.0039]
        win.colorSpace = 'rgb'
        win.backgroundImage = ''
        win.backgroundFit = 'none'
        win.units = 'height'
    if expInfo is not None:
        # get/measure frame rate if not already in expInfo
        if win._monitorFrameRate is None:
            win._monitorFrameRate = win.getActualFrameRate(infoMsg='Attempting to measure frame rate of screen, please wait...')
        expInfo['frameRate'] = win._monitorFrameRate
    win.hideMessage()
    if PILOTING:
        # show a visual indicator if we're in piloting mode
        if prefs.piloting['showPilotingIndicator']:
            win.showPilotingIndicator()
        # always show the mouse in piloting mode
        if prefs.piloting['forceMouseVisible']:
            win.mouseVisible = True
    
    return win


def setupDevices(expInfo, thisExp, win):
    """
    Setup whatever devices are available (mouse, keyboard, speaker, eyetracker, etc.) and add them to 
    the device manager (deviceManager)
    
    Parameters
    ==========
    expInfo : dict
        Information about this experiment, created by the `setupExpInfo` function.
    thisExp : psychopy.data.ExperimentHandler
        Handler object for this experiment, contains the data to save and information about 
        where to save it to.
    win : psychopy.visual.Window
        Window in which to run this experiment.
    Returns
    ==========
    bool
        True if completed successfully.
    """
    # --- Setup input devices ---
    ioConfig = {}
    
    # Setup iohub keyboard
    ioConfig['Keyboard'] = dict(use_keymap='psychopy')
    
    # Setup iohub experiment
    ioConfig['Experiment'] = dict(filename=thisExp.dataFileName)
    
    # Start ioHub server
    ioServer = io.launchHubServer(window=win, **ioConfig)
    
    # store ioServer object in the device manager
    deviceManager.ioServer = ioServer
    
    # create a default keyboard (e.g. to check for escape)
    if deviceManager.getDevice('defaultKeyboard') is None:
        deviceManager.addDevice(
            deviceClass='keyboard', deviceName='defaultKeyboard', backend='iohub'
        )
    # return True if completed successfully
    return True

def pauseExperiment(thisExp, win=None, timers=[], currentRoutine=None):
    """
    Pause this experiment, preventing the flow from advancing to the next routine until resumed.
    
    Parameters
    ==========
    thisExp : psychopy.data.ExperimentHandler
        Handler object for this experiment, contains the data to save and information about 
        where to save it to.
    win : psychopy.visual.Window
        Window for this experiment.
    timers : list, tuple
        List of timers to reset once pausing is finished.
    currentRoutine : psychopy.data.Routine
        Current Routine we are in at time of pausing, if any. This object tells PsychoPy what Components to pause/play/dispatch.
    """
    # if we are not paused, do nothing
    if thisExp.status != PAUSED:
        return
    
    # start a timer to figure out how long we're paused for
    pauseTimer = core.Clock()
    # pause any playback components
    if currentRoutine is not None:
        for comp in currentRoutine.getPlaybackComponents():
            comp.pause()
    # make sure we have a keyboard
    defaultKeyboard = deviceManager.getDevice('defaultKeyboard')
    if defaultKeyboard is None:
        defaultKeyboard = deviceManager.addKeyboard(
            deviceClass='keyboard',
            deviceName='defaultKeyboard',
            backend='ioHub',
        )
    # run a while loop while we wait to unpause
    while thisExp.status == PAUSED:
        # check for quit (typically the Esc key)
        if defaultKeyboard.getKeys(keyList=['escape']):
            endExperiment(thisExp, win=win)
        # dispatch messages on response components
        if currentRoutine is not None:
            for comp in currentRoutine.getDispatchComponents():
                comp.device.dispatchMessages()
        # sleep 1ms so other threads can execute
        clock.time.sleep(0.001)
    # if stop was requested while paused, quit
    if thisExp.status == FINISHED:
        endExperiment(thisExp, win=win)
    # resume any playback components
    if currentRoutine is not None:
        for comp in currentRoutine.getPlaybackComponents():
            comp.play()
    # reset any timers
    for timer in timers:
        timer.addTime(-pauseTimer.getTime())


def run(expInfo, thisExp, win, globalClock=None, thisSession=None):
    """
    Run the experiment flow.
    
    Parameters
    ==========
    expInfo : dict
        Information about this experiment, created by the `setupExpInfo` function.
    thisExp : psychopy.data.ExperimentHandler
        Handler object for this experiment, contains the data to save and information about 
        where to save it to.
    psychopy.visual.Window
        Window in which to run this experiment.
    globalClock : psychopy.core.clock.Clock or None
        Clock to get global time from - supply None to make a new one.
    thisSession : psychopy.session.Session or None
        Handle of the Session object this experiment is being run from, if any.
    """
    # mark experiment as started
    thisExp.status = STARTED
    # update experiment info
    expInfo['date'] = data.getDateStr()
    expInfo['expName'] = expName
    expInfo['expVersion'] = expVersion
    expInfo['psychopyVersion'] = psychopyVersion
    # make sure window is set to foreground to prevent losing focus
    win.winHandle.activate()
    # make sure variables created by exec are available globally
    exec = environmenttools.setExecEnvironment(globals())
    # get device handles from dict of input devices
    ioServer = deviceManager.ioServer
    # get/create a default keyboard (e.g. to check for escape)
    defaultKeyboard = deviceManager.getDevice('defaultKeyboard')
    if defaultKeyboard is None:
        deviceManager.addDevice(
            deviceClass='keyboard', deviceName='defaultKeyboard', backend='ioHub'
        )
    eyetracker = deviceManager.getDevice('eyetracker')
    # make sure we're running in the directory for this experiment
    os.chdir(_thisDir)
    # get filename from ExperimentHandler for convenience
    filename = thisExp.dataFileName
    frameTolerance = 0.001  # how close to onset before 'same' frame
    endExpNow = False  # flag for 'escape' or other condition => quit the exp
    # get frame duration from frame rate in expInfo
    if 'frameRate' in expInfo and expInfo['frameRate'] is not None:
        frameDur = 1.0 / round(expInfo['frameRate'])
    else:
        frameDur = 1.0 / 60.0  # could not measure, so guess
    
    # Start Code - component code to be run after the window creation
    
    # --- Initialize components for Routine "Intro" ---
    text_22 = visual.TextStim(win=win, name='text_22',
        text='The Necker cube is an ambiguous figure and can be "perceived" in two ways, see below and confirm you can see both views.\n\n(press space to continue)\n',
        font='Open Sans',
        units='deg', pos=(0, 7), draggable=False, height=1.2, wrapWidth=40.0, ori=0.0, 
        color='black', colorSpace='rgb', opacity=None, 
        languageStyle='LTR',
        depth=0.0);
    image_9 = visual.ImageStim(
        win=win,
        name='image_9', units='deg', 
        image='intro.png', mask=None, anchor='center',
        ori=0.0, pos=(0, -4), draggable=False, size=(16, 14),
        color=[1,1,1], colorSpace='rgb', opacity=None,
        flipHoriz=False, flipVert=False,
        texRes=128.0, interpolate=True, depth=-1.0)
    key_resp_7 = keyboard.Keyboard(deviceName='defaultKeyboard', backend='ioHub')
    # Run 'Begin Experiment' code from code_2
    import serial
    port = serial.Serial(port = "COM3" , baudrate = 115200)
    
    
    # --- Initialize components for Routine "intro2" ---
    text_23 = visual.TextStim(win=win, name='text_23',
        text='You will be shown the Necker cube several times and will need to indicate which of the two you perceived.\n\nPut on headphones and make sure you can hear the sound that will play after pressing space.\n\n(space to continue)',
        font='Open Sans',
        units='deg', pos=(0, 0), draggable=False, height=1.2, wrapWidth=40.0, ori=0.0, 
        color='black', colorSpace='rgb', opacity=None, 
        languageStyle='LTR',
        depth=0.0);
    key_resp_8 = keyboard.Keyboard(deviceName='defaultKeyboard', backend='ioHub')
    
    # --- Initialize components for Routine "sound_test" ---
    sound_7 = sound.Sound(
        'A', 
        secs=1.0, 
        stereo=True, 
        hamming=True, 
        speaker=None,    name='sound_7'
    )
    sound_7.setVolume(1.0)
    
    # --- Initialize components for Routine "instructions" ---
    text_3 = visual.TextStim(win=win, name='text_3',
        text="Fixate on the cross in the middle of the screen\nMake sure the chair\\'s front legs are on the line\n\nDo not blink\n\nAfter each stimulus, indicate which was the immediate first percept you saw by answering the question that follows using the arrow buttons. \nImmediately return your gaze to the fixation cross.\n\n(press space to begin)",
        font='Open Sans',
        units='deg', pos=(0, 0), draggable=False, height=1.2, wrapWidth=40.0, ori=0.0, 
        color='black', colorSpace='rgb', opacity=None, 
        languageStyle='LTR',
        depth=0.0);
    key_resp_2 = keyboard.Keyboard(deviceName='defaultKeyboard', backend='ioHub')
    
    # --- Initialize components for Routine "cross" ---
    text_6 = visual.TextStim(win=win, name='text_6',
        text='+',
        font='Arial',
        units='deg', pos=(0, 0), draggable=False, height=0.5, wrapWidth=None, ori=0.0, 
        color='black', colorSpace='rgb', opacity=None, 
        languageStyle='LTR',
        depth=0.0);
    
    # --- Initialize components for Routine "Practice_run" ---
    text_25 = visual.TextStim(win=win, name='text_25',
        text='Ready for a quick practice run?\n\nNote: the question after stimulus presentation does not stay constant\n\n(press space to continue)',
        font='Open Sans',
        units='deg', pos=(0, 0), draggable=False, height=1.2, wrapWidth=None, ori=0.0, 
        color='black', colorSpace='rgb', opacity=None, 
        languageStyle='LTR',
        depth=0.0);
    key_resp_10 = keyboard.Keyboard(deviceName='defaultKeyboard', backend='ioHub')
    
    # --- Initialize components for Routine "blank_cross" ---
    text_4 = visual.TextStim(win=win, name='text_4',
        text='',
        font='Arial',
        units='deg', pos=(0, 0), draggable=False, height=0.5, wrapWidth=None, ori=0.0, 
        color='black', colorSpace='rgb', opacity=None, 
        languageStyle='LTR',
        depth=0.0);
    
    # --- Initialize components for Routine "NeckerBaseline" ---
    image_4 = visual.ImageStim(
        win=win,
        name='image_4', units='deg', 
        image='Necker6.png', mask=None, anchor='center',
        ori=0.0, pos=(0, 0), draggable=False, size=(6, 5.25),
        color=[1,1,1], colorSpace='rgb', opacity=None,
        flipHoriz=False, flipVert=False,
        texRes=128.0, interpolate=True, depth=0.0)
    text_7 = visual.TextStim(win=win, name='text_7',
        text='+',
        font='Arial',
        units='deg', pos=(0, 0), draggable=False, height=0.5, wrapWidth=None, ori=0.0, 
        color='black', colorSpace='rgb', opacity=None, 
        languageStyle='LTR',
        depth=-1.0);
    # Run 'Begin Experiment' code from code
    import serial
    port = serial.Serial(port = "COM3" , baudrate = 115200)
    
    # --- Initialize components for Routine "blank" ---
    image4 = visual.ImageStim(
        win=win,
        name='image4', units='deg', 
        image='default.png', mask=None, anchor='center',
        ori=0.0, pos=(0, 0), draggable=False, size=(17, 7),
        color=[1, 1, 1], colorSpace='rgb', opacity=None,
        flipHoriz=False, flipVert=False,
        texRes=128.0, interpolate=True, depth=0.0)
    key_resp = keyboard.Keyboard(deviceName='defaultKeyboard', backend='ioHub')
    text_8 = visual.TextStim(win=win, name='text_8',
        text='+',
        font='Arial',
        units='deg', pos=(0, 0), draggable=False, height=0.5, wrapWidth=None, ori=0.0, 
        color='black', colorSpace='rgb', opacity=None, 
        languageStyle='LTR',
        depth=-2.0);
    
    # --- Initialize components for Routine "Baseline" ---
    text_26 = visual.TextStim(win=win, name='text_26',
        text='Ready to begin?\n\n(press space to begin)',
        font='Open Sans',
        units='deg', pos=(0, 0), draggable=False, height=1.2, wrapWidth=35.0, ori=0.0, 
        color='black', colorSpace='rgb', opacity=None, 
        languageStyle='LTR',
        depth=0.0);
    key_resp_11 = keyboard.Keyboard(deviceName='defaultKeyboard', backend='ioHub')
    
    # --- Initialize components for Routine "cross" ---
    text_6 = visual.TextStim(win=win, name='text_6',
        text='+',
        font='Arial',
        units='deg', pos=(0, 0), draggable=False, height=0.5, wrapWidth=None, ori=0.0, 
        color='black', colorSpace='rgb', opacity=None, 
        languageStyle='LTR',
        depth=0.0);
    
    # --- Initialize components for Routine "blank_cross" ---
    text_4 = visual.TextStim(win=win, name='text_4',
        text='',
        font='Arial',
        units='deg', pos=(0, 0), draggable=False, height=0.5, wrapWidth=None, ori=0.0, 
        color='black', colorSpace='rgb', opacity=None, 
        languageStyle='LTR',
        depth=0.0);
    
    # --- Initialize components for Routine "Base_trigger" ---
    # Run 'Begin Experiment' code from code_5
    port.write(str.encode(chr(1)))
    
    # --- Initialize components for Routine "Necker" ---
    image_3 = visual.ImageStim(
        win=win,
        name='image_3', units='deg', 
        image='Necker6.png', mask=None, anchor='center',
        ori=0.0, pos=(0, 0), draggable=False, size=(6, 5.25),
        color=[1,1,1], colorSpace='rgb', opacity=None,
        flipHoriz=False, flipVert=False,
        texRes=128.0, interpolate=True, depth=0.0)
    text_5 = visual.TextStim(win=win, name='text_5',
        text='+',
        font='Arial',
        units='deg', pos=(0, 0), draggable=False, height=0.5, wrapWidth=None, ori=0.0, 
        color='black', colorSpace='rgb', opacity=None, 
        languageStyle='LTR',
        depth=-1.0);
    sound_2 = sound.Sound(
        'A', 
        secs=0.05, 
        stereo=True, 
        hamming=True, 
        speaker=None,    name='sound_2'
    )
    sound_2.setVolume(1.0)
    
    # --- Initialize components for Routine "blank" ---
    image4 = visual.ImageStim(
        win=win,
        name='image4', units='deg', 
        image='default.png', mask=None, anchor='center',
        ori=0.0, pos=(0, 0), draggable=False, size=(17, 7),
        color=[1, 1, 1], colorSpace='rgb', opacity=None,
        flipHoriz=False, flipVert=False,
        texRes=128.0, interpolate=True, depth=0.0)
    key_resp = keyboard.Keyboard(deviceName='defaultKeyboard', backend='ioHub')
    text_8 = visual.TextStim(win=win, name='text_8',
        text='+',
        font='Arial',
        units='deg', pos=(0, 0), draggable=False, height=0.5, wrapWidth=None, ori=0.0, 
        color='black', colorSpace='rgb', opacity=None, 
        languageStyle='LTR',
        depth=-2.0);
    
    # --- Initialize components for Routine "break_2" ---
    text_9 = visual.TextStim(win=win, name='text_9',
        text="You can now take a short break. Rest your eyes. \n\nPress space when you're ready to go again",
        font='Open Sans',
        units='deg', pos=(0, 0), draggable=False, height=1.2, wrapWidth=40.0, ori=0.0, 
        color='black', colorSpace='rgb', opacity=None, 
        languageStyle='LTR',
        depth=0.0);
    key_resp_3 = keyboard.Keyboard(deviceName='defaultKeyboard', backend='ioHub')
    
    # --- Initialize components for Routine "cross" ---
    text_6 = visual.TextStim(win=win, name='text_6',
        text='+',
        font='Arial',
        units='deg', pos=(0, 0), draggable=False, height=0.5, wrapWidth=None, ori=0.0, 
        color='black', colorSpace='rgb', opacity=None, 
        languageStyle='LTR',
        depth=0.0);
    
    # --- Initialize components for Routine "Instr_gonogo" ---
    text_11 = visual.TextStim(win=win, name='text_11',
        text='Press space when you see the following percept paired with the tone',
        font='Open Sans',
        units='deg', pos=(0, 0), draggable=False, height=1.2, wrapWidth=40.0, ori=0.0, 
        color='black', colorSpace='rgb', opacity=None, 
        languageStyle='LTR',
        depth=0.0);
    image_5 = visual.ImageStim(
        win=win,
        name='image_5', units='deg', 
        image='R.png', mask=None, anchor='center',
        ori=0.0, pos=(0, 0), draggable=False, size=(8, 7),
        color=[1,1,1], colorSpace='rgb', opacity=None,
        flipHoriz=False, flipVert=False,
        texRes=128.0, interpolate=True, depth=-1.0)
    sound_3 = sound.Sound(
        '440.wav', 
        secs=0.05, 
        stereo=True, 
        hamming=True, 
        speaker=None,    name='sound_3'
    )
    sound_3.setVolume(1.0)
    text_12 = visual.TextStim(win=win, name='text_12',
        text='withold from pressing otherwise',
        font='Open Sans',
        units='deg', pos=(0, 0), draggable=False, height=1.2, wrapWidth=40.0, ori=0.0, 
        color='black', colorSpace='rgb', opacity=None, 
        languageStyle='LTR',
        depth=-3.0);
    text_13 = visual.TextStim(win=win, name='text_13',
        text='Here is the pair again, only press space when these two are perceived together',
        font='Open Sans',
        units='deg', pos=(0, 0), draggable=False, height=1.2, wrapWidth=40.0, ori=0.0, 
        color='black', colorSpace='rgb', opacity=None, 
        languageStyle='LTR',
        depth=-4.0);
    image_6 = visual.ImageStim(
        win=win,
        name='image_6', units='deg', 
        image='R.png', mask=None, anchor='center',
        ori=0.0, pos=(0, 0), draggable=False, size=(8, 7),
        color=[1,1,1], colorSpace='rgb', opacity=None,
        flipHoriz=False, flipVert=False,
        texRes=128.0, interpolate=True, depth=-5.0)
    sound_4 = sound.Sound(
        '440.wav', 
        secs=0.05, 
        stereo=True, 
        hamming=True, 
        speaker=None,    name='sound_4'
    )
    sound_4.setVolume(1.0)
    text_14 = visual.TextStim(win=win, name='text_14',
        text='ready?\n\n(press space)',
        font='Open Sans',
        units='deg', pos=(0, 0), draggable=False, height=2.0, wrapWidth=40.0, ori=0.0, 
        color='black', colorSpace='rgb', opacity=None, 
        languageStyle='LTR',
        depth=-7.0);
    key_resp_5 = keyboard.Keyboard(deviceName='defaultKeyboard', backend='ioHub')
    text_20 = visual.TextStim(win=win, name='text_20',
        text='+',
        font='Open Sans',
        units='deg', pos=(0, 0), draggable=False, height=1.0, wrapWidth=None, ori=0.0, 
        color='black', colorSpace='rgb', opacity=None, 
        languageStyle='LTR',
        depth=-9.0);
    text_21 = visual.TextStim(win=win, name='text_21',
        text='+',
        font='Open Sans',
        units='deg', pos=(0, 0), draggable=False, height=1.0, wrapWidth=None, ori=0.0, 
        color='black', colorSpace='rgb', opacity=None, 
        languageStyle='LTR',
        depth=-10.0);
    
    # --- Initialize components for Routine "last_instructions" ---
    image_10 = visual.ImageStim(
        win=win,
        name='image_10', units='deg', 
        image='GoNoGo2.png', mask=None, anchor='center',
        ori=0.0, pos=(0, -5), draggable=False, size=(35, 16),
        color=[1,1,1], colorSpace='rgb', opacity=None,
        flipHoriz=False, flipVert=False,
        texRes=128.0, interpolate=True, depth=0.0)
    key_resp_9 = keyboard.Keyboard(deviceName='defaultKeyboard', backend='ioHub')
    text_24 = visual.TextStim(win=win, name='text_24',
        text='So here is a recap:\nThere are four possible scenarios, you only press space for the one. \n(press space to continue)',
        font='Open Sans',
        units='deg', pos=(0, 8), draggable=False, height=1.2, wrapWidth=40.0, ori=0.0, 
        color='black', colorSpace='rgb', opacity=None, 
        languageStyle='LTR',
        depth=-2.0);
    
    # --- Initialize components for Routine "dontpress1" ---
    text_15 = visual.TextStim(win=win, name='text_15',
        text='+',
        font='Open Sans',
        units='deg', pos=(0, 0), draggable=False, height=0.5, wrapWidth=None, ori=0.0, 
        color='black', colorSpace='rgb', opacity=None, 
        languageStyle='LTR',
        depth=0.0);
    image_7 = visual.ImageStim(
        win=win,
        name='image_7', units='deg', 
        image='default.png', mask=None, anchor='center',
        ori=0.0, pos=(0, 0), draggable=False, size=(8, 7),
        color=[1,1,1], colorSpace='rgb', opacity=None,
        flipHoriz=False, flipVert=False,
        texRes=128.0, interpolate=True, depth=-1.0)
    text_16 = visual.TextStim(win=win, name='text_16',
        text="DON'T PRESS SPACE",
        font='Open Sans',
        units='deg', pos=(0, 0), draggable=False, height=2.0, wrapWidth=40.0, ori=0.0, 
        color='black', colorSpace='rgb', opacity=None, 
        languageStyle='LTR',
        depth=-2.0);
    sound_6 = sound.Sound(
        'A', 
        secs=0.05, 
        stereo=True, 
        hamming=True, 
        speaker=None,    name='sound_6'
    )
    sound_6.setVolume(1.0)
    
    # --- Initialize components for Routine "pressEx" ---
    text_17 = visual.TextStim(win=win, name='text_17',
        text='+',
        font='Open Sans',
        units='deg', pos=(0, 0), draggable=False, height=0.5, wrapWidth=None, ori=0.0, 
        color='black', colorSpace='rgb', opacity=None, 
        languageStyle='LTR',
        depth=0.0);
    image_8 = visual.ImageStim(
        win=win,
        name='image_8', units='deg', 
        image='default.png', mask=None, anchor='center',
        ori=0.0, pos=(0, 0), draggable=False, size=(8, 7),
        color=[1,1,1], colorSpace='rgb', opacity=None,
        flipHoriz=False, flipVert=False,
        texRes=128.0, interpolate=True, depth=-1.0)
    text_18 = visual.TextStim(win=win, name='text_18',
        text='PRESS SPACE',
        font='Open Sans',
        units='deg', pos=(0, 0), draggable=False, height=2.0, wrapWidth=40.0, ori=0.0, 
        color='black', colorSpace='rgb', opacity=None, 
        languageStyle='LTR',
        depth=-2.0);
    sound_5 = sound.Sound(
        'A', 
        secs=0.05, 
        stereo=True, 
        hamming=True, 
        speaker=None,    name='sound_5'
    )
    sound_5.setVolume(1.0)
    
    # --- Initialize components for Routine "ready_" ---
    text_19 = visual.TextStim(win=win, name='text_19',
        text='Ready?\n(press space to begin)',
        font='Open Sans',
        units='deg', pos=(0, 0), draggable=False, height=1.2, wrapWidth=40.0, ori=0.0, 
        color='black', colorSpace='rgb', opacity=None, 
        languageStyle='LTR',
        depth=0.0);
    key_resp_6 = keyboard.Keyboard(deviceName='defaultKeyboard', backend='ioHub')
    
    # --- Initialize components for Routine "blank_cross" ---
    text_4 = visual.TextStim(win=win, name='text_4',
        text='',
        font='Arial',
        units='deg', pos=(0, 0), draggable=False, height=0.5, wrapWidth=None, ori=0.0, 
        color='black', colorSpace='rgb', opacity=None, 
        languageStyle='LTR',
        depth=0.0);
    
    # --- Initialize components for Routine "trial" ---
    sound_1 = sound.Sound(
        'A', 
        secs=0.05, 
        stereo=True, 
        hamming=True, 
        speaker=None,    name='sound_1'
    )
    sound_1.setVolume(1.0)
    image_2 = visual.ImageStim(
        win=win,
        name='image_2', units='deg', 
        image='default.png', mask=None, anchor='center',
        ori=0.0, pos=(0, 0), draggable=False, size=(6, 5.25),
        color=[1,1,1], colorSpace='rgb', opacity=None,
        flipHoriz=False, flipVert=False,
        texRes=128.0, interpolate=True, depth=-1.0)
    text_2 = visual.TextStim(win=win, name='text_2',
        text='+',
        font='Open Sans',
        units='deg', pos=(0, 0), draggable=False, height=0.5, wrapWidth=None, ori=0.0, 
        color='black', colorSpace='rgb', opacity=None, 
        languageStyle='LTR',
        depth=-2.0);
    G0_NoGo_key = keyboard.Keyboard(deviceName='defaultKeyboard', backend='ioHub')
    
    # --- Initialize components for Routine "goNogo" ---
    key_resp_4 = keyboard.Keyboard(deviceName='defaultKeyboard', backend='ioHub')
    text_10 = visual.TextStim(win=win, name='text_10',
        text='+',
        font='Open Sans',
        units='deg', pos=(0, 0), draggable=False, height=0.5, wrapWidth=None, ori=0.0, 
        color='black', colorSpace='rgb', opacity=None, 
        languageStyle='LTR',
        depth=-1.0);
    
    # --- Initialize components for Routine "break_2" ---
    text_9 = visual.TextStim(win=win, name='text_9',
        text="You can now take a short break. Rest your eyes. \n\nPress space when you're ready to go again",
        font='Open Sans',
        units='deg', pos=(0, 0), draggable=False, height=1.2, wrapWidth=40.0, ori=0.0, 
        color='black', colorSpace='rgb', opacity=None, 
        languageStyle='LTR',
        depth=0.0);
    key_resp_3 = keyboard.Keyboard(deviceName='defaultKeyboard', backend='ioHub')
    
    # --- Initialize components for Routine "instructions" ---
    text_3 = visual.TextStim(win=win, name='text_3',
        text="Fixate on the cross in the middle of the screen\nMake sure the chair\\'s front legs are on the line\n\nDo not blink\n\nAfter each stimulus, indicate which was the immediate first percept you saw by answering the question that follows using the arrow buttons. \nImmediately return your gaze to the fixation cross.\n\n(press space to begin)",
        font='Open Sans',
        units='deg', pos=(0, 0), draggable=False, height=1.2, wrapWidth=40.0, ori=0.0, 
        color='black', colorSpace='rgb', opacity=None, 
        languageStyle='LTR',
        depth=0.0);
    key_resp_2 = keyboard.Keyboard(deviceName='defaultKeyboard', backend='ioHub')
    
    # --- Initialize components for Routine "cross" ---
    text_6 = visual.TextStim(win=win, name='text_6',
        text='+',
        font='Arial',
        units='deg', pos=(0, 0), draggable=False, height=0.5, wrapWidth=None, ori=0.0, 
        color='black', colorSpace='rgb', opacity=None, 
        languageStyle='LTR',
        depth=0.0);
    
    # --- Initialize components for Routine "blank_cross" ---
    text_4 = visual.TextStim(win=win, name='text_4',
        text='',
        font='Arial',
        units='deg', pos=(0, 0), draggable=False, height=0.5, wrapWidth=None, ori=0.0, 
        color='black', colorSpace='rgb', opacity=None, 
        languageStyle='LTR',
        depth=0.0);
    
    # --- Initialize components for Routine "conditioned_trigger" ---
    # Run 'Begin Experiment' code from code_4
    port.write(str.encode(chr(2)))
    
    # --- Initialize components for Routine "Necker" ---
    image_3 = visual.ImageStim(
        win=win,
        name='image_3', units='deg', 
        image='Necker6.png', mask=None, anchor='center',
        ori=0.0, pos=(0, 0), draggable=False, size=(6, 5.25),
        color=[1,1,1], colorSpace='rgb', opacity=None,
        flipHoriz=False, flipVert=False,
        texRes=128.0, interpolate=True, depth=0.0)
    text_5 = visual.TextStim(win=win, name='text_5',
        text='+',
        font='Arial',
        units='deg', pos=(0, 0), draggable=False, height=0.5, wrapWidth=None, ori=0.0, 
        color='black', colorSpace='rgb', opacity=None, 
        languageStyle='LTR',
        depth=-1.0);
    sound_2 = sound.Sound(
        'A', 
        secs=0.05, 
        stereo=True, 
        hamming=True, 
        speaker=None,    name='sound_2'
    )
    sound_2.setVolume(1.0)
    
    # --- Initialize components for Routine "blank" ---
    image4 = visual.ImageStim(
        win=win,
        name='image4', units='deg', 
        image='default.png', mask=None, anchor='center',
        ori=0.0, pos=(0, 0), draggable=False, size=(17, 7),
        color=[1, 1, 1], colorSpace='rgb', opacity=None,
        flipHoriz=False, flipVert=False,
        texRes=128.0, interpolate=True, depth=0.0)
    key_resp = keyboard.Keyboard(deviceName='defaultKeyboard', backend='ioHub')
    text_8 = visual.TextStim(win=win, name='text_8',
        text='+',
        font='Arial',
        units='deg', pos=(0, 0), draggable=False, height=0.5, wrapWidth=None, ori=0.0, 
        color='black', colorSpace='rgb', opacity=None, 
        languageStyle='LTR',
        depth=-2.0);
    
    # --- Initialize components for Routine "break_2" ---
    text_9 = visual.TextStim(win=win, name='text_9',
        text="You can now take a short break. Rest your eyes. \n\nPress space when you're ready to go again",
        font='Open Sans',
        units='deg', pos=(0, 0), draggable=False, height=1.2, wrapWidth=40.0, ori=0.0, 
        color='black', colorSpace='rgb', opacity=None, 
        languageStyle='LTR',
        depth=0.0);
    key_resp_3 = keyboard.Keyboard(deviceName='defaultKeyboard', backend='ioHub')
    
    # --- Initialize components for Routine "Thanks" ---
    text_27 = visual.TextStim(win=win, name='text_27',
        text='Thank you!!\n\nThe End. ',
        font='Open Sans',
        pos=(0, 0), draggable=False, height=0.05, wrapWidth=None, ori=0.0, 
        color='white', colorSpace='rgb', opacity=None, 
        languageStyle='LTR',
        depth=0.0);
    
    # create some handy timers
    
    # global clock to track the time since experiment started
    if globalClock is None:
        # create a clock if not given one
        globalClock = core.Clock()
    if isinstance(globalClock, str):
        # if given a string, make a clock accoridng to it
        if globalClock == 'float':
            # get timestamps as a simple value
            globalClock = core.Clock(format='float')
        elif globalClock == 'iso':
            # get timestamps in ISO format
            globalClock = core.Clock(format='%Y-%m-%d_%H:%M:%S.%f%z')
        else:
            # get timestamps in a custom format
            globalClock = core.Clock(format=globalClock)
    if ioServer is not None:
        ioServer.syncClock(globalClock)
    logging.setDefaultClock(globalClock)
    if eyetracker is not None:
        eyetracker.enableEventReporting()
    # routine timer to track time remaining of each (possibly non-slip) routine
    routineTimer = core.Clock()
    win.flip()  # flip window to reset last flip timer
    # store the exact time the global clock started
    expInfo['expStart'] = data.getDateStr(
        format='%Y-%m-%d %Hh%M.%S.%f %z', fractionalSecondDigits=6
    )
    
    # --- Prepare to start Routine "Intro" ---
    # create an object to store info about Routine Intro
    Intro = data.Routine(
        name='Intro',
        components=[text_22, image_9, key_resp_7],
    )
    Intro.status = NOT_STARTED
    continueRoutine = True
    # update component parameters for each repeat
    # create starting attributes for key_resp_7
    key_resp_7.keys = []
    key_resp_7.rt = []
    _key_resp_7_allKeys = []
    # store start times for Intro
    Intro.tStartRefresh = win.getFutureFlipTime(clock=globalClock)
    Intro.tStart = globalClock.getTime(format='float')
    Intro.status = STARTED
    thisExp.addData('Intro.started', Intro.tStart)
    Intro.maxDuration = None
    # keep track of which components have finished
    IntroComponents = Intro.components
    for thisComponent in Intro.components:
        thisComponent.tStart = None
        thisComponent.tStop = None
        thisComponent.tStartRefresh = None
        thisComponent.tStopRefresh = None
        if hasattr(thisComponent, 'status'):
            thisComponent.status = NOT_STARTED
    # reset timers
    t = 0
    _timeToFirstFrame = win.getFutureFlipTime(clock="now")
    frameN = -1
    
    # --- Run Routine "Intro" ---
    thisExp.currentRoutine = Intro
    Intro.forceEnded = routineForceEnded = not continueRoutine
    while continueRoutine:
        # get current time
        t = routineTimer.getTime()
        tThisFlip = win.getFutureFlipTime(clock=routineTimer)
        tThisFlipGlobal = win.getFutureFlipTime(clock=None)
        frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
        # update/draw components on each frame
        
        # *text_22* updates
        
        # if text_22 is starting this frame...
        if text_22.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            text_22.frameNStart = frameN  # exact frame index
            text_22.tStart = t  # local t and not account for scr refresh
            text_22.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(text_22, 'tStartRefresh')  # time at next scr refresh
            # update status
            text_22.status = STARTED
            text_22.setAutoDraw(True)
        
        # if text_22 is active this frame...
        if text_22.status == STARTED:
            # update params
            pass
        
        # *image_9* updates
        
        # if image_9 is starting this frame...
        if image_9.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            image_9.frameNStart = frameN  # exact frame index
            image_9.tStart = t  # local t and not account for scr refresh
            image_9.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(image_9, 'tStartRefresh')  # time at next scr refresh
            # update status
            image_9.status = STARTED
            image_9.setAutoDraw(True)
        
        # if image_9 is active this frame...
        if image_9.status == STARTED:
            # update params
            pass
        
        # *key_resp_7* updates
        waitOnFlip = False
        
        # if key_resp_7 is starting this frame...
        if key_resp_7.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            key_resp_7.frameNStart = frameN  # exact frame index
            key_resp_7.tStart = t  # local t and not account for scr refresh
            key_resp_7.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(key_resp_7, 'tStartRefresh')  # time at next scr refresh
            # update status
            key_resp_7.status = STARTED
            # keyboard checking is just starting
            waitOnFlip = True
            win.callOnFlip(key_resp_7.clock.reset)  # t=0 on next screen flip
            win.callOnFlip(key_resp_7.clearEvents, eventType='keyboard')  # clear events on next screen flip
        if key_resp_7.status == STARTED and not waitOnFlip:
            theseKeys = key_resp_7.getKeys(keyList=['space'], ignoreKeys=["escape"], waitRelease=False)
            _key_resp_7_allKeys.extend(theseKeys)
            if len(_key_resp_7_allKeys):
                key_resp_7.keys = _key_resp_7_allKeys[-1].name  # just the last key pressed
                key_resp_7.rt = _key_resp_7_allKeys[-1].rt
                key_resp_7.duration = _key_resp_7_allKeys[-1].duration
                # a response ends the routine
                continueRoutine = False
        
        # check for quit (typically the Esc key)
        if defaultKeyboard.getKeys(keyList=["escape"]):
            thisExp.status = FINISHED
        if thisExp.status == FINISHED or endExpNow:
            endExperiment(thisExp, win=win)
            return
        # pause experiment here if requested
        if thisExp.status == PAUSED:
            pauseExperiment(
                thisExp=thisExp, 
                win=win, 
                timers=[routineTimer, globalClock], 
                currentRoutine=Intro,
            )
            # skip the frame we paused on
            continue
        
        # has a Component requested the Routine to end?
        if not continueRoutine:
            Intro.forceEnded = routineForceEnded = True
        # has the Routine been forcibly ended?
        if Intro.forceEnded or routineForceEnded:
            break
        # has every Component finished?
        continueRoutine = False
        for thisComponent in Intro.components:
            if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                continueRoutine = True
                break  # at least one component has not yet finished
        
        # refresh the screen
        if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
            win.flip()
    
    # --- Ending Routine "Intro" ---
    for thisComponent in Intro.components:
        if hasattr(thisComponent, "setAutoDraw"):
            thisComponent.setAutoDraw(False)
    # store stop times for Intro
    Intro.tStop = globalClock.getTime(format='float')
    Intro.tStopRefresh = tThisFlipGlobal
    thisExp.addData('Intro.stopped', Intro.tStop)
    # check responses
    if key_resp_7.keys in ['', [], None]:  # No response was made
        key_resp_7.keys = None
    thisExp.addData('key_resp_7.keys',key_resp_7.keys)
    if key_resp_7.keys != None:  # we had a response
        thisExp.addData('key_resp_7.rt', key_resp_7.rt)
        thisExp.addData('key_resp_7.duration', key_resp_7.duration)
    thisExp.nextEntry()
    # the Routine "Intro" was not non-slip safe, so reset the non-slip timer
    routineTimer.reset()
    
    # --- Prepare to start Routine "intro2" ---
    # create an object to store info about Routine intro2
    intro2 = data.Routine(
        name='intro2',
        components=[text_23, key_resp_8],
    )
    intro2.status = NOT_STARTED
    continueRoutine = True
    # update component parameters for each repeat
    # create starting attributes for key_resp_8
    key_resp_8.keys = []
    key_resp_8.rt = []
    _key_resp_8_allKeys = []
    # store start times for intro2
    intro2.tStartRefresh = win.getFutureFlipTime(clock=globalClock)
    intro2.tStart = globalClock.getTime(format='float')
    intro2.status = STARTED
    thisExp.addData('intro2.started', intro2.tStart)
    intro2.maxDuration = None
    # keep track of which components have finished
    intro2Components = intro2.components
    for thisComponent in intro2.components:
        thisComponent.tStart = None
        thisComponent.tStop = None
        thisComponent.tStartRefresh = None
        thisComponent.tStopRefresh = None
        if hasattr(thisComponent, 'status'):
            thisComponent.status = NOT_STARTED
    # reset timers
    t = 0
    _timeToFirstFrame = win.getFutureFlipTime(clock="now")
    frameN = -1
    
    # --- Run Routine "intro2" ---
    thisExp.currentRoutine = intro2
    intro2.forceEnded = routineForceEnded = not continueRoutine
    while continueRoutine:
        # get current time
        t = routineTimer.getTime()
        tThisFlip = win.getFutureFlipTime(clock=routineTimer)
        tThisFlipGlobal = win.getFutureFlipTime(clock=None)
        frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
        # update/draw components on each frame
        
        # *text_23* updates
        
        # if text_23 is starting this frame...
        if text_23.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            text_23.frameNStart = frameN  # exact frame index
            text_23.tStart = t  # local t and not account for scr refresh
            text_23.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(text_23, 'tStartRefresh')  # time at next scr refresh
            # update status
            text_23.status = STARTED
            text_23.setAutoDraw(True)
        
        # if text_23 is active this frame...
        if text_23.status == STARTED:
            # update params
            pass
        
        # *key_resp_8* updates
        waitOnFlip = False
        
        # if key_resp_8 is starting this frame...
        if key_resp_8.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            key_resp_8.frameNStart = frameN  # exact frame index
            key_resp_8.tStart = t  # local t and not account for scr refresh
            key_resp_8.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(key_resp_8, 'tStartRefresh')  # time at next scr refresh
            # update status
            key_resp_8.status = STARTED
            # keyboard checking is just starting
            waitOnFlip = True
            win.callOnFlip(key_resp_8.clock.reset)  # t=0 on next screen flip
            win.callOnFlip(key_resp_8.clearEvents, eventType='keyboard')  # clear events on next screen flip
        if key_resp_8.status == STARTED and not waitOnFlip:
            theseKeys = key_resp_8.getKeys(keyList=['space'], ignoreKeys=["escape"], waitRelease=False)
            _key_resp_8_allKeys.extend(theseKeys)
            if len(_key_resp_8_allKeys):
                key_resp_8.keys = _key_resp_8_allKeys[-1].name  # just the last key pressed
                key_resp_8.rt = _key_resp_8_allKeys[-1].rt
                key_resp_8.duration = _key_resp_8_allKeys[-1].duration
                # a response ends the routine
                continueRoutine = False
        
        # check for quit (typically the Esc key)
        if defaultKeyboard.getKeys(keyList=["escape"]):
            thisExp.status = FINISHED
        if thisExp.status == FINISHED or endExpNow:
            endExperiment(thisExp, win=win)
            return
        # pause experiment here if requested
        if thisExp.status == PAUSED:
            pauseExperiment(
                thisExp=thisExp, 
                win=win, 
                timers=[routineTimer, globalClock], 
                currentRoutine=intro2,
            )
            # skip the frame we paused on
            continue
        
        # has a Component requested the Routine to end?
        if not continueRoutine:
            intro2.forceEnded = routineForceEnded = True
        # has the Routine been forcibly ended?
        if intro2.forceEnded or routineForceEnded:
            break
        # has every Component finished?
        continueRoutine = False
        for thisComponent in intro2.components:
            if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                continueRoutine = True
                break  # at least one component has not yet finished
        
        # refresh the screen
        if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
            win.flip()
    
    # --- Ending Routine "intro2" ---
    for thisComponent in intro2.components:
        if hasattr(thisComponent, "setAutoDraw"):
            thisComponent.setAutoDraw(False)
    # store stop times for intro2
    intro2.tStop = globalClock.getTime(format='float')
    intro2.tStopRefresh = tThisFlipGlobal
    thisExp.addData('intro2.stopped', intro2.tStop)
    # check responses
    if key_resp_8.keys in ['', [], None]:  # No response was made
        key_resp_8.keys = None
    thisExp.addData('key_resp_8.keys',key_resp_8.keys)
    if key_resp_8.keys != None:  # we had a response
        thisExp.addData('key_resp_8.rt', key_resp_8.rt)
        thisExp.addData('key_resp_8.duration', key_resp_8.duration)
    thisExp.nextEntry()
    # the Routine "intro2" was not non-slip safe, so reset the non-slip timer
    routineTimer.reset()
    
    # --- Prepare to start Routine "sound_test" ---
    # create an object to store info about Routine sound_test
    sound_test = data.Routine(
        name='sound_test',
        components=[sound_7],
    )
    sound_test.status = NOT_STARTED
    continueRoutine = True
    # update component parameters for each repeat
    sound_7.setSound('A', secs=1.0, hamming=True)
    sound_7.setVolume(1.0, log=False)
    sound_7.seek(0)
    # store start times for sound_test
    sound_test.tStartRefresh = win.getFutureFlipTime(clock=globalClock)
    sound_test.tStart = globalClock.getTime(format='float')
    sound_test.status = STARTED
    thisExp.addData('sound_test.started', sound_test.tStart)
    sound_test.maxDuration = None
    # keep track of which components have finished
    sound_testComponents = sound_test.components
    for thisComponent in sound_test.components:
        thisComponent.tStart = None
        thisComponent.tStop = None
        thisComponent.tStartRefresh = None
        thisComponent.tStopRefresh = None
        if hasattr(thisComponent, 'status'):
            thisComponent.status = NOT_STARTED
    # reset timers
    t = 0
    _timeToFirstFrame = win.getFutureFlipTime(clock="now")
    frameN = -1
    
    # --- Run Routine "sound_test" ---
    thisExp.currentRoutine = sound_test
    sound_test.forceEnded = routineForceEnded = not continueRoutine
    while continueRoutine and routineTimer.getTime() < 1.0:
        # get current time
        t = routineTimer.getTime()
        tThisFlip = win.getFutureFlipTime(clock=routineTimer)
        tThisFlipGlobal = win.getFutureFlipTime(clock=None)
        frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
        # update/draw components on each frame
        
        # *sound_7* updates
        
        # if sound_7 is starting this frame...
        if sound_7.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            sound_7.frameNStart = frameN  # exact frame index
            sound_7.tStart = t  # local t and not account for scr refresh
            sound_7.tStartRefresh = tThisFlipGlobal  # on global time
            # add timestamp to datafile
            thisExp.addData('sound_7.started', tThisFlipGlobal)
            # update status
            sound_7.status = STARTED
            sound_7.play(when=win)  # sync with win flip
        
        # if sound_7 is stopping this frame...
        if sound_7.status == STARTED:
            # is it time to stop? (based on global clock, using actual start)
            if tThisFlipGlobal > sound_7.tStartRefresh + 1.0-frameTolerance or sound_7.isFinished:
                # keep track of stop time/frame for later
                sound_7.tStop = t  # not accounting for scr refresh
                sound_7.tStopRefresh = tThisFlipGlobal  # on global time
                sound_7.frameNStop = frameN  # exact frame index
                # add timestamp to datafile
                thisExp.timestampOnFlip(win, 'sound_7.stopped')
                # update status
                sound_7.status = FINISHED
                sound_7.stop()
        
        # check for quit (typically the Esc key)
        if defaultKeyboard.getKeys(keyList=["escape"]):
            thisExp.status = FINISHED
        if thisExp.status == FINISHED or endExpNow:
            endExperiment(thisExp, win=win)
            return
        # pause experiment here if requested
        if thisExp.status == PAUSED:
            pauseExperiment(
                thisExp=thisExp, 
                win=win, 
                timers=[routineTimer, globalClock], 
                currentRoutine=sound_test,
            )
            # skip the frame we paused on
            continue
        
        # has a Component requested the Routine to end?
        if not continueRoutine:
            sound_test.forceEnded = routineForceEnded = True
        # has the Routine been forcibly ended?
        if sound_test.forceEnded or routineForceEnded:
            break
        # has every Component finished?
        continueRoutine = False
        for thisComponent in sound_test.components:
            if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                continueRoutine = True
                break  # at least one component has not yet finished
        
        # refresh the screen
        if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
            win.flip()
    
    # --- Ending Routine "sound_test" ---
    for thisComponent in sound_test.components:
        if hasattr(thisComponent, "setAutoDraw"):
            thisComponent.setAutoDraw(False)
    # store stop times for sound_test
    sound_test.tStop = globalClock.getTime(format='float')
    sound_test.tStopRefresh = tThisFlipGlobal
    thisExp.addData('sound_test.stopped', sound_test.tStop)
    sound_7.pause()  # ensure sound has stopped at end of Routine
    # using non-slip timing so subtract the expected duration of this Routine (unless ended on request)
    if sound_test.maxDurationReached:
        routineTimer.addTime(-sound_test.maxDuration)
    elif sound_test.forceEnded:
        routineTimer.reset()
    else:
        routineTimer.addTime(-1.000000)
    thisExp.nextEntry()
    
    # --- Prepare to start Routine "instructions" ---
    # create an object to store info about Routine instructions
    instructions = data.Routine(
        name='instructions',
        components=[text_3, key_resp_2],
    )
    instructions.status = NOT_STARTED
    continueRoutine = True
    # update component parameters for each repeat
    # create starting attributes for key_resp_2
    key_resp_2.keys = []
    key_resp_2.rt = []
    _key_resp_2_allKeys = []
    # store start times for instructions
    instructions.tStartRefresh = win.getFutureFlipTime(clock=globalClock)
    instructions.tStart = globalClock.getTime(format='float')
    instructions.status = STARTED
    thisExp.addData('instructions.started', instructions.tStart)
    instructions.maxDuration = None
    # keep track of which components have finished
    instructionsComponents = instructions.components
    for thisComponent in instructions.components:
        thisComponent.tStart = None
        thisComponent.tStop = None
        thisComponent.tStartRefresh = None
        thisComponent.tStopRefresh = None
        if hasattr(thisComponent, 'status'):
            thisComponent.status = NOT_STARTED
    # reset timers
    t = 0
    _timeToFirstFrame = win.getFutureFlipTime(clock="now")
    frameN = -1
    
    # --- Run Routine "instructions" ---
    thisExp.currentRoutine = instructions
    instructions.forceEnded = routineForceEnded = not continueRoutine
    while continueRoutine:
        # get current time
        t = routineTimer.getTime()
        tThisFlip = win.getFutureFlipTime(clock=routineTimer)
        tThisFlipGlobal = win.getFutureFlipTime(clock=None)
        frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
        # update/draw components on each frame
        
        # *text_3* updates
        
        # if text_3 is starting this frame...
        if text_3.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            text_3.frameNStart = frameN  # exact frame index
            text_3.tStart = t  # local t and not account for scr refresh
            text_3.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(text_3, 'tStartRefresh')  # time at next scr refresh
            # update status
            text_3.status = STARTED
            text_3.setAutoDraw(True)
        
        # if text_3 is active this frame...
        if text_3.status == STARTED:
            # update params
            pass
        
        # *key_resp_2* updates
        waitOnFlip = False
        
        # if key_resp_2 is starting this frame...
        if key_resp_2.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            key_resp_2.frameNStart = frameN  # exact frame index
            key_resp_2.tStart = t  # local t and not account for scr refresh
            key_resp_2.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(key_resp_2, 'tStartRefresh')  # time at next scr refresh
            # update status
            key_resp_2.status = STARTED
            # keyboard checking is just starting
            waitOnFlip = True
            win.callOnFlip(key_resp_2.clock.reset)  # t=0 on next screen flip
            win.callOnFlip(key_resp_2.clearEvents, eventType='keyboard')  # clear events on next screen flip
        if key_resp_2.status == STARTED and not waitOnFlip:
            theseKeys = key_resp_2.getKeys(keyList=['space'], ignoreKeys=["escape"], waitRelease=False)
            _key_resp_2_allKeys.extend(theseKeys)
            if len(_key_resp_2_allKeys):
                key_resp_2.keys = _key_resp_2_allKeys[-1].name  # just the last key pressed
                key_resp_2.rt = _key_resp_2_allKeys[-1].rt
                key_resp_2.duration = _key_resp_2_allKeys[-1].duration
                # a response ends the routine
                continueRoutine = False
        
        # check for quit (typically the Esc key)
        if defaultKeyboard.getKeys(keyList=["escape"]):
            thisExp.status = FINISHED
        if thisExp.status == FINISHED or endExpNow:
            endExperiment(thisExp, win=win)
            return
        # pause experiment here if requested
        if thisExp.status == PAUSED:
            pauseExperiment(
                thisExp=thisExp, 
                win=win, 
                timers=[routineTimer, globalClock], 
                currentRoutine=instructions,
            )
            # skip the frame we paused on
            continue
        
        # has a Component requested the Routine to end?
        if not continueRoutine:
            instructions.forceEnded = routineForceEnded = True
        # has the Routine been forcibly ended?
        if instructions.forceEnded or routineForceEnded:
            break
        # has every Component finished?
        continueRoutine = False
        for thisComponent in instructions.components:
            if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                continueRoutine = True
                break  # at least one component has not yet finished
        
        # refresh the screen
        if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
            win.flip()
    
    # --- Ending Routine "instructions" ---
    for thisComponent in instructions.components:
        if hasattr(thisComponent, "setAutoDraw"):
            thisComponent.setAutoDraw(False)
    # store stop times for instructions
    instructions.tStop = globalClock.getTime(format='float')
    instructions.tStopRefresh = tThisFlipGlobal
    thisExp.addData('instructions.stopped', instructions.tStop)
    # check responses
    if key_resp_2.keys in ['', [], None]:  # No response was made
        key_resp_2.keys = None
    thisExp.addData('key_resp_2.keys',key_resp_2.keys)
    if key_resp_2.keys != None:  # we had a response
        thisExp.addData('key_resp_2.rt', key_resp_2.rt)
        thisExp.addData('key_resp_2.duration', key_resp_2.duration)
    thisExp.nextEntry()
    # the Routine "instructions" was not non-slip safe, so reset the non-slip timer
    routineTimer.reset()
    
    # --- Prepare to start Routine "cross" ---
    # create an object to store info about Routine cross
    cross = data.Routine(
        name='cross',
        components=[text_6],
    )
    cross.status = NOT_STARTED
    continueRoutine = True
    # update component parameters for each repeat
    # store start times for cross
    cross.tStartRefresh = win.getFutureFlipTime(clock=globalClock)
    cross.tStart = globalClock.getTime(format='float')
    cross.status = STARTED
    thisExp.addData('cross.started', cross.tStart)
    cross.maxDuration = None
    # keep track of which components have finished
    crossComponents = cross.components
    for thisComponent in cross.components:
        thisComponent.tStart = None
        thisComponent.tStop = None
        thisComponent.tStartRefresh = None
        thisComponent.tStopRefresh = None
        if hasattr(thisComponent, 'status'):
            thisComponent.status = NOT_STARTED
    # reset timers
    t = 0
    _timeToFirstFrame = win.getFutureFlipTime(clock="now")
    frameN = -1
    
    # --- Run Routine "cross" ---
    thisExp.currentRoutine = cross
    cross.forceEnded = routineForceEnded = not continueRoutine
    while continueRoutine and routineTimer.getTime() < 1.0:
        # get current time
        t = routineTimer.getTime()
        tThisFlip = win.getFutureFlipTime(clock=routineTimer)
        tThisFlipGlobal = win.getFutureFlipTime(clock=None)
        frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
        # update/draw components on each frame
        
        # *text_6* updates
        
        # if text_6 is starting this frame...
        if text_6.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            text_6.frameNStart = frameN  # exact frame index
            text_6.tStart = t  # local t and not account for scr refresh
            text_6.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(text_6, 'tStartRefresh')  # time at next scr refresh
            # update status
            text_6.status = STARTED
            text_6.setAutoDraw(True)
        
        # if text_6 is active this frame...
        if text_6.status == STARTED:
            # update params
            pass
        
        # if text_6 is stopping this frame...
        if text_6.status == STARTED:
            # is it time to stop? (based on global clock, using actual start)
            if tThisFlipGlobal > text_6.tStartRefresh + 1.0-frameTolerance:
                # keep track of stop time/frame for later
                text_6.tStop = t  # not accounting for scr refresh
                text_6.tStopRefresh = tThisFlipGlobal  # on global time
                text_6.frameNStop = frameN  # exact frame index
                # update status
                text_6.status = FINISHED
                text_6.setAutoDraw(False)
        
        # check for quit (typically the Esc key)
        if defaultKeyboard.getKeys(keyList=["escape"]):
            thisExp.status = FINISHED
        if thisExp.status == FINISHED or endExpNow:
            endExperiment(thisExp, win=win)
            return
        # pause experiment here if requested
        if thisExp.status == PAUSED:
            pauseExperiment(
                thisExp=thisExp, 
                win=win, 
                timers=[routineTimer, globalClock], 
                currentRoutine=cross,
            )
            # skip the frame we paused on
            continue
        
        # has a Component requested the Routine to end?
        if not continueRoutine:
            cross.forceEnded = routineForceEnded = True
        # has the Routine been forcibly ended?
        if cross.forceEnded or routineForceEnded:
            break
        # has every Component finished?
        continueRoutine = False
        for thisComponent in cross.components:
            if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                continueRoutine = True
                break  # at least one component has not yet finished
        
        # refresh the screen
        if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
            win.flip()
    
    # --- Ending Routine "cross" ---
    for thisComponent in cross.components:
        if hasattr(thisComponent, "setAutoDraw"):
            thisComponent.setAutoDraw(False)
    # store stop times for cross
    cross.tStop = globalClock.getTime(format='float')
    cross.tStopRefresh = tThisFlipGlobal
    thisExp.addData('cross.stopped', cross.tStop)
    # using non-slip timing so subtract the expected duration of this Routine (unless ended on request)
    if cross.maxDurationReached:
        routineTimer.addTime(-cross.maxDuration)
    elif cross.forceEnded:
        routineTimer.reset()
    else:
        routineTimer.addTime(-1.000000)
    thisExp.nextEntry()
    
    # --- Prepare to start Routine "Practice_run" ---
    # create an object to store info about Routine Practice_run
    Practice_run = data.Routine(
        name='Practice_run',
        components=[text_25, key_resp_10],
    )
    Practice_run.status = NOT_STARTED
    continueRoutine = True
    # update component parameters for each repeat
    # create starting attributes for key_resp_10
    key_resp_10.keys = []
    key_resp_10.rt = []
    _key_resp_10_allKeys = []
    # store start times for Practice_run
    Practice_run.tStartRefresh = win.getFutureFlipTime(clock=globalClock)
    Practice_run.tStart = globalClock.getTime(format='float')
    Practice_run.status = STARTED
    thisExp.addData('Practice_run.started', Practice_run.tStart)
    Practice_run.maxDuration = None
    # keep track of which components have finished
    Practice_runComponents = Practice_run.components
    for thisComponent in Practice_run.components:
        thisComponent.tStart = None
        thisComponent.tStop = None
        thisComponent.tStartRefresh = None
        thisComponent.tStopRefresh = None
        if hasattr(thisComponent, 'status'):
            thisComponent.status = NOT_STARTED
    # reset timers
    t = 0
    _timeToFirstFrame = win.getFutureFlipTime(clock="now")
    frameN = -1
    
    # --- Run Routine "Practice_run" ---
    thisExp.currentRoutine = Practice_run
    Practice_run.forceEnded = routineForceEnded = not continueRoutine
    while continueRoutine:
        # get current time
        t = routineTimer.getTime()
        tThisFlip = win.getFutureFlipTime(clock=routineTimer)
        tThisFlipGlobal = win.getFutureFlipTime(clock=None)
        frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
        # update/draw components on each frame
        
        # *text_25* updates
        
        # if text_25 is starting this frame...
        if text_25.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            text_25.frameNStart = frameN  # exact frame index
            text_25.tStart = t  # local t and not account for scr refresh
            text_25.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(text_25, 'tStartRefresh')  # time at next scr refresh
            # update status
            text_25.status = STARTED
            text_25.setAutoDraw(True)
        
        # if text_25 is active this frame...
        if text_25.status == STARTED:
            # update params
            pass
        
        # *key_resp_10* updates
        waitOnFlip = False
        
        # if key_resp_10 is starting this frame...
        if key_resp_10.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            key_resp_10.frameNStart = frameN  # exact frame index
            key_resp_10.tStart = t  # local t and not account for scr refresh
            key_resp_10.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(key_resp_10, 'tStartRefresh')  # time at next scr refresh
            # update status
            key_resp_10.status = STARTED
            # keyboard checking is just starting
            waitOnFlip = True
            win.callOnFlip(key_resp_10.clock.reset)  # t=0 on next screen flip
            win.callOnFlip(key_resp_10.clearEvents, eventType='keyboard')  # clear events on next screen flip
        if key_resp_10.status == STARTED and not waitOnFlip:
            theseKeys = key_resp_10.getKeys(keyList=['space'], ignoreKeys=["escape"], waitRelease=False)
            _key_resp_10_allKeys.extend(theseKeys)
            if len(_key_resp_10_allKeys):
                key_resp_10.keys = _key_resp_10_allKeys[-1].name  # just the last key pressed
                key_resp_10.rt = _key_resp_10_allKeys[-1].rt
                key_resp_10.duration = _key_resp_10_allKeys[-1].duration
                # a response ends the routine
                continueRoutine = False
        
        # check for quit (typically the Esc key)
        if defaultKeyboard.getKeys(keyList=["escape"]):
            thisExp.status = FINISHED
        if thisExp.status == FINISHED or endExpNow:
            endExperiment(thisExp, win=win)
            return
        # pause experiment here if requested
        if thisExp.status == PAUSED:
            pauseExperiment(
                thisExp=thisExp, 
                win=win, 
                timers=[routineTimer, globalClock], 
                currentRoutine=Practice_run,
            )
            # skip the frame we paused on
            continue
        
        # has a Component requested the Routine to end?
        if not continueRoutine:
            Practice_run.forceEnded = routineForceEnded = True
        # has the Routine been forcibly ended?
        if Practice_run.forceEnded or routineForceEnded:
            break
        # has every Component finished?
        continueRoutine = False
        for thisComponent in Practice_run.components:
            if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                continueRoutine = True
                break  # at least one component has not yet finished
        
        # refresh the screen
        if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
            win.flip()
    
    # --- Ending Routine "Practice_run" ---
    for thisComponent in Practice_run.components:
        if hasattr(thisComponent, "setAutoDraw"):
            thisComponent.setAutoDraw(False)
    # store stop times for Practice_run
    Practice_run.tStop = globalClock.getTime(format='float')
    Practice_run.tStopRefresh = tThisFlipGlobal
    thisExp.addData('Practice_run.stopped', Practice_run.tStop)
    # check responses
    if key_resp_10.keys in ['', [], None]:  # No response was made
        key_resp_10.keys = None
    thisExp.addData('key_resp_10.keys',key_resp_10.keys)
    if key_resp_10.keys != None:  # we had a response
        thisExp.addData('key_resp_10.rt', key_resp_10.rt)
        thisExp.addData('key_resp_10.duration', key_resp_10.duration)
    thisExp.nextEntry()
    # the Routine "Practice_run" was not non-slip safe, so reset the non-slip timer
    routineTimer.reset()
    
    # set up handler to look after randomisation of conditions etc
    trials_9 = data.TrialHandler2(
        name='trials_9',
        nReps=1.0, 
        method='random', 
        extraInfo=expInfo, 
        originPath=-1, 
        trialList=data.importConditions('LorR.xlsx'), 
        seed=None, 
        isTrials=True, 
    )
    thisExp.addLoop(trials_9)  # add the loop to the experiment
    thisTrial_9 = trials_9.trialList[0]  # so we can initialise stimuli with some values
    # abbreviate parameter names if possible (e.g. rgb = thisTrial_9.rgb)
    if thisTrial_9 != None:
        for paramName in thisTrial_9:
            globals()[paramName] = thisTrial_9[paramName]
    if thisSession is not None:
        # if running in a Session with a Liaison client, send data up to now
        thisSession.sendExperimentData()
    
    for thisTrial_9 in trials_9:
        trials_9.status = STARTED
        if hasattr(thisTrial_9, 'status'):
            thisTrial_9.status = STARTED
        currentLoop = trials_9
        thisExp.timestampOnFlip(win, 'thisRow.t', format=globalClock.format)
        if thisSession is not None:
            # if running in a Session with a Liaison client, send data up to now
            thisSession.sendExperimentData()
        # abbreviate parameter names if possible (e.g. rgb = thisTrial_9.rgb)
        if thisTrial_9 != None:
            for paramName in thisTrial_9:
                globals()[paramName] = thisTrial_9[paramName]
        
        # --- Prepare to start Routine "blank_cross" ---
        # create an object to store info about Routine blank_cross
        blank_cross = data.Routine(
            name='blank_cross',
            components=[text_4],
        )
        blank_cross.status = NOT_STARTED
        continueRoutine = True
        # update component parameters for each repeat
        text_4.setText('+')
        # store start times for blank_cross
        blank_cross.tStartRefresh = win.getFutureFlipTime(clock=globalClock)
        blank_cross.tStart = globalClock.getTime(format='float')
        blank_cross.status = STARTED
        thisExp.addData('blank_cross.started', blank_cross.tStart)
        blank_cross.maxDuration = None
        # keep track of which components have finished
        blank_crossComponents = blank_cross.components
        for thisComponent in blank_cross.components:
            thisComponent.tStart = None
            thisComponent.tStop = None
            thisComponent.tStartRefresh = None
            thisComponent.tStopRefresh = None
            if hasattr(thisComponent, 'status'):
                thisComponent.status = NOT_STARTED
        # reset timers
        t = 0
        _timeToFirstFrame = win.getFutureFlipTime(clock="now")
        frameN = -1
        
        # --- Run Routine "blank_cross" ---
        thisExp.currentRoutine = blank_cross
        blank_cross.forceEnded = routineForceEnded = not continueRoutine
        while continueRoutine:
            # if trial has changed, end Routine now
            if hasattr(thisTrial_9, 'status') and thisTrial_9.status == STOPPING:
                continueRoutine = False
            # get current time
            t = routineTimer.getTime()
            tThisFlip = win.getFutureFlipTime(clock=routineTimer)
            tThisFlipGlobal = win.getFutureFlipTime(clock=None)
            frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
            # update/draw components on each frame
            
            # *text_4* updates
            
            # if text_4 is starting this frame...
            if text_4.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                # keep track of start time/frame for later
                text_4.frameNStart = frameN  # exact frame index
                text_4.tStart = t  # local t and not account for scr refresh
                text_4.tStartRefresh = tThisFlipGlobal  # on global time
                win.timeOnFlip(text_4, 'tStartRefresh')  # time at next scr refresh
                # add timestamp to datafile
                thisExp.timestampOnFlip(win, 'text_4.started')
                # update status
                text_4.status = STARTED
                text_4.setAutoDraw(True)
            
            # if text_4 is active this frame...
            if text_4.status == STARTED:
                # update params
                pass
            
            # if text_4 is stopping this frame...
            if text_4.status == STARTED:
                if frameN >= (text_4.frameNStart + randint(62, 125)):
                    # keep track of stop time/frame for later
                    text_4.tStop = t  # not accounting for scr refresh
                    text_4.tStopRefresh = tThisFlipGlobal  # on global time
                    text_4.frameNStop = frameN  # exact frame index
                    # add timestamp to datafile
                    thisExp.timestampOnFlip(win, 'text_4.stopped')
                    # update status
                    text_4.status = FINISHED
                    text_4.setAutoDraw(False)
            
            # check for quit (typically the Esc key)
            if defaultKeyboard.getKeys(keyList=["escape"]):
                thisExp.status = FINISHED
            if thisExp.status == FINISHED or endExpNow:
                endExperiment(thisExp, win=win)
                return
            # pause experiment here if requested
            if thisExp.status == PAUSED:
                pauseExperiment(
                    thisExp=thisExp, 
                    win=win, 
                    timers=[routineTimer, globalClock], 
                    currentRoutine=blank_cross,
                )
                # skip the frame we paused on
                continue
            
            # has a Component requested the Routine to end?
            if not continueRoutine:
                blank_cross.forceEnded = routineForceEnded = True
            # has the Routine been forcibly ended?
            if blank_cross.forceEnded or routineForceEnded:
                break
            # has every Component finished?
            continueRoutine = False
            for thisComponent in blank_cross.components:
                if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                    continueRoutine = True
                    break  # at least one component has not yet finished
            
            # refresh the screen
            if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                win.flip()
        
        # --- Ending Routine "blank_cross" ---
        for thisComponent in blank_cross.components:
            if hasattr(thisComponent, "setAutoDraw"):
                thisComponent.setAutoDraw(False)
        # store stop times for blank_cross
        blank_cross.tStop = globalClock.getTime(format='float')
        blank_cross.tStopRefresh = tThisFlipGlobal
        thisExp.addData('blank_cross.stopped', blank_cross.tStop)
        # the Routine "blank_cross" was not non-slip safe, so reset the non-slip timer
        routineTimer.reset()
        
        # --- Prepare to start Routine "NeckerBaseline" ---
        # create an object to store info about Routine NeckerBaseline
        NeckerBaseline = data.Routine(
            name='NeckerBaseline',
            components=[image_4, text_7],
        )
        NeckerBaseline.status = NOT_STARTED
        continueRoutine = True
        # update component parameters for each repeat
        # Run 'Begin Routine' code from code
        port.write(str.encode(chr(1)))
        # store start times for NeckerBaseline
        NeckerBaseline.tStartRefresh = win.getFutureFlipTime(clock=globalClock)
        NeckerBaseline.tStart = globalClock.getTime(format='float')
        NeckerBaseline.status = STARTED
        thisExp.addData('NeckerBaseline.started', NeckerBaseline.tStart)
        NeckerBaseline.maxDuration = None
        # keep track of which components have finished
        NeckerBaselineComponents = NeckerBaseline.components
        for thisComponent in NeckerBaseline.components:
            thisComponent.tStart = None
            thisComponent.tStop = None
            thisComponent.tStartRefresh = None
            thisComponent.tStopRefresh = None
            if hasattr(thisComponent, 'status'):
                thisComponent.status = NOT_STARTED
        # reset timers
        t = 0
        _timeToFirstFrame = win.getFutureFlipTime(clock="now")
        frameN = -1
        
        # --- Run Routine "NeckerBaseline" ---
        thisExp.currentRoutine = NeckerBaseline
        NeckerBaseline.forceEnded = routineForceEnded = not continueRoutine
        while continueRoutine and routineTimer.getTime() < 0.8:
            # if trial has changed, end Routine now
            if hasattr(thisTrial_9, 'status') and thisTrial_9.status == STOPPING:
                continueRoutine = False
            # get current time
            t = routineTimer.getTime()
            tThisFlip = win.getFutureFlipTime(clock=routineTimer)
            tThisFlipGlobal = win.getFutureFlipTime(clock=None)
            frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
            # update/draw components on each frame
            
            # *image_4* updates
            
            # if image_4 is starting this frame...
            if image_4.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                # keep track of start time/frame for later
                image_4.frameNStart = frameN  # exact frame index
                image_4.tStart = t  # local t and not account for scr refresh
                image_4.tStartRefresh = tThisFlipGlobal  # on global time
                win.timeOnFlip(image_4, 'tStartRefresh')  # time at next scr refresh
                # update status
                image_4.status = STARTED
                image_4.setAutoDraw(True)
            
            # if image_4 is active this frame...
            if image_4.status == STARTED:
                # update params
                pass
            
            # if image_4 is stopping this frame...
            if image_4.status == STARTED:
                # is it time to stop? (based on global clock, using actual start)
                if tThisFlipGlobal > image_4.tStartRefresh + 0.15-frameTolerance:
                    # keep track of stop time/frame for later
                    image_4.tStop = t  # not accounting for scr refresh
                    image_4.tStopRefresh = tThisFlipGlobal  # on global time
                    image_4.frameNStop = frameN  # exact frame index
                    # update status
                    image_4.status = FINISHED
                    image_4.setAutoDraw(False)
            
            # *text_7* updates
            
            # if text_7 is starting this frame...
            if text_7.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                # keep track of start time/frame for later
                text_7.frameNStart = frameN  # exact frame index
                text_7.tStart = t  # local t and not account for scr refresh
                text_7.tStartRefresh = tThisFlipGlobal  # on global time
                win.timeOnFlip(text_7, 'tStartRefresh')  # time at next scr refresh
                # update status
                text_7.status = STARTED
                text_7.setAutoDraw(True)
            
            # if text_7 is active this frame...
            if text_7.status == STARTED:
                # update params
                pass
            
            # if text_7 is stopping this frame...
            if text_7.status == STARTED:
                # is it time to stop? (based on global clock, using actual start)
                if tThisFlipGlobal > text_7.tStartRefresh + 0.8-frameTolerance:
                    # keep track of stop time/frame for later
                    text_7.tStop = t  # not accounting for scr refresh
                    text_7.tStopRefresh = tThisFlipGlobal  # on global time
                    text_7.frameNStop = frameN  # exact frame index
                    # update status
                    text_7.status = FINISHED
                    text_7.setAutoDraw(False)
            
            # check for quit (typically the Esc key)
            if defaultKeyboard.getKeys(keyList=["escape"]):
                thisExp.status = FINISHED
            if thisExp.status == FINISHED or endExpNow:
                endExperiment(thisExp, win=win)
                return
            # pause experiment here if requested
            if thisExp.status == PAUSED:
                pauseExperiment(
                    thisExp=thisExp, 
                    win=win, 
                    timers=[routineTimer, globalClock], 
                    currentRoutine=NeckerBaseline,
                )
                # skip the frame we paused on
                continue
            
            # has a Component requested the Routine to end?
            if not continueRoutine:
                NeckerBaseline.forceEnded = routineForceEnded = True
            # has the Routine been forcibly ended?
            if NeckerBaseline.forceEnded or routineForceEnded:
                break
            # has every Component finished?
            continueRoutine = False
            for thisComponent in NeckerBaseline.components:
                if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                    continueRoutine = True
                    break  # at least one component has not yet finished
            
            # refresh the screen
            if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                win.flip()
        
        # --- Ending Routine "NeckerBaseline" ---
        for thisComponent in NeckerBaseline.components:
            if hasattr(thisComponent, "setAutoDraw"):
                thisComponent.setAutoDraw(False)
        # store stop times for NeckerBaseline
        NeckerBaseline.tStop = globalClock.getTime(format='float')
        NeckerBaseline.tStopRefresh = tThisFlipGlobal
        thisExp.addData('NeckerBaseline.stopped', NeckerBaseline.tStop)
        # using non-slip timing so subtract the expected duration of this Routine (unless ended on request)
        if NeckerBaseline.maxDurationReached:
            routineTimer.addTime(-NeckerBaseline.maxDuration)
        elif NeckerBaseline.forceEnded:
            routineTimer.reset()
        else:
            routineTimer.addTime(-0.800000)
        
        # --- Prepare to start Routine "blank" ---
        # create an object to store info about Routine blank
        blank = data.Routine(
            name='blank',
            components=[image4, key_resp, text_8],
        )
        blank.status = NOT_STARTED
        continueRoutine = True
        # update component parameters for each repeat
        image4.setImage(choice)
        # create starting attributes for key_resp
        key_resp.keys = []
        key_resp.rt = []
        _key_resp_allKeys = []
        # store start times for blank
        blank.tStartRefresh = win.getFutureFlipTime(clock=globalClock)
        blank.tStart = globalClock.getTime(format='float')
        blank.status = STARTED
        thisExp.addData('blank.started', blank.tStart)
        blank.maxDuration = None
        # keep track of which components have finished
        blankComponents = blank.components
        for thisComponent in blank.components:
            thisComponent.tStart = None
            thisComponent.tStop = None
            thisComponent.tStartRefresh = None
            thisComponent.tStopRefresh = None
            if hasattr(thisComponent, 'status'):
                thisComponent.status = NOT_STARTED
        # reset timers
        t = 0
        _timeToFirstFrame = win.getFutureFlipTime(clock="now")
        frameN = -1
        
        # --- Run Routine "blank" ---
        thisExp.currentRoutine = blank
        blank.forceEnded = routineForceEnded = not continueRoutine
        while continueRoutine and routineTimer.getTime() < 3.0:
            # if trial has changed, end Routine now
            if hasattr(thisTrial_9, 'status') and thisTrial_9.status == STOPPING:
                continueRoutine = False
            # get current time
            t = routineTimer.getTime()
            tThisFlip = win.getFutureFlipTime(clock=routineTimer)
            tThisFlipGlobal = win.getFutureFlipTime(clock=None)
            frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
            # update/draw components on each frame
            
            # *image4* updates
            
            # if image4 is starting this frame...
            if image4.status == NOT_STARTED and tThisFlip >= 0-frameTolerance:
                # keep track of start time/frame for later
                image4.frameNStart = frameN  # exact frame index
                image4.tStart = t  # local t and not account for scr refresh
                image4.tStartRefresh = tThisFlipGlobal  # on global time
                win.timeOnFlip(image4, 'tStartRefresh')  # time at next scr refresh
                # update status
                image4.status = STARTED
                image4.setAutoDraw(True)
            
            # if image4 is active this frame...
            if image4.status == STARTED:
                # update params
                pass
            
            # if image4 is stopping this frame...
            if image4.status == STARTED:
                # is it time to stop? (based on global clock, using actual start)
                if tThisFlipGlobal > image4.tStartRefresh + 3-frameTolerance:
                    # keep track of stop time/frame for later
                    image4.tStop = t  # not accounting for scr refresh
                    image4.tStopRefresh = tThisFlipGlobal  # on global time
                    image4.frameNStop = frameN  # exact frame index
                    # update status
                    image4.status = FINISHED
                    image4.setAutoDraw(False)
            
            # *key_resp* updates
            waitOnFlip = False
            
            # if key_resp is starting this frame...
            if key_resp.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                # keep track of start time/frame for later
                key_resp.frameNStart = frameN  # exact frame index
                key_resp.tStart = t  # local t and not account for scr refresh
                key_resp.tStartRefresh = tThisFlipGlobal  # on global time
                win.timeOnFlip(key_resp, 'tStartRefresh')  # time at next scr refresh
                # add timestamp to datafile
                thisExp.timestampOnFlip(win, 'key_resp.started')
                # update status
                key_resp.status = STARTED
                # keyboard checking is just starting
                waitOnFlip = True
                win.callOnFlip(key_resp.clock.reset)  # t=0 on next screen flip
            
            # if key_resp is stopping this frame...
            if key_resp.status == STARTED:
                # is it time to stop? (based on global clock, using actual start)
                if tThisFlipGlobal > key_resp.tStartRefresh + 3-frameTolerance:
                    # keep track of stop time/frame for later
                    key_resp.tStop = t  # not accounting for scr refresh
                    key_resp.tStopRefresh = tThisFlipGlobal  # on global time
                    key_resp.frameNStop = frameN  # exact frame index
                    # add timestamp to datafile
                    thisExp.timestampOnFlip(win, 'key_resp.stopped')
                    # update status
                    key_resp.status = FINISHED
                    key_resp.status = FINISHED
            if key_resp.status == STARTED and not waitOnFlip:
                theseKeys = key_resp.getKeys(keyList=['left','right'], ignoreKeys=["escape"], waitRelease=False)
                _key_resp_allKeys.extend(theseKeys)
                if len(_key_resp_allKeys):
                    key_resp.keys = _key_resp_allKeys[-1].name  # just the last key pressed
                    key_resp.rt = _key_resp_allKeys[-1].rt
                    key_resp.duration = _key_resp_allKeys[-1].duration
                    # a response ends the routine
                    continueRoutine = False
            
            # *text_8* updates
            
            # if text_8 is starting this frame...
            if text_8.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                # keep track of start time/frame for later
                text_8.frameNStart = frameN  # exact frame index
                text_8.tStart = t  # local t and not account for scr refresh
                text_8.tStartRefresh = tThisFlipGlobal  # on global time
                win.timeOnFlip(text_8, 'tStartRefresh')  # time at next scr refresh
                # update status
                text_8.status = STARTED
                text_8.setAutoDraw(True)
            
            # if text_8 is active this frame...
            if text_8.status == STARTED:
                # update params
                pass
            
            # if text_8 is stopping this frame...
            if text_8.status == STARTED:
                # is it time to stop? (based on global clock, using actual start)
                if tThisFlipGlobal > text_8.tStartRefresh + 3-frameTolerance:
                    # keep track of stop time/frame for later
                    text_8.tStop = t  # not accounting for scr refresh
                    text_8.tStopRefresh = tThisFlipGlobal  # on global time
                    text_8.frameNStop = frameN  # exact frame index
                    # update status
                    text_8.status = FINISHED
                    text_8.setAutoDraw(False)
            
            # check for quit (typically the Esc key)
            if defaultKeyboard.getKeys(keyList=["escape"]):
                thisExp.status = FINISHED
            if thisExp.status == FINISHED or endExpNow:
                endExperiment(thisExp, win=win)
                return
            # pause experiment here if requested
            if thisExp.status == PAUSED:
                pauseExperiment(
                    thisExp=thisExp, 
                    win=win, 
                    timers=[routineTimer, globalClock], 
                    currentRoutine=blank,
                )
                # skip the frame we paused on
                continue
            
            # has a Component requested the Routine to end?
            if not continueRoutine:
                blank.forceEnded = routineForceEnded = True
            # has the Routine been forcibly ended?
            if blank.forceEnded or routineForceEnded:
                break
            # has every Component finished?
            continueRoutine = False
            for thisComponent in blank.components:
                if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                    continueRoutine = True
                    break  # at least one component has not yet finished
            
            # refresh the screen
            if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                win.flip()
        
        # --- Ending Routine "blank" ---
        for thisComponent in blank.components:
            if hasattr(thisComponent, "setAutoDraw"):
                thisComponent.setAutoDraw(False)
        # store stop times for blank
        blank.tStop = globalClock.getTime(format='float')
        blank.tStopRefresh = tThisFlipGlobal
        thisExp.addData('blank.stopped', blank.tStop)
        # check responses
        if key_resp.keys in ['', [], None]:  # No response was made
            key_resp.keys = None
        trials_9.addData('key_resp.keys',key_resp.keys)
        if key_resp.keys != None:  # we had a response
            trials_9.addData('key_resp.rt', key_resp.rt)
            trials_9.addData('key_resp.duration', key_resp.duration)
        # using non-slip timing so subtract the expected duration of this Routine (unless ended on request)
        if blank.maxDurationReached:
            routineTimer.addTime(-blank.maxDuration)
        elif blank.forceEnded:
            routineTimer.reset()
        else:
            routineTimer.addTime(-3.000000)
        # mark thisTrial_9 as finished
        if hasattr(thisTrial_9, 'status'):
            thisTrial_9.status = FINISHED
        # if awaiting a pause, pause now
        if trials_9.status == PAUSED:
            thisExp.status = PAUSED
            pauseExperiment(
                thisExp=thisExp, 
                win=win, 
                timers=[globalClock], 
            )
            # once done pausing, restore running status
            trials_9.status = STARTED
        thisExp.nextEntry()
        
    # completed 1.0 repeats of 'trials_9'
    trials_9.status = FINISHED
    
    if thisSession is not None:
        # if running in a Session with a Liaison client, send data up to now
        thisSession.sendExperimentData()
    
    # --- Prepare to start Routine "Baseline" ---
    # create an object to store info about Routine Baseline
    Baseline = data.Routine(
        name='Baseline',
        components=[text_26, key_resp_11],
    )
    Baseline.status = NOT_STARTED
    continueRoutine = True
    # update component parameters for each repeat
    # create starting attributes for key_resp_11
    key_resp_11.keys = []
    key_resp_11.rt = []
    _key_resp_11_allKeys = []
    # store start times for Baseline
    Baseline.tStartRefresh = win.getFutureFlipTime(clock=globalClock)
    Baseline.tStart = globalClock.getTime(format='float')
    Baseline.status = STARTED
    thisExp.addData('Baseline.started', Baseline.tStart)
    Baseline.maxDuration = None
    # keep track of which components have finished
    BaselineComponents = Baseline.components
    for thisComponent in Baseline.components:
        thisComponent.tStart = None
        thisComponent.tStop = None
        thisComponent.tStartRefresh = None
        thisComponent.tStopRefresh = None
        if hasattr(thisComponent, 'status'):
            thisComponent.status = NOT_STARTED
    # reset timers
    t = 0
    _timeToFirstFrame = win.getFutureFlipTime(clock="now")
    frameN = -1
    
    # --- Run Routine "Baseline" ---
    thisExp.currentRoutine = Baseline
    Baseline.forceEnded = routineForceEnded = not continueRoutine
    while continueRoutine:
        # get current time
        t = routineTimer.getTime()
        tThisFlip = win.getFutureFlipTime(clock=routineTimer)
        tThisFlipGlobal = win.getFutureFlipTime(clock=None)
        frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
        # update/draw components on each frame
        
        # *text_26* updates
        
        # if text_26 is starting this frame...
        if text_26.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            text_26.frameNStart = frameN  # exact frame index
            text_26.tStart = t  # local t and not account for scr refresh
            text_26.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(text_26, 'tStartRefresh')  # time at next scr refresh
            # update status
            text_26.status = STARTED
            text_26.setAutoDraw(True)
        
        # if text_26 is active this frame...
        if text_26.status == STARTED:
            # update params
            pass
        
        # *key_resp_11* updates
        waitOnFlip = False
        
        # if key_resp_11 is starting this frame...
        if key_resp_11.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            key_resp_11.frameNStart = frameN  # exact frame index
            key_resp_11.tStart = t  # local t and not account for scr refresh
            key_resp_11.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(key_resp_11, 'tStartRefresh')  # time at next scr refresh
            # update status
            key_resp_11.status = STARTED
            # keyboard checking is just starting
            waitOnFlip = True
            win.callOnFlip(key_resp_11.clock.reset)  # t=0 on next screen flip
            win.callOnFlip(key_resp_11.clearEvents, eventType='keyboard')  # clear events on next screen flip
        if key_resp_11.status == STARTED and not waitOnFlip:
            theseKeys = key_resp_11.getKeys(keyList=['space'], ignoreKeys=["escape"], waitRelease=False)
            _key_resp_11_allKeys.extend(theseKeys)
            if len(_key_resp_11_allKeys):
                key_resp_11.keys = _key_resp_11_allKeys[-1].name  # just the last key pressed
                key_resp_11.rt = _key_resp_11_allKeys[-1].rt
                key_resp_11.duration = _key_resp_11_allKeys[-1].duration
                # a response ends the routine
                continueRoutine = False
        
        # check for quit (typically the Esc key)
        if defaultKeyboard.getKeys(keyList=["escape"]):
            thisExp.status = FINISHED
        if thisExp.status == FINISHED or endExpNow:
            endExperiment(thisExp, win=win)
            return
        # pause experiment here if requested
        if thisExp.status == PAUSED:
            pauseExperiment(
                thisExp=thisExp, 
                win=win, 
                timers=[routineTimer, globalClock], 
                currentRoutine=Baseline,
            )
            # skip the frame we paused on
            continue
        
        # has a Component requested the Routine to end?
        if not continueRoutine:
            Baseline.forceEnded = routineForceEnded = True
        # has the Routine been forcibly ended?
        if Baseline.forceEnded or routineForceEnded:
            break
        # has every Component finished?
        continueRoutine = False
        for thisComponent in Baseline.components:
            if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                continueRoutine = True
                break  # at least one component has not yet finished
        
        # refresh the screen
        if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
            win.flip()
    
    # --- Ending Routine "Baseline" ---
    for thisComponent in Baseline.components:
        if hasattr(thisComponent, "setAutoDraw"):
            thisComponent.setAutoDraw(False)
    # store stop times for Baseline
    Baseline.tStop = globalClock.getTime(format='float')
    Baseline.tStopRefresh = tThisFlipGlobal
    thisExp.addData('Baseline.stopped', Baseline.tStop)
    # check responses
    if key_resp_11.keys in ['', [], None]:  # No response was made
        key_resp_11.keys = None
    thisExp.addData('key_resp_11.keys',key_resp_11.keys)
    if key_resp_11.keys != None:  # we had a response
        thisExp.addData('key_resp_11.rt', key_resp_11.rt)
        thisExp.addData('key_resp_11.duration', key_resp_11.duration)
    thisExp.nextEntry()
    # the Routine "Baseline" was not non-slip safe, so reset the non-slip timer
    routineTimer.reset()
    
    # --- Prepare to start Routine "cross" ---
    # create an object to store info about Routine cross
    cross = data.Routine(
        name='cross',
        components=[text_6],
    )
    cross.status = NOT_STARTED
    continueRoutine = True
    # update component parameters for each repeat
    # store start times for cross
    cross.tStartRefresh = win.getFutureFlipTime(clock=globalClock)
    cross.tStart = globalClock.getTime(format='float')
    cross.status = STARTED
    thisExp.addData('cross.started', cross.tStart)
    cross.maxDuration = None
    # keep track of which components have finished
    crossComponents = cross.components
    for thisComponent in cross.components:
        thisComponent.tStart = None
        thisComponent.tStop = None
        thisComponent.tStartRefresh = None
        thisComponent.tStopRefresh = None
        if hasattr(thisComponent, 'status'):
            thisComponent.status = NOT_STARTED
    # reset timers
    t = 0
    _timeToFirstFrame = win.getFutureFlipTime(clock="now")
    frameN = -1
    
    # --- Run Routine "cross" ---
    thisExp.currentRoutine = cross
    cross.forceEnded = routineForceEnded = not continueRoutine
    while continueRoutine and routineTimer.getTime() < 1.0:
        # get current time
        t = routineTimer.getTime()
        tThisFlip = win.getFutureFlipTime(clock=routineTimer)
        tThisFlipGlobal = win.getFutureFlipTime(clock=None)
        frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
        # update/draw components on each frame
        
        # *text_6* updates
        
        # if text_6 is starting this frame...
        if text_6.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            text_6.frameNStart = frameN  # exact frame index
            text_6.tStart = t  # local t and not account for scr refresh
            text_6.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(text_6, 'tStartRefresh')  # time at next scr refresh
            # update status
            text_6.status = STARTED
            text_6.setAutoDraw(True)
        
        # if text_6 is active this frame...
        if text_6.status == STARTED:
            # update params
            pass
        
        # if text_6 is stopping this frame...
        if text_6.status == STARTED:
            # is it time to stop? (based on global clock, using actual start)
            if tThisFlipGlobal > text_6.tStartRefresh + 1.0-frameTolerance:
                # keep track of stop time/frame for later
                text_6.tStop = t  # not accounting for scr refresh
                text_6.tStopRefresh = tThisFlipGlobal  # on global time
                text_6.frameNStop = frameN  # exact frame index
                # update status
                text_6.status = FINISHED
                text_6.setAutoDraw(False)
        
        # check for quit (typically the Esc key)
        if defaultKeyboard.getKeys(keyList=["escape"]):
            thisExp.status = FINISHED
        if thisExp.status == FINISHED or endExpNow:
            endExperiment(thisExp, win=win)
            return
        # pause experiment here if requested
        if thisExp.status == PAUSED:
            pauseExperiment(
                thisExp=thisExp, 
                win=win, 
                timers=[routineTimer, globalClock], 
                currentRoutine=cross,
            )
            # skip the frame we paused on
            continue
        
        # has a Component requested the Routine to end?
        if not continueRoutine:
            cross.forceEnded = routineForceEnded = True
        # has the Routine been forcibly ended?
        if cross.forceEnded or routineForceEnded:
            break
        # has every Component finished?
        continueRoutine = False
        for thisComponent in cross.components:
            if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                continueRoutine = True
                break  # at least one component has not yet finished
        
        # refresh the screen
        if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
            win.flip()
    
    # --- Ending Routine "cross" ---
    for thisComponent in cross.components:
        if hasattr(thisComponent, "setAutoDraw"):
            thisComponent.setAutoDraw(False)
    # store stop times for cross
    cross.tStop = globalClock.getTime(format='float')
    cross.tStopRefresh = tThisFlipGlobal
    thisExp.addData('cross.stopped', cross.tStop)
    # using non-slip timing so subtract the expected duration of this Routine (unless ended on request)
    if cross.maxDurationReached:
        routineTimer.addTime(-cross.maxDuration)
    elif cross.forceEnded:
        routineTimer.reset()
    else:
        routineTimer.addTime(-1.000000)
    thisExp.nextEntry()
    
    # set up handler to look after randomisation of conditions etc
    trials_6 = data.TrialHandler2(
        name='trials_6',
        nReps=5.0, 
        method='random', 
        extraInfo=expInfo, 
        originPath=-1, 
        trialList=[None], 
        seed=None, 
        isTrials=True, 
    )
    thisExp.addLoop(trials_6)  # add the loop to the experiment
    thisTrial_6 = trials_6.trialList[0]  # so we can initialise stimuli with some values
    # abbreviate parameter names if possible (e.g. rgb = thisTrial_6.rgb)
    if thisTrial_6 != None:
        for paramName in thisTrial_6:
            globals()[paramName] = thisTrial_6[paramName]
    if thisSession is not None:
        # if running in a Session with a Liaison client, send data up to now
        thisSession.sendExperimentData()
    
    for thisTrial_6 in trials_6:
        trials_6.status = STARTED
        if hasattr(thisTrial_6, 'status'):
            thisTrial_6.status = STARTED
        currentLoop = trials_6
        thisExp.timestampOnFlip(win, 'thisRow.t', format=globalClock.format)
        if thisSession is not None:
            # if running in a Session with a Liaison client, send data up to now
            thisSession.sendExperimentData()
        # abbreviate parameter names if possible (e.g. rgb = thisTrial_6.rgb)
        if thisTrial_6 != None:
            for paramName in thisTrial_6:
                globals()[paramName] = thisTrial_6[paramName]
        
        # set up handler to look after randomisation of conditions etc
        trials_3 = data.TrialHandler2(
            name='trials_3',
            nReps=3.0, 
            method='random', 
            extraInfo=expInfo, 
            originPath=-1, 
            trialList=data.importConditions('LorR.xlsx'), 
            seed=None, 
            isTrials=True, 
        )
        thisExp.addLoop(trials_3)  # add the loop to the experiment
        thisTrial_3 = trials_3.trialList[0]  # so we can initialise stimuli with some values
        # abbreviate parameter names if possible (e.g. rgb = thisTrial_3.rgb)
        if thisTrial_3 != None:
            for paramName in thisTrial_3:
                globals()[paramName] = thisTrial_3[paramName]
        if thisSession is not None:
            # if running in a Session with a Liaison client, send data up to now
            thisSession.sendExperimentData()
        
        for thisTrial_3 in trials_3:
            trials_3.status = STARTED
            if hasattr(thisTrial_3, 'status'):
                thisTrial_3.status = STARTED
            currentLoop = trials_3
            thisExp.timestampOnFlip(win, 'thisRow.t', format=globalClock.format)
            if thisSession is not None:
                # if running in a Session with a Liaison client, send data up to now
                thisSession.sendExperimentData()
            # abbreviate parameter names if possible (e.g. rgb = thisTrial_3.rgb)
            if thisTrial_3 != None:
                for paramName in thisTrial_3:
                    globals()[paramName] = thisTrial_3[paramName]
            
            # --- Prepare to start Routine "blank_cross" ---
            # create an object to store info about Routine blank_cross
            blank_cross = data.Routine(
                name='blank_cross',
                components=[text_4],
            )
            blank_cross.status = NOT_STARTED
            continueRoutine = True
            # update component parameters for each repeat
            text_4.setText('+')
            # store start times for blank_cross
            blank_cross.tStartRefresh = win.getFutureFlipTime(clock=globalClock)
            blank_cross.tStart = globalClock.getTime(format='float')
            blank_cross.status = STARTED
            thisExp.addData('blank_cross.started', blank_cross.tStart)
            blank_cross.maxDuration = None
            # keep track of which components have finished
            blank_crossComponents = blank_cross.components
            for thisComponent in blank_cross.components:
                thisComponent.tStart = None
                thisComponent.tStop = None
                thisComponent.tStartRefresh = None
                thisComponent.tStopRefresh = None
                if hasattr(thisComponent, 'status'):
                    thisComponent.status = NOT_STARTED
            # reset timers
            t = 0
            _timeToFirstFrame = win.getFutureFlipTime(clock="now")
            frameN = -1
            
            # --- Run Routine "blank_cross" ---
            thisExp.currentRoutine = blank_cross
            blank_cross.forceEnded = routineForceEnded = not continueRoutine
            while continueRoutine:
                # if trial has changed, end Routine now
                if hasattr(thisTrial_3, 'status') and thisTrial_3.status == STOPPING:
                    continueRoutine = False
                # get current time
                t = routineTimer.getTime()
                tThisFlip = win.getFutureFlipTime(clock=routineTimer)
                tThisFlipGlobal = win.getFutureFlipTime(clock=None)
                frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
                # update/draw components on each frame
                
                # *text_4* updates
                
                # if text_4 is starting this frame...
                if text_4.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                    # keep track of start time/frame for later
                    text_4.frameNStart = frameN  # exact frame index
                    text_4.tStart = t  # local t and not account for scr refresh
                    text_4.tStartRefresh = tThisFlipGlobal  # on global time
                    win.timeOnFlip(text_4, 'tStartRefresh')  # time at next scr refresh
                    # add timestamp to datafile
                    thisExp.timestampOnFlip(win, 'text_4.started')
                    # update status
                    text_4.status = STARTED
                    text_4.setAutoDraw(True)
                
                # if text_4 is active this frame...
                if text_4.status == STARTED:
                    # update params
                    pass
                
                # if text_4 is stopping this frame...
                if text_4.status == STARTED:
                    if frameN >= (text_4.frameNStart + randint(62, 125)):
                        # keep track of stop time/frame for later
                        text_4.tStop = t  # not accounting for scr refresh
                        text_4.tStopRefresh = tThisFlipGlobal  # on global time
                        text_4.frameNStop = frameN  # exact frame index
                        # add timestamp to datafile
                        thisExp.timestampOnFlip(win, 'text_4.stopped')
                        # update status
                        text_4.status = FINISHED
                        text_4.setAutoDraw(False)
                
                # check for quit (typically the Esc key)
                if defaultKeyboard.getKeys(keyList=["escape"]):
                    thisExp.status = FINISHED
                if thisExp.status == FINISHED or endExpNow:
                    endExperiment(thisExp, win=win)
                    return
                # pause experiment here if requested
                if thisExp.status == PAUSED:
                    pauseExperiment(
                        thisExp=thisExp, 
                        win=win, 
                        timers=[routineTimer, globalClock], 
                        currentRoutine=blank_cross,
                    )
                    # skip the frame we paused on
                    continue
                
                # has a Component requested the Routine to end?
                if not continueRoutine:
                    blank_cross.forceEnded = routineForceEnded = True
                # has the Routine been forcibly ended?
                if blank_cross.forceEnded or routineForceEnded:
                    break
                # has every Component finished?
                continueRoutine = False
                for thisComponent in blank_cross.components:
                    if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                        continueRoutine = True
                        break  # at least one component has not yet finished
                
                # refresh the screen
                if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                    win.flip()
            
            # --- Ending Routine "blank_cross" ---
            for thisComponent in blank_cross.components:
                if hasattr(thisComponent, "setAutoDraw"):
                    thisComponent.setAutoDraw(False)
            # store stop times for blank_cross
            blank_cross.tStop = globalClock.getTime(format='float')
            blank_cross.tStopRefresh = tThisFlipGlobal
            thisExp.addData('blank_cross.stopped', blank_cross.tStop)
            # the Routine "blank_cross" was not non-slip safe, so reset the non-slip timer
            routineTimer.reset()
            
            # --- Prepare to start Routine "Base_trigger" ---
            # create an object to store info about Routine Base_trigger
            Base_trigger = data.Routine(
                name='Base_trigger',
                components=[],
            )
            Base_trigger.status = NOT_STARTED
            continueRoutine = True
            # update component parameters for each repeat
            # store start times for Base_trigger
            Base_trigger.tStartRefresh = win.getFutureFlipTime(clock=globalClock)
            Base_trigger.tStart = globalClock.getTime(format='float')
            Base_trigger.status = STARTED
            thisExp.addData('Base_trigger.started', Base_trigger.tStart)
            Base_trigger.maxDuration = None
            # keep track of which components have finished
            Base_triggerComponents = Base_trigger.components
            for thisComponent in Base_trigger.components:
                thisComponent.tStart = None
                thisComponent.tStop = None
                thisComponent.tStartRefresh = None
                thisComponent.tStopRefresh = None
                if hasattr(thisComponent, 'status'):
                    thisComponent.status = NOT_STARTED
            # reset timers
            t = 0
            _timeToFirstFrame = win.getFutureFlipTime(clock="now")
            frameN = -1
            
            # --- Run Routine "Base_trigger" ---
            thisExp.currentRoutine = Base_trigger
            Base_trigger.forceEnded = routineForceEnded = not continueRoutine
            while continueRoutine:
                # if trial has changed, end Routine now
                if hasattr(thisTrial_3, 'status') and thisTrial_3.status == STOPPING:
                    continueRoutine = False
                # get current time
                t = routineTimer.getTime()
                tThisFlip = win.getFutureFlipTime(clock=routineTimer)
                tThisFlipGlobal = win.getFutureFlipTime(clock=None)
                frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
                # update/draw components on each frame
                
                # check for quit (typically the Esc key)
                if defaultKeyboard.getKeys(keyList=["escape"]):
                    thisExp.status = FINISHED
                if thisExp.status == FINISHED or endExpNow:
                    endExperiment(thisExp, win=win)
                    return
                # pause experiment here if requested
                if thisExp.status == PAUSED:
                    pauseExperiment(
                        thisExp=thisExp, 
                        win=win, 
                        timers=[routineTimer, globalClock], 
                        currentRoutine=Base_trigger,
                    )
                    # skip the frame we paused on
                    continue
                
                # has a Component requested the Routine to end?
                if not continueRoutine:
                    Base_trigger.forceEnded = routineForceEnded = True
                # has the Routine been forcibly ended?
                if Base_trigger.forceEnded or routineForceEnded:
                    break
                # has every Component finished?
                continueRoutine = False
                for thisComponent in Base_trigger.components:
                    if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                        continueRoutine = True
                        break  # at least one component has not yet finished
                
                # refresh the screen
                if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                    win.flip()
            
            # --- Ending Routine "Base_trigger" ---
            for thisComponent in Base_trigger.components:
                if hasattr(thisComponent, "setAutoDraw"):
                    thisComponent.setAutoDraw(False)
            # store stop times for Base_trigger
            Base_trigger.tStop = globalClock.getTime(format='float')
            Base_trigger.tStopRefresh = tThisFlipGlobal
            thisExp.addData('Base_trigger.stopped', Base_trigger.tStop)
            # the Routine "Base_trigger" was not non-slip safe, so reset the non-slip timer
            routineTimer.reset()
            
            # --- Prepare to start Routine "Necker" ---
            # create an object to store info about Routine Necker
            Necker = data.Routine(
                name='Necker',
                components=[image_3, text_5, sound_2],
            )
            Necker.status = NOT_STARTED
            continueRoutine = True
            # update component parameters for each repeat
            sound_2.setSound(Sound, secs=0.05, hamming=True)
            sound_2.setVolume(1.0, log=False)
            sound_2.seek(0)
            # store start times for Necker
            Necker.tStartRefresh = win.getFutureFlipTime(clock=globalClock)
            Necker.tStart = globalClock.getTime(format='float')
            Necker.status = STARTED
            thisExp.addData('Necker.started', Necker.tStart)
            Necker.maxDuration = None
            # keep track of which components have finished
            NeckerComponents = Necker.components
            for thisComponent in Necker.components:
                thisComponent.tStart = None
                thisComponent.tStop = None
                thisComponent.tStartRefresh = None
                thisComponent.tStopRefresh = None
                if hasattr(thisComponent, 'status'):
                    thisComponent.status = NOT_STARTED
            # reset timers
            t = 0
            _timeToFirstFrame = win.getFutureFlipTime(clock="now")
            frameN = -1
            
            # --- Run Routine "Necker" ---
            thisExp.currentRoutine = Necker
            Necker.forceEnded = routineForceEnded = not continueRoutine
            while continueRoutine:
                # if trial has changed, end Routine now
                if hasattr(thisTrial_3, 'status') and thisTrial_3.status == STOPPING:
                    continueRoutine = False
                # get current time
                t = routineTimer.getTime()
                tThisFlip = win.getFutureFlipTime(clock=routineTimer)
                tThisFlipGlobal = win.getFutureFlipTime(clock=None)
                frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
                # update/draw components on each frame
                
                # *image_3* updates
                
                # if image_3 is starting this frame...
                if image_3.status == NOT_STARTED and tThisFlip >= 0-frameTolerance:
                    # keep track of start time/frame for later
                    image_3.frameNStart = frameN  # exact frame index
                    image_3.tStart = t  # local t and not account for scr refresh
                    image_3.tStartRefresh = tThisFlipGlobal  # on global time
                    win.timeOnFlip(image_3, 'tStartRefresh')  # time at next scr refresh
                    # add timestamp to datafile
                    thisExp.timestampOnFlip(win, 'image_3.started')
                    # update status
                    image_3.status = STARTED
                    image_3.setAutoDraw(True)
                
                # if image_3 is active this frame...
                if image_3.status == STARTED:
                    # update params
                    pass
                
                # if image_3 is stopping this frame...
                if image_3.status == STARTED:
                    # is it time to stop? (based on global clock, using actual start)
                    if tThisFlipGlobal > image_3.tStartRefresh + 0.15-frameTolerance:
                        # keep track of stop time/frame for later
                        image_3.tStop = t  # not accounting for scr refresh
                        image_3.tStopRefresh = tThisFlipGlobal  # on global time
                        image_3.frameNStop = frameN  # exact frame index
                        # add timestamp to datafile
                        thisExp.timestampOnFlip(win, 'image_3.stopped')
                        # update status
                        image_3.status = FINISHED
                        image_3.setAutoDraw(False)
                
                # *text_5* updates
                
                # if text_5 is starting this frame...
                if text_5.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                    # keep track of start time/frame for later
                    text_5.frameNStart = frameN  # exact frame index
                    text_5.tStart = t  # local t and not account for scr refresh
                    text_5.tStartRefresh = tThisFlipGlobal  # on global time
                    win.timeOnFlip(text_5, 'tStartRefresh')  # time at next scr refresh
                    # add timestamp to datafile
                    thisExp.timestampOnFlip(win, 'text_5.started')
                    # update status
                    text_5.status = STARTED
                    text_5.setAutoDraw(True)
                
                # if text_5 is active this frame...
                if text_5.status == STARTED:
                    # update params
                    pass
                
                # if text_5 is stopping this frame...
                if text_5.status == STARTED:
                    # is it time to stop? (based on global clock, using actual start)
                    if tThisFlipGlobal > text_5.tStartRefresh + 1.5-frameTolerance:
                        # keep track of stop time/frame for later
                        text_5.tStop = t  # not accounting for scr refresh
                        text_5.tStopRefresh = tThisFlipGlobal  # on global time
                        text_5.frameNStop = frameN  # exact frame index
                        # add timestamp to datafile
                        thisExp.timestampOnFlip(win, 'text_5.stopped')
                        # update status
                        text_5.status = FINISHED
                        text_5.setAutoDraw(False)
                
                # *sound_2* updates
                
                # if sound_2 is starting this frame...
                if sound_2.status == NOT_STARTED and tThisFlip >= delay-frameTolerance:
                    # keep track of start time/frame for later
                    sound_2.frameNStart = frameN  # exact frame index
                    sound_2.tStart = t  # local t and not account for scr refresh
                    sound_2.tStartRefresh = tThisFlipGlobal  # on global time
                    # add timestamp to datafile
                    thisExp.addData('sound_2.started', tThisFlipGlobal)
                    # update status
                    sound_2.status = STARTED
                    sound_2.play(when=win)  # sync with win flip
                
                # if sound_2 is stopping this frame...
                if sound_2.status == STARTED:
                    # is it time to stop? (based on global clock, using actual start)
                    if tThisFlipGlobal > sound_2.tStartRefresh + 0.05-frameTolerance or sound_2.isFinished:
                        # keep track of stop time/frame for later
                        sound_2.tStop = t  # not accounting for scr refresh
                        sound_2.tStopRefresh = tThisFlipGlobal  # on global time
                        sound_2.frameNStop = frameN  # exact frame index
                        # add timestamp to datafile
                        thisExp.timestampOnFlip(win, 'sound_2.stopped')
                        # update status
                        sound_2.status = FINISHED
                        sound_2.stop()
                
                # check for quit (typically the Esc key)
                if defaultKeyboard.getKeys(keyList=["escape"]):
                    thisExp.status = FINISHED
                if thisExp.status == FINISHED or endExpNow:
                    endExperiment(thisExp, win=win)
                    return
                # pause experiment here if requested
                if thisExp.status == PAUSED:
                    pauseExperiment(
                        thisExp=thisExp, 
                        win=win, 
                        timers=[routineTimer, globalClock], 
                        currentRoutine=Necker,
                    )
                    # skip the frame we paused on
                    continue
                
                # has a Component requested the Routine to end?
                if not continueRoutine:
                    Necker.forceEnded = routineForceEnded = True
                # has the Routine been forcibly ended?
                if Necker.forceEnded or routineForceEnded:
                    break
                # has every Component finished?
                continueRoutine = False
                for thisComponent in Necker.components:
                    if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                        continueRoutine = True
                        break  # at least one component has not yet finished
                
                # refresh the screen
                if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                    win.flip()
            
            # --- Ending Routine "Necker" ---
            for thisComponent in Necker.components:
                if hasattr(thisComponent, "setAutoDraw"):
                    thisComponent.setAutoDraw(False)
            # store stop times for Necker
            Necker.tStop = globalClock.getTime(format='float')
            Necker.tStopRefresh = tThisFlipGlobal
            thisExp.addData('Necker.stopped', Necker.tStop)
            sound_2.pause()  # ensure sound has stopped at end of Routine
            # the Routine "Necker" was not non-slip safe, so reset the non-slip timer
            routineTimer.reset()
            
            # --- Prepare to start Routine "blank" ---
            # create an object to store info about Routine blank
            blank = data.Routine(
                name='blank',
                components=[image4, key_resp, text_8],
            )
            blank.status = NOT_STARTED
            continueRoutine = True
            # update component parameters for each repeat
            image4.setImage(choice)
            # create starting attributes for key_resp
            key_resp.keys = []
            key_resp.rt = []
            _key_resp_allKeys = []
            # store start times for blank
            blank.tStartRefresh = win.getFutureFlipTime(clock=globalClock)
            blank.tStart = globalClock.getTime(format='float')
            blank.status = STARTED
            thisExp.addData('blank.started', blank.tStart)
            blank.maxDuration = None
            # keep track of which components have finished
            blankComponents = blank.components
            for thisComponent in blank.components:
                thisComponent.tStart = None
                thisComponent.tStop = None
                thisComponent.tStartRefresh = None
                thisComponent.tStopRefresh = None
                if hasattr(thisComponent, 'status'):
                    thisComponent.status = NOT_STARTED
            # reset timers
            t = 0
            _timeToFirstFrame = win.getFutureFlipTime(clock="now")
            frameN = -1
            
            # --- Run Routine "blank" ---
            thisExp.currentRoutine = blank
            blank.forceEnded = routineForceEnded = not continueRoutine
            while continueRoutine and routineTimer.getTime() < 3.0:
                # if trial has changed, end Routine now
                if hasattr(thisTrial_3, 'status') and thisTrial_3.status == STOPPING:
                    continueRoutine = False
                # get current time
                t = routineTimer.getTime()
                tThisFlip = win.getFutureFlipTime(clock=routineTimer)
                tThisFlipGlobal = win.getFutureFlipTime(clock=None)
                frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
                # update/draw components on each frame
                
                # *image4* updates
                
                # if image4 is starting this frame...
                if image4.status == NOT_STARTED and tThisFlip >= 0-frameTolerance:
                    # keep track of start time/frame for later
                    image4.frameNStart = frameN  # exact frame index
                    image4.tStart = t  # local t and not account for scr refresh
                    image4.tStartRefresh = tThisFlipGlobal  # on global time
                    win.timeOnFlip(image4, 'tStartRefresh')  # time at next scr refresh
                    # update status
                    image4.status = STARTED
                    image4.setAutoDraw(True)
                
                # if image4 is active this frame...
                if image4.status == STARTED:
                    # update params
                    pass
                
                # if image4 is stopping this frame...
                if image4.status == STARTED:
                    # is it time to stop? (based on global clock, using actual start)
                    if tThisFlipGlobal > image4.tStartRefresh + 3-frameTolerance:
                        # keep track of stop time/frame for later
                        image4.tStop = t  # not accounting for scr refresh
                        image4.tStopRefresh = tThisFlipGlobal  # on global time
                        image4.frameNStop = frameN  # exact frame index
                        # update status
                        image4.status = FINISHED
                        image4.setAutoDraw(False)
                
                # *key_resp* updates
                waitOnFlip = False
                
                # if key_resp is starting this frame...
                if key_resp.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                    # keep track of start time/frame for later
                    key_resp.frameNStart = frameN  # exact frame index
                    key_resp.tStart = t  # local t and not account for scr refresh
                    key_resp.tStartRefresh = tThisFlipGlobal  # on global time
                    win.timeOnFlip(key_resp, 'tStartRefresh')  # time at next scr refresh
                    # add timestamp to datafile
                    thisExp.timestampOnFlip(win, 'key_resp.started')
                    # update status
                    key_resp.status = STARTED
                    # keyboard checking is just starting
                    waitOnFlip = True
                    win.callOnFlip(key_resp.clock.reset)  # t=0 on next screen flip
                
                # if key_resp is stopping this frame...
                if key_resp.status == STARTED:
                    # is it time to stop? (based on global clock, using actual start)
                    if tThisFlipGlobal > key_resp.tStartRefresh + 3-frameTolerance:
                        # keep track of stop time/frame for later
                        key_resp.tStop = t  # not accounting for scr refresh
                        key_resp.tStopRefresh = tThisFlipGlobal  # on global time
                        key_resp.frameNStop = frameN  # exact frame index
                        # add timestamp to datafile
                        thisExp.timestampOnFlip(win, 'key_resp.stopped')
                        # update status
                        key_resp.status = FINISHED
                        key_resp.status = FINISHED
                if key_resp.status == STARTED and not waitOnFlip:
                    theseKeys = key_resp.getKeys(keyList=['left','right'], ignoreKeys=["escape"], waitRelease=False)
                    _key_resp_allKeys.extend(theseKeys)
                    if len(_key_resp_allKeys):
                        key_resp.keys = _key_resp_allKeys[-1].name  # just the last key pressed
                        key_resp.rt = _key_resp_allKeys[-1].rt
                        key_resp.duration = _key_resp_allKeys[-1].duration
                        # a response ends the routine
                        continueRoutine = False
                
                # *text_8* updates
                
                # if text_8 is starting this frame...
                if text_8.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                    # keep track of start time/frame for later
                    text_8.frameNStart = frameN  # exact frame index
                    text_8.tStart = t  # local t and not account for scr refresh
                    text_8.tStartRefresh = tThisFlipGlobal  # on global time
                    win.timeOnFlip(text_8, 'tStartRefresh')  # time at next scr refresh
                    # update status
                    text_8.status = STARTED
                    text_8.setAutoDraw(True)
                
                # if text_8 is active this frame...
                if text_8.status == STARTED:
                    # update params
                    pass
                
                # if text_8 is stopping this frame...
                if text_8.status == STARTED:
                    # is it time to stop? (based on global clock, using actual start)
                    if tThisFlipGlobal > text_8.tStartRefresh + 3-frameTolerance:
                        # keep track of stop time/frame for later
                        text_8.tStop = t  # not accounting for scr refresh
                        text_8.tStopRefresh = tThisFlipGlobal  # on global time
                        text_8.frameNStop = frameN  # exact frame index
                        # update status
                        text_8.status = FINISHED
                        text_8.setAutoDraw(False)
                
                # check for quit (typically the Esc key)
                if defaultKeyboard.getKeys(keyList=["escape"]):
                    thisExp.status = FINISHED
                if thisExp.status == FINISHED or endExpNow:
                    endExperiment(thisExp, win=win)
                    return
                # pause experiment here if requested
                if thisExp.status == PAUSED:
                    pauseExperiment(
                        thisExp=thisExp, 
                        win=win, 
                        timers=[routineTimer, globalClock], 
                        currentRoutine=blank,
                    )
                    # skip the frame we paused on
                    continue
                
                # has a Component requested the Routine to end?
                if not continueRoutine:
                    blank.forceEnded = routineForceEnded = True
                # has the Routine been forcibly ended?
                if blank.forceEnded or routineForceEnded:
                    break
                # has every Component finished?
                continueRoutine = False
                for thisComponent in blank.components:
                    if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                        continueRoutine = True
                        break  # at least one component has not yet finished
                
                # refresh the screen
                if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                    win.flip()
            
            # --- Ending Routine "blank" ---
            for thisComponent in blank.components:
                if hasattr(thisComponent, "setAutoDraw"):
                    thisComponent.setAutoDraw(False)
            # store stop times for blank
            blank.tStop = globalClock.getTime(format='float')
            blank.tStopRefresh = tThisFlipGlobal
            thisExp.addData('blank.stopped', blank.tStop)
            # check responses
            if key_resp.keys in ['', [], None]:  # No response was made
                key_resp.keys = None
            trials_3.addData('key_resp.keys',key_resp.keys)
            if key_resp.keys != None:  # we had a response
                trials_3.addData('key_resp.rt', key_resp.rt)
                trials_3.addData('key_resp.duration', key_resp.duration)
            # using non-slip timing so subtract the expected duration of this Routine (unless ended on request)
            if blank.maxDurationReached:
                routineTimer.addTime(-blank.maxDuration)
            elif blank.forceEnded:
                routineTimer.reset()
            else:
                routineTimer.addTime(-3.000000)
            # mark thisTrial_3 as finished
            if hasattr(thisTrial_3, 'status'):
                thisTrial_3.status = FINISHED
            # if awaiting a pause, pause now
            if trials_3.status == PAUSED:
                thisExp.status = PAUSED
                pauseExperiment(
                    thisExp=thisExp, 
                    win=win, 
                    timers=[globalClock], 
                )
                # once done pausing, restore running status
                trials_3.status = STARTED
            thisExp.nextEntry()
            
        # completed 3.0 repeats of 'trials_3'
        trials_3.status = FINISHED
        
        if thisSession is not None:
            # if running in a Session with a Liaison client, send data up to now
            thisSession.sendExperimentData()
        
        # --- Prepare to start Routine "break_2" ---
        # create an object to store info about Routine break_2
        break_2 = data.Routine(
            name='break_2',
            components=[text_9, key_resp_3],
        )
        break_2.status = NOT_STARTED
        continueRoutine = True
        # update component parameters for each repeat
        # create starting attributes for key_resp_3
        key_resp_3.keys = []
        key_resp_3.rt = []
        _key_resp_3_allKeys = []
        # store start times for break_2
        break_2.tStartRefresh = win.getFutureFlipTime(clock=globalClock)
        break_2.tStart = globalClock.getTime(format='float')
        break_2.status = STARTED
        thisExp.addData('break_2.started', break_2.tStart)
        break_2.maxDuration = None
        # keep track of which components have finished
        break_2Components = break_2.components
        for thisComponent in break_2.components:
            thisComponent.tStart = None
            thisComponent.tStop = None
            thisComponent.tStartRefresh = None
            thisComponent.tStopRefresh = None
            if hasattr(thisComponent, 'status'):
                thisComponent.status = NOT_STARTED
        # reset timers
        t = 0
        _timeToFirstFrame = win.getFutureFlipTime(clock="now")
        frameN = -1
        
        # --- Run Routine "break_2" ---
        thisExp.currentRoutine = break_2
        break_2.forceEnded = routineForceEnded = not continueRoutine
        while continueRoutine:
            # if trial has changed, end Routine now
            if hasattr(thisTrial_6, 'status') and thisTrial_6.status == STOPPING:
                continueRoutine = False
            # get current time
            t = routineTimer.getTime()
            tThisFlip = win.getFutureFlipTime(clock=routineTimer)
            tThisFlipGlobal = win.getFutureFlipTime(clock=None)
            frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
            # update/draw components on each frame
            
            # *text_9* updates
            
            # if text_9 is starting this frame...
            if text_9.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                # keep track of start time/frame for later
                text_9.frameNStart = frameN  # exact frame index
                text_9.tStart = t  # local t and not account for scr refresh
                text_9.tStartRefresh = tThisFlipGlobal  # on global time
                win.timeOnFlip(text_9, 'tStartRefresh')  # time at next scr refresh
                # update status
                text_9.status = STARTED
                text_9.setAutoDraw(True)
            
            # if text_9 is active this frame...
            if text_9.status == STARTED:
                # update params
                pass
            
            # *key_resp_3* updates
            waitOnFlip = False
            
            # if key_resp_3 is starting this frame...
            if key_resp_3.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                # keep track of start time/frame for later
                key_resp_3.frameNStart = frameN  # exact frame index
                key_resp_3.tStart = t  # local t and not account for scr refresh
                key_resp_3.tStartRefresh = tThisFlipGlobal  # on global time
                win.timeOnFlip(key_resp_3, 'tStartRefresh')  # time at next scr refresh
                # update status
                key_resp_3.status = STARTED
                # keyboard checking is just starting
                waitOnFlip = True
                win.callOnFlip(key_resp_3.clock.reset)  # t=0 on next screen flip
                win.callOnFlip(key_resp_3.clearEvents, eventType='keyboard')  # clear events on next screen flip
            if key_resp_3.status == STARTED and not waitOnFlip:
                theseKeys = key_resp_3.getKeys(keyList=['space'], ignoreKeys=["escape"], waitRelease=False)
                _key_resp_3_allKeys.extend(theseKeys)
                if len(_key_resp_3_allKeys):
                    key_resp_3.keys = _key_resp_3_allKeys[-1].name  # just the last key pressed
                    key_resp_3.rt = _key_resp_3_allKeys[-1].rt
                    key_resp_3.duration = _key_resp_3_allKeys[-1].duration
                    # a response ends the routine
                    continueRoutine = False
            
            # check for quit (typically the Esc key)
            if defaultKeyboard.getKeys(keyList=["escape"]):
                thisExp.status = FINISHED
            if thisExp.status == FINISHED or endExpNow:
                endExperiment(thisExp, win=win)
                return
            # pause experiment here if requested
            if thisExp.status == PAUSED:
                pauseExperiment(
                    thisExp=thisExp, 
                    win=win, 
                    timers=[routineTimer, globalClock], 
                    currentRoutine=break_2,
                )
                # skip the frame we paused on
                continue
            
            # has a Component requested the Routine to end?
            if not continueRoutine:
                break_2.forceEnded = routineForceEnded = True
            # has the Routine been forcibly ended?
            if break_2.forceEnded or routineForceEnded:
                break
            # has every Component finished?
            continueRoutine = False
            for thisComponent in break_2.components:
                if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                    continueRoutine = True
                    break  # at least one component has not yet finished
            
            # refresh the screen
            if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                win.flip()
        
        # --- Ending Routine "break_2" ---
        for thisComponent in break_2.components:
            if hasattr(thisComponent, "setAutoDraw"):
                thisComponent.setAutoDraw(False)
        # store stop times for break_2
        break_2.tStop = globalClock.getTime(format='float')
        break_2.tStopRefresh = tThisFlipGlobal
        thisExp.addData('break_2.stopped', break_2.tStop)
        # check responses
        if key_resp_3.keys in ['', [], None]:  # No response was made
            key_resp_3.keys = None
        trials_6.addData('key_resp_3.keys',key_resp_3.keys)
        if key_resp_3.keys != None:  # we had a response
            trials_6.addData('key_resp_3.rt', key_resp_3.rt)
            trials_6.addData('key_resp_3.duration', key_resp_3.duration)
        # the Routine "break_2" was not non-slip safe, so reset the non-slip timer
        routineTimer.reset()
        # mark thisTrial_6 as finished
        if hasattr(thisTrial_6, 'status'):
            thisTrial_6.status = FINISHED
        # if awaiting a pause, pause now
        if trials_6.status == PAUSED:
            thisExp.status = PAUSED
            pauseExperiment(
                thisExp=thisExp, 
                win=win, 
                timers=[globalClock], 
            )
            # once done pausing, restore running status
            trials_6.status = STARTED
        thisExp.nextEntry()
        
    # completed 5.0 repeats of 'trials_6'
    trials_6.status = FINISHED
    
    if thisSession is not None:
        # if running in a Session with a Liaison client, send data up to now
        thisSession.sendExperimentData()
    
    # --- Prepare to start Routine "cross" ---
    # create an object to store info about Routine cross
    cross = data.Routine(
        name='cross',
        components=[text_6],
    )
    cross.status = NOT_STARTED
    continueRoutine = True
    # update component parameters for each repeat
    # store start times for cross
    cross.tStartRefresh = win.getFutureFlipTime(clock=globalClock)
    cross.tStart = globalClock.getTime(format='float')
    cross.status = STARTED
    thisExp.addData('cross.started', cross.tStart)
    cross.maxDuration = None
    # keep track of which components have finished
    crossComponents = cross.components
    for thisComponent in cross.components:
        thisComponent.tStart = None
        thisComponent.tStop = None
        thisComponent.tStartRefresh = None
        thisComponent.tStopRefresh = None
        if hasattr(thisComponent, 'status'):
            thisComponent.status = NOT_STARTED
    # reset timers
    t = 0
    _timeToFirstFrame = win.getFutureFlipTime(clock="now")
    frameN = -1
    
    # --- Run Routine "cross" ---
    thisExp.currentRoutine = cross
    cross.forceEnded = routineForceEnded = not continueRoutine
    while continueRoutine and routineTimer.getTime() < 1.0:
        # get current time
        t = routineTimer.getTime()
        tThisFlip = win.getFutureFlipTime(clock=routineTimer)
        tThisFlipGlobal = win.getFutureFlipTime(clock=None)
        frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
        # update/draw components on each frame
        
        # *text_6* updates
        
        # if text_6 is starting this frame...
        if text_6.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            text_6.frameNStart = frameN  # exact frame index
            text_6.tStart = t  # local t and not account for scr refresh
            text_6.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(text_6, 'tStartRefresh')  # time at next scr refresh
            # update status
            text_6.status = STARTED
            text_6.setAutoDraw(True)
        
        # if text_6 is active this frame...
        if text_6.status == STARTED:
            # update params
            pass
        
        # if text_6 is stopping this frame...
        if text_6.status == STARTED:
            # is it time to stop? (based on global clock, using actual start)
            if tThisFlipGlobal > text_6.tStartRefresh + 1.0-frameTolerance:
                # keep track of stop time/frame for later
                text_6.tStop = t  # not accounting for scr refresh
                text_6.tStopRefresh = tThisFlipGlobal  # on global time
                text_6.frameNStop = frameN  # exact frame index
                # update status
                text_6.status = FINISHED
                text_6.setAutoDraw(False)
        
        # check for quit (typically the Esc key)
        if defaultKeyboard.getKeys(keyList=["escape"]):
            thisExp.status = FINISHED
        if thisExp.status == FINISHED or endExpNow:
            endExperiment(thisExp, win=win)
            return
        # pause experiment here if requested
        if thisExp.status == PAUSED:
            pauseExperiment(
                thisExp=thisExp, 
                win=win, 
                timers=[routineTimer, globalClock], 
                currentRoutine=cross,
            )
            # skip the frame we paused on
            continue
        
        # has a Component requested the Routine to end?
        if not continueRoutine:
            cross.forceEnded = routineForceEnded = True
        # has the Routine been forcibly ended?
        if cross.forceEnded or routineForceEnded:
            break
        # has every Component finished?
        continueRoutine = False
        for thisComponent in cross.components:
            if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                continueRoutine = True
                break  # at least one component has not yet finished
        
        # refresh the screen
        if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
            win.flip()
    
    # --- Ending Routine "cross" ---
    for thisComponent in cross.components:
        if hasattr(thisComponent, "setAutoDraw"):
            thisComponent.setAutoDraw(False)
    # store stop times for cross
    cross.tStop = globalClock.getTime(format='float')
    cross.tStopRefresh = tThisFlipGlobal
    thisExp.addData('cross.stopped', cross.tStop)
    # using non-slip timing so subtract the expected duration of this Routine (unless ended on request)
    if cross.maxDurationReached:
        routineTimer.addTime(-cross.maxDuration)
    elif cross.forceEnded:
        routineTimer.reset()
    else:
        routineTimer.addTime(-1.000000)
    thisExp.nextEntry()
    
    # --- Prepare to start Routine "Instr_gonogo" ---
    # create an object to store info about Routine Instr_gonogo
    Instr_gonogo = data.Routine(
        name='Instr_gonogo',
        components=[text_11, image_5, sound_3, text_12, text_13, image_6, sound_4, text_14, key_resp_5, text_20, text_21],
    )
    Instr_gonogo.status = NOT_STARTED
    continueRoutine = True
    # update component parameters for each repeat
    sound_3.setSound('440.wav', secs=0.05, hamming=True)
    sound_3.setVolume(1.0, log=False)
    sound_3.seek(0)
    sound_4.setSound('440.wav', secs=0.05, hamming=True)
    sound_4.setVolume(1.0, log=False)
    sound_4.seek(0)
    # create starting attributes for key_resp_5
    key_resp_5.keys = []
    key_resp_5.rt = []
    _key_resp_5_allKeys = []
    # store start times for Instr_gonogo
    Instr_gonogo.tStartRefresh = win.getFutureFlipTime(clock=globalClock)
    Instr_gonogo.tStart = globalClock.getTime(format='float')
    Instr_gonogo.status = STARTED
    thisExp.addData('Instr_gonogo.started', Instr_gonogo.tStart)
    Instr_gonogo.maxDuration = None
    # keep track of which components have finished
    Instr_gonogoComponents = Instr_gonogo.components
    for thisComponent in Instr_gonogo.components:
        thisComponent.tStart = None
        thisComponent.tStop = None
        thisComponent.tStartRefresh = None
        thisComponent.tStopRefresh = None
        if hasattr(thisComponent, 'status'):
            thisComponent.status = NOT_STARTED
    # reset timers
    t = 0
    _timeToFirstFrame = win.getFutureFlipTime(clock="now")
    frameN = -1
    
    # --- Run Routine "Instr_gonogo" ---
    thisExp.currentRoutine = Instr_gonogo
    Instr_gonogo.forceEnded = routineForceEnded = not continueRoutine
    while continueRoutine:
        # get current time
        t = routineTimer.getTime()
        tThisFlip = win.getFutureFlipTime(clock=routineTimer)
        tThisFlipGlobal = win.getFutureFlipTime(clock=None)
        frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
        # update/draw components on each frame
        
        # *text_11* updates
        
        # if text_11 is starting this frame...
        if text_11.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            text_11.frameNStart = frameN  # exact frame index
            text_11.tStart = t  # local t and not account for scr refresh
            text_11.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(text_11, 'tStartRefresh')  # time at next scr refresh
            # update status
            text_11.status = STARTED
            text_11.setAutoDraw(True)
        
        # if text_11 is active this frame...
        if text_11.status == STARTED:
            # update params
            pass
        
        # if text_11 is stopping this frame...
        if text_11.status == STARTED:
            # is it time to stop? (based on global clock, using actual start)
            if tThisFlipGlobal > text_11.tStartRefresh + 4.5-frameTolerance:
                # keep track of stop time/frame for later
                text_11.tStop = t  # not accounting for scr refresh
                text_11.tStopRefresh = tThisFlipGlobal  # on global time
                text_11.frameNStop = frameN  # exact frame index
                # update status
                text_11.status = FINISHED
                text_11.setAutoDraw(False)
        
        # *image_5* updates
        
        # if image_5 is starting this frame...
        if image_5.status == NOT_STARTED and tThisFlip >= 5-frameTolerance:
            # keep track of start time/frame for later
            image_5.frameNStart = frameN  # exact frame index
            image_5.tStart = t  # local t and not account for scr refresh
            image_5.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(image_5, 'tStartRefresh')  # time at next scr refresh
            # update status
            image_5.status = STARTED
            image_5.setAutoDraw(True)
        
        # if image_5 is active this frame...
        if image_5.status == STARTED:
            # update params
            pass
        
        # if image_5 is stopping this frame...
        if image_5.status == STARTED:
            # is it time to stop? (based on global clock, using actual start)
            if tThisFlipGlobal > image_5.tStartRefresh + 1-frameTolerance:
                # keep track of stop time/frame for later
                image_5.tStop = t  # not accounting for scr refresh
                image_5.tStopRefresh = tThisFlipGlobal  # on global time
                image_5.frameNStop = frameN  # exact frame index
                # update status
                image_5.status = FINISHED
                image_5.setAutoDraw(False)
        
        # *sound_3* updates
        
        # if sound_3 is starting this frame...
        if sound_3.status == NOT_STARTED and tThisFlip >= 5-frameTolerance:
            # keep track of start time/frame for later
            sound_3.frameNStart = frameN  # exact frame index
            sound_3.tStart = t  # local t and not account for scr refresh
            sound_3.tStartRefresh = tThisFlipGlobal  # on global time
            # update status
            sound_3.status = STARTED
            sound_3.play(when=win)  # sync with win flip
        
        # if sound_3 is stopping this frame...
        if sound_3.status == STARTED:
            # is it time to stop? (based on global clock, using actual start)
            if tThisFlipGlobal > sound_3.tStartRefresh + 0.05-frameTolerance or sound_3.isFinished:
                # keep track of stop time/frame for later
                sound_3.tStop = t  # not accounting for scr refresh
                sound_3.tStopRefresh = tThisFlipGlobal  # on global time
                sound_3.frameNStop = frameN  # exact frame index
                # update status
                sound_3.status = FINISHED
                sound_3.stop()
        
        # *text_12* updates
        
        # if text_12 is starting this frame...
        if text_12.status == NOT_STARTED and tThisFlip >= 6-frameTolerance:
            # keep track of start time/frame for later
            text_12.frameNStart = frameN  # exact frame index
            text_12.tStart = t  # local t and not account for scr refresh
            text_12.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(text_12, 'tStartRefresh')  # time at next scr refresh
            # update status
            text_12.status = STARTED
            text_12.setAutoDraw(True)
        
        # if text_12 is active this frame...
        if text_12.status == STARTED:
            # update params
            pass
        
        # if text_12 is stopping this frame...
        if text_12.status == STARTED:
            # is it time to stop? (based on global clock, using actual start)
            if tThisFlipGlobal > text_12.tStartRefresh + 3-frameTolerance:
                # keep track of stop time/frame for later
                text_12.tStop = t  # not accounting for scr refresh
                text_12.tStopRefresh = tThisFlipGlobal  # on global time
                text_12.frameNStop = frameN  # exact frame index
                # update status
                text_12.status = FINISHED
                text_12.setAutoDraw(False)
        
        # *text_13* updates
        
        # if text_13 is starting this frame...
        if text_13.status == NOT_STARTED and tThisFlip >= 9-frameTolerance:
            # keep track of start time/frame for later
            text_13.frameNStart = frameN  # exact frame index
            text_13.tStart = t  # local t and not account for scr refresh
            text_13.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(text_13, 'tStartRefresh')  # time at next scr refresh
            # update status
            text_13.status = STARTED
            text_13.setAutoDraw(True)
        
        # if text_13 is active this frame...
        if text_13.status == STARTED:
            # update params
            pass
        
        # if text_13 is stopping this frame...
        if text_13.status == STARTED:
            # is it time to stop? (based on global clock, using actual start)
            if tThisFlipGlobal > text_13.tStartRefresh + 3.6-frameTolerance:
                # keep track of stop time/frame for later
                text_13.tStop = t  # not accounting for scr refresh
                text_13.tStopRefresh = tThisFlipGlobal  # on global time
                text_13.frameNStop = frameN  # exact frame index
                # update status
                text_13.status = FINISHED
                text_13.setAutoDraw(False)
        
        # *image_6* updates
        
        # if image_6 is starting this frame...
        if image_6.status == NOT_STARTED and tThisFlip >= 13-frameTolerance:
            # keep track of start time/frame for later
            image_6.frameNStart = frameN  # exact frame index
            image_6.tStart = t  # local t and not account for scr refresh
            image_6.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(image_6, 'tStartRefresh')  # time at next scr refresh
            # update status
            image_6.status = STARTED
            image_6.setAutoDraw(True)
        
        # if image_6 is active this frame...
        if image_6.status == STARTED:
            # update params
            pass
        
        # if image_6 is stopping this frame...
        if image_6.status == STARTED:
            # is it time to stop? (based on global clock, using actual start)
            if tThisFlipGlobal > image_6.tStartRefresh + 1.0-frameTolerance:
                # keep track of stop time/frame for later
                image_6.tStop = t  # not accounting for scr refresh
                image_6.tStopRefresh = tThisFlipGlobal  # on global time
                image_6.frameNStop = frameN  # exact frame index
                # update status
                image_6.status = FINISHED
                image_6.setAutoDraw(False)
        
        # *sound_4* updates
        
        # if sound_4 is starting this frame...
        if sound_4.status == NOT_STARTED and tThisFlip >= 13-frameTolerance:
            # keep track of start time/frame for later
            sound_4.frameNStart = frameN  # exact frame index
            sound_4.tStart = t  # local t and not account for scr refresh
            sound_4.tStartRefresh = tThisFlipGlobal  # on global time
            # update status
            sound_4.status = STARTED
            sound_4.play(when=win)  # sync with win flip
        
        # if sound_4 is stopping this frame...
        if sound_4.status == STARTED:
            # is it time to stop? (based on global clock, using actual start)
            if tThisFlipGlobal > sound_4.tStartRefresh + 0.05-frameTolerance or sound_4.isFinished:
                # keep track of stop time/frame for later
                sound_4.tStop = t  # not accounting for scr refresh
                sound_4.tStopRefresh = tThisFlipGlobal  # on global time
                sound_4.frameNStop = frameN  # exact frame index
                # update status
                sound_4.status = FINISHED
                sound_4.stop()
        
        # *text_14* updates
        
        # if text_14 is starting this frame...
        if text_14.status == NOT_STARTED and tThisFlip >= 14-frameTolerance:
            # keep track of start time/frame for later
            text_14.frameNStart = frameN  # exact frame index
            text_14.tStart = t  # local t and not account for scr refresh
            text_14.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(text_14, 'tStartRefresh')  # time at next scr refresh
            # update status
            text_14.status = STARTED
            text_14.setAutoDraw(True)
        
        # if text_14 is active this frame...
        if text_14.status == STARTED:
            # update params
            pass
        
        # *key_resp_5* updates
        waitOnFlip = False
        
        # if key_resp_5 is starting this frame...
        if key_resp_5.status == NOT_STARTED and tThisFlip >= 14-frameTolerance:
            # keep track of start time/frame for later
            key_resp_5.frameNStart = frameN  # exact frame index
            key_resp_5.tStart = t  # local t and not account for scr refresh
            key_resp_5.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(key_resp_5, 'tStartRefresh')  # time at next scr refresh
            # update status
            key_resp_5.status = STARTED
            # keyboard checking is just starting
            waitOnFlip = True
            win.callOnFlip(key_resp_5.clock.reset)  # t=0 on next screen flip
            win.callOnFlip(key_resp_5.clearEvents, eventType='keyboard')  # clear events on next screen flip
        if key_resp_5.status == STARTED and not waitOnFlip:
            theseKeys = key_resp_5.getKeys(keyList=['space'], ignoreKeys=["escape"], waitRelease=False)
            _key_resp_5_allKeys.extend(theseKeys)
            if len(_key_resp_5_allKeys):
                key_resp_5.keys = _key_resp_5_allKeys[-1].name  # just the last key pressed
                key_resp_5.rt = _key_resp_5_allKeys[-1].rt
                key_resp_5.duration = _key_resp_5_allKeys[-1].duration
                # a response ends the routine
                continueRoutine = False
        
        # *text_20* updates
        
        # if text_20 is starting this frame...
        if text_20.status == NOT_STARTED and tThisFlip >= 4.5-frameTolerance:
            # keep track of start time/frame for later
            text_20.frameNStart = frameN  # exact frame index
            text_20.tStart = t  # local t and not account for scr refresh
            text_20.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(text_20, 'tStartRefresh')  # time at next scr refresh
            # update status
            text_20.status = STARTED
            text_20.setAutoDraw(True)
        
        # if text_20 is active this frame...
        if text_20.status == STARTED:
            # update params
            pass
        
        # if text_20 is stopping this frame...
        if text_20.status == STARTED:
            # is it time to stop? (based on global clock, using actual start)
            if tThisFlipGlobal > text_20.tStartRefresh + 1.5-frameTolerance:
                # keep track of stop time/frame for later
                text_20.tStop = t  # not accounting for scr refresh
                text_20.tStopRefresh = tThisFlipGlobal  # on global time
                text_20.frameNStop = frameN  # exact frame index
                # update status
                text_20.status = FINISHED
                text_20.setAutoDraw(False)
        
        # *text_21* updates
        
        # if text_21 is starting this frame...
        if text_21.status == NOT_STARTED and tThisFlip >= 12.6-frameTolerance:
            # keep track of start time/frame for later
            text_21.frameNStart = frameN  # exact frame index
            text_21.tStart = t  # local t and not account for scr refresh
            text_21.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(text_21, 'tStartRefresh')  # time at next scr refresh
            # update status
            text_21.status = STARTED
            text_21.setAutoDraw(True)
        
        # if text_21 is active this frame...
        if text_21.status == STARTED:
            # update params
            pass
        
        # if text_21 is stopping this frame...
        if text_21.status == STARTED:
            # is it time to stop? (based on global clock, using actual start)
            if tThisFlipGlobal > text_21.tStartRefresh + 1.4-frameTolerance:
                # keep track of stop time/frame for later
                text_21.tStop = t  # not accounting for scr refresh
                text_21.tStopRefresh = tThisFlipGlobal  # on global time
                text_21.frameNStop = frameN  # exact frame index
                # update status
                text_21.status = FINISHED
                text_21.setAutoDraw(False)
        
        # check for quit (typically the Esc key)
        if defaultKeyboard.getKeys(keyList=["escape"]):
            thisExp.status = FINISHED
        if thisExp.status == FINISHED or endExpNow:
            endExperiment(thisExp, win=win)
            return
        # pause experiment here if requested
        if thisExp.status == PAUSED:
            pauseExperiment(
                thisExp=thisExp, 
                win=win, 
                timers=[routineTimer, globalClock], 
                currentRoutine=Instr_gonogo,
            )
            # skip the frame we paused on
            continue
        
        # has a Component requested the Routine to end?
        if not continueRoutine:
            Instr_gonogo.forceEnded = routineForceEnded = True
        # has the Routine been forcibly ended?
        if Instr_gonogo.forceEnded or routineForceEnded:
            break
        # has every Component finished?
        continueRoutine = False
        for thisComponent in Instr_gonogo.components:
            if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                continueRoutine = True
                break  # at least one component has not yet finished
        
        # refresh the screen
        if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
            win.flip()
    
    # --- Ending Routine "Instr_gonogo" ---
    for thisComponent in Instr_gonogo.components:
        if hasattr(thisComponent, "setAutoDraw"):
            thisComponent.setAutoDraw(False)
    # store stop times for Instr_gonogo
    Instr_gonogo.tStop = globalClock.getTime(format='float')
    Instr_gonogo.tStopRefresh = tThisFlipGlobal
    thisExp.addData('Instr_gonogo.stopped', Instr_gonogo.tStop)
    sound_3.pause()  # ensure sound has stopped at end of Routine
    sound_4.pause()  # ensure sound has stopped at end of Routine
    # check responses
    if key_resp_5.keys in ['', [], None]:  # No response was made
        key_resp_5.keys = None
    thisExp.addData('key_resp_5.keys',key_resp_5.keys)
    if key_resp_5.keys != None:  # we had a response
        thisExp.addData('key_resp_5.rt', key_resp_5.rt)
        thisExp.addData('key_resp_5.duration', key_resp_5.duration)
    thisExp.nextEntry()
    # the Routine "Instr_gonogo" was not non-slip safe, so reset the non-slip timer
    routineTimer.reset()
    
    # --- Prepare to start Routine "last_instructions" ---
    # create an object to store info about Routine last_instructions
    last_instructions = data.Routine(
        name='last_instructions',
        components=[image_10, key_resp_9, text_24],
    )
    last_instructions.status = NOT_STARTED
    continueRoutine = True
    # update component parameters for each repeat
    # create starting attributes for key_resp_9
    key_resp_9.keys = []
    key_resp_9.rt = []
    _key_resp_9_allKeys = []
    # store start times for last_instructions
    last_instructions.tStartRefresh = win.getFutureFlipTime(clock=globalClock)
    last_instructions.tStart = globalClock.getTime(format='float')
    last_instructions.status = STARTED
    thisExp.addData('last_instructions.started', last_instructions.tStart)
    last_instructions.maxDuration = None
    # keep track of which components have finished
    last_instructionsComponents = last_instructions.components
    for thisComponent in last_instructions.components:
        thisComponent.tStart = None
        thisComponent.tStop = None
        thisComponent.tStartRefresh = None
        thisComponent.tStopRefresh = None
        if hasattr(thisComponent, 'status'):
            thisComponent.status = NOT_STARTED
    # reset timers
    t = 0
    _timeToFirstFrame = win.getFutureFlipTime(clock="now")
    frameN = -1
    
    # --- Run Routine "last_instructions" ---
    thisExp.currentRoutine = last_instructions
    last_instructions.forceEnded = routineForceEnded = not continueRoutine
    while continueRoutine:
        # get current time
        t = routineTimer.getTime()
        tThisFlip = win.getFutureFlipTime(clock=routineTimer)
        tThisFlipGlobal = win.getFutureFlipTime(clock=None)
        frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
        # update/draw components on each frame
        
        # *image_10* updates
        
        # if image_10 is starting this frame...
        if image_10.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            image_10.frameNStart = frameN  # exact frame index
            image_10.tStart = t  # local t and not account for scr refresh
            image_10.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(image_10, 'tStartRefresh')  # time at next scr refresh
            # update status
            image_10.status = STARTED
            image_10.setAutoDraw(True)
        
        # if image_10 is active this frame...
        if image_10.status == STARTED:
            # update params
            pass
        
        # *key_resp_9* updates
        waitOnFlip = False
        
        # if key_resp_9 is starting this frame...
        if key_resp_9.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            key_resp_9.frameNStart = frameN  # exact frame index
            key_resp_9.tStart = t  # local t and not account for scr refresh
            key_resp_9.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(key_resp_9, 'tStartRefresh')  # time at next scr refresh
            # update status
            key_resp_9.status = STARTED
            # keyboard checking is just starting
            waitOnFlip = True
            win.callOnFlip(key_resp_9.clock.reset)  # t=0 on next screen flip
            win.callOnFlip(key_resp_9.clearEvents, eventType='keyboard')  # clear events on next screen flip
        if key_resp_9.status == STARTED and not waitOnFlip:
            theseKeys = key_resp_9.getKeys(keyList=['space'], ignoreKeys=["escape"], waitRelease=False)
            _key_resp_9_allKeys.extend(theseKeys)
            if len(_key_resp_9_allKeys):
                key_resp_9.keys = _key_resp_9_allKeys[-1].name  # just the last key pressed
                key_resp_9.rt = _key_resp_9_allKeys[-1].rt
                key_resp_9.duration = _key_resp_9_allKeys[-1].duration
                # a response ends the routine
                continueRoutine = False
        
        # *text_24* updates
        
        # if text_24 is starting this frame...
        if text_24.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            text_24.frameNStart = frameN  # exact frame index
            text_24.tStart = t  # local t and not account for scr refresh
            text_24.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(text_24, 'tStartRefresh')  # time at next scr refresh
            # update status
            text_24.status = STARTED
            text_24.setAutoDraw(True)
        
        # if text_24 is active this frame...
        if text_24.status == STARTED:
            # update params
            pass
        
        # check for quit (typically the Esc key)
        if defaultKeyboard.getKeys(keyList=["escape"]):
            thisExp.status = FINISHED
        if thisExp.status == FINISHED or endExpNow:
            endExperiment(thisExp, win=win)
            return
        # pause experiment here if requested
        if thisExp.status == PAUSED:
            pauseExperiment(
                thisExp=thisExp, 
                win=win, 
                timers=[routineTimer, globalClock], 
                currentRoutine=last_instructions,
            )
            # skip the frame we paused on
            continue
        
        # has a Component requested the Routine to end?
        if not continueRoutine:
            last_instructions.forceEnded = routineForceEnded = True
        # has the Routine been forcibly ended?
        if last_instructions.forceEnded or routineForceEnded:
            break
        # has every Component finished?
        continueRoutine = False
        for thisComponent in last_instructions.components:
            if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                continueRoutine = True
                break  # at least one component has not yet finished
        
        # refresh the screen
        if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
            win.flip()
    
    # --- Ending Routine "last_instructions" ---
    for thisComponent in last_instructions.components:
        if hasattr(thisComponent, "setAutoDraw"):
            thisComponent.setAutoDraw(False)
    # store stop times for last_instructions
    last_instructions.tStop = globalClock.getTime(format='float')
    last_instructions.tStopRefresh = tThisFlipGlobal
    thisExp.addData('last_instructions.stopped', last_instructions.tStop)
    # check responses
    if key_resp_9.keys in ['', [], None]:  # No response was made
        key_resp_9.keys = None
    thisExp.addData('key_resp_9.keys',key_resp_9.keys)
    if key_resp_9.keys != None:  # we had a response
        thisExp.addData('key_resp_9.rt', key_resp_9.rt)
        thisExp.addData('key_resp_9.duration', key_resp_9.duration)
    thisExp.nextEntry()
    # the Routine "last_instructions" was not non-slip safe, so reset the non-slip timer
    routineTimer.reset()
    
    # set up handler to look after randomisation of conditions etc
    trials_7 = data.TrialHandler2(
        name='trials_7',
        nReps=1.0, 
        method='sequential', 
        extraInfo=expInfo, 
        originPath=-1, 
        trialList=data.importConditions(
        'SoundEx.xlsx', 
        selection='0:3'
    )
    , 
        seed=None, 
        isTrials=True, 
    )
    thisExp.addLoop(trials_7)  # add the loop to the experiment
    thisTrial_7 = trials_7.trialList[0]  # so we can initialise stimuli with some values
    # abbreviate parameter names if possible (e.g. rgb = thisTrial_7.rgb)
    if thisTrial_7 != None:
        for paramName in thisTrial_7:
            globals()[paramName] = thisTrial_7[paramName]
    if thisSession is not None:
        # if running in a Session with a Liaison client, send data up to now
        thisSession.sendExperimentData()
    
    for thisTrial_7 in trials_7:
        trials_7.status = STARTED
        if hasattr(thisTrial_7, 'status'):
            thisTrial_7.status = STARTED
        currentLoop = trials_7
        thisExp.timestampOnFlip(win, 'thisRow.t', format=globalClock.format)
        if thisSession is not None:
            # if running in a Session with a Liaison client, send data up to now
            thisSession.sendExperimentData()
        # abbreviate parameter names if possible (e.g. rgb = thisTrial_7.rgb)
        if thisTrial_7 != None:
            for paramName in thisTrial_7:
                globals()[paramName] = thisTrial_7[paramName]
        
        # --- Prepare to start Routine "dontpress1" ---
        # create an object to store info about Routine dontpress1
        dontpress1 = data.Routine(
            name='dontpress1',
            components=[text_15, image_7, text_16, sound_6],
        )
        dontpress1.status = NOT_STARTED
        continueRoutine = True
        # update component parameters for each repeat
        image_7.setImage(image)
        sound_6.setSound(Sound, secs=0.05, hamming=True)
        sound_6.setVolume(1.0, log=False)
        sound_6.seek(0)
        # store start times for dontpress1
        dontpress1.tStartRefresh = win.getFutureFlipTime(clock=globalClock)
        dontpress1.tStart = globalClock.getTime(format='float')
        dontpress1.status = STARTED
        thisExp.addData('dontpress1.started', dontpress1.tStart)
        dontpress1.maxDuration = None
        # keep track of which components have finished
        dontpress1Components = dontpress1.components
        for thisComponent in dontpress1.components:
            thisComponent.tStart = None
            thisComponent.tStop = None
            thisComponent.tStartRefresh = None
            thisComponent.tStopRefresh = None
            if hasattr(thisComponent, 'status'):
                thisComponent.status = NOT_STARTED
        # reset timers
        t = 0
        _timeToFirstFrame = win.getFutureFlipTime(clock="now")
        frameN = -1
        
        # --- Run Routine "dontpress1" ---
        thisExp.currentRoutine = dontpress1
        dontpress1.forceEnded = routineForceEnded = not continueRoutine
        while continueRoutine and routineTimer.getTime() < 2.2:
            # if trial has changed, end Routine now
            if hasattr(thisTrial_7, 'status') and thisTrial_7.status == STOPPING:
                continueRoutine = False
            # get current time
            t = routineTimer.getTime()
            tThisFlip = win.getFutureFlipTime(clock=routineTimer)
            tThisFlipGlobal = win.getFutureFlipTime(clock=None)
            frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
            # update/draw components on each frame
            
            # *text_15* updates
            
            # if text_15 is starting this frame...
            if text_15.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                # keep track of start time/frame for later
                text_15.frameNStart = frameN  # exact frame index
                text_15.tStart = t  # local t and not account for scr refresh
                text_15.tStartRefresh = tThisFlipGlobal  # on global time
                win.timeOnFlip(text_15, 'tStartRefresh')  # time at next scr refresh
                # update status
                text_15.status = STARTED
                text_15.setAutoDraw(True)
            
            # if text_15 is active this frame...
            if text_15.status == STARTED:
                # update params
                pass
            
            # if text_15 is stopping this frame...
            if text_15.status == STARTED:
                # is it time to stop? (based on global clock, using actual start)
                if tThisFlipGlobal > text_15.tStartRefresh + 1.2-frameTolerance:
                    # keep track of stop time/frame for later
                    text_15.tStop = t  # not accounting for scr refresh
                    text_15.tStopRefresh = tThisFlipGlobal  # on global time
                    text_15.frameNStop = frameN  # exact frame index
                    # update status
                    text_15.status = FINISHED
                    text_15.setAutoDraw(False)
            
            # *image_7* updates
            
            # if image_7 is starting this frame...
            if image_7.status == NOT_STARTED and tThisFlip >= 0.4-frameTolerance:
                # keep track of start time/frame for later
                image_7.frameNStart = frameN  # exact frame index
                image_7.tStart = t  # local t and not account for scr refresh
                image_7.tStartRefresh = tThisFlipGlobal  # on global time
                win.timeOnFlip(image_7, 'tStartRefresh')  # time at next scr refresh
                # update status
                image_7.status = STARTED
                image_7.setAutoDraw(True)
            
            # if image_7 is active this frame...
            if image_7.status == STARTED:
                # update params
                pass
            
            # if image_7 is stopping this frame...
            if image_7.status == STARTED:
                # is it time to stop? (based on global clock, using actual start)
                if tThisFlipGlobal > image_7.tStartRefresh + 0.4-frameTolerance:
                    # keep track of stop time/frame for later
                    image_7.tStop = t  # not accounting for scr refresh
                    image_7.tStopRefresh = tThisFlipGlobal  # on global time
                    image_7.frameNStop = frameN  # exact frame index
                    # update status
                    image_7.status = FINISHED
                    image_7.setAutoDraw(False)
            
            # *text_16* updates
            
            # if text_16 is starting this frame...
            if text_16.status == NOT_STARTED and tThisFlip >= 1.2-frameTolerance:
                # keep track of start time/frame for later
                text_16.frameNStart = frameN  # exact frame index
                text_16.tStart = t  # local t and not account for scr refresh
                text_16.tStartRefresh = tThisFlipGlobal  # on global time
                win.timeOnFlip(text_16, 'tStartRefresh')  # time at next scr refresh
                # update status
                text_16.status = STARTED
                text_16.setAutoDraw(True)
            
            # if text_16 is active this frame...
            if text_16.status == STARTED:
                # update params
                pass
            
            # if text_16 is stopping this frame...
            if text_16.status == STARTED:
                # is it time to stop? (based on global clock, using actual start)
                if tThisFlipGlobal > text_16.tStartRefresh + 1.0-frameTolerance:
                    # keep track of stop time/frame for later
                    text_16.tStop = t  # not accounting for scr refresh
                    text_16.tStopRefresh = tThisFlipGlobal  # on global time
                    text_16.frameNStop = frameN  # exact frame index
                    # update status
                    text_16.status = FINISHED
                    text_16.setAutoDraw(False)
            
            # *sound_6* updates
            
            # if sound_6 is starting this frame...
            if sound_6.status == NOT_STARTED and tThisFlip >= 0.4-frameTolerance:
                # keep track of start time/frame for later
                sound_6.frameNStart = frameN  # exact frame index
                sound_6.tStart = t  # local t and not account for scr refresh
                sound_6.tStartRefresh = tThisFlipGlobal  # on global time
                # update status
                sound_6.status = STARTED
                sound_6.play(when=win)  # sync with win flip
            
            # if sound_6 is stopping this frame...
            if sound_6.status == STARTED:
                # is it time to stop? (based on global clock, using actual start)
                if tThisFlipGlobal > sound_6.tStartRefresh + 0.05-frameTolerance or sound_6.isFinished:
                    # keep track of stop time/frame for later
                    sound_6.tStop = t  # not accounting for scr refresh
                    sound_6.tStopRefresh = tThisFlipGlobal  # on global time
                    sound_6.frameNStop = frameN  # exact frame index
                    # update status
                    sound_6.status = FINISHED
                    sound_6.stop()
            
            # check for quit (typically the Esc key)
            if defaultKeyboard.getKeys(keyList=["escape"]):
                thisExp.status = FINISHED
            if thisExp.status == FINISHED or endExpNow:
                endExperiment(thisExp, win=win)
                return
            # pause experiment here if requested
            if thisExp.status == PAUSED:
                pauseExperiment(
                    thisExp=thisExp, 
                    win=win, 
                    timers=[routineTimer, globalClock], 
                    currentRoutine=dontpress1,
                )
                # skip the frame we paused on
                continue
            
            # has a Component requested the Routine to end?
            if not continueRoutine:
                dontpress1.forceEnded = routineForceEnded = True
            # has the Routine been forcibly ended?
            if dontpress1.forceEnded or routineForceEnded:
                break
            # has every Component finished?
            continueRoutine = False
            for thisComponent in dontpress1.components:
                if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                    continueRoutine = True
                    break  # at least one component has not yet finished
            
            # refresh the screen
            if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                win.flip()
        
        # --- Ending Routine "dontpress1" ---
        for thisComponent in dontpress1.components:
            if hasattr(thisComponent, "setAutoDraw"):
                thisComponent.setAutoDraw(False)
        # store stop times for dontpress1
        dontpress1.tStop = globalClock.getTime(format='float')
        dontpress1.tStopRefresh = tThisFlipGlobal
        thisExp.addData('dontpress1.stopped', dontpress1.tStop)
        sound_6.pause()  # ensure sound has stopped at end of Routine
        # using non-slip timing so subtract the expected duration of this Routine (unless ended on request)
        if dontpress1.maxDurationReached:
            routineTimer.addTime(-dontpress1.maxDuration)
        elif dontpress1.forceEnded:
            routineTimer.reset()
        else:
            routineTimer.addTime(-2.200000)
        # mark thisTrial_7 as finished
        if hasattr(thisTrial_7, 'status'):
            thisTrial_7.status = FINISHED
        # if awaiting a pause, pause now
        if trials_7.status == PAUSED:
            thisExp.status = PAUSED
            pauseExperiment(
                thisExp=thisExp, 
                win=win, 
                timers=[globalClock], 
            )
            # once done pausing, restore running status
            trials_7.status = STARTED
        thisExp.nextEntry()
        
    # completed 1.0 repeats of 'trials_7'
    trials_7.status = FINISHED
    
    if thisSession is not None:
        # if running in a Session with a Liaison client, send data up to now
        thisSession.sendExperimentData()
    
    # set up handler to look after randomisation of conditions etc
    trials_8 = data.TrialHandler2(
        name='trials_8',
        nReps=2.0, 
        method='sequential', 
        extraInfo=expInfo, 
        originPath=-1, 
        trialList=data.importConditions(
        'SoundEx.xlsx', 
        selection='3'
    )
    , 
        seed=None, 
        isTrials=True, 
    )
    thisExp.addLoop(trials_8)  # add the loop to the experiment
    thisTrial_8 = trials_8.trialList[0]  # so we can initialise stimuli with some values
    # abbreviate parameter names if possible (e.g. rgb = thisTrial_8.rgb)
    if thisTrial_8 != None:
        for paramName in thisTrial_8:
            globals()[paramName] = thisTrial_8[paramName]
    if thisSession is not None:
        # if running in a Session with a Liaison client, send data up to now
        thisSession.sendExperimentData()
    
    for thisTrial_8 in trials_8:
        trials_8.status = STARTED
        if hasattr(thisTrial_8, 'status'):
            thisTrial_8.status = STARTED
        currentLoop = trials_8
        thisExp.timestampOnFlip(win, 'thisRow.t', format=globalClock.format)
        if thisSession is not None:
            # if running in a Session with a Liaison client, send data up to now
            thisSession.sendExperimentData()
        # abbreviate parameter names if possible (e.g. rgb = thisTrial_8.rgb)
        if thisTrial_8 != None:
            for paramName in thisTrial_8:
                globals()[paramName] = thisTrial_8[paramName]
        
        # --- Prepare to start Routine "pressEx" ---
        # create an object to store info about Routine pressEx
        pressEx = data.Routine(
            name='pressEx',
            components=[text_17, image_8, text_18, sound_5],
        )
        pressEx.status = NOT_STARTED
        continueRoutine = True
        # update component parameters for each repeat
        image_8.setImage(image)
        sound_5.setSound(Sound, secs=0.05, hamming=True)
        sound_5.setVolume(1.0, log=False)
        sound_5.seek(0)
        # store start times for pressEx
        pressEx.tStartRefresh = win.getFutureFlipTime(clock=globalClock)
        pressEx.tStart = globalClock.getTime(format='float')
        pressEx.status = STARTED
        thisExp.addData('pressEx.started', pressEx.tStart)
        pressEx.maxDuration = None
        # keep track of which components have finished
        pressExComponents = pressEx.components
        for thisComponent in pressEx.components:
            thisComponent.tStart = None
            thisComponent.tStop = None
            thisComponent.tStartRefresh = None
            thisComponent.tStopRefresh = None
            if hasattr(thisComponent, 'status'):
                thisComponent.status = NOT_STARTED
        # reset timers
        t = 0
        _timeToFirstFrame = win.getFutureFlipTime(clock="now")
        frameN = -1
        
        # --- Run Routine "pressEx" ---
        thisExp.currentRoutine = pressEx
        pressEx.forceEnded = routineForceEnded = not continueRoutine
        while continueRoutine and routineTimer.getTime() < 2.4:
            # if trial has changed, end Routine now
            if hasattr(thisTrial_8, 'status') and thisTrial_8.status == STOPPING:
                continueRoutine = False
            # get current time
            t = routineTimer.getTime()
            tThisFlip = win.getFutureFlipTime(clock=routineTimer)
            tThisFlipGlobal = win.getFutureFlipTime(clock=None)
            frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
            # update/draw components on each frame
            
            # *text_17* updates
            
            # if text_17 is starting this frame...
            if text_17.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                # keep track of start time/frame for later
                text_17.frameNStart = frameN  # exact frame index
                text_17.tStart = t  # local t and not account for scr refresh
                text_17.tStartRefresh = tThisFlipGlobal  # on global time
                win.timeOnFlip(text_17, 'tStartRefresh')  # time at next scr refresh
                # update status
                text_17.status = STARTED
                text_17.setAutoDraw(True)
            
            # if text_17 is active this frame...
            if text_17.status == STARTED:
                # update params
                pass
            
            # if text_17 is stopping this frame...
            if text_17.status == STARTED:
                # is it time to stop? (based on global clock, using actual start)
                if tThisFlipGlobal > text_17.tStartRefresh + 1.2-frameTolerance:
                    # keep track of stop time/frame for later
                    text_17.tStop = t  # not accounting for scr refresh
                    text_17.tStopRefresh = tThisFlipGlobal  # on global time
                    text_17.frameNStop = frameN  # exact frame index
                    # update status
                    text_17.status = FINISHED
                    text_17.setAutoDraw(False)
            
            # *image_8* updates
            
            # if image_8 is starting this frame...
            if image_8.status == NOT_STARTED and tThisFlip >= 0.4-frameTolerance:
                # keep track of start time/frame for later
                image_8.frameNStart = frameN  # exact frame index
                image_8.tStart = t  # local t and not account for scr refresh
                image_8.tStartRefresh = tThisFlipGlobal  # on global time
                win.timeOnFlip(image_8, 'tStartRefresh')  # time at next scr refresh
                # update status
                image_8.status = STARTED
                image_8.setAutoDraw(True)
            
            # if image_8 is active this frame...
            if image_8.status == STARTED:
                # update params
                pass
            
            # if image_8 is stopping this frame...
            if image_8.status == STARTED:
                # is it time to stop? (based on global clock, using actual start)
                if tThisFlipGlobal > image_8.tStartRefresh + 0.4-frameTolerance:
                    # keep track of stop time/frame for later
                    image_8.tStop = t  # not accounting for scr refresh
                    image_8.tStopRefresh = tThisFlipGlobal  # on global time
                    image_8.frameNStop = frameN  # exact frame index
                    # update status
                    image_8.status = FINISHED
                    image_8.setAutoDraw(False)
            
            # *text_18* updates
            
            # if text_18 is starting this frame...
            if text_18.status == NOT_STARTED and tThisFlip >= 1.2-frameTolerance:
                # keep track of start time/frame for later
                text_18.frameNStart = frameN  # exact frame index
                text_18.tStart = t  # local t and not account for scr refresh
                text_18.tStartRefresh = tThisFlipGlobal  # on global time
                win.timeOnFlip(text_18, 'tStartRefresh')  # time at next scr refresh
                # update status
                text_18.status = STARTED
                text_18.setAutoDraw(True)
            
            # if text_18 is active this frame...
            if text_18.status == STARTED:
                # update params
                pass
            
            # if text_18 is stopping this frame...
            if text_18.status == STARTED:
                # is it time to stop? (based on global clock, using actual start)
                if tThisFlipGlobal > text_18.tStartRefresh + 1.2-frameTolerance:
                    # keep track of stop time/frame for later
                    text_18.tStop = t  # not accounting for scr refresh
                    text_18.tStopRefresh = tThisFlipGlobal  # on global time
                    text_18.frameNStop = frameN  # exact frame index
                    # update status
                    text_18.status = FINISHED
                    text_18.setAutoDraw(False)
            
            # *sound_5* updates
            
            # if sound_5 is starting this frame...
            if sound_5.status == NOT_STARTED and tThisFlip >= 0.4-frameTolerance:
                # keep track of start time/frame for later
                sound_5.frameNStart = frameN  # exact frame index
                sound_5.tStart = t  # local t and not account for scr refresh
                sound_5.tStartRefresh = tThisFlipGlobal  # on global time
                # update status
                sound_5.status = STARTED
                sound_5.play(when=win)  # sync with win flip
            
            # if sound_5 is stopping this frame...
            if sound_5.status == STARTED:
                # is it time to stop? (based on global clock, using actual start)
                if tThisFlipGlobal > sound_5.tStartRefresh + 0.05-frameTolerance or sound_5.isFinished:
                    # keep track of stop time/frame for later
                    sound_5.tStop = t  # not accounting for scr refresh
                    sound_5.tStopRefresh = tThisFlipGlobal  # on global time
                    sound_5.frameNStop = frameN  # exact frame index
                    # update status
                    sound_5.status = FINISHED
                    sound_5.stop()
            
            # check for quit (typically the Esc key)
            if defaultKeyboard.getKeys(keyList=["escape"]):
                thisExp.status = FINISHED
            if thisExp.status == FINISHED or endExpNow:
                endExperiment(thisExp, win=win)
                return
            # pause experiment here if requested
            if thisExp.status == PAUSED:
                pauseExperiment(
                    thisExp=thisExp, 
                    win=win, 
                    timers=[routineTimer, globalClock], 
                    currentRoutine=pressEx,
                )
                # skip the frame we paused on
                continue
            
            # has a Component requested the Routine to end?
            if not continueRoutine:
                pressEx.forceEnded = routineForceEnded = True
            # has the Routine been forcibly ended?
            if pressEx.forceEnded or routineForceEnded:
                break
            # has every Component finished?
            continueRoutine = False
            for thisComponent in pressEx.components:
                if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                    continueRoutine = True
                    break  # at least one component has not yet finished
            
            # refresh the screen
            if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                win.flip()
        
        # --- Ending Routine "pressEx" ---
        for thisComponent in pressEx.components:
            if hasattr(thisComponent, "setAutoDraw"):
                thisComponent.setAutoDraw(False)
        # store stop times for pressEx
        pressEx.tStop = globalClock.getTime(format='float')
        pressEx.tStopRefresh = tThisFlipGlobal
        thisExp.addData('pressEx.stopped', pressEx.tStop)
        sound_5.pause()  # ensure sound has stopped at end of Routine
        # using non-slip timing so subtract the expected duration of this Routine (unless ended on request)
        if pressEx.maxDurationReached:
            routineTimer.addTime(-pressEx.maxDuration)
        elif pressEx.forceEnded:
            routineTimer.reset()
        else:
            routineTimer.addTime(-2.400000)
        # mark thisTrial_8 as finished
        if hasattr(thisTrial_8, 'status'):
            thisTrial_8.status = FINISHED
        # if awaiting a pause, pause now
        if trials_8.status == PAUSED:
            thisExp.status = PAUSED
            pauseExperiment(
                thisExp=thisExp, 
                win=win, 
                timers=[globalClock], 
            )
            # once done pausing, restore running status
            trials_8.status = STARTED
        thisExp.nextEntry()
        
    # completed 2.0 repeats of 'trials_8'
    trials_8.status = FINISHED
    
    if thisSession is not None:
        # if running in a Session with a Liaison client, send data up to now
        thisSession.sendExperimentData()
    
    # --- Prepare to start Routine "ready_" ---
    # create an object to store info about Routine ready_
    ready_ = data.Routine(
        name='ready_',
        components=[text_19, key_resp_6],
    )
    ready_.status = NOT_STARTED
    continueRoutine = True
    # update component parameters for each repeat
    # create starting attributes for key_resp_6
    key_resp_6.keys = []
    key_resp_6.rt = []
    _key_resp_6_allKeys = []
    # store start times for ready_
    ready_.tStartRefresh = win.getFutureFlipTime(clock=globalClock)
    ready_.tStart = globalClock.getTime(format='float')
    ready_.status = STARTED
    thisExp.addData('ready_.started', ready_.tStart)
    ready_.maxDuration = None
    # keep track of which components have finished
    ready_Components = ready_.components
    for thisComponent in ready_.components:
        thisComponent.tStart = None
        thisComponent.tStop = None
        thisComponent.tStartRefresh = None
        thisComponent.tStopRefresh = None
        if hasattr(thisComponent, 'status'):
            thisComponent.status = NOT_STARTED
    # reset timers
    t = 0
    _timeToFirstFrame = win.getFutureFlipTime(clock="now")
    frameN = -1
    
    # --- Run Routine "ready_" ---
    thisExp.currentRoutine = ready_
    ready_.forceEnded = routineForceEnded = not continueRoutine
    while continueRoutine:
        # get current time
        t = routineTimer.getTime()
        tThisFlip = win.getFutureFlipTime(clock=routineTimer)
        tThisFlipGlobal = win.getFutureFlipTime(clock=None)
        frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
        # update/draw components on each frame
        
        # *text_19* updates
        
        # if text_19 is starting this frame...
        if text_19.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            text_19.frameNStart = frameN  # exact frame index
            text_19.tStart = t  # local t and not account for scr refresh
            text_19.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(text_19, 'tStartRefresh')  # time at next scr refresh
            # update status
            text_19.status = STARTED
            text_19.setAutoDraw(True)
        
        # if text_19 is active this frame...
        if text_19.status == STARTED:
            # update params
            pass
        
        # *key_resp_6* updates
        waitOnFlip = False
        
        # if key_resp_6 is starting this frame...
        if key_resp_6.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            key_resp_6.frameNStart = frameN  # exact frame index
            key_resp_6.tStart = t  # local t and not account for scr refresh
            key_resp_6.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(key_resp_6, 'tStartRefresh')  # time at next scr refresh
            # update status
            key_resp_6.status = STARTED
            # keyboard checking is just starting
            waitOnFlip = True
            win.callOnFlip(key_resp_6.clock.reset)  # t=0 on next screen flip
            win.callOnFlip(key_resp_6.clearEvents, eventType='keyboard')  # clear events on next screen flip
        if key_resp_6.status == STARTED and not waitOnFlip:
            theseKeys = key_resp_6.getKeys(keyList=['space'], ignoreKeys=["escape"], waitRelease=False)
            _key_resp_6_allKeys.extend(theseKeys)
            if len(_key_resp_6_allKeys):
                key_resp_6.keys = _key_resp_6_allKeys[-1].name  # just the last key pressed
                key_resp_6.rt = _key_resp_6_allKeys[-1].rt
                key_resp_6.duration = _key_resp_6_allKeys[-1].duration
                # a response ends the routine
                continueRoutine = False
        
        # check for quit (typically the Esc key)
        if defaultKeyboard.getKeys(keyList=["escape"]):
            thisExp.status = FINISHED
        if thisExp.status == FINISHED or endExpNow:
            endExperiment(thisExp, win=win)
            return
        # pause experiment here if requested
        if thisExp.status == PAUSED:
            pauseExperiment(
                thisExp=thisExp, 
                win=win, 
                timers=[routineTimer, globalClock], 
                currentRoutine=ready_,
            )
            # skip the frame we paused on
            continue
        
        # has a Component requested the Routine to end?
        if not continueRoutine:
            ready_.forceEnded = routineForceEnded = True
        # has the Routine been forcibly ended?
        if ready_.forceEnded or routineForceEnded:
            break
        # has every Component finished?
        continueRoutine = False
        for thisComponent in ready_.components:
            if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                continueRoutine = True
                break  # at least one component has not yet finished
        
        # refresh the screen
        if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
            win.flip()
    
    # --- Ending Routine "ready_" ---
    for thisComponent in ready_.components:
        if hasattr(thisComponent, "setAutoDraw"):
            thisComponent.setAutoDraw(False)
    # store stop times for ready_
    ready_.tStop = globalClock.getTime(format='float')
    ready_.tStopRefresh = tThisFlipGlobal
    thisExp.addData('ready_.stopped', ready_.tStop)
    # check responses
    if key_resp_6.keys in ['', [], None]:  # No response was made
        key_resp_6.keys = None
    thisExp.addData('key_resp_6.keys',key_resp_6.keys)
    if key_resp_6.keys != None:  # we had a response
        thisExp.addData('key_resp_6.rt', key_resp_6.rt)
        thisExp.addData('key_resp_6.duration', key_resp_6.duration)
    thisExp.nextEntry()
    # the Routine "ready_" was not non-slip safe, so reset the non-slip timer
    routineTimer.reset()
    
    # set up handler to look after randomisation of conditions etc
    trials_5 = data.TrialHandler2(
        name='trials_5',
        nReps=5.0, 
        method='random', 
        extraInfo=expInfo, 
        originPath=-1, 
        trialList=[None], 
        seed=None, 
        isTrials=True, 
    )
    thisExp.addLoop(trials_5)  # add the loop to the experiment
    thisTrial_5 = trials_5.trialList[0]  # so we can initialise stimuli with some values
    # abbreviate parameter names if possible (e.g. rgb = thisTrial_5.rgb)
    if thisTrial_5 != None:
        for paramName in thisTrial_5:
            globals()[paramName] = thisTrial_5[paramName]
    if thisSession is not None:
        # if running in a Session with a Liaison client, send data up to now
        thisSession.sendExperimentData()
    
    for thisTrial_5 in trials_5:
        trials_5.status = STARTED
        if hasattr(thisTrial_5, 'status'):
            thisTrial_5.status = STARTED
        currentLoop = trials_5
        thisExp.timestampOnFlip(win, 'thisRow.t', format=globalClock.format)
        if thisSession is not None:
            # if running in a Session with a Liaison client, send data up to now
            thisSession.sendExperimentData()
        # abbreviate parameter names if possible (e.g. rgb = thisTrial_5.rgb)
        if thisTrial_5 != None:
            for paramName in thisTrial_5:
                globals()[paramName] = thisTrial_5[paramName]
        
        # set up handler to look after randomisation of conditions etc
        trials = data.TrialHandler2(
            name='trials',
            nReps=4.0, 
            method='random', 
            extraInfo=expInfo, 
            originPath=-1, 
            trialList=data.importConditions('SoundA.xlsx'), 
            seed=None, 
            isTrials=True, 
        )
        thisExp.addLoop(trials)  # add the loop to the experiment
        thisTrial = trials.trialList[0]  # so we can initialise stimuli with some values
        # abbreviate parameter names if possible (e.g. rgb = thisTrial.rgb)
        if thisTrial != None:
            for paramName in thisTrial:
                globals()[paramName] = thisTrial[paramName]
        if thisSession is not None:
            # if running in a Session with a Liaison client, send data up to now
            thisSession.sendExperimentData()
        
        for thisTrial in trials:
            trials.status = STARTED
            if hasattr(thisTrial, 'status'):
                thisTrial.status = STARTED
            currentLoop = trials
            thisExp.timestampOnFlip(win, 'thisRow.t', format=globalClock.format)
            if thisSession is not None:
                # if running in a Session with a Liaison client, send data up to now
                thisSession.sendExperimentData()
            # abbreviate parameter names if possible (e.g. rgb = thisTrial.rgb)
            if thisTrial != None:
                for paramName in thisTrial:
                    globals()[paramName] = thisTrial[paramName]
            
            # --- Prepare to start Routine "blank_cross" ---
            # create an object to store info about Routine blank_cross
            blank_cross = data.Routine(
                name='blank_cross',
                components=[text_4],
            )
            blank_cross.status = NOT_STARTED
            continueRoutine = True
            # update component parameters for each repeat
            text_4.setText('+')
            # store start times for blank_cross
            blank_cross.tStartRefresh = win.getFutureFlipTime(clock=globalClock)
            blank_cross.tStart = globalClock.getTime(format='float')
            blank_cross.status = STARTED
            thisExp.addData('blank_cross.started', blank_cross.tStart)
            blank_cross.maxDuration = None
            # keep track of which components have finished
            blank_crossComponents = blank_cross.components
            for thisComponent in blank_cross.components:
                thisComponent.tStart = None
                thisComponent.tStop = None
                thisComponent.tStartRefresh = None
                thisComponent.tStopRefresh = None
                if hasattr(thisComponent, 'status'):
                    thisComponent.status = NOT_STARTED
            # reset timers
            t = 0
            _timeToFirstFrame = win.getFutureFlipTime(clock="now")
            frameN = -1
            
            # --- Run Routine "blank_cross" ---
            thisExp.currentRoutine = blank_cross
            blank_cross.forceEnded = routineForceEnded = not continueRoutine
            while continueRoutine:
                # if trial has changed, end Routine now
                if hasattr(thisTrial, 'status') and thisTrial.status == STOPPING:
                    continueRoutine = False
                # get current time
                t = routineTimer.getTime()
                tThisFlip = win.getFutureFlipTime(clock=routineTimer)
                tThisFlipGlobal = win.getFutureFlipTime(clock=None)
                frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
                # update/draw components on each frame
                
                # *text_4* updates
                
                # if text_4 is starting this frame...
                if text_4.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                    # keep track of start time/frame for later
                    text_4.frameNStart = frameN  # exact frame index
                    text_4.tStart = t  # local t and not account for scr refresh
                    text_4.tStartRefresh = tThisFlipGlobal  # on global time
                    win.timeOnFlip(text_4, 'tStartRefresh')  # time at next scr refresh
                    # add timestamp to datafile
                    thisExp.timestampOnFlip(win, 'text_4.started')
                    # update status
                    text_4.status = STARTED
                    text_4.setAutoDraw(True)
                
                # if text_4 is active this frame...
                if text_4.status == STARTED:
                    # update params
                    pass
                
                # if text_4 is stopping this frame...
                if text_4.status == STARTED:
                    if frameN >= (text_4.frameNStart + randint(62, 125)):
                        # keep track of stop time/frame for later
                        text_4.tStop = t  # not accounting for scr refresh
                        text_4.tStopRefresh = tThisFlipGlobal  # on global time
                        text_4.frameNStop = frameN  # exact frame index
                        # add timestamp to datafile
                        thisExp.timestampOnFlip(win, 'text_4.stopped')
                        # update status
                        text_4.status = FINISHED
                        text_4.setAutoDraw(False)
                
                # check for quit (typically the Esc key)
                if defaultKeyboard.getKeys(keyList=["escape"]):
                    thisExp.status = FINISHED
                if thisExp.status == FINISHED or endExpNow:
                    endExperiment(thisExp, win=win)
                    return
                # pause experiment here if requested
                if thisExp.status == PAUSED:
                    pauseExperiment(
                        thisExp=thisExp, 
                        win=win, 
                        timers=[routineTimer, globalClock], 
                        currentRoutine=blank_cross,
                    )
                    # skip the frame we paused on
                    continue
                
                # has a Component requested the Routine to end?
                if not continueRoutine:
                    blank_cross.forceEnded = routineForceEnded = True
                # has the Routine been forcibly ended?
                if blank_cross.forceEnded or routineForceEnded:
                    break
                # has every Component finished?
                continueRoutine = False
                for thisComponent in blank_cross.components:
                    if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                        continueRoutine = True
                        break  # at least one component has not yet finished
                
                # refresh the screen
                if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                    win.flip()
            
            # --- Ending Routine "blank_cross" ---
            for thisComponent in blank_cross.components:
                if hasattr(thisComponent, "setAutoDraw"):
                    thisComponent.setAutoDraw(False)
            # store stop times for blank_cross
            blank_cross.tStop = globalClock.getTime(format='float')
            blank_cross.tStopRefresh = tThisFlipGlobal
            thisExp.addData('blank_cross.stopped', blank_cross.tStop)
            # the Routine "blank_cross" was not non-slip safe, so reset the non-slip timer
            routineTimer.reset()
            
            # --- Prepare to start Routine "trial" ---
            # create an object to store info about Routine trial
            trial = data.Routine(
                name='trial',
                components=[sound_1, image_2, text_2, G0_NoGo_key],
            )
            trial.status = NOT_STARTED
            continueRoutine = True
            # update component parameters for each repeat
            sound_1.setSound(Sound, secs=0.05, hamming=True)
            sound_1.setVolume(1.0, log=False)
            sound_1.seek(0)
            image_2.setImage(image)
            # create starting attributes for G0_NoGo_key
            G0_NoGo_key.keys = []
            G0_NoGo_key.rt = []
            _G0_NoGo_key_allKeys = []
            # store start times for trial
            trial.tStartRefresh = win.getFutureFlipTime(clock=globalClock)
            trial.tStart = globalClock.getTime(format='float')
            trial.status = STARTED
            thisExp.addData('trial.started', trial.tStart)
            trial.maxDuration = None
            # keep track of which components have finished
            trialComponents = trial.components
            for thisComponent in trial.components:
                thisComponent.tStart = None
                thisComponent.tStop = None
                thisComponent.tStartRefresh = None
                thisComponent.tStopRefresh = None
                if hasattr(thisComponent, 'status'):
                    thisComponent.status = NOT_STARTED
            # reset timers
            t = 0
            _timeToFirstFrame = win.getFutureFlipTime(clock="now")
            frameN = -1
            
            # --- Run Routine "trial" ---
            thisExp.currentRoutine = trial
            trial.forceEnded = routineForceEnded = not continueRoutine
            while continueRoutine and routineTimer.getTime() < 1.5:
                # if trial has changed, end Routine now
                if hasattr(thisTrial, 'status') and thisTrial.status == STOPPING:
                    continueRoutine = False
                # get current time
                t = routineTimer.getTime()
                tThisFlip = win.getFutureFlipTime(clock=routineTimer)
                tThisFlipGlobal = win.getFutureFlipTime(clock=None)
                frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
                # update/draw components on each frame
                
                # *sound_1* updates
                
                # if sound_1 is starting this frame...
                if sound_1.status == NOT_STARTED and tThisFlip >= 0-frameTolerance:
                    # keep track of start time/frame for later
                    sound_1.frameNStart = frameN  # exact frame index
                    sound_1.tStart = t  # local t and not account for scr refresh
                    sound_1.tStartRefresh = tThisFlipGlobal  # on global time
                    # add timestamp to datafile
                    thisExp.addData('sound_1.started', tThisFlipGlobal)
                    # update status
                    sound_1.status = STARTED
                    sound_1.play(when=win)  # sync with win flip
                
                # if sound_1 is stopping this frame...
                if sound_1.status == STARTED:
                    # is it time to stop? (based on global clock, using actual start)
                    if tThisFlipGlobal > sound_1.tStartRefresh + 0.05-frameTolerance or sound_1.isFinished:
                        # keep track of stop time/frame for later
                        sound_1.tStop = t  # not accounting for scr refresh
                        sound_1.tStopRefresh = tThisFlipGlobal  # on global time
                        sound_1.frameNStop = frameN  # exact frame index
                        # add timestamp to datafile
                        thisExp.timestampOnFlip(win, 'sound_1.stopped')
                        # update status
                        sound_1.status = FINISHED
                        sound_1.stop()
                
                # *image_2* updates
                
                # if image_2 is starting this frame...
                if image_2.status == NOT_STARTED and tThisFlip >= 0-frameTolerance:
                    # keep track of start time/frame for later
                    image_2.frameNStart = frameN  # exact frame index
                    image_2.tStart = t  # local t and not account for scr refresh
                    image_2.tStartRefresh = tThisFlipGlobal  # on global time
                    win.timeOnFlip(image_2, 'tStartRefresh')  # time at next scr refresh
                    # add timestamp to datafile
                    thisExp.timestampOnFlip(win, 'image_2.started')
                    # update status
                    image_2.status = STARTED
                    image_2.setAutoDraw(True)
                
                # if image_2 is active this frame...
                if image_2.status == STARTED:
                    # update params
                    pass
                
                # if image_2 is stopping this frame...
                if image_2.status == STARTED:
                    # is it time to stop? (based on global clock, using actual start)
                    if tThisFlipGlobal > image_2.tStartRefresh + 0.15-frameTolerance:
                        # keep track of stop time/frame for later
                        image_2.tStop = t  # not accounting for scr refresh
                        image_2.tStopRefresh = tThisFlipGlobal  # on global time
                        image_2.frameNStop = frameN  # exact frame index
                        # add timestamp to datafile
                        thisExp.timestampOnFlip(win, 'image_2.stopped')
                        # update status
                        image_2.status = FINISHED
                        image_2.setAutoDraw(False)
                
                # *text_2* updates
                
                # if text_2 is starting this frame...
                if text_2.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                    # keep track of start time/frame for later
                    text_2.frameNStart = frameN  # exact frame index
                    text_2.tStart = t  # local t and not account for scr refresh
                    text_2.tStartRefresh = tThisFlipGlobal  # on global time
                    win.timeOnFlip(text_2, 'tStartRefresh')  # time at next scr refresh
                    # update status
                    text_2.status = STARTED
                    text_2.setAutoDraw(True)
                
                # if text_2 is active this frame...
                if text_2.status == STARTED:
                    # update params
                    pass
                
                # if text_2 is stopping this frame...
                if text_2.status == STARTED:
                    # is it time to stop? (based on global clock, using actual start)
                    if tThisFlipGlobal > text_2.tStartRefresh + 1.5-frameTolerance:
                        # keep track of stop time/frame for later
                        text_2.tStop = t  # not accounting for scr refresh
                        text_2.tStopRefresh = tThisFlipGlobal  # on global time
                        text_2.frameNStop = frameN  # exact frame index
                        # update status
                        text_2.status = FINISHED
                        text_2.setAutoDraw(False)
                
                # *G0_NoGo_key* updates
                waitOnFlip = False
                
                # if G0_NoGo_key is starting this frame...
                if G0_NoGo_key.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                    # keep track of start time/frame for later
                    G0_NoGo_key.frameNStart = frameN  # exact frame index
                    G0_NoGo_key.tStart = t  # local t and not account for scr refresh
                    G0_NoGo_key.tStartRefresh = tThisFlipGlobal  # on global time
                    win.timeOnFlip(G0_NoGo_key, 'tStartRefresh')  # time at next scr refresh
                    # add timestamp to datafile
                    thisExp.timestampOnFlip(win, 'G0_NoGo_key.started')
                    # update status
                    G0_NoGo_key.status = STARTED
                    # keyboard checking is just starting
                    waitOnFlip = True
                    win.callOnFlip(G0_NoGo_key.clock.reset)  # t=0 on next screen flip
                    win.callOnFlip(G0_NoGo_key.clearEvents, eventType='keyboard')  # clear events on next screen flip
                
                # if G0_NoGo_key is stopping this frame...
                if G0_NoGo_key.status == STARTED:
                    # is it time to stop? (based on global clock, using actual start)
                    if tThisFlipGlobal > G0_NoGo_key.tStartRefresh + 1.5-frameTolerance:
                        # keep track of stop time/frame for later
                        G0_NoGo_key.tStop = t  # not accounting for scr refresh
                        G0_NoGo_key.tStopRefresh = tThisFlipGlobal  # on global time
                        G0_NoGo_key.frameNStop = frameN  # exact frame index
                        # add timestamp to datafile
                        thisExp.timestampOnFlip(win, 'G0_NoGo_key.stopped')
                        # update status
                        G0_NoGo_key.status = FINISHED
                        G0_NoGo_key.status = FINISHED
                if G0_NoGo_key.status == STARTED and not waitOnFlip:
                    theseKeys = G0_NoGo_key.getKeys(keyList=['space'], ignoreKeys=["escape"], waitRelease=False)
                    _G0_NoGo_key_allKeys.extend(theseKeys)
                    if len(_G0_NoGo_key_allKeys):
                        G0_NoGo_key.keys = _G0_NoGo_key_allKeys[-1].name  # just the last key pressed
                        G0_NoGo_key.rt = _G0_NoGo_key_allKeys[-1].rt
                        G0_NoGo_key.duration = _G0_NoGo_key_allKeys[-1].duration
                        # a response ends the routine
                        continueRoutine = False
                
                # check for quit (typically the Esc key)
                if defaultKeyboard.getKeys(keyList=["escape"]):
                    thisExp.status = FINISHED
                if thisExp.status == FINISHED or endExpNow:
                    endExperiment(thisExp, win=win)
                    return
                # pause experiment here if requested
                if thisExp.status == PAUSED:
                    pauseExperiment(
                        thisExp=thisExp, 
                        win=win, 
                        timers=[routineTimer, globalClock], 
                        currentRoutine=trial,
                    )
                    # skip the frame we paused on
                    continue
                
                # has a Component requested the Routine to end?
                if not continueRoutine:
                    trial.forceEnded = routineForceEnded = True
                # has the Routine been forcibly ended?
                if trial.forceEnded or routineForceEnded:
                    break
                # has every Component finished?
                continueRoutine = False
                for thisComponent in trial.components:
                    if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                        continueRoutine = True
                        break  # at least one component has not yet finished
                
                # refresh the screen
                if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                    win.flip()
            
            # --- Ending Routine "trial" ---
            for thisComponent in trial.components:
                if hasattr(thisComponent, "setAutoDraw"):
                    thisComponent.setAutoDraw(False)
            # store stop times for trial
            trial.tStop = globalClock.getTime(format='float')
            trial.tStopRefresh = tThisFlipGlobal
            thisExp.addData('trial.stopped', trial.tStop)
            sound_1.pause()  # ensure sound has stopped at end of Routine
            # check responses
            if G0_NoGo_key.keys in ['', [], None]:  # No response was made
                G0_NoGo_key.keys = None
            trials.addData('G0_NoGo_key.keys',G0_NoGo_key.keys)
            if G0_NoGo_key.keys != None:  # we had a response
                trials.addData('G0_NoGo_key.rt', G0_NoGo_key.rt)
                trials.addData('G0_NoGo_key.duration', G0_NoGo_key.duration)
            # using non-slip timing so subtract the expected duration of this Routine (unless ended on request)
            if trial.maxDurationReached:
                routineTimer.addTime(-trial.maxDuration)
            elif trial.forceEnded:
                routineTimer.reset()
            else:
                routineTimer.addTime(-1.500000)
            
            # --- Prepare to start Routine "goNogo" ---
            # create an object to store info about Routine goNogo
            goNogo = data.Routine(
                name='goNogo',
                components=[key_resp_4, text_10],
            )
            goNogo.status = NOT_STARTED
            continueRoutine = True
            # update component parameters for each repeat
            # create starting attributes for key_resp_4
            key_resp_4.keys = []
            key_resp_4.rt = []
            _key_resp_4_allKeys = []
            # store start times for goNogo
            goNogo.tStartRefresh = win.getFutureFlipTime(clock=globalClock)
            goNogo.tStart = globalClock.getTime(format='float')
            goNogo.status = STARTED
            thisExp.addData('goNogo.started', goNogo.tStart)
            goNogo.maxDuration = None
            # keep track of which components have finished
            goNogoComponents = goNogo.components
            for thisComponent in goNogo.components:
                thisComponent.tStart = None
                thisComponent.tStop = None
                thisComponent.tStartRefresh = None
                thisComponent.tStopRefresh = None
                if hasattr(thisComponent, 'status'):
                    thisComponent.status = NOT_STARTED
            # reset timers
            t = 0
            _timeToFirstFrame = win.getFutureFlipTime(clock="now")
            frameN = -1
            
            # --- Run Routine "goNogo" ---
            thisExp.currentRoutine = goNogo
            goNogo.forceEnded = routineForceEnded = not continueRoutine
            while continueRoutine and routineTimer.getTime() < 1.4:
                # if trial has changed, end Routine now
                if hasattr(thisTrial, 'status') and thisTrial.status == STOPPING:
                    continueRoutine = False
                # get current time
                t = routineTimer.getTime()
                tThisFlip = win.getFutureFlipTime(clock=routineTimer)
                tThisFlipGlobal = win.getFutureFlipTime(clock=None)
                frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
                # update/draw components on each frame
                
                # *key_resp_4* updates
                waitOnFlip = False
                
                # if key_resp_4 is starting this frame...
                if key_resp_4.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                    # keep track of start time/frame for later
                    key_resp_4.frameNStart = frameN  # exact frame index
                    key_resp_4.tStart = t  # local t and not account for scr refresh
                    key_resp_4.tStartRefresh = tThisFlipGlobal  # on global time
                    win.timeOnFlip(key_resp_4, 'tStartRefresh')  # time at next scr refresh
                    # add timestamp to datafile
                    thisExp.timestampOnFlip(win, 'key_resp_4.started')
                    # update status
                    key_resp_4.status = STARTED
                    # keyboard checking is just starting
                    waitOnFlip = True
                    win.callOnFlip(key_resp_4.clock.reset)  # t=0 on next screen flip
                    win.callOnFlip(key_resp_4.clearEvents, eventType='keyboard')  # clear events on next screen flip
                
                # if key_resp_4 is stopping this frame...
                if key_resp_4.status == STARTED:
                    # is it time to stop? (based on global clock, using actual start)
                    if tThisFlipGlobal > key_resp_4.tStartRefresh + 1.4-frameTolerance:
                        # keep track of stop time/frame for later
                        key_resp_4.tStop = t  # not accounting for scr refresh
                        key_resp_4.tStopRefresh = tThisFlipGlobal  # on global time
                        key_resp_4.frameNStop = frameN  # exact frame index
                        # add timestamp to datafile
                        thisExp.timestampOnFlip(win, 'key_resp_4.stopped')
                        # update status
                        key_resp_4.status = FINISHED
                        key_resp_4.status = FINISHED
                if key_resp_4.status == STARTED and not waitOnFlip:
                    theseKeys = key_resp_4.getKeys(keyList=['space'], ignoreKeys=["escape"], waitRelease=False)
                    _key_resp_4_allKeys.extend(theseKeys)
                    if len(_key_resp_4_allKeys):
                        key_resp_4.keys = _key_resp_4_allKeys[-1].name  # just the last key pressed
                        key_resp_4.rt = _key_resp_4_allKeys[-1].rt
                        key_resp_4.duration = _key_resp_4_allKeys[-1].duration
                        # a response ends the routine
                        continueRoutine = False
                
                # *text_10* updates
                
                # if text_10 is starting this frame...
                if text_10.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                    # keep track of start time/frame for later
                    text_10.frameNStart = frameN  # exact frame index
                    text_10.tStart = t  # local t and not account for scr refresh
                    text_10.tStartRefresh = tThisFlipGlobal  # on global time
                    win.timeOnFlip(text_10, 'tStartRefresh')  # time at next scr refresh
                    # add timestamp to datafile
                    thisExp.timestampOnFlip(win, 'text_10.started')
                    # update status
                    text_10.status = STARTED
                    text_10.setAutoDraw(True)
                
                # if text_10 is active this frame...
                if text_10.status == STARTED:
                    # update params
                    pass
                
                # if text_10 is stopping this frame...
                if text_10.status == STARTED:
                    # is it time to stop? (based on global clock, using actual start)
                    if tThisFlipGlobal > text_10.tStartRefresh + 1.4-frameTolerance:
                        # keep track of stop time/frame for later
                        text_10.tStop = t  # not accounting for scr refresh
                        text_10.tStopRefresh = tThisFlipGlobal  # on global time
                        text_10.frameNStop = frameN  # exact frame index
                        # add timestamp to datafile
                        thisExp.timestampOnFlip(win, 'text_10.stopped')
                        # update status
                        text_10.status = FINISHED
                        text_10.setAutoDraw(False)
                
                # check for quit (typically the Esc key)
                if defaultKeyboard.getKeys(keyList=["escape"]):
                    thisExp.status = FINISHED
                if thisExp.status == FINISHED or endExpNow:
                    endExperiment(thisExp, win=win)
                    return
                # pause experiment here if requested
                if thisExp.status == PAUSED:
                    pauseExperiment(
                        thisExp=thisExp, 
                        win=win, 
                        timers=[routineTimer, globalClock], 
                        currentRoutine=goNogo,
                    )
                    # skip the frame we paused on
                    continue
                
                # has a Component requested the Routine to end?
                if not continueRoutine:
                    goNogo.forceEnded = routineForceEnded = True
                # has the Routine been forcibly ended?
                if goNogo.forceEnded or routineForceEnded:
                    break
                # has every Component finished?
                continueRoutine = False
                for thisComponent in goNogo.components:
                    if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                        continueRoutine = True
                        break  # at least one component has not yet finished
                
                # refresh the screen
                if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                    win.flip()
            
            # --- Ending Routine "goNogo" ---
            for thisComponent in goNogo.components:
                if hasattr(thisComponent, "setAutoDraw"):
                    thisComponent.setAutoDraw(False)
            # store stop times for goNogo
            goNogo.tStop = globalClock.getTime(format='float')
            goNogo.tStopRefresh = tThisFlipGlobal
            thisExp.addData('goNogo.stopped', goNogo.tStop)
            # check responses
            if key_resp_4.keys in ['', [], None]:  # No response was made
                key_resp_4.keys = None
            trials.addData('key_resp_4.keys',key_resp_4.keys)
            if key_resp_4.keys != None:  # we had a response
                trials.addData('key_resp_4.rt', key_resp_4.rt)
                trials.addData('key_resp_4.duration', key_resp_4.duration)
            # using non-slip timing so subtract the expected duration of this Routine (unless ended on request)
            if goNogo.maxDurationReached:
                routineTimer.addTime(-goNogo.maxDuration)
            elif goNogo.forceEnded:
                routineTimer.reset()
            else:
                routineTimer.addTime(-1.400000)
            # mark thisTrial as finished
            if hasattr(thisTrial, 'status'):
                thisTrial.status = FINISHED
            # if awaiting a pause, pause now
            if trials.status == PAUSED:
                thisExp.status = PAUSED
                pauseExperiment(
                    thisExp=thisExp, 
                    win=win, 
                    timers=[globalClock], 
                )
                # once done pausing, restore running status
                trials.status = STARTED
            thisExp.nextEntry()
            
        # completed 4.0 repeats of 'trials'
        trials.status = FINISHED
        
        if thisSession is not None:
            # if running in a Session with a Liaison client, send data up to now
            thisSession.sendExperimentData()
        
        # --- Prepare to start Routine "break_2" ---
        # create an object to store info about Routine break_2
        break_2 = data.Routine(
            name='break_2',
            components=[text_9, key_resp_3],
        )
        break_2.status = NOT_STARTED
        continueRoutine = True
        # update component parameters for each repeat
        # create starting attributes for key_resp_3
        key_resp_3.keys = []
        key_resp_3.rt = []
        _key_resp_3_allKeys = []
        # store start times for break_2
        break_2.tStartRefresh = win.getFutureFlipTime(clock=globalClock)
        break_2.tStart = globalClock.getTime(format='float')
        break_2.status = STARTED
        thisExp.addData('break_2.started', break_2.tStart)
        break_2.maxDuration = None
        # keep track of which components have finished
        break_2Components = break_2.components
        for thisComponent in break_2.components:
            thisComponent.tStart = None
            thisComponent.tStop = None
            thisComponent.tStartRefresh = None
            thisComponent.tStopRefresh = None
            if hasattr(thisComponent, 'status'):
                thisComponent.status = NOT_STARTED
        # reset timers
        t = 0
        _timeToFirstFrame = win.getFutureFlipTime(clock="now")
        frameN = -1
        
        # --- Run Routine "break_2" ---
        thisExp.currentRoutine = break_2
        break_2.forceEnded = routineForceEnded = not continueRoutine
        while continueRoutine:
            # if trial has changed, end Routine now
            if hasattr(thisTrial_5, 'status') and thisTrial_5.status == STOPPING:
                continueRoutine = False
            # get current time
            t = routineTimer.getTime()
            tThisFlip = win.getFutureFlipTime(clock=routineTimer)
            tThisFlipGlobal = win.getFutureFlipTime(clock=None)
            frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
            # update/draw components on each frame
            
            # *text_9* updates
            
            # if text_9 is starting this frame...
            if text_9.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                # keep track of start time/frame for later
                text_9.frameNStart = frameN  # exact frame index
                text_9.tStart = t  # local t and not account for scr refresh
                text_9.tStartRefresh = tThisFlipGlobal  # on global time
                win.timeOnFlip(text_9, 'tStartRefresh')  # time at next scr refresh
                # update status
                text_9.status = STARTED
                text_9.setAutoDraw(True)
            
            # if text_9 is active this frame...
            if text_9.status == STARTED:
                # update params
                pass
            
            # *key_resp_3* updates
            waitOnFlip = False
            
            # if key_resp_3 is starting this frame...
            if key_resp_3.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                # keep track of start time/frame for later
                key_resp_3.frameNStart = frameN  # exact frame index
                key_resp_3.tStart = t  # local t and not account for scr refresh
                key_resp_3.tStartRefresh = tThisFlipGlobal  # on global time
                win.timeOnFlip(key_resp_3, 'tStartRefresh')  # time at next scr refresh
                # update status
                key_resp_3.status = STARTED
                # keyboard checking is just starting
                waitOnFlip = True
                win.callOnFlip(key_resp_3.clock.reset)  # t=0 on next screen flip
                win.callOnFlip(key_resp_3.clearEvents, eventType='keyboard')  # clear events on next screen flip
            if key_resp_3.status == STARTED and not waitOnFlip:
                theseKeys = key_resp_3.getKeys(keyList=['space'], ignoreKeys=["escape"], waitRelease=False)
                _key_resp_3_allKeys.extend(theseKeys)
                if len(_key_resp_3_allKeys):
                    key_resp_3.keys = _key_resp_3_allKeys[-1].name  # just the last key pressed
                    key_resp_3.rt = _key_resp_3_allKeys[-1].rt
                    key_resp_3.duration = _key_resp_3_allKeys[-1].duration
                    # a response ends the routine
                    continueRoutine = False
            
            # check for quit (typically the Esc key)
            if defaultKeyboard.getKeys(keyList=["escape"]):
                thisExp.status = FINISHED
            if thisExp.status == FINISHED or endExpNow:
                endExperiment(thisExp, win=win)
                return
            # pause experiment here if requested
            if thisExp.status == PAUSED:
                pauseExperiment(
                    thisExp=thisExp, 
                    win=win, 
                    timers=[routineTimer, globalClock], 
                    currentRoutine=break_2,
                )
                # skip the frame we paused on
                continue
            
            # has a Component requested the Routine to end?
            if not continueRoutine:
                break_2.forceEnded = routineForceEnded = True
            # has the Routine been forcibly ended?
            if break_2.forceEnded or routineForceEnded:
                break
            # has every Component finished?
            continueRoutine = False
            for thisComponent in break_2.components:
                if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                    continueRoutine = True
                    break  # at least one component has not yet finished
            
            # refresh the screen
            if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                win.flip()
        
        # --- Ending Routine "break_2" ---
        for thisComponent in break_2.components:
            if hasattr(thisComponent, "setAutoDraw"):
                thisComponent.setAutoDraw(False)
        # store stop times for break_2
        break_2.tStop = globalClock.getTime(format='float')
        break_2.tStopRefresh = tThisFlipGlobal
        thisExp.addData('break_2.stopped', break_2.tStop)
        # check responses
        if key_resp_3.keys in ['', [], None]:  # No response was made
            key_resp_3.keys = None
        trials_5.addData('key_resp_3.keys',key_resp_3.keys)
        if key_resp_3.keys != None:  # we had a response
            trials_5.addData('key_resp_3.rt', key_resp_3.rt)
            trials_5.addData('key_resp_3.duration', key_resp_3.duration)
        # the Routine "break_2" was not non-slip safe, so reset the non-slip timer
        routineTimer.reset()
        # mark thisTrial_5 as finished
        if hasattr(thisTrial_5, 'status'):
            thisTrial_5.status = FINISHED
        # if awaiting a pause, pause now
        if trials_5.status == PAUSED:
            thisExp.status = PAUSED
            pauseExperiment(
                thisExp=thisExp, 
                win=win, 
                timers=[globalClock], 
            )
            # once done pausing, restore running status
            trials_5.status = STARTED
        thisExp.nextEntry()
        
    # completed 5.0 repeats of 'trials_5'
    trials_5.status = FINISHED
    
    if thisSession is not None:
        # if running in a Session with a Liaison client, send data up to now
        thisSession.sendExperimentData()
    
    # --- Prepare to start Routine "instructions" ---
    # create an object to store info about Routine instructions
    instructions = data.Routine(
        name='instructions',
        components=[text_3, key_resp_2],
    )
    instructions.status = NOT_STARTED
    continueRoutine = True
    # update component parameters for each repeat
    # create starting attributes for key_resp_2
    key_resp_2.keys = []
    key_resp_2.rt = []
    _key_resp_2_allKeys = []
    # store start times for instructions
    instructions.tStartRefresh = win.getFutureFlipTime(clock=globalClock)
    instructions.tStart = globalClock.getTime(format='float')
    instructions.status = STARTED
    thisExp.addData('instructions.started', instructions.tStart)
    instructions.maxDuration = None
    # keep track of which components have finished
    instructionsComponents = instructions.components
    for thisComponent in instructions.components:
        thisComponent.tStart = None
        thisComponent.tStop = None
        thisComponent.tStartRefresh = None
        thisComponent.tStopRefresh = None
        if hasattr(thisComponent, 'status'):
            thisComponent.status = NOT_STARTED
    # reset timers
    t = 0
    _timeToFirstFrame = win.getFutureFlipTime(clock="now")
    frameN = -1
    
    # --- Run Routine "instructions" ---
    thisExp.currentRoutine = instructions
    instructions.forceEnded = routineForceEnded = not continueRoutine
    while continueRoutine:
        # get current time
        t = routineTimer.getTime()
        tThisFlip = win.getFutureFlipTime(clock=routineTimer)
        tThisFlipGlobal = win.getFutureFlipTime(clock=None)
        frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
        # update/draw components on each frame
        
        # *text_3* updates
        
        # if text_3 is starting this frame...
        if text_3.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            text_3.frameNStart = frameN  # exact frame index
            text_3.tStart = t  # local t and not account for scr refresh
            text_3.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(text_3, 'tStartRefresh')  # time at next scr refresh
            # update status
            text_3.status = STARTED
            text_3.setAutoDraw(True)
        
        # if text_3 is active this frame...
        if text_3.status == STARTED:
            # update params
            pass
        
        # *key_resp_2* updates
        waitOnFlip = False
        
        # if key_resp_2 is starting this frame...
        if key_resp_2.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            key_resp_2.frameNStart = frameN  # exact frame index
            key_resp_2.tStart = t  # local t and not account for scr refresh
            key_resp_2.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(key_resp_2, 'tStartRefresh')  # time at next scr refresh
            # update status
            key_resp_2.status = STARTED
            # keyboard checking is just starting
            waitOnFlip = True
            win.callOnFlip(key_resp_2.clock.reset)  # t=0 on next screen flip
            win.callOnFlip(key_resp_2.clearEvents, eventType='keyboard')  # clear events on next screen flip
        if key_resp_2.status == STARTED and not waitOnFlip:
            theseKeys = key_resp_2.getKeys(keyList=['space'], ignoreKeys=["escape"], waitRelease=False)
            _key_resp_2_allKeys.extend(theseKeys)
            if len(_key_resp_2_allKeys):
                key_resp_2.keys = _key_resp_2_allKeys[-1].name  # just the last key pressed
                key_resp_2.rt = _key_resp_2_allKeys[-1].rt
                key_resp_2.duration = _key_resp_2_allKeys[-1].duration
                # a response ends the routine
                continueRoutine = False
        
        # check for quit (typically the Esc key)
        if defaultKeyboard.getKeys(keyList=["escape"]):
            thisExp.status = FINISHED
        if thisExp.status == FINISHED or endExpNow:
            endExperiment(thisExp, win=win)
            return
        # pause experiment here if requested
        if thisExp.status == PAUSED:
            pauseExperiment(
                thisExp=thisExp, 
                win=win, 
                timers=[routineTimer, globalClock], 
                currentRoutine=instructions,
            )
            # skip the frame we paused on
            continue
        
        # has a Component requested the Routine to end?
        if not continueRoutine:
            instructions.forceEnded = routineForceEnded = True
        # has the Routine been forcibly ended?
        if instructions.forceEnded or routineForceEnded:
            break
        # has every Component finished?
        continueRoutine = False
        for thisComponent in instructions.components:
            if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                continueRoutine = True
                break  # at least one component has not yet finished
        
        # refresh the screen
        if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
            win.flip()
    
    # --- Ending Routine "instructions" ---
    for thisComponent in instructions.components:
        if hasattr(thisComponent, "setAutoDraw"):
            thisComponent.setAutoDraw(False)
    # store stop times for instructions
    instructions.tStop = globalClock.getTime(format='float')
    instructions.tStopRefresh = tThisFlipGlobal
    thisExp.addData('instructions.stopped', instructions.tStop)
    # check responses
    if key_resp_2.keys in ['', [], None]:  # No response was made
        key_resp_2.keys = None
    thisExp.addData('key_resp_2.keys',key_resp_2.keys)
    if key_resp_2.keys != None:  # we had a response
        thisExp.addData('key_resp_2.rt', key_resp_2.rt)
        thisExp.addData('key_resp_2.duration', key_resp_2.duration)
    thisExp.nextEntry()
    # the Routine "instructions" was not non-slip safe, so reset the non-slip timer
    routineTimer.reset()
    
    # --- Prepare to start Routine "cross" ---
    # create an object to store info about Routine cross
    cross = data.Routine(
        name='cross',
        components=[text_6],
    )
    cross.status = NOT_STARTED
    continueRoutine = True
    # update component parameters for each repeat
    # store start times for cross
    cross.tStartRefresh = win.getFutureFlipTime(clock=globalClock)
    cross.tStart = globalClock.getTime(format='float')
    cross.status = STARTED
    thisExp.addData('cross.started', cross.tStart)
    cross.maxDuration = None
    # keep track of which components have finished
    crossComponents = cross.components
    for thisComponent in cross.components:
        thisComponent.tStart = None
        thisComponent.tStop = None
        thisComponent.tStartRefresh = None
        thisComponent.tStopRefresh = None
        if hasattr(thisComponent, 'status'):
            thisComponent.status = NOT_STARTED
    # reset timers
    t = 0
    _timeToFirstFrame = win.getFutureFlipTime(clock="now")
    frameN = -1
    
    # --- Run Routine "cross" ---
    thisExp.currentRoutine = cross
    cross.forceEnded = routineForceEnded = not continueRoutine
    while continueRoutine and routineTimer.getTime() < 1.0:
        # get current time
        t = routineTimer.getTime()
        tThisFlip = win.getFutureFlipTime(clock=routineTimer)
        tThisFlipGlobal = win.getFutureFlipTime(clock=None)
        frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
        # update/draw components on each frame
        
        # *text_6* updates
        
        # if text_6 is starting this frame...
        if text_6.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            text_6.frameNStart = frameN  # exact frame index
            text_6.tStart = t  # local t and not account for scr refresh
            text_6.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(text_6, 'tStartRefresh')  # time at next scr refresh
            # update status
            text_6.status = STARTED
            text_6.setAutoDraw(True)
        
        # if text_6 is active this frame...
        if text_6.status == STARTED:
            # update params
            pass
        
        # if text_6 is stopping this frame...
        if text_6.status == STARTED:
            # is it time to stop? (based on global clock, using actual start)
            if tThisFlipGlobal > text_6.tStartRefresh + 1.0-frameTolerance:
                # keep track of stop time/frame for later
                text_6.tStop = t  # not accounting for scr refresh
                text_6.tStopRefresh = tThisFlipGlobal  # on global time
                text_6.frameNStop = frameN  # exact frame index
                # update status
                text_6.status = FINISHED
                text_6.setAutoDraw(False)
        
        # check for quit (typically the Esc key)
        if defaultKeyboard.getKeys(keyList=["escape"]):
            thisExp.status = FINISHED
        if thisExp.status == FINISHED or endExpNow:
            endExperiment(thisExp, win=win)
            return
        # pause experiment here if requested
        if thisExp.status == PAUSED:
            pauseExperiment(
                thisExp=thisExp, 
                win=win, 
                timers=[routineTimer, globalClock], 
                currentRoutine=cross,
            )
            # skip the frame we paused on
            continue
        
        # has a Component requested the Routine to end?
        if not continueRoutine:
            cross.forceEnded = routineForceEnded = True
        # has the Routine been forcibly ended?
        if cross.forceEnded or routineForceEnded:
            break
        # has every Component finished?
        continueRoutine = False
        for thisComponent in cross.components:
            if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                continueRoutine = True
                break  # at least one component has not yet finished
        
        # refresh the screen
        if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
            win.flip()
    
    # --- Ending Routine "cross" ---
    for thisComponent in cross.components:
        if hasattr(thisComponent, "setAutoDraw"):
            thisComponent.setAutoDraw(False)
    # store stop times for cross
    cross.tStop = globalClock.getTime(format='float')
    cross.tStopRefresh = tThisFlipGlobal
    thisExp.addData('cross.stopped', cross.tStop)
    # using non-slip timing so subtract the expected duration of this Routine (unless ended on request)
    if cross.maxDurationReached:
        routineTimer.addTime(-cross.maxDuration)
    elif cross.forceEnded:
        routineTimer.reset()
    else:
        routineTimer.addTime(-1.000000)
    thisExp.nextEntry()
    
    # set up handler to look after randomisation of conditions etc
    trials_4 = data.TrialHandler2(
        name='trials_4',
        nReps=5.0, 
        method='random', 
        extraInfo=expInfo, 
        originPath=-1, 
        trialList=[None], 
        seed=None, 
        isTrials=True, 
    )
    thisExp.addLoop(trials_4)  # add the loop to the experiment
    thisTrial_4 = trials_4.trialList[0]  # so we can initialise stimuli with some values
    # abbreviate parameter names if possible (e.g. rgb = thisTrial_4.rgb)
    if thisTrial_4 != None:
        for paramName in thisTrial_4:
            globals()[paramName] = thisTrial_4[paramName]
    if thisSession is not None:
        # if running in a Session with a Liaison client, send data up to now
        thisSession.sendExperimentData()
    
    for thisTrial_4 in trials_4:
        trials_4.status = STARTED
        if hasattr(thisTrial_4, 'status'):
            thisTrial_4.status = STARTED
        currentLoop = trials_4
        thisExp.timestampOnFlip(win, 'thisRow.t', format=globalClock.format)
        if thisSession is not None:
            # if running in a Session with a Liaison client, send data up to now
            thisSession.sendExperimentData()
        # abbreviate parameter names if possible (e.g. rgb = thisTrial_4.rgb)
        if thisTrial_4 != None:
            for paramName in thisTrial_4:
                globals()[paramName] = thisTrial_4[paramName]
        
        # set up handler to look after randomisation of conditions etc
        trials_2 = data.TrialHandler2(
            name='trials_2',
            nReps=3.0, 
            method='random', 
            extraInfo=expInfo, 
            originPath=-1, 
            trialList=data.importConditions('LorR.xlsx'), 
            seed=None, 
            isTrials=True, 
        )
        thisExp.addLoop(trials_2)  # add the loop to the experiment
        thisTrial_2 = trials_2.trialList[0]  # so we can initialise stimuli with some values
        # abbreviate parameter names if possible (e.g. rgb = thisTrial_2.rgb)
        if thisTrial_2 != None:
            for paramName in thisTrial_2:
                globals()[paramName] = thisTrial_2[paramName]
        if thisSession is not None:
            # if running in a Session with a Liaison client, send data up to now
            thisSession.sendExperimentData()
        
        for thisTrial_2 in trials_2:
            trials_2.status = STARTED
            if hasattr(thisTrial_2, 'status'):
                thisTrial_2.status = STARTED
            currentLoop = trials_2
            thisExp.timestampOnFlip(win, 'thisRow.t', format=globalClock.format)
            if thisSession is not None:
                # if running in a Session with a Liaison client, send data up to now
                thisSession.sendExperimentData()
            # abbreviate parameter names if possible (e.g. rgb = thisTrial_2.rgb)
            if thisTrial_2 != None:
                for paramName in thisTrial_2:
                    globals()[paramName] = thisTrial_2[paramName]
            
            # --- Prepare to start Routine "blank_cross" ---
            # create an object to store info about Routine blank_cross
            blank_cross = data.Routine(
                name='blank_cross',
                components=[text_4],
            )
            blank_cross.status = NOT_STARTED
            continueRoutine = True
            # update component parameters for each repeat
            text_4.setText('+')
            # store start times for blank_cross
            blank_cross.tStartRefresh = win.getFutureFlipTime(clock=globalClock)
            blank_cross.tStart = globalClock.getTime(format='float')
            blank_cross.status = STARTED
            thisExp.addData('blank_cross.started', blank_cross.tStart)
            blank_cross.maxDuration = None
            # keep track of which components have finished
            blank_crossComponents = blank_cross.components
            for thisComponent in blank_cross.components:
                thisComponent.tStart = None
                thisComponent.tStop = None
                thisComponent.tStartRefresh = None
                thisComponent.tStopRefresh = None
                if hasattr(thisComponent, 'status'):
                    thisComponent.status = NOT_STARTED
            # reset timers
            t = 0
            _timeToFirstFrame = win.getFutureFlipTime(clock="now")
            frameN = -1
            
            # --- Run Routine "blank_cross" ---
            thisExp.currentRoutine = blank_cross
            blank_cross.forceEnded = routineForceEnded = not continueRoutine
            while continueRoutine:
                # if trial has changed, end Routine now
                if hasattr(thisTrial_2, 'status') and thisTrial_2.status == STOPPING:
                    continueRoutine = False
                # get current time
                t = routineTimer.getTime()
                tThisFlip = win.getFutureFlipTime(clock=routineTimer)
                tThisFlipGlobal = win.getFutureFlipTime(clock=None)
                frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
                # update/draw components on each frame
                
                # *text_4* updates
                
                # if text_4 is starting this frame...
                if text_4.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                    # keep track of start time/frame for later
                    text_4.frameNStart = frameN  # exact frame index
                    text_4.tStart = t  # local t and not account for scr refresh
                    text_4.tStartRefresh = tThisFlipGlobal  # on global time
                    win.timeOnFlip(text_4, 'tStartRefresh')  # time at next scr refresh
                    # add timestamp to datafile
                    thisExp.timestampOnFlip(win, 'text_4.started')
                    # update status
                    text_4.status = STARTED
                    text_4.setAutoDraw(True)
                
                # if text_4 is active this frame...
                if text_4.status == STARTED:
                    # update params
                    pass
                
                # if text_4 is stopping this frame...
                if text_4.status == STARTED:
                    if frameN >= (text_4.frameNStart + randint(62, 125)):
                        # keep track of stop time/frame for later
                        text_4.tStop = t  # not accounting for scr refresh
                        text_4.tStopRefresh = tThisFlipGlobal  # on global time
                        text_4.frameNStop = frameN  # exact frame index
                        # add timestamp to datafile
                        thisExp.timestampOnFlip(win, 'text_4.stopped')
                        # update status
                        text_4.status = FINISHED
                        text_4.setAutoDraw(False)
                
                # check for quit (typically the Esc key)
                if defaultKeyboard.getKeys(keyList=["escape"]):
                    thisExp.status = FINISHED
                if thisExp.status == FINISHED or endExpNow:
                    endExperiment(thisExp, win=win)
                    return
                # pause experiment here if requested
                if thisExp.status == PAUSED:
                    pauseExperiment(
                        thisExp=thisExp, 
                        win=win, 
                        timers=[routineTimer, globalClock], 
                        currentRoutine=blank_cross,
                    )
                    # skip the frame we paused on
                    continue
                
                # has a Component requested the Routine to end?
                if not continueRoutine:
                    blank_cross.forceEnded = routineForceEnded = True
                # has the Routine been forcibly ended?
                if blank_cross.forceEnded or routineForceEnded:
                    break
                # has every Component finished?
                continueRoutine = False
                for thisComponent in blank_cross.components:
                    if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                        continueRoutine = True
                        break  # at least one component has not yet finished
                
                # refresh the screen
                if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                    win.flip()
            
            # --- Ending Routine "blank_cross" ---
            for thisComponent in blank_cross.components:
                if hasattr(thisComponent, "setAutoDraw"):
                    thisComponent.setAutoDraw(False)
            # store stop times for blank_cross
            blank_cross.tStop = globalClock.getTime(format='float')
            blank_cross.tStopRefresh = tThisFlipGlobal
            thisExp.addData('blank_cross.stopped', blank_cross.tStop)
            # the Routine "blank_cross" was not non-slip safe, so reset the non-slip timer
            routineTimer.reset()
            
            # --- Prepare to start Routine "conditioned_trigger" ---
            # create an object to store info about Routine conditioned_trigger
            conditioned_trigger = data.Routine(
                name='conditioned_trigger',
                components=[],
            )
            conditioned_trigger.status = NOT_STARTED
            continueRoutine = True
            # update component parameters for each repeat
            # store start times for conditioned_trigger
            conditioned_trigger.tStartRefresh = win.getFutureFlipTime(clock=globalClock)
            conditioned_trigger.tStart = globalClock.getTime(format='float')
            conditioned_trigger.status = STARTED
            thisExp.addData('conditioned_trigger.started', conditioned_trigger.tStart)
            conditioned_trigger.maxDuration = None
            # keep track of which components have finished
            conditioned_triggerComponents = conditioned_trigger.components
            for thisComponent in conditioned_trigger.components:
                thisComponent.tStart = None
                thisComponent.tStop = None
                thisComponent.tStartRefresh = None
                thisComponent.tStopRefresh = None
                if hasattr(thisComponent, 'status'):
                    thisComponent.status = NOT_STARTED
            # reset timers
            t = 0
            _timeToFirstFrame = win.getFutureFlipTime(clock="now")
            frameN = -1
            
            # --- Run Routine "conditioned_trigger" ---
            thisExp.currentRoutine = conditioned_trigger
            conditioned_trigger.forceEnded = routineForceEnded = not continueRoutine
            while continueRoutine:
                # if trial has changed, end Routine now
                if hasattr(thisTrial_2, 'status') and thisTrial_2.status == STOPPING:
                    continueRoutine = False
                # get current time
                t = routineTimer.getTime()
                tThisFlip = win.getFutureFlipTime(clock=routineTimer)
                tThisFlipGlobal = win.getFutureFlipTime(clock=None)
                frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
                # update/draw components on each frame
                
                # check for quit (typically the Esc key)
                if defaultKeyboard.getKeys(keyList=["escape"]):
                    thisExp.status = FINISHED
                if thisExp.status == FINISHED or endExpNow:
                    endExperiment(thisExp, win=win)
                    return
                # pause experiment here if requested
                if thisExp.status == PAUSED:
                    pauseExperiment(
                        thisExp=thisExp, 
                        win=win, 
                        timers=[routineTimer, globalClock], 
                        currentRoutine=conditioned_trigger,
                    )
                    # skip the frame we paused on
                    continue
                
                # has a Component requested the Routine to end?
                if not continueRoutine:
                    conditioned_trigger.forceEnded = routineForceEnded = True
                # has the Routine been forcibly ended?
                if conditioned_trigger.forceEnded or routineForceEnded:
                    break
                # has every Component finished?
                continueRoutine = False
                for thisComponent in conditioned_trigger.components:
                    if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                        continueRoutine = True
                        break  # at least one component has not yet finished
                
                # refresh the screen
                if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                    win.flip()
            
            # --- Ending Routine "conditioned_trigger" ---
            for thisComponent in conditioned_trigger.components:
                if hasattr(thisComponent, "setAutoDraw"):
                    thisComponent.setAutoDraw(False)
            # store stop times for conditioned_trigger
            conditioned_trigger.tStop = globalClock.getTime(format='float')
            conditioned_trigger.tStopRefresh = tThisFlipGlobal
            thisExp.addData('conditioned_trigger.stopped', conditioned_trigger.tStop)
            # the Routine "conditioned_trigger" was not non-slip safe, so reset the non-slip timer
            routineTimer.reset()
            
            # --- Prepare to start Routine "Necker" ---
            # create an object to store info about Routine Necker
            Necker = data.Routine(
                name='Necker',
                components=[image_3, text_5, sound_2],
            )
            Necker.status = NOT_STARTED
            continueRoutine = True
            # update component parameters for each repeat
            sound_2.setSound(Sound, secs=0.05, hamming=True)
            sound_2.setVolume(1.0, log=False)
            sound_2.seek(0)
            # store start times for Necker
            Necker.tStartRefresh = win.getFutureFlipTime(clock=globalClock)
            Necker.tStart = globalClock.getTime(format='float')
            Necker.status = STARTED
            thisExp.addData('Necker.started', Necker.tStart)
            Necker.maxDuration = None
            # keep track of which components have finished
            NeckerComponents = Necker.components
            for thisComponent in Necker.components:
                thisComponent.tStart = None
                thisComponent.tStop = None
                thisComponent.tStartRefresh = None
                thisComponent.tStopRefresh = None
                if hasattr(thisComponent, 'status'):
                    thisComponent.status = NOT_STARTED
            # reset timers
            t = 0
            _timeToFirstFrame = win.getFutureFlipTime(clock="now")
            frameN = -1
            
            # --- Run Routine "Necker" ---
            thisExp.currentRoutine = Necker
            Necker.forceEnded = routineForceEnded = not continueRoutine
            while continueRoutine:
                # if trial has changed, end Routine now
                if hasattr(thisTrial_2, 'status') and thisTrial_2.status == STOPPING:
                    continueRoutine = False
                # get current time
                t = routineTimer.getTime()
                tThisFlip = win.getFutureFlipTime(clock=routineTimer)
                tThisFlipGlobal = win.getFutureFlipTime(clock=None)
                frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
                # update/draw components on each frame
                
                # *image_3* updates
                
                # if image_3 is starting this frame...
                if image_3.status == NOT_STARTED and tThisFlip >= 0-frameTolerance:
                    # keep track of start time/frame for later
                    image_3.frameNStart = frameN  # exact frame index
                    image_3.tStart = t  # local t and not account for scr refresh
                    image_3.tStartRefresh = tThisFlipGlobal  # on global time
                    win.timeOnFlip(image_3, 'tStartRefresh')  # time at next scr refresh
                    # add timestamp to datafile
                    thisExp.timestampOnFlip(win, 'image_3.started')
                    # update status
                    image_3.status = STARTED
                    image_3.setAutoDraw(True)
                
                # if image_3 is active this frame...
                if image_3.status == STARTED:
                    # update params
                    pass
                
                # if image_3 is stopping this frame...
                if image_3.status == STARTED:
                    # is it time to stop? (based on global clock, using actual start)
                    if tThisFlipGlobal > image_3.tStartRefresh + 0.15-frameTolerance:
                        # keep track of stop time/frame for later
                        image_3.tStop = t  # not accounting for scr refresh
                        image_3.tStopRefresh = tThisFlipGlobal  # on global time
                        image_3.frameNStop = frameN  # exact frame index
                        # add timestamp to datafile
                        thisExp.timestampOnFlip(win, 'image_3.stopped')
                        # update status
                        image_3.status = FINISHED
                        image_3.setAutoDraw(False)
                
                # *text_5* updates
                
                # if text_5 is starting this frame...
                if text_5.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                    # keep track of start time/frame for later
                    text_5.frameNStart = frameN  # exact frame index
                    text_5.tStart = t  # local t and not account for scr refresh
                    text_5.tStartRefresh = tThisFlipGlobal  # on global time
                    win.timeOnFlip(text_5, 'tStartRefresh')  # time at next scr refresh
                    # add timestamp to datafile
                    thisExp.timestampOnFlip(win, 'text_5.started')
                    # update status
                    text_5.status = STARTED
                    text_5.setAutoDraw(True)
                
                # if text_5 is active this frame...
                if text_5.status == STARTED:
                    # update params
                    pass
                
                # if text_5 is stopping this frame...
                if text_5.status == STARTED:
                    # is it time to stop? (based on global clock, using actual start)
                    if tThisFlipGlobal > text_5.tStartRefresh + 1.5-frameTolerance:
                        # keep track of stop time/frame for later
                        text_5.tStop = t  # not accounting for scr refresh
                        text_5.tStopRefresh = tThisFlipGlobal  # on global time
                        text_5.frameNStop = frameN  # exact frame index
                        # add timestamp to datafile
                        thisExp.timestampOnFlip(win, 'text_5.stopped')
                        # update status
                        text_5.status = FINISHED
                        text_5.setAutoDraw(False)
                
                # *sound_2* updates
                
                # if sound_2 is starting this frame...
                if sound_2.status == NOT_STARTED and tThisFlip >= delay-frameTolerance:
                    # keep track of start time/frame for later
                    sound_2.frameNStart = frameN  # exact frame index
                    sound_2.tStart = t  # local t and not account for scr refresh
                    sound_2.tStartRefresh = tThisFlipGlobal  # on global time
                    # add timestamp to datafile
                    thisExp.addData('sound_2.started', tThisFlipGlobal)
                    # update status
                    sound_2.status = STARTED
                    sound_2.play(when=win)  # sync with win flip
                
                # if sound_2 is stopping this frame...
                if sound_2.status == STARTED:
                    # is it time to stop? (based on global clock, using actual start)
                    if tThisFlipGlobal > sound_2.tStartRefresh + 0.05-frameTolerance or sound_2.isFinished:
                        # keep track of stop time/frame for later
                        sound_2.tStop = t  # not accounting for scr refresh
                        sound_2.tStopRefresh = tThisFlipGlobal  # on global time
                        sound_2.frameNStop = frameN  # exact frame index
                        # add timestamp to datafile
                        thisExp.timestampOnFlip(win, 'sound_2.stopped')
                        # update status
                        sound_2.status = FINISHED
                        sound_2.stop()
                
                # check for quit (typically the Esc key)
                if defaultKeyboard.getKeys(keyList=["escape"]):
                    thisExp.status = FINISHED
                if thisExp.status == FINISHED or endExpNow:
                    endExperiment(thisExp, win=win)
                    return
                # pause experiment here if requested
                if thisExp.status == PAUSED:
                    pauseExperiment(
                        thisExp=thisExp, 
                        win=win, 
                        timers=[routineTimer, globalClock], 
                        currentRoutine=Necker,
                    )
                    # skip the frame we paused on
                    continue
                
                # has a Component requested the Routine to end?
                if not continueRoutine:
                    Necker.forceEnded = routineForceEnded = True
                # has the Routine been forcibly ended?
                if Necker.forceEnded or routineForceEnded:
                    break
                # has every Component finished?
                continueRoutine = False
                for thisComponent in Necker.components:
                    if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                        continueRoutine = True
                        break  # at least one component has not yet finished
                
                # refresh the screen
                if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                    win.flip()
            
            # --- Ending Routine "Necker" ---
            for thisComponent in Necker.components:
                if hasattr(thisComponent, "setAutoDraw"):
                    thisComponent.setAutoDraw(False)
            # store stop times for Necker
            Necker.tStop = globalClock.getTime(format='float')
            Necker.tStopRefresh = tThisFlipGlobal
            thisExp.addData('Necker.stopped', Necker.tStop)
            sound_2.pause()  # ensure sound has stopped at end of Routine
            # the Routine "Necker" was not non-slip safe, so reset the non-slip timer
            routineTimer.reset()
            
            # --- Prepare to start Routine "blank" ---
            # create an object to store info about Routine blank
            blank = data.Routine(
                name='blank',
                components=[image4, key_resp, text_8],
            )
            blank.status = NOT_STARTED
            continueRoutine = True
            # update component parameters for each repeat
            image4.setImage(choice)
            # create starting attributes for key_resp
            key_resp.keys = []
            key_resp.rt = []
            _key_resp_allKeys = []
            # store start times for blank
            blank.tStartRefresh = win.getFutureFlipTime(clock=globalClock)
            blank.tStart = globalClock.getTime(format='float')
            blank.status = STARTED
            thisExp.addData('blank.started', blank.tStart)
            blank.maxDuration = None
            # keep track of which components have finished
            blankComponents = blank.components
            for thisComponent in blank.components:
                thisComponent.tStart = None
                thisComponent.tStop = None
                thisComponent.tStartRefresh = None
                thisComponent.tStopRefresh = None
                if hasattr(thisComponent, 'status'):
                    thisComponent.status = NOT_STARTED
            # reset timers
            t = 0
            _timeToFirstFrame = win.getFutureFlipTime(clock="now")
            frameN = -1
            
            # --- Run Routine "blank" ---
            thisExp.currentRoutine = blank
            blank.forceEnded = routineForceEnded = not continueRoutine
            while continueRoutine and routineTimer.getTime() < 3.0:
                # if trial has changed, end Routine now
                if hasattr(thisTrial_2, 'status') and thisTrial_2.status == STOPPING:
                    continueRoutine = False
                # get current time
                t = routineTimer.getTime()
                tThisFlip = win.getFutureFlipTime(clock=routineTimer)
                tThisFlipGlobal = win.getFutureFlipTime(clock=None)
                frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
                # update/draw components on each frame
                
                # *image4* updates
                
                # if image4 is starting this frame...
                if image4.status == NOT_STARTED and tThisFlip >= 0-frameTolerance:
                    # keep track of start time/frame for later
                    image4.frameNStart = frameN  # exact frame index
                    image4.tStart = t  # local t and not account for scr refresh
                    image4.tStartRefresh = tThisFlipGlobal  # on global time
                    win.timeOnFlip(image4, 'tStartRefresh')  # time at next scr refresh
                    # update status
                    image4.status = STARTED
                    image4.setAutoDraw(True)
                
                # if image4 is active this frame...
                if image4.status == STARTED:
                    # update params
                    pass
                
                # if image4 is stopping this frame...
                if image4.status == STARTED:
                    # is it time to stop? (based on global clock, using actual start)
                    if tThisFlipGlobal > image4.tStartRefresh + 3-frameTolerance:
                        # keep track of stop time/frame for later
                        image4.tStop = t  # not accounting for scr refresh
                        image4.tStopRefresh = tThisFlipGlobal  # on global time
                        image4.frameNStop = frameN  # exact frame index
                        # update status
                        image4.status = FINISHED
                        image4.setAutoDraw(False)
                
                # *key_resp* updates
                waitOnFlip = False
                
                # if key_resp is starting this frame...
                if key_resp.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                    # keep track of start time/frame for later
                    key_resp.frameNStart = frameN  # exact frame index
                    key_resp.tStart = t  # local t and not account for scr refresh
                    key_resp.tStartRefresh = tThisFlipGlobal  # on global time
                    win.timeOnFlip(key_resp, 'tStartRefresh')  # time at next scr refresh
                    # add timestamp to datafile
                    thisExp.timestampOnFlip(win, 'key_resp.started')
                    # update status
                    key_resp.status = STARTED
                    # keyboard checking is just starting
                    waitOnFlip = True
                    win.callOnFlip(key_resp.clock.reset)  # t=0 on next screen flip
                
                # if key_resp is stopping this frame...
                if key_resp.status == STARTED:
                    # is it time to stop? (based on global clock, using actual start)
                    if tThisFlipGlobal > key_resp.tStartRefresh + 3-frameTolerance:
                        # keep track of stop time/frame for later
                        key_resp.tStop = t  # not accounting for scr refresh
                        key_resp.tStopRefresh = tThisFlipGlobal  # on global time
                        key_resp.frameNStop = frameN  # exact frame index
                        # add timestamp to datafile
                        thisExp.timestampOnFlip(win, 'key_resp.stopped')
                        # update status
                        key_resp.status = FINISHED
                        key_resp.status = FINISHED
                if key_resp.status == STARTED and not waitOnFlip:
                    theseKeys = key_resp.getKeys(keyList=['left','right'], ignoreKeys=["escape"], waitRelease=False)
                    _key_resp_allKeys.extend(theseKeys)
                    if len(_key_resp_allKeys):
                        key_resp.keys = _key_resp_allKeys[-1].name  # just the last key pressed
                        key_resp.rt = _key_resp_allKeys[-1].rt
                        key_resp.duration = _key_resp_allKeys[-1].duration
                        # a response ends the routine
                        continueRoutine = False
                
                # *text_8* updates
                
                # if text_8 is starting this frame...
                if text_8.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                    # keep track of start time/frame for later
                    text_8.frameNStart = frameN  # exact frame index
                    text_8.tStart = t  # local t and not account for scr refresh
                    text_8.tStartRefresh = tThisFlipGlobal  # on global time
                    win.timeOnFlip(text_8, 'tStartRefresh')  # time at next scr refresh
                    # update status
                    text_8.status = STARTED
                    text_8.setAutoDraw(True)
                
                # if text_8 is active this frame...
                if text_8.status == STARTED:
                    # update params
                    pass
                
                # if text_8 is stopping this frame...
                if text_8.status == STARTED:
                    # is it time to stop? (based on global clock, using actual start)
                    if tThisFlipGlobal > text_8.tStartRefresh + 3-frameTolerance:
                        # keep track of stop time/frame for later
                        text_8.tStop = t  # not accounting for scr refresh
                        text_8.tStopRefresh = tThisFlipGlobal  # on global time
                        text_8.frameNStop = frameN  # exact frame index
                        # update status
                        text_8.status = FINISHED
                        text_8.setAutoDraw(False)
                
                # check for quit (typically the Esc key)
                if defaultKeyboard.getKeys(keyList=["escape"]):
                    thisExp.status = FINISHED
                if thisExp.status == FINISHED or endExpNow:
                    endExperiment(thisExp, win=win)
                    return
                # pause experiment here if requested
                if thisExp.status == PAUSED:
                    pauseExperiment(
                        thisExp=thisExp, 
                        win=win, 
                        timers=[routineTimer, globalClock], 
                        currentRoutine=blank,
                    )
                    # skip the frame we paused on
                    continue
                
                # has a Component requested the Routine to end?
                if not continueRoutine:
                    blank.forceEnded = routineForceEnded = True
                # has the Routine been forcibly ended?
                if blank.forceEnded or routineForceEnded:
                    break
                # has every Component finished?
                continueRoutine = False
                for thisComponent in blank.components:
                    if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                        continueRoutine = True
                        break  # at least one component has not yet finished
                
                # refresh the screen
                if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                    win.flip()
            
            # --- Ending Routine "blank" ---
            for thisComponent in blank.components:
                if hasattr(thisComponent, "setAutoDraw"):
                    thisComponent.setAutoDraw(False)
            # store stop times for blank
            blank.tStop = globalClock.getTime(format='float')
            blank.tStopRefresh = tThisFlipGlobal
            thisExp.addData('blank.stopped', blank.tStop)
            # check responses
            if key_resp.keys in ['', [], None]:  # No response was made
                key_resp.keys = None
            trials_2.addData('key_resp.keys',key_resp.keys)
            if key_resp.keys != None:  # we had a response
                trials_2.addData('key_resp.rt', key_resp.rt)
                trials_2.addData('key_resp.duration', key_resp.duration)
            # using non-slip timing so subtract the expected duration of this Routine (unless ended on request)
            if blank.maxDurationReached:
                routineTimer.addTime(-blank.maxDuration)
            elif blank.forceEnded:
                routineTimer.reset()
            else:
                routineTimer.addTime(-3.000000)
            # mark thisTrial_2 as finished
            if hasattr(thisTrial_2, 'status'):
                thisTrial_2.status = FINISHED
            # if awaiting a pause, pause now
            if trials_2.status == PAUSED:
                thisExp.status = PAUSED
                pauseExperiment(
                    thisExp=thisExp, 
                    win=win, 
                    timers=[globalClock], 
                )
                # once done pausing, restore running status
                trials_2.status = STARTED
            thisExp.nextEntry()
            
        # completed 3.0 repeats of 'trials_2'
        trials_2.status = FINISHED
        
        if thisSession is not None:
            # if running in a Session with a Liaison client, send data up to now
            thisSession.sendExperimentData()
        
        # --- Prepare to start Routine "break_2" ---
        # create an object to store info about Routine break_2
        break_2 = data.Routine(
            name='break_2',
            components=[text_9, key_resp_3],
        )
        break_2.status = NOT_STARTED
        continueRoutine = True
        # update component parameters for each repeat
        # create starting attributes for key_resp_3
        key_resp_3.keys = []
        key_resp_3.rt = []
        _key_resp_3_allKeys = []
        # store start times for break_2
        break_2.tStartRefresh = win.getFutureFlipTime(clock=globalClock)
        break_2.tStart = globalClock.getTime(format='float')
        break_2.status = STARTED
        thisExp.addData('break_2.started', break_2.tStart)
        break_2.maxDuration = None
        # keep track of which components have finished
        break_2Components = break_2.components
        for thisComponent in break_2.components:
            thisComponent.tStart = None
            thisComponent.tStop = None
            thisComponent.tStartRefresh = None
            thisComponent.tStopRefresh = None
            if hasattr(thisComponent, 'status'):
                thisComponent.status = NOT_STARTED
        # reset timers
        t = 0
        _timeToFirstFrame = win.getFutureFlipTime(clock="now")
        frameN = -1
        
        # --- Run Routine "break_2" ---
        thisExp.currentRoutine = break_2
        break_2.forceEnded = routineForceEnded = not continueRoutine
        while continueRoutine:
            # if trial has changed, end Routine now
            if hasattr(thisTrial_4, 'status') and thisTrial_4.status == STOPPING:
                continueRoutine = False
            # get current time
            t = routineTimer.getTime()
            tThisFlip = win.getFutureFlipTime(clock=routineTimer)
            tThisFlipGlobal = win.getFutureFlipTime(clock=None)
            frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
            # update/draw components on each frame
            
            # *text_9* updates
            
            # if text_9 is starting this frame...
            if text_9.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                # keep track of start time/frame for later
                text_9.frameNStart = frameN  # exact frame index
                text_9.tStart = t  # local t and not account for scr refresh
                text_9.tStartRefresh = tThisFlipGlobal  # on global time
                win.timeOnFlip(text_9, 'tStartRefresh')  # time at next scr refresh
                # update status
                text_9.status = STARTED
                text_9.setAutoDraw(True)
            
            # if text_9 is active this frame...
            if text_9.status == STARTED:
                # update params
                pass
            
            # *key_resp_3* updates
            waitOnFlip = False
            
            # if key_resp_3 is starting this frame...
            if key_resp_3.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                # keep track of start time/frame for later
                key_resp_3.frameNStart = frameN  # exact frame index
                key_resp_3.tStart = t  # local t and not account for scr refresh
                key_resp_3.tStartRefresh = tThisFlipGlobal  # on global time
                win.timeOnFlip(key_resp_3, 'tStartRefresh')  # time at next scr refresh
                # update status
                key_resp_3.status = STARTED
                # keyboard checking is just starting
                waitOnFlip = True
                win.callOnFlip(key_resp_3.clock.reset)  # t=0 on next screen flip
                win.callOnFlip(key_resp_3.clearEvents, eventType='keyboard')  # clear events on next screen flip
            if key_resp_3.status == STARTED and not waitOnFlip:
                theseKeys = key_resp_3.getKeys(keyList=['space'], ignoreKeys=["escape"], waitRelease=False)
                _key_resp_3_allKeys.extend(theseKeys)
                if len(_key_resp_3_allKeys):
                    key_resp_3.keys = _key_resp_3_allKeys[-1].name  # just the last key pressed
                    key_resp_3.rt = _key_resp_3_allKeys[-1].rt
                    key_resp_3.duration = _key_resp_3_allKeys[-1].duration
                    # a response ends the routine
                    continueRoutine = False
            
            # check for quit (typically the Esc key)
            if defaultKeyboard.getKeys(keyList=["escape"]):
                thisExp.status = FINISHED
            if thisExp.status == FINISHED or endExpNow:
                endExperiment(thisExp, win=win)
                return
            # pause experiment here if requested
            if thisExp.status == PAUSED:
                pauseExperiment(
                    thisExp=thisExp, 
                    win=win, 
                    timers=[routineTimer, globalClock], 
                    currentRoutine=break_2,
                )
                # skip the frame we paused on
                continue
            
            # has a Component requested the Routine to end?
            if not continueRoutine:
                break_2.forceEnded = routineForceEnded = True
            # has the Routine been forcibly ended?
            if break_2.forceEnded or routineForceEnded:
                break
            # has every Component finished?
            continueRoutine = False
            for thisComponent in break_2.components:
                if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                    continueRoutine = True
                    break  # at least one component has not yet finished
            
            # refresh the screen
            if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                win.flip()
        
        # --- Ending Routine "break_2" ---
        for thisComponent in break_2.components:
            if hasattr(thisComponent, "setAutoDraw"):
                thisComponent.setAutoDraw(False)
        # store stop times for break_2
        break_2.tStop = globalClock.getTime(format='float')
        break_2.tStopRefresh = tThisFlipGlobal
        thisExp.addData('break_2.stopped', break_2.tStop)
        # check responses
        if key_resp_3.keys in ['', [], None]:  # No response was made
            key_resp_3.keys = None
        trials_4.addData('key_resp_3.keys',key_resp_3.keys)
        if key_resp_3.keys != None:  # we had a response
            trials_4.addData('key_resp_3.rt', key_resp_3.rt)
            trials_4.addData('key_resp_3.duration', key_resp_3.duration)
        # the Routine "break_2" was not non-slip safe, so reset the non-slip timer
        routineTimer.reset()
        # mark thisTrial_4 as finished
        if hasattr(thisTrial_4, 'status'):
            thisTrial_4.status = FINISHED
        # if awaiting a pause, pause now
        if trials_4.status == PAUSED:
            thisExp.status = PAUSED
            pauseExperiment(
                thisExp=thisExp, 
                win=win, 
                timers=[globalClock], 
            )
            # once done pausing, restore running status
            trials_4.status = STARTED
        thisExp.nextEntry()
        
    # completed 5.0 repeats of 'trials_4'
    trials_4.status = FINISHED
    
    if thisSession is not None:
        # if running in a Session with a Liaison client, send data up to now
        thisSession.sendExperimentData()
    
    # --- Prepare to start Routine "Thanks" ---
    # create an object to store info about Routine Thanks
    Thanks = data.Routine(
        name='Thanks',
        components=[text_27],
    )
    Thanks.status = NOT_STARTED
    continueRoutine = True
    # update component parameters for each repeat
    # store start times for Thanks
    Thanks.tStartRefresh = win.getFutureFlipTime(clock=globalClock)
    Thanks.tStart = globalClock.getTime(format='float')
    Thanks.status = STARTED
    thisExp.addData('Thanks.started', Thanks.tStart)
    Thanks.maxDuration = None
    # keep track of which components have finished
    ThanksComponents = Thanks.components
    for thisComponent in Thanks.components:
        thisComponent.tStart = None
        thisComponent.tStop = None
        thisComponent.tStartRefresh = None
        thisComponent.tStopRefresh = None
        if hasattr(thisComponent, 'status'):
            thisComponent.status = NOT_STARTED
    # reset timers
    t = 0
    _timeToFirstFrame = win.getFutureFlipTime(clock="now")
    frameN = -1
    
    # --- Run Routine "Thanks" ---
    thisExp.currentRoutine = Thanks
    Thanks.forceEnded = routineForceEnded = not continueRoutine
    while continueRoutine and routineTimer.getTime() < 3.0:
        # get current time
        t = routineTimer.getTime()
        tThisFlip = win.getFutureFlipTime(clock=routineTimer)
        tThisFlipGlobal = win.getFutureFlipTime(clock=None)
        frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
        # update/draw components on each frame
        
        # *text_27* updates
        
        # if text_27 is starting this frame...
        if text_27.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
            # keep track of start time/frame for later
            text_27.frameNStart = frameN  # exact frame index
            text_27.tStart = t  # local t and not account for scr refresh
            text_27.tStartRefresh = tThisFlipGlobal  # on global time
            win.timeOnFlip(text_27, 'tStartRefresh')  # time at next scr refresh
            # add timestamp to datafile
            thisExp.timestampOnFlip(win, 'text_27.started')
            # update status
            text_27.status = STARTED
            text_27.setAutoDraw(True)
        
        # if text_27 is active this frame...
        if text_27.status == STARTED:
            # update params
            pass
        
        # if text_27 is stopping this frame...
        if text_27.status == STARTED:
            # is it time to stop? (based on global clock, using actual start)
            if tThisFlipGlobal > text_27.tStartRefresh + 3-frameTolerance:
                # keep track of stop time/frame for later
                text_27.tStop = t  # not accounting for scr refresh
                text_27.tStopRefresh = tThisFlipGlobal  # on global time
                text_27.frameNStop = frameN  # exact frame index
                # add timestamp to datafile
                thisExp.timestampOnFlip(win, 'text_27.stopped')
                # update status
                text_27.status = FINISHED
                text_27.setAutoDraw(False)
        
        # check for quit (typically the Esc key)
        if defaultKeyboard.getKeys(keyList=["escape"]):
            thisExp.status = FINISHED
        if thisExp.status == FINISHED or endExpNow:
            endExperiment(thisExp, win=win)
            return
        # pause experiment here if requested
        if thisExp.status == PAUSED:
            pauseExperiment(
                thisExp=thisExp, 
                win=win, 
                timers=[routineTimer, globalClock], 
                currentRoutine=Thanks,
            )
            # skip the frame we paused on
            continue
        
        # has a Component requested the Routine to end?
        if not continueRoutine:
            Thanks.forceEnded = routineForceEnded = True
        # has the Routine been forcibly ended?
        if Thanks.forceEnded or routineForceEnded:
            break
        # has every Component finished?
        continueRoutine = False
        for thisComponent in Thanks.components:
            if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                continueRoutine = True
                break  # at least one component has not yet finished
        
        # refresh the screen
        if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
            win.flip()
    
    # --- Ending Routine "Thanks" ---
    for thisComponent in Thanks.components:
        if hasattr(thisComponent, "setAutoDraw"):
            thisComponent.setAutoDraw(False)
    # store stop times for Thanks
    Thanks.tStop = globalClock.getTime(format='float')
    Thanks.tStopRefresh = tThisFlipGlobal
    thisExp.addData('Thanks.stopped', Thanks.tStop)
    # using non-slip timing so subtract the expected duration of this Routine (unless ended on request)
    if Thanks.maxDurationReached:
        routineTimer.addTime(-Thanks.maxDuration)
    elif Thanks.forceEnded:
        routineTimer.reset()
    else:
        routineTimer.addTime(-3.000000)
    thisExp.nextEntry()
    # Run 'End Experiment' code from code_2
    port.close();
    
    # Run 'End Experiment' code from code
    port.close();
    
    # mark experiment as finished
    endExperiment(thisExp, win=win)


def saveData(thisExp):
    """
    Save data from this experiment
    
    Parameters
    ==========
    thisExp : psychopy.data.ExperimentHandler
        Handler object for this experiment, contains the data to save and information about 
        where to save it to.
    """
    filename = thisExp.dataFileName
    # these shouldn't be strictly necessary (should auto-save)
    thisExp.saveAsWideText(filename + '.csv', delim='auto')
    thisExp.saveAsPickle(filename)


def endExperiment(thisExp, win=None):
    """
    End this experiment, performing final shut down operations.
    
    This function does NOT close the window or end the Python process - use `quit` for this.
    
    Parameters
    ==========
    thisExp : psychopy.data.ExperimentHandler
        Handler object for this experiment, contains the data to save and information about 
        where to save it to.
    win : psychopy.visual.Window
        Window for this experiment.
    """
    # stop any playback components
    if thisExp.currentRoutine is not None:
        for comp in thisExp.currentRoutine.getPlaybackComponents():
            comp.stop()
    if win is not None:
        # remove autodraw from all current components
        win.clearAutoDraw()
        # Flip one final time so any remaining win.callOnFlip() 
        # and win.timeOnFlip() tasks get executed
        win.flip()
    # return console logger level to WARNING
    logging.console.setLevel(logging.WARNING)
    # mark experiment handler as finished
    thisExp.status = FINISHED
    # run any 'at exit' functions
    for fcn in runAtExit:
        fcn()
    logging.flush()


def quit(thisExp, win=None, thisSession=None):
    """
    Fully quit, closing the window and ending the Python process.
    
    Parameters
    ==========
    win : psychopy.visual.Window
        Window to close.
    thisSession : psychopy.session.Session or None
        Handle of the Session object this experiment is being run from, if any.
    """
    thisExp.abort()  # or data files will save again on exit
    # make sure everything is closed down
    if win is not None:
        # Flip one final time so any remaining win.callOnFlip() 
        # and win.timeOnFlip() tasks get executed before quitting
        win.flip()
        win.close()
    logging.flush()
    if thisSession is not None:
        thisSession.stop()
    # terminate Python process
    core.quit()


# if running this experiment as a script...
if __name__ == '__main__':
    # call all functions in order
    expInfo = showExpInfoDlg(expInfo=expInfo)
    thisExp = setupData(expInfo=expInfo)
    logFile = setupLogging(filename=thisExp.dataFileName)
    win = setupWindow(expInfo=expInfo)
    setupDevices(expInfo=expInfo, thisExp=thisExp, win=win)
    run(
        expInfo=expInfo, 
        thisExp=thisExp, 
        win=win,
        globalClock='float'
    )
    saveData(thisExp=thisExp)
    quit(thisExp=thisExp, win=win)
