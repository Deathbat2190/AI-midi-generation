import numpy as np
from mido import MidiFile, Message, MetaMessage, MidiTrack

LOWEST_NOTE = 60  # C4
HIGHEST_NOTE = 84  # C6
INPUT_DIM = HIGHEST_NOTE - LOWEST_NOTE
OUTPUT_DIM = INPUT_DIM


def parse_midi(filename):
    midi_file = MidiFile(filename)

    resolution = midi_file.ticks_per_beat
    print(f'Resolution: {resolution}')

    total_ticks = 0

    for track in midi_file.tracks:
        track_ticks = 0
        for event in track:
            event_type = str(event.type)
            if event_type == 'note_on' or event_type == 'note_off' or event_type == 'end_of_track':
                track_ticks += event.time

            if track_ticks > total_ticks:
                total_ticks = track_ticks

    print(f'Total ticks: {total_ticks}')

    piano_roll = np.zeros((INPUT_DIM, total_ticks), dtype=int)

    notes_starts = {}
    for track in midi_file.tracks:
        total_ticks = 0
        for event in track:
            event_type = str(event.type)
            if event_type == 'note_on' and event.velocity > 0:
                total_ticks += event.time
                note_index = event.note - LOWEST_NOTE
                piano_roll[note_index][total_ticks] = 1
                notes_starts[note_index] = total_ticks
            elif event_type == 'note_off' or (event_type == 'note_on' and event.velocity == 0):
                total_ticks += event.time
                note_index = event.note - LOWEST_NOTE
                if note_index in notes_starts:
                    piano_roll[note_index][notes_starts[note_index]: total_ticks] = 1
                    del notes_starts[note_index]

    # test = np.zeros((INPUT_DIM, 32), dtype=str)
    # for j in range(0, HIGHEST_NOTE - LOWEST_NOTE):
    #     for i in range(0, 32):
    #         test[j][i] = str(piano_roll[j][i * resolution//8]
    #                          ) if piano_roll[j][i * resolution//8] == 1 else '_'

    # np.savetxt('test.txt', test, fmt='%c')


def main():
    parse_midi('test.mid')


if __name__ == "__main__":
    main()
