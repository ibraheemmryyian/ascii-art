import soundcard as sc
import numpy as np

def test():
    spk = sc.default_speaker()
    print("Speaker:", spk.name)
    m = sc.get_microphone(id=str(spk.name), include_loopback=True)
    print("Mic:", m.name)
    with m.recorder(samplerate=44100) as mic:
        data = mic.record(numframes=1024)
        print("Data shape:", data.shape)
        print("Max amp:", np.max(np.abs(data)))

if __name__ == "__main__":
    test()
