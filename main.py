from midi_parser import midi_to_input
from network import *
import tensorflow as tf

def main():

    SEQUENCE_LENGTH = 100
    MIDI_FOLDER = '.'#/midi/beethoven'

    # if not os.path.isfile(MIDI_FOLDER + '/output/parsed.bin'):
    input_notes = midi_to_input(MIDI_FOLDER)
    # else:
    #     with open(MIDI_FOLDER + '/output/parsed.bin', 'rb') as path:
    #         input_notes = pickle.load(path)
    
    # network_input, network_output, note_variants_count = create_input_sequences(input_notes, SEQUENCE_LENGTH)

    # physical_devices = tf.config.list_physical_devices('GPU') 
    # tf.config.experimental.set_memory_growth(physical_devices[0], True)
    
    # print('Starting training...')
    # model = create_network1(network_input, note_variants_count)
    # train_network(model,'BLSTM', network_input, network_output)

    # model = create_network2(network_input, note_variants_count)
    # train_network(model,'BLSTM_Att', network_input, network_output)

    # model = create_network3(network_input, note_variants_count)
    # train_network(model,'BLSTM_Att_LSTM', network_input, network_output)
    
    generate_midi(input_notes, MIDI_FOLDER, None, SEQUENCE_LENGTH, 1000)

if __name__ == "__main__":
    main()
