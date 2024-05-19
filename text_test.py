from psychopy import visual, core, event, monitors, gui, data

mon = monitors.Monitor('myMonitor', width=53.0, distance=70.0)

win = visual.Window(fullscr=True,
                    monitor=mon,
                    winType='pyglet',
                    units='pix',
                    size = [1920, 1080],
                    color = (0.1954, 0.1954, 0.1954))
            
stim = visual.TextStim(win = win, text = "Jaka sylaba wariacie?", color = '#FFFFFF')
#box = visual.Rect(win, height = 600, width = 600, color = '#000000')
text=""
#win.flip()
#box.draw()
stim.draw()
while True:
    key = event.waitKeys()[0]
    if key == 'return':
        break
    elif key == 'backspace':
        text = text[:-1] 
    else:
        text += key
    # Update textbox
    stim.text = text
    win.flip()
    #box.draw()
    stim.draw()
    
print(stim.text)