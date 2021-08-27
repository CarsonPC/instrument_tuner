import sounddevice as sd
import numpy as np
import tkinter as tk
import time

#sounddevice initialization
#sampling freq 48000 Hz
fs = 48000
sd.default.samplerate = fs
sd.default.channels = 1
sd.default.dtype = 'int32'
maxarg = 2**32-1
#data is array that holds sound 
data = np.array([])

#Tkinter initialization
animation_window_width = 1000
animation_window_height = 600
animation_refresh_seconds = 0.01


#window init
def create_animation_window():
    window = tk.Tk()
    window.title("Ad-Free tuner")
    window.geometry(f'{animation_window_width}x{animation_window_height}')
    return window

#canvas on window init
def create_animation_canvas(window):
    canvas = tk.Canvas(window)
    canvas.configure(bg="black")
    canvas.pack(fill = "both", expand = True)
    return canvas

#callback is function from sounddevice for interacting with it's data
def callback(indata, outdata, frames, time, status):
    global data
    data = np.frombuffer(indata, dtype=np.int32)

#frequency conversion to note based on 440Hz = A
def get_note(myrec, freq):
    sharp = '';
    if freq:
        #ignore faint noises
        if np.amax(myrec) <= 303:
            return('X')
        n = 12*np.log2(freq/440)
        if n-np.round(n) > 0.0:
            sharp = '+'*int((n-np.floor(n))*10)       
        else:
            sharp = '-'*int((np.round(n)-n)*10)
        letters = ['A','B','C','D','E','F','G']
        return (letters[(0+int(n)) % 7] + sharp)
    
    return ('X')

#function handling text in top right
def text_update(frequency, note, canvas):
    canvas.create_text(animation_window_width * 0.8,
                                  animation_window_height * 0.1,
                                  fill="#05f",
                                  anchor = tk.CENTER,
                                  text = 'Frequency: ' + str(frequency) +
                                  '\nNote: ' + note,
                                  width = 300,
                                  font = ("Courier", 16))
    
#this normalizes data to be centered at middle of the window
#and max values between 0, animation_window_height
def normalize_dat():
    return (data/maxarg*animation_window_height/2+animation_window_height/2).astype(int)

#gets frequency from sample based on number of times it cycles
def get_freq(myrec, canvas):
    cycles = 0
    freq = 0
    #getting how many seconds in each sample so correct frequency can be found
    secpersample = len(myrec)/fs
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
    if myrec.any():
        if np.amax(myrec) <= 303:
            return(0)
    if secpersample:
        freq = int(cycles/(2*secpersample))
    return freq


#main loop
def plot_wave(window, canvas):
    
    #loops until window closed
    while True:
        canvas.delete("all")
        myrec = normalize_dat()
        freq = get_freq(myrec, canvas)
        note = get_note(myrec, freq)
        
        
        #introduces intentional lag, if you want to remove this
        #take text update function body into this spot and remove
        #canvas.after(...)
        canvas.after(50, text_update(freq, note, canvas))
        
        
        canvas.pack()
        window.update()
        
        

    
#start tkinter window
animation_window = create_animation_window()
animation_canvas = create_animation_canvas(animation_window)

#start sounddevice
stream = sd.Stream(blocksize = 0, callback = callback)
stream.start()

#start program
while stream.active:
    plot_wave(animation_window, animation_canvas)

#end program
stream.stop()



