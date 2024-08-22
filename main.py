import pygame
import pyaudio
import wave
import numpy
import librosa
from pygame_render import RenderEngine

pygame.init()

# set constants (this is fullscreen for me)
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080

CHUNK = 1024 # how much audio data is read at a time by the audio playback
RATE = 44100 # sampling rate of the audio file (not sure what happens if you try to read an audio file with a different sampling rate)

# initialize render engine
engine = RenderEngine(SCREEN_WIDTH, SCREEN_HEIGHT)
shader_visualizer = engine.load_shader_from_path('vertex.glsl', 'fragment.glsl')
layer = engine.make_layer(size=(SCREEN_WIDTH, SCREEN_HEIGHT), components=4) # create an empty texture to feed into the shader later
pygame.display.toggle_fullscreen()

# initialize audio stream
wf = wave.open('audiofile.wav', 'rb') # this is where you load your .wav audio file
p = pyaudio.PyAudio()

stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                channels=wf.getnchannels(),
                rate=wf.getframerate(),
                output=True)

# fourier analysis (constant-q tranform)
def fourier_analysis_cqt(data):
    data = data.reshape(-1, 2) # separate stereo audio into left and right channel
    left_channel = data[:, 0] # only use the left channel moving forward
    left_channel = numpy.array(left_channel, dtype=float)
    # constant q-tranform (as far as I understand, it is basically a fourier analysis with higher resolution at lower frequencies, mimicking human logarithmic pitch perception)
    spectrum = librosa.cqt(left_channel, sr = 44100, n_bins = 64)
    return abs(spectrum)

data = numpy.frombuffer(wf.readframes(wf.getnframes()), dtype=numpy.int16)
amplitude = fourier_analysis_cqt(data)
amplitude = librosa.amplitude_to_db(amplitude) # convert amplitude to decibel to mimick human loudness perception (librosa is a blessing)

wf.rewind() # we have to rewind to be able to read the audio file again and feed it to the audio stream
data_chunk = wf.readframes(CHUNK)

current_frame = 0

run = True
while run:
    
    engine.clear() # clears the screen

    # audio playback
    if len(data_chunk) > 0:
        stream.write(data_chunk)
        data_chunk = wf.readframes(CHUNK)
    else:
        stream.stop_stream()
        stream.close()

    # visual rendering
    current_frame = wf.tell() * 86 // 44100 # this variable tells us where we are within the audio playback, allowing us to sync the visualizer to it

    amplitude_frame = amplitude[:, current_frame]
    amplitude_array = numpy.array(amplitude_frame, dtype=numpy.float32) # this array contains 64 amplitude values, each representing a small frequency range at the current frame

    shader_visualizer['u_amplitude'] = amplitude_array # feed amplitude array into shader
    engine.render(layer.texture, engine.screen, shader=shader_visualizer) # apply the shader to our empty texture and then render it onto the screen

    # event handler
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.display.toggle_fullscreen() # you can press escape to toggle between fullscreen and windowed mode
        if event.type == pygame.QUIT:
            run = False

    pygame.display.flip() # updates the screen

p.terminate()
pygame.quit()