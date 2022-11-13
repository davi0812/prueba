import whisper
import mysql.connector
from pyannote.audio import Pipeline
from pydub import AudioSegment
from dash import dcc, html
import re


def convert_to_wav(id, file, format):
    print("Convirtiendo a wav")
    given_audio = AudioSegment.from_file(file, format=format)
    outfile = "assets/ready/" + id + ".wav"
    given_audio.export(outfile, format="wav")
    return outfile


def millisec(timeStr):
    spl = timeStr.split(":")
    s = (int)((int(spl[0]) * 60 * 60 + int(spl[1]) * 60 + float(spl[2])) * 1000)
    return s


def do_diarization(file):
    print("Realizando diarizacion")
    pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization",
                                        use_auth_token="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")
    diarization = pipeline(file)
    for turn, _, speaker in diarization.itertracks(yield_label=True):
        print(f"start={turn.start:.1f}s stop={turn.end:.1f}s speaker_{speaker}")
    with open("diarization.txt", "w") as text_file:
        text_file.write(str(diarization))


def do_grouping():
    print("Realizando agrupamiento")
    dzs = open('diarization.txt').read().splitlines()
    groups = []
    g = []
    lastend = 0

    for d in dzs:
        if g and (g[0].split()[-1] != d.split()[-1]):  # same speaker
            groups.append(g)
            g = []

        g.append(d)

        end = re.findall('[0-9]+:[0-9]+:[0-9]+\.[0-9]+', string=d)[1]
        end = millisec(end)
        if (lastend > end):  # segment engulfed by a previous segment
            groups.append(g)
            g = []
        else:
            lastend = end
    if g:
        groups.append(g)
    print(*groups, sep='\n')
    return groups


def do_split(id, groups):
    ofile = 'assets/ready/' + id + '.wav'
    print("Realizando spit de audios")
    audio = AudioSegment.from_wav(ofile)
    gidx = -1
    positions = []
    for g in groups:
        start = re.findall('[0-9]+:[0-9]+:[0-9]+\.[0-9]+', string=g[0])[0]
        end = re.findall('[0-9]+:[0-9]+:[0-9]+\.[0-9]+', string=g[-1])[1]
        speaker = re.findall('SPEAKER_\d+', string=g[0])[0]
        positions.append(speaker)
        start = millisec(start)  # - spacermilli
        end = millisec(end)  # - spacermilli
        gidx += 1
        file = 'assets/ready/' + id + '_' + str(gidx) + '.wav'
        audio[start:end].export(file, format='wav')
    return gidx, positions


def do_transcribe(id, gidx, speakers):
    print("Realizando transcripcion")
    tfinal = []
    model = whisper.load_model("base")
    uniS = set(speakers)
    unicos = list(uniS)
    print(f"Se han encontrado {len(unicos)} speakers")
    for item in unicos:
        print(f"Nuevo nombre para {item}")
        newName = input()
        speakers = list(map(lambda x: x.replace(item, newName), speakers))
    for i in range(gidx + 1):
        file = 'assets/ready/' + id + '_' + str(i) + '.wav'
        result = model.transcribe(file)
        message = speakers[i] + ": " + result["text"]
        print(message)
        tfinal.append(html.P(message))
    return html.Div(tfinal)


