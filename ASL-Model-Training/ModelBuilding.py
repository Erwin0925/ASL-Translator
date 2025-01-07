import os
import numpy as np
from sklearn.model_selection import train_test_split
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from tensorflow.keras.callbacks import TensorBoard
from tensorflow.keras.optimizers import Adam

class ModelBuilding:
    def __init__(self, desired_path="C:\\Users\\erwin\\Desktop\\ASL_Translation_FYP"):
        self.desired_path = desired_path
        self.DATA_PATH = os.path.join(desired_path, 'ASL_Dataset')
        self.actions = np.array([
            "Family", "Friends", "Work", "School", "Home", "Car", "Happy", "Sad", "Play", 
            "Help", "Eat", "Drink", "Sleep", "Sorry", "Computer", "Money", "Phone", "Cloth", "Me", "Stop"
        ])
        self.sequence_length = 30
        self.label_map = {label: num for num, label in enumerate(self.actions)}
        self.sequences, self.labels = self.prepare_data()

    def prepare_data(self):
        sequences, labels = [], []
        for action in self.actions:
            for sequence in np.array(os.listdir(os.path.join(self.DATA_PATH, action))).astype(int):
                window = []
                for frame_num in range(self.sequence_length):
                    res = np.load(os.path.join(self.DATA_PATH, action, str(sequence), f"{frame_num}.npy"))
                    window.append(res)
                sequences.append(window)
                labels.append(self.label_map[action])
        return sequences, labels

    def build_lstm_model(self):
        log_dir = os.path.join('Logs')
        tb_callback = TensorBoard(log_dir=log_dir)

        self.LSTM_model = Sequential()
        self.LSTM_model.add(LSTM(64, return_sequences=True, input_shape=(30, 1662)))
        self.LSTM_model.add(LSTM(128, return_sequences=True))
        self.LSTM_model.add(LSTM(64))
        self.LSTM_model.add(Dense(64, activation='relu'))
        self.LSTM_model.add(Dense(32, activation='relu'))
        self.LSTM_model.add(Dense(self.actions.shape[0], activation='softmax'))

        self.LSTM_model.compile(optimizer='Adam', loss='categorical_crossentropy', metrics=['categorical_accuracy'])

        X = np.array(self.sequences)
        y = to_categorical(self.labels).astype(int)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        self.LSTM_model.fit(X_train, y_train, epochs=2000, callbacks=[tb_callback], validation_data=(X_test, y_test))