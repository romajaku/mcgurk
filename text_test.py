from psychopy import visual, core, event, monitors, gui, data

mon = monitors.Monitor('myMonitor', width=53.0, distance=70.0)

win = visual.Window(fullscr=True,
                    monitor=mon,
                    winType='pyglet',
                    units='pix',
                    size = [1920, 1080],
                    color = (0.1954, 0.1954, 0.1954))
            
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
    
print(stim.text)