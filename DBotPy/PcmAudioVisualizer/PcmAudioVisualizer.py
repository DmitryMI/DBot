from matplotlib import pyplot as plt
import argparse
import os.path
import wave
import numpy
import scipy.fft

def main():
    parser = argparse.ArgumentParser(
                    prog='PcmAudioVisualizer',
                    epilog='By The Gang of Three')

    parser.add_argument("pcm_file", help="PCM audio file")
    parser.add_argument("--channels", default=1)
    args = parser.parse_args()

    if not os.path.exists(args.pcm_file):
        print(f"File {args.pcm_file} does not exist!")
        return

    with open(args.pcm_file, "rb") as fin:
        pcm_bytes = fin.read()

    '''
    with wave.open('output.wav', 'wb') as wavfile:
        wavfile.setnchannels(args.channels)
        wavfile.setsampwidth(4 // args.channels)
        wavfile.setframerate(48000)
        wavfile.writeframes(pcm_data)
    '''

    # data = pcm_to_float(pcm_data, args.channels)

    pcm_data = numpy.frombuffer(pcm_bytes, numpy.int16)

    ftrans = scipy.fft.fft(pcm_data)
    ftrans_real = [] 
    for i in ftrans:
        ftrans_real.append(abs(i.real))

    plt.subplot(211)
    plt.plot(pcm_data)
    plt.subplot(212)
    plt.plot(ftrans_real)
    plt.xlim(left=0, right=20000)
    plt.show()

if __name__ == "__main__":
    main()