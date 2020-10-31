# from mido import MidiFile, Message, MetaMessage, MidiTrack
import pretty_midi
import glob
import pickle

def midi_to_input(midi_folder):
    input_notes = []

    for file in glob.glob(midi_folder + '/*.mid'):
        midi_file = pretty_midi.PrettyMIDI(file)
        midi_notes = midi_file.instruments[0].notes
        print(str(midi_file.estimate_tempo()))
        # # quantize to 32nd notes
        quantize_length = midi_file.tick_to_time(midi_file.resolution / 8)
        print(quantize_length)

        notes = []
        notes_start = 0
        notes_end = 10000000
        i = 0
        midi_notes.sort(key=lambda note: note.start)
        for note in midi_notes:
            # print(note)
            i += 1
            if len(notes) == 0 or note.start == notes_start:
                notes.append(note)
                notes_start = note.start
                notes_end = note.end if note.end < notes_end else notes_end
            elif note.start != notes_start:
                # print('chord found: ' + str(notes))
                # note_length = ((notes_end - notes_start) // quantize_length) * quantize_length
                note_length = (round((notes_end - notes_start) / quantize_length)) * quantize_length

                note_length = note_length if note_length > 0 else quantize_length

                if notes_end > note.start:
                    note_length = notes_end - note.start

                if len(notes) == 1 and note.start > notes_start:
                    input_notes.append(str(notes[0].pitch) + ' ' + str(note_length))
                elif len(notes) > 1:
                    input_notes.append(':'.join(str(chord_note.pitch) for chord_note in notes) + ' ' + str(note_length))

                if note.start > notes_end:
                    input_notes.append('rest ' + str(((note.start - notes_end) // quantize_length) * quantize_length))
                    # print('rest found: ' + str((note.start - notes_end) // quantize_length))
                # if note.start < notes_start:
                #     input_notes.append(str(note.pitch) + ' ' + str( ((notes_start - note.start) // quantize_length) * quantize_length))
                # else:
                notes = [note]
                notes_start = note.start
                notes_end = note.end

            # if i == 150:
            #     break

        # for note in input_notes:
        #     print(note)
        for i in range(92, 115):
            print(midi_notes[i])

    with open(midi_folder + '/output/parsed.bin', 'wb') as path:
        pickle.dump(input_notes, path)

    return input_notes

def output_to_midi(predicted_output, midi_folder):
    
    output_file = pretty_midi.PrettyMIDI()
    piano = pretty_midi.Instrument(program=0, is_drum=False, name='Piano')
    output_file.instruments.append(piano)

    note_offset = 0
    for element in predicted_output:
        temp = element.split(' ')
        pitch = temp[0]
        length = temp[1]

        if ':' in pitch:
            chord_pitches = pitch.split(':')
            for chord_pitch in chord_pitches:
                piano.notes.append(pretty_midi.Note(100, int(chord_pitch), note_offset, note_offset + float(length)))
        elif pitch != 'rest':
            piano.notes.append(pretty_midi.Note(100, int(pitch), note_offset, note_offset + float(length)))
            
        note_offset += float(length)


    output_file.write(midi_folder + '/output/test_output.mid')