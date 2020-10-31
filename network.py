from midi_parser import output_to_midi
import pickle
import numpy as np
from keras import utils
from keras_self_attention import SeqSelfAttention
from keras.models import Sequential
from keras.layers import Dense, Dropout, LSTM, Activation, Bidirectional, Flatten
from keras.callbacks import ModelCheckpoint
import os

def create_network1(network_input, note_variants_count):
    model = Sequential([
        Bidirectional(LSTM(32, input_shape=(network_input.shape[1], network_input.shape[2]), return_sequences=True)),
        Dropout(0.3),
        Flatten(),
        Dense(note_variants_count),
        Activation('softmax')
    ])
    model.compile(loss='categorical_crossentropy', optimizer='adam')
    return model

def create_network2(network_input, note_variants_count):
    model = Sequential([
        Bidirectional(LSTM(512, input_shape=(network_input.shape[1], network_input.shape[2]), return_sequences=True)),
        SeqSelfAttention(attention_activation='sigmoid'),
        Dropout(0.3),
        Flatten(),
        Dense(note_variants_count),
        Activation('softmax')
    ])
    model.compile(loss='categorical_crossentropy', optimizer='adam')
    return model

def create_network3(network_input, note_variants_count):
    model = Sequential([
        Bidirectional(LSTM(512, input_shape=(network_input.shape[1], network_input.shape[2]), return_sequences=True)),
        SeqSelfAttention(attention_activation='sigmoid'),
        Dropout(0.3),
        LSTM(512, return_sequences=True),
        Dropout(0.3),
        Flatten(),
        Dense(note_variants_count),
        Activation('softmax')
    ])
    model.compile(loss='categorical_crossentropy', optimizer='adam')
    return model

def train_network(model, model_name, network_input, network_output):
    filepath = os.path.abspath('models/' + model_name + '/' + model_name + '_{epoch:03d}_{loss:.4f}_weights.hdf5')
    checkpoint = ModelCheckpoint(filepath, period=5, monitor='loss', verbose=1, save_best_only=False, mode='min')
    model.fit(network_input, network_output, epochs=50, batch_size=64, callbacks=[checkpoint])

def load_network(filename):
    pass

def generate_midi(input_notes, midi_folder, network_file, sequence_length, note_count):

    with open(midi_folder + '/output/parsed.bin', 'rb') as path:
        input_notes = pickle.load(path)

    network_input, normalized_input, note_variants = create_input_sequences(input_notes, sequence_length, for_generation=True)
    model = load_network(network_file)
    # predicted_output = generate_output(model, network_input, note_variants, note_count)
    predicted_output = input_notes
    output_to_midi(predicted_output, midi_folder)

def generate_output(model, network_input, note_variants, note_count):
    
    current_sequence = network_input[np.random.randint(0, len(network_input) - 1)]
    int_to_note_map = dict((number, note) for number, note in enumerate(note_variants))
    predicted_output = []

    for _ in range(note_count):
        input_sequence = np.reshape(current_sequence, (1, len(current_sequence), 1))
        input_sequence = input_sequence / len(network_input)

        prediction = model.predict(input_sequence, verbose=0)

        max_index = np.argmax(prediction)
        predicted_output.append(int_to_note_map[max_index])

        current_sequence.append(max_index)
        current_sequence = current_sequence[1:]
    
    return predicted_output

def create_input_sequences(input_notes, sequence_length, for_generation=False):

    note_variants = sorted(set(note for note in input_notes))
    note_to_int_map = dict((note, number) for number, note in enumerate(note_variants))
    
    network_input = []
    network_output = []
    print(f'input notes length: {len(input_notes)}')
    for i in range(0, len(input_notes) - sequence_length):
        input_sequence = input_notes[i:i + sequence_length]
        output_sequence = input_notes[i + sequence_length]

        network_input.append([note_to_int_map[note] for note in input_sequence])
        network_output.append(note_to_int_map[output_sequence])

    sequences_count = len(network_input)
    
    network_input = np.reshape(network_input, (sequences_count, sequence_length, 1))
    normalized_input = network_input / len(note_variants)
    
    network_output = utils.to_categorical(network_output)

    if for_generation is True:
        return network_input, normalized_input, note_variants
    else:
        return normalized_input, network_output, len(note_variants)

