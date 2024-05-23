#
# Copyright (c) 1996-2021, SR Research Ltd., All Rights Reserved
#
# For use by SR Research licencees only. Redistribution and use in source
# and binary forms, with or without modification, are NOT permitted.
#
# Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in
# the documentation and/or other materials provided with the distribution.
#
# Neither name of SR Research Ltd nor the name of contributors may be used
# to endorse or promote products derived from this software without
# specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS ``AS
# IS'' AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
# TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
# PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE REGENTS OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# DESCRIPTION:
# This is a basic example, which shows how connect to and disconnect from
# the tracker, how to open and close data file, how to start/stop recording,
# and the standard messages for integration with the Data Viewer software.
# Four pictures will be shown one-by-one and each trial terminates upon a
# keypress response (the spacebar) or until 3 secs have elapsed.

# Last updated: 3/29/2021

from __future__ import division
from __future__ import print_function

import pylink
import os
import platform
import random
import time
import sys
import csv 
from EyeLinkCoreGraphicsPsychoPy import EyeLinkCoreGraphicsPsychoPy
from psychopy import visual, core, event, monitors, gui, data
from PIL import Image  # for preparing the Host backdrop image
from psychopy.constants import STOPPED, PLAYING
from string import ascii_letters, digits

import numpy as np  # whole numpy lib is available, prepend 'np.'
from numpy import (sin, cos, tan, log, log10, pi, average,
                   sqrt, std, deg2rad, rad2deg, linspace, asarray)
from numpy.random import random, randint, normal, shuffle, choice as randchoice

# Switch to the script folder
script_path = os.path.dirname(sys.argv[0])
if len(script_path) != 0:
    os.chdir(script_path)

# Show only critical log message in the PsychoPy console
from psychopy import logging
logging.console.setLevel(logging.CRITICAL)

# Set this variable to True if you use the built-in retina screen as your
# primary display device on macOS. If have an external monitor, set this
# variable True if you choose to "Optimize for Built-in Retina Display"
# in the Displays preference settings.
use_retina = False

# Set this variable to True to run the script in "Dummy Mode"
dummy_mode = True

# Set this variable to True to run the task in full screen mode
# It is easier to debug the script in non-fullscreen mode
full_screen = True

# creates nested dictionary of all conditions
dir_path = os.path.dirname(os.path.realpath(__file__))
trials = data.importConditions(os.path.join(dir_path, r'listy_naglowki', 'trials.csv'))

#shuffle trials
shuffle(trials)

# Set up EDF data file name and local data folder
#
# The EDF data filename should not exceed 8 alphanumeric characters
# use ONLY number 0-9, letters, & _ (underscore) in the filename
edf_fname = 'TEST'

# Prompt user to specify an EDF data filename
# before we open a fullscreen window
dlg_title = 'Enter EDF File Name'
dlg_prompt = 'Please enter a file name with 8 or fewer characters\n' + \
             '[letters, numbers, and underscore].'

# loop until we get a valid filename
while True:
    dlg = gui.Dlg(dlg_title)
    dlg.addText(dlg_prompt)
    dlg.addField('File Name:', edf_fname)
    # show dialog and wait for OK or Cancel
    ok_data = dlg.show()
    if dlg.OK:  # if ok_data is not None
        print('EDF data filename: {}'.format(ok_data))
    else:
        print('user cancelled')
        core.quit()
        sys.exit()

    # get the string entered by the experimenter
    tmp_str = dlg.data[0]
    # strip trailing characters, ignore the ".edf" extension
    edf_fname = tmp_str.rstrip().split('.')[0]

    # check if the filename is valid (length <= 8 & no special char)
    allowed_char = ascii_letters + digits + '_'
    if not all([c in allowed_char for c in edf_fname]):
        print('ERROR: Invalid EDF filename')
    elif len(edf_fname) > 8:
        print('ERROR: EDF filename should not exceed 8 characters')
    else:
        break

# Set up a folder to store the EDF data files and the associated resources
# e.g., files defining the interest areas used in each trial
results_folder = 'results'
if not os.path.exists(results_folder):
    os.makedirs(results_folder)

# We download EDF data file from the EyeLink Host PC to the local hard
# drive at the end of each testing session, here we rename the EDF to
# include session start date/time
time_str = time.strftime("_%Y_%m_%d_%H_%M", time.localtime())
session_identifier = edf_fname + time_str

# create a folder for the current testing session in the "results" folder
session_folder = os.path.join(results_folder, session_identifier)
if not os.path.exists(session_folder):
    os.makedirs(session_folder)

# Step 1: Connect to the EyeLink Host PC
#
# The Host IP address, by default, is "100.1.1.1".
# the "el_tracker" objected created here can be accessed through the Pylink
# Set the Host PC address to "None" (without quotes) to run the script
# in "Dummy Mode"
if dummy_mode:
    el_tracker = pylink.EyeLink(None)
else:
    try:
        el_tracker = pylink.EyeLink("100.1.1.1")
    except RuntimeError as error:
        print('ERROR:', error)
        core.quit()
        sys.exit()

# Step 2: Open an EDF data file on the Host PC
edf_file = edf_fname + ".EDF"
try:
    el_tracker.openDataFile(edf_file)
except RuntimeError as err:
    print('ERROR:', err)
    # close the link if we have one open
    if el_tracker.isConnected():
        el_tracker.close()
    core.quit()
    sys.exit()

# Add a header text to the EDF file to identify the current experiment name
# This is OPTIONAL. If your text starts with "RECORDED BY " it will be
# available in DataViewer's Inspector window by clicking
# the EDF session node in the top panel and looking for the "Recorded By:"
# field in the bottom panel of the Inspector.
preamble_text = 'RECORDED BY %s' % os.path.basename(__file__)
el_tracker.sendCommand("add_file_preamble_text '%s'" % preamble_text)

# Step 3: Configure the tracker
#
# Put the tracker in offline mode before we change tracking parameters
el_tracker.setOfflineMode()

# Get the software version:  1-EyeLink I, 2-EyeLink II, 3/4-EyeLink 1000,
# 5-EyeLink 1000 Plus, 6-Portable DUO
eyelink_ver = 0  # set version to 0, in case running in Dummy mode
if not dummy_mode:
    vstr = el_tracker.getTrackerVersionString()
    eyelink_ver = int(vstr.split()[-1].split('.')[0])
    # print out some version info in the shell
    print('Running experiment on %s, version %d' % (vstr, eyelink_ver))

# File and Link data control
# what eye events to save in the EDF file, include everything by default
file_event_flags = 'LEFT,RIGHT,FIXATION,SACCADE,BLINK,MESSAGE,BUTTON,INPUT'
# what eye events to make available over the link, include everything by default
link_event_flags = 'LEFT,RIGHT,FIXATION,SACCADE,BLINK,BUTTON,FIXUPDATE,INPUT'
# what sample data to save in the EDF data file and to make available
# over the link, include the 'HTARGET' flag to save head target sticker
# data for supported eye trackers
if eyelink_ver > 3:
    file_sample_flags = 'LEFT,RIGHT,GAZE,HREF,RAW,AREA,HTARGET,GAZERES,BUTTON,STATUS,INPUT'
    link_sample_flags = 'LEFT,RIGHT,GAZE,GAZERES,AREA,HTARGET,STATUS,INPUT'
else:
    file_sample_flags = 'LEFT,RIGHT,GAZE,HREF,RAW,AREA,GAZERES,BUTTON,STATUS,INPUT'
    link_sample_flags = 'LEFT,RIGHT,GAZE,GAZERES,AREA,STATUS,INPUT'
el_tracker.sendCommand("file_event_filter = %s" % file_event_flags)
el_tracker.sendCommand("file_sample_data = %s" % file_sample_flags)
el_tracker.sendCommand("link_event_filter = %s" % link_event_flags)
el_tracker.sendCommand("link_sample_data = %s" % link_sample_flags)

# Optional tracking parameters
# Sample rate, 250, 500, 1000, or 2000, check your tracker specification
# if eyelink_ver > 2:
#     el_tracker.sendCommand("sample_rate 1000")
# Choose a calibration type, H3, HV3, HV5, HV13 (HV = horizontal/vertical),
el_tracker.sendCommand("calibration_type = HV9")
# Set a gamepad button to accept calibration/drift check target
# You need a supported gamepad/button box that is connected to the Host PC
el_tracker.sendCommand("button_function 5 'accept_target_fixation'")

# Step 4: set up a graphics environment for calibration
#
# Open a window, be sure to specify monitor parameters
mon = monitors.Monitor('myMonitor', width=53.0, distance=70.0)
win = visual.Window(fullscr=full_screen,
                    monitor=mon,
                    winType='pyglet',
                    units='pix',
                    size = [1920, 1080],
                    color = (0.1954, 0.1954, 0.1954))

# get the native screen resolution used by PsychoPy
scn_width, scn_height = win.size
# resolution fix for Mac retina displays
if 'Darwin' in platform.system():
    if use_retina:
        scn_width = int(scn_width/2.0)
        scn_height = int(scn_height/2.0)

# Pass the display pixel coordinates (left, top, right, bottom) to the tracker
# see the EyeLink Installation Guide, "Customizing Screen Settings"
el_coords = "screen_pixel_coords = 0 0 %d %d" % (scn_width - 1, scn_height - 1)
el_tracker.sendCommand(el_coords)

# Write a DISPLAY_COORDS message to the EDF file
# Data Viewer needs this piece of info for proper visualization, see Data
# Viewer User Manual, "Protocol for EyeLink Data to Viewer Integration"
dv_coords = "DISPLAY_COORDS  0 0 %d %d" % (scn_width - 1, scn_height - 1)
el_tracker.sendMessage(dv_coords)

# Configure a graphics environment (genv) for tracker calibration
genv = EyeLinkCoreGraphicsPsychoPy(el_tracker, win)
print(genv)  # print out the version number of the CoreGraphics library

# Set background and foreground colors for the calibration target
# in PsychoPy, (-1, -1, -1)=black, (1, 1, 1)=white, (0, 0, 0)=mid-gray
foreground_color = (-1, -1, -1)
background_color = win.color
genv.setCalibrationColors(foreground_color, background_color)


genv.setCalibrationSounds('', '', '')


# Request Pylink to use the PsychoPy window we opened above for calibration
pylink.openGraphicsEx(genv)


# define a few helper functions for trial handling


def clear_screen(win):
    """ clear up the PsychoPy window"""
    win.fillColor = genv.getBackgroundColor()
    win.flip()


def show_msg(win, text, wait_for_keypress=True):
    """ Show task instructions on screen"""
    msg = visual.TextStim(win, text,
                          color=genv.getForegroundColor(),
                          wrapWidth=scn_width/2)
    clear_screen(win)
    msg.draw()
    win.flip()
    # wait indefinitely, terminates upon any key press
    if wait_for_keypress:
        event.waitKeys()
        clear_screen(win)


def terminate_task():
    """ Terminate the task gracefully and retrieve the EDF data file

    file_to_retrieve: The EDF on the Host that we would like to download
    win: the current window used by the experimental script
    """

    el_tracker = pylink.getEYELINK()

    if el_tracker.isConnected():
        # Terminate the current trial first if the task terminated prematurely
        error = el_tracker.isRecording()
        if error == pylink.TRIAL_OK:
            abort_trial()

        # Put tracker in Offline mode
        el_tracker.setOfflineMode()

        # Clear the Host PC screen and wait for 500 ms
        el_tracker.sendCommand('clear_screen 0')
        pylink.msecDelay(500)

        # Close the edf data file on the Host
        el_tracker.closeDataFile()

        # Show a file transfer message on the screen
        msg = 'EDF data is transferring from EyeLink Host PC...'
        show_msg(win, msg, wait_for_keypress=False)

        # Download the EDF data file from the Host PC to a local data folder
        # parameters: source_file_on_the_host, destination_file_on_local_drive
        local_edf = os.path.join(session_folder, session_identifier + '.EDF')
        try:
            el_tracker.receiveDataFile(edf_file, local_edf)
        except RuntimeError as error:
            print('ERROR:', error)

        # Close the link to the tracker.
        el_tracker.close()

    # close the PsychoPy window
    win.close()

    # quit PsychoPy
    core.quit()
    sys.exit()


def abort_trial():
    """Ends recording """

    el_tracker = pylink.getEYELINK()

    # Stop recording
    if el_tracker.isRecording():
        # add 100 ms to catch final trial events
        pylink.pumpDelay(100)
        el_tracker.stopRecording()

    # clear the screen
    clear_screen(win)
    # Send a message to clear the Data Viewer screen
    bgcolor_RGB = (116, 116, 116)
    el_tracker.sendMessage('!V CLEAR %d %d %d' % bgcolor_RGB)

    # send a message to mark trial end
    el_tracker.sendMessage('TRIAL_RESULT %d' % pylink.TRIAL_ERROR)

    return pylink.TRIAL_ERROR


def run_trial(trials, trial_index):
    """ Helper function specifying the events that will occur in a single trial
    trial_index - record the order of trial presentation in the task
    """
    print("running trial")
    mov = visual.MovieStim3(
        win = win, 
        filename=os.path.join('videos', trials[trial_index]['file']),
        volume = 100)
        
    print("mov created")
    # dimension of the video
    vid_w, vid_h = mov.size
    
    # background color of the video
    bgcolor_RGB = (116, 116, 116)

    text_krzyzyk = visual.TextStim(win=win, name='text_krzyzyk',
        text='+',
        font='Arial',
        pos=(0, -103), height=60, wrapWidth=None, ori=0.0, 
        color='white', colorSpace='rgb', opacity=None, 
        languageStyle='LTR',
        depth=0.0);


    tlo = visual.GratingStim(
        win=win, name='tlo',
        tex=None, mask=None,
        ori=0.0, pos=(0, 0), size=(2000, 2000), sf=None, phase=0.0,
        color=[0.0351, 0.2336, 0.2404], colorSpace='rgb',
        opacity=None, contrast=1.0, blendmode='avg',
        texRes=128.0, interpolate=True, depth=-1.0)

    print("krzyz i tlo created")
    # get a reference to the currently active EyeLink connection
    el_tracker = pylink.getEYELINK()

    # put the tracker in the offline mode first
    el_tracker.setOfflineMode()

    # clear the host screen before we draw the backdrop
    el_tracker.sendCommand('clear_screen 0')

    # send a "TRIALID" message to mark the start of a trial, see Data
    # Viewer User Manual, "Protocol for EyeLink Data to Viewer Integration"
    el_tracker.sendMessage('TRIALID %d' % trial_index)
    el_tracker.sendMessage("The phoneme is: " + trials[trial_index]['phoneme'])
    el_tracker.sendMessage("The visime is: " + trials[trial_index]['visime'])

    # record_status_message : show some info on the Host PC
    # here we show how many trial has been tested
    status_msg = 'TRIAL number %d' % trial_index
    el_tracker.sendCommand("record_status_message '%s'" % status_msg)

    # Skip drift-check if running the script in Dummy Mode
    while not dummy_mode:
        # terminate the task if no longer connected to the tracker or
        # user pressed Ctrl-C to terminate the task
        if (not el_tracker.isConnected()) or el_tracker.breakPressed():
            terminate_task()
            return pylink.ABORT_EXPT

        # drift-check and re-do camera setup if ESCAPE is pressed
        try:
            error = el_tracker.doDriftCorrect(int(scn_width/2.0),
                                              int(643), 1, 1)
            # break following a success drift-check
            if error is not pylink.ESC_KEY:
                break
        except:
            pass

    # put tracker in idle/offline mode before recording
    el_tracker.setOfflineMode()


    # Start recording
    # arguments: sample_to_file, events_to_file, sample_over_link,
    # event_over_link (1-yes, 0-no)
    try:
        el_tracker.startRecording(1, 1, 1, 1)
    except RuntimeError as error:
        print("ERROR:", error)
        abort_trial()
        return pylink.TRIAL_ERROR
    

    # Allocate some time for the tracker to cache some samples
    pylink.pumpDelay(100)
    print("po eyetrackin business")
    # show fixation cross before the image
    tlo.draw()
    text_krzyzyk.draw()  
    win.flip()
    fix_cross_time2 = core.getTime()
    el_tracker.sendMessage('fix_cross2_onset')
    # present the cross for a given time
    event.clearEvents()  # clear cached PsychoPy events
    time_out = False
    while not time_out:
        # present the cross for 1 s
        if core.getTime() - fix_cross_time2 >= 1:
        #if core.getTime() - fix_cross_time2 >= 0.1:
            el_tracker.sendMessage('fix_cross2_offset')
            break
            
    pylink.pumpDelay(100)

    # show the video, and log a message to mark the onset of the video
    print("clock stuff")
    clear_screen(win)
    tlo.draw()
    
    frame_num = 0
    mov_clock = core.Clock()
    mov_clock.reset()
    previous_frame_timestamp = mov.getCurrentFrameTime()
    el_tracker.sendMessage('Video stimulus onset')
    
    # Okay dotąd jest raczej okay -  tu video playbackd
    print("bd filmik")
    while (mov.status is not STOPPED):
        error = el_tracker.isRecording()
        if error is not pylink.TRIAL_OK:
            el_tracker.sendMessage('tracker_disconnected')
            abort_trial()
            return error
        # check for keyboard events
        for keycode, modifier in event.getKeys(modifiers=True):
            # Abort a trial if "ESCAPE" is pressed
            if keycode == 'escape':
                el_tracker.sendMessage('trial_skipped_by_user')
                # clear the screen
                win.flip()
                # abort trial
                abort_trial()
                return pylink.SKIP_TRIAL
            # Terminate the task if Ctrl-c
            if keycode == 'c' and (modifier['ctrl'] is True):
                el_tracker.sendMessage('terminated_by_user')
                terminate_task()
                return pylink.ABORT_EXPT
        # draw movie frames
        mov.draw()
        win.flip()
            
    # record the duration of the video
    vid_duration = int(mov_clock.getTime()*1000)
    print("Był filmik")
    el_tracker.sendMessage('Video stimulus end')
    el_tracker.sendMessage('Video length: {}'.format(vid_duration))
    # clear the screen
    clear_screen(win)
    el_tracker.sendMessage('blank_screen')


    win.flip()
    el_tracker.stopRecording()
    
    # Get participant input with dialogue box
    print("bd pytanie")
    stim = visual.TextStim(win = win, text = "Jaka sylaba wariacie?", color = '#000000')
    box = visual.Rect(win, height = 50, width = 200, color = '#FFFFFF')
    text=""
    stim.draw()
    box.draw()
    win.flip()
    while True:
        key = event.waitKeys()[0]
        if key == 'return':
            break
        elif key == 'backspace':
            text = text[:-1] 
        elif key.isalpha() and len(key)==1:
            text += key
        stim.text = text
        box.draw()
        stim.draw()
        win.flip()
    
    sylaba = stim.text
    print("było pytanie")
    # record trial variables to the EDF data file, for details, see Data
    # Viewer User Manual, "Protocol for EyeLink Data to Viewer Integration"
    el_tracker.sendMessage('!V TRIAL_VAR condition %s' % trials[trial_index]['syllable'])
    el_tracker.sendMessage('Participant reported syllable: ' + stim.text)


    # send a 'TRIAL_RESULT' message to mark the end of trial, see Data
    # Viewer User Manual, "Protocol for EyeLink Data to Viewer Integration"
    el_tracker.sendMessage('TRIAL_RESULT %d' % pylink.TRIAL_OK)

    stimulus = trials[trial_index]['syllable']
    fields=[trial_index,stimulus,sylaba]
    results.append(fields)




## step 5a: pre-calibration instructions

# Initialize components for Routine "welcome"
text_1 = visual.TextStim(win=win, name='text_2',
    text='W tym zadaniu zobaczysz filmiki z osobą wypowiadającą sylabę,'
        +'\nktóre będą pojawiać się pojedynczo na ekranie.'
        + '\n\nTwoim zadaniem będzie napisanie, jaką sylabę wymówiła osoba. '
        + '\n\n\nW sumie zobaczysz 54 filmiki. Całość zadania zajmie ok. 10 minut.'
        + '\n\n\n\nNaciśnij SPACJĘ, aby przejść dalej. ',
    font='Arial',
    pos=(0, 0), height=30, wrapWidth=scn_width/2, ori=0.0, 
    color='black', colorSpace='rgb', opacity=None, 
    languageStyle='LTR',
    depth=0.0);
text_1.draw()  
win.flip()
# show the text until the SPACEBAR is pressed
event.clearEvents()  # clear cached PsychoPy events
get_keypress = False
while not get_keypress:
# check keyboard events
    for keycode, modifier in event.getKeys(modifiers=True):
        # Stop stimulus presentation when the spacebar is pressed
        if keycode == 'space':
            get_keypress = True
            
text_2 = visual.TextStim(win=win, name='text_2',
    text='Sylabę, która wymówiła osoba, będziesz zapisywać przy pomocy klawiatury.'
        +'\nNaciśnij SPACJĘ, aby przejść dalej. ',
    font='Arial',
    pos=(0, 0), height=30, wrapWidth=scn_width/2, ori=0.0, 
    color='black', colorSpace='rgb', opacity=None, 
    languageStyle='LTR',
    depth=0.0);
text_2.draw()  
win.flip()
# show the text until the SPACEBAR is pressed
event.clearEvents()  # clear cached PsychoPy events
get_keypress = False
while not get_keypress:
# check keyboard events
    for keycode, modifier in event.getKeys(modifiers=True):
        # Stop stimulus presentation when the spacebar is pressed
        if keycode == 'space':
            get_keypress = True
            

text_3 = visual.TextStim(win=win, name='text_2',
    text='Podczas zadania będziemy zbierać dane o przy pomocy okulografu.'
        + '\nW związku z tym ważne jest, aby nie poruszyć głową w trakcie całości trwania zadania.'
        + '\n\nUważaj na to no zwłaszcza podczas pisania. Pomiędzy filmikami utrzymuj wzrok na krzyżyku na środku ekranu.'
        +'\n\n\nNaciśnij SPACJĘ, aby przejść dalej. ',
    font='Arial',
    pos=(0, 0), height=30, wrapWidth=scn_width/2, ori=0.0, 
    color='black', colorSpace='rgb', opacity=None, 
    languageStyle='LTR',
    depth=0.0);
text_3.draw()  
win.flip()
# show the text until the SPACEBAR is pressed
event.clearEvents()  # clear cached PsychoPy events
get_keypress = False
while not get_keypress:
# check keyboard events
    for keycode, modifier in event.getKeys(modifiers=True):
        # Stop stimulus presentation when the spacebar is pressed
        if keycode == 'space':
            get_keypress = True
            
text_3 = visual.TextStim(win=win, name='text_2',
    text='Podczas zadania będziemy zbierać dane o przy pomocy okulografu.'
        + '\nW związku z tym ważne jest, aby nie poruszyć głową w trakcie całości trwania zadania.'
        + '\n\nUważaj na to no zwłaszcza podczas pisania. Pomiędzy filmikami utrzymuj wzrok na krzyżyku na środku ekranu.'
        +'\n\n\nNaciśnij SPACJĘ, aby przejść dalej. ',
    font='Arial',
    pos=(0, 0), height=30, wrapWidth=scn_width/2, ori=0.0, 
    color='black', colorSpace='rgb', opacity=None, 
    languageStyle='LTR',
    depth=0.0);
text_3.draw()  
win.flip()
# show the text until the SPACEBAR is pressed
event.clearEvents()  # clear cached PsychoPy events
get_keypress = False
while not get_keypress:
# check keyboard events
    for keycode, modifier in event.getKeys(modifiers=True):
        # Stop stimulus presentation when the spacebar is pressed
        if keycode == 'space':
            get_keypress = True
            
text_4 = visual.TextStim(win=win, name='text_2',
    text='Pamiętaj: Zapisuj sylabę, jaką wymówiła osoba na filmiku.'
        + '\nOdpowiadaj od razu po zniknięciu filmiku, gdy pojawi się szary ekran.'
        +'\n\n\nNaciśnij SPACJĘ, aby przejść dalej. ',
    font='Arial',
    pos=(0, 0), height=30, wrapWidth=scn_width/2, ori=0.0, 
    color='black', colorSpace='rgb', opacity=None, 
    languageStyle='LTR',
    depth=0.0);
text_4.draw()  
win.flip()
# show the text until the SPACEBAR is pressed
event.clearEvents()  # clear cached PsychoPy events
get_keypress = False
while not get_keypress:
# check keyboard events
    for keycode, modifier in event.getKeys(modifiers=True):
        # Stop stimulus presentation when the spacebar is pressed
        if keycode == 'space':
            get_keypress = True

## Step 5: Set up the camera and calibrate the tracker

# skip this step if running the script in Dummy Mode
if not dummy_mode:
    try:
        win.flip()
        el_tracker.doTrackerSetup()
    except RuntimeError as err:
        print('ERROR:', err)
        el_tracker.exitCalibration()

## Step 6: Run the experimental trials, index all the trials
results = []
trial_index = 0
for x in range(len(trials)-1):
    print("petla trials")
    trial_index += 1
    run_trial(trials, trial_index, results)
    print("po run")
   

with open(r'C:\Users\EAPL2\Desktop\mcGurk\results\{}.csv'.format(session_identifier), 'w-+', newline='') as f:
    writer = csv.writer(f)
    writer.writerows(a)


text_koniec = visual.TextStim(win=win, name='text_koniec',
    text='Dziękujemy, to już koniec badania. \n\n\n\nNaciśnij spację, aby zakończyć',
    font='Arial',
    pos=(0, 0), height=30, wrapWidth=None, ori=0.0, 
    color='black', colorSpace='rgb', opacity=None, 
    languageStyle='LTR',
    depth=0.0);

text_koniec.draw()  
win.flip()
# show the text until the SPACEBAR is pressed
event.clearEvents()  # clear cached PsychoPy events
get_keypress = False
while not get_keypress:
# check keyboard events
    for keycode, modifier in event.getKeys(modifiers=True):
        # Stop stimulus presentation when the spacebar is pressed
        if keycode == 'space':
            get_keypress = True


# Step 7: disconnect, download the EDF file, then terminate the task
terminate_task()
