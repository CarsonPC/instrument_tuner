import sounddevice as sd
import numpy as np
import tkinter as tk
import time

#sampling freq 48000 Hz
fs = 48000
sd.default.samplerate = fs
sd.default.channels = 1
sd.default.dtype = 'int32'
duration = 0.035 #seconds

animation_window_width = 1000
animation_window_height = 600
animation_refresh_seconds = 0.01
maxarg = 2**32-1

data = np.array([])
def create_animation_window():
    window = tk.Tk()
    window.title("Ad-Free tuner")
    window.geometry(f'{animation_window_width}x{animation_window_height}')
    return window

def create_animation_canvas(window):
    canvas = tk.Canvas(window)
    canvas.configure(bg="black")
    canvas.pack(fill = "both", expand = True)
    return canvas

def callback(indata, outdata, frames, time, status):
    global data
    data = np.frombuffer(indata, dtype=np.int32)
def freq_to_note(freq):
    sharp = '';
    if freq:
        n = 12*np.log2(freq/440)
        if n-np.floor(n) > 0:
            sharp = '+'*int((n-np.floor(n))*10)       
        else:
            sharp = '-'*int((np.floor(n)-n)*10)
        letters = ['A','B','C','D','E','F','G']
        return (letters[(0+int(n)) % 7] + sharp)
    return ('X' + sharp)

def text_update(frequency, note, canvas):
    canvas.create_text(animation_window_width * 0.8,
                                  animation_window_height * 0.1,
                                  fill="#05f",
                                  anchor = tk.CENTER,
                                  text = 'Frequency: ' + str(frequency) +
                                  '\nNote: ' + note,
                                  width = 300,
                                  font = ("Courier", 16))
    

def plot_wave(window, canvas):
    while True:

        myrec = (data/maxarg*animation_window_height/2+300).astype(int)
        secpersample = len(myrec)/fs
        canvas.delete("all")
        
        cycles = 0
        less = True
        for i in range(2,len(myrec)):
            if myrec[i] < 300 and less == False:
                less = True
                cycles+=1
            if myrec[i] >= 300 and less == True:
                less = False
                cycles+=1

            line = canvas.create_line(i-1, myrec[i-1],i,myrec[i]
                                      , fill="#00fc00", width =5)
        note = 'X'
        freq = cycles
        if secpersample:
            freq = int(cycles/(2*secpersample))
            note= freq_to_note(freq)
            if np.amax(myrec) <= 303:
                freq = 0
                note = 'X'
        #introduces intentional lag, if you want to remove this
        #take text update function body into this spot and remove
        #canvas.after(...)
        canvas.after(10, text_update(freq, note, canvas))
        
        
        canvas.pack()
        window.update()
        
        

    

animation_window = create_animation_window()
animation_canvas = create_animation_canvas(animation_window)
stream = sd.Stream(blocksize = 0, callback = callback)
stream.start()
while stream.active:
    plot_wave(animation_window, animation_canvas)

stream.stop()



