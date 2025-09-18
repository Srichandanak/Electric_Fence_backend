import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense

# Generate synthetic frequency-domain training data
def generate_training_data(samples=500):
    X, y = [], []
    for _ in range(samples):
        normal = np.random.rand(8) * 0.5
        threat = np.random.rand(8) * 0.5 + 0.5

        if np.random.rand() > 0.5:
            X.append(normal)
            y.append(0)
        else:
            X.append(threat)
            y.append(1)
    X = np.array(X).reshape(-1, 1, 8)  # (samples, timesteps=1, features=4)
    y = np.array(y)
    return X, y

# Build and train LSTM
X_train, y_train = generate_training_data()
model = Sequential([
    LSTM(8, input_shape=(1, 8)),
    Dense(1, activation='sigmoid')
])
model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
model.fit(X_train, y_train, epochs=5, batch_size=16, verbose=0)

def predict_threat(freq_features):
    freq_features = freq_features[:8]  # trim to 4 features
    x = np.array(freq_features).reshape(1, 1, 8)
    pred = model.predict(x, verbose=0)[0][0]
    return pred > 0.5
