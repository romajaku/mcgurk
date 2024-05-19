from psychopy.visual import Window, MovieStim3
from psychopy.constants import STOPPED, PLAYING

# create the window and stimulus object
w = Window(screen=0, size=[1280,720], units='pix')
f = r'C:\Users\EAPL2\Desktop\eyelink_exemplary_software\videos\Bo_Go.mp4'
mov = MovieStim3(w, f) 
while(mov.status is not STOPPED):
    # draw movie frames
    mov.draw()
    win.flip()
    # check if a new frame is on screen and log a VFRAME message
    current_frame_timestamp = mov.getCurrentFrameTime()
    if current_frame_timestamp != previous_frame_timestamp:
        frame_num += 1
        time_offset = -1 * int(current_frame_timestamp*1000)
        previous_frame_timestamp = current_frame_timestamp
#play the movie
#s.play() # this call returns but nothing  happens
