from psychopy import gui

dlg_title = "Sylaba"
dlg_prompt = "Proszę napisz sylabę najbliższą do tej która wymówiona była na nagraniu"
sylaba = ''
dlg = gui.Dlg(dlg_title)
dlg.addText(dlg_prompt)
dlg.addField('sylaba')
while True:
    # show dialog and wait for OK or Cancel
    ok_data = dlg.show()
    if dlg.OK:  # if ok_data is not None
        sylaba = ok_data['sylaba']
        print('EDF data filename: {}'.format(sylaba))
        break
    else:
        print('user cancelled')
        core.quit()
        sys.exit()