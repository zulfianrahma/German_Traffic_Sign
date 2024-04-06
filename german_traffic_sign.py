# -*- coding: utf-8 -*-
"""german_traffic_sign.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1wjSq7XyFvkCoqnSlQI4vKXRVKWq7jfPJ

# 1. Install and Import Dependencies

- Instalasi **opendatasets** untuk proses import data dari **Kaggle**
"""

!pip install opendatasets

"""- Import dan konfigurasi library yang digunakan"""

# Commented out IPython magic to ensure Python compatibility.
import pandas as pd
import numpy as np
import tensorflow as tf
import opendatasets as od

from keras.models import Sequential
from keras.models import Sequential, load_model
from keras.layers import Conv2D, Dense, Flatten, Dropout, MaxPool2D
from sklearn.model_selection import train_test_split
import pickle
import seaborn as sns
import matplotlib
import matplotlib.pyplot as plt
matplotlib.style.use('ggplot')
# %matplotlib inline
# %config InlineBackend.figure_format = 'retina'

"""# 2. Import Dataset

- Import dataset dari **Kaggle** (diperlukan *username* dan *key* dari akun **Kaggle** yang akan digunakan untuk download data)
"""

# import dataset
od.download('https://www.kaggle.com/datasets/saadhaxxan/germantrafficsigns')

"""- Memuat data yang telah didownload"""

## Load the data
training_file = "/content/germantrafficsigns/train.p"
testing_file = "/content/germantrafficsigns/test.p"
validation_file = "/content/germantrafficsigns/valid.p"

# Open and load the training file
with open(training_file, mode='rb') as f:
    train = pickle.load(f)

# Open and load the testing file
with open(testing_file, mode='rb') as f:
    test = pickle.load(f)

# Open and load the validation file
with open(validation_file, mode='rb') as f:
    valid = pickle.load(f)

print("Data loaded")

"""# 3. Eksplorasi Data

- Memuat data **signnames.csv**
"""

## Buat pandas dataframe untuk load data csv
## File csv ini berupa ClassId dan SignName

sign_name_df = pd.read_csv('/content/germantrafficsigns/signnames.csv')
SIGN_NAMES = sign_name_df.SignName.values
sign_name_df.set_index('ClassId', inplace=True)
sign_name_df.head(10)

"""- mendefinisikan fitur dan label pada data pickle yang telah dimuat (**train**, **test**, **validation**)"""

# Definisikan fitur dan label untuk data training
X_train, y_train = train['features'], train['labels']

# Mengubah lists menjadi numpy arrays
X_train = np.array(X_train)
y_train = np.array(y_train)
print(X_train.shape, y_train.shape)

# Definisikan fitur dan label untuk data testing
X_test, y_test = test['features'], test['labels']

# Mengubah lists menjadi numpy arrays
X_test = np.array(X_test)
y_test = np.array(y_test)
print(X_test.shape, y_test.shape)

# Definisikan fitur dan label untuk data validation
X_val, y_val = valid['features'], valid['labels']

# Mengubah lists menjadi numpy arrays
X_val = np.array(X_val)
y_val = np.array(y_val)
print(X_val.shape, y_val.shape)

"""- Melakukan visualisasi distribusi kelas pada data training, validasi, dan testing"""

n_labels = np.unique(y_train).size
def hist_data(y_data, title=None, ax=None, **kwargs):
    if not ax :
        fig = plt.figure()
        ax = fig.add_subplot(111)
    ax.hist(y_data, np.arange(-0.5, n_labels+1.5), stacked=True, **kwargs)
    ax.set_xlim(-0.5, n_labels-0.5)
    if 'label' in kwargs : ax.legend()
    if title : ax.set_title(title)

fig,ax = plt.subplots(1,3, figsize=(20,5))
hist_data(y_train, title='Distribusi kelas pada data training', ax=ax[0])
hist_data(y_val, title='Distribusi kelas pada data validasi', ax=ax[1], color='black')
hist_data(y_test, title='Distribusi kelas pada data test', ax=ax[2], color='grey')

"""Dari gambar visualisasi di atas terlihat bahwa distribusi kelas masing-masing bagian data terlihat mirip. Oleh karena itu, kita tidak perlu melakukan proses normalisasi.

- Melakukan konversi label data menggunakan teknik **one hot encoding** (mengubah tipe data **string** menjadi fitur **kategorik**)
"""

# Konversi label dengan teknik one hot encoding
from tensorflow.keras.utils import to_categorical

y_train = to_categorical(y_train, 43)
y_val = to_categorical(y_val, 43)

"""# 4. Training Model

- Membuat fungsi **callback** untuk menghentikan proses pelatihan ketika sudah mencapai tingkat parameter yang diinginkan
"""

class myCallback(tf.keras.callbacks.Callback):
  def on_epoch_end(self, epoch, logs={}):
    if(logs.get('accuracy') > 0.96):
      print("\nAkurasi telah mencapai >96%. Stop training!")
      self.model.stop_training = True

callbacks = myCallback()

"""- Membuat model menggunakan CNN"""

# Building the model
model = Sequential()

# First layer
model.add(Conv2D(filters=32, kernel_size=(5,5), activation='relu', input_shape=X_train.shape[1:]))
model.add(Conv2D(filters=32, kernel_size=(5,5), activation='relu'))
model.add(MaxPool2D(pool_size=(2, 2)))
model.add(Dropout(rate=0.25))

# Second layer
model.add(Conv2D(filters=64, kernel_size=(3, 3), activation='relu'))
model.add(Conv2D(filters=64, kernel_size=(3, 3), activation='relu'))
model.add(MaxPool2D(pool_size=(2, 2)))
model.add(Dropout(0.25))

# Third layer
model.add(Flatten())
model.add(Dense(256, activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(43, activation='softmax'))

model.summary()

"""- Melakukan kompilasi model dan memanggil fungsi **fit** untuk memulai proses pelatihan model"""

# Compile the model
model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
epochs = 25
history = model.fit(X_train, y_train, batch_size=32, epochs=epochs, validation_data=(X_val, y_val), callbacks=[callbacks])
model.save("my_model.h5")

"""- Menampilkan grafik nilai akurasi dan loss"""

# Plotting graphs for accuracy
plt.figure(0)
plt.plot(history.history['accuracy'], label='training accuracy')
plt.plot(history.history['val_accuracy'], label='val accuracy')
plt.title('Accuracy')
plt.xlabel('epochs')
plt.ylabel('accuracy')
plt.legend()
plt.show()

# Plotting graphs for loss
plt.figure(1)
plt.plot(history.history['loss'], label='training loss')
plt.plot(history.history['val_loss'], label='val loss')
plt.title('Loss')
plt.xlabel('epochs')
plt.ylabel('loss')
plt.legend()
plt.show()

"""# 5. Testing Model

- Menguji akurasi model yang telah dilatih pada data uji
"""

# Testing accuracy with the test data
from sklearn.metrics import accuracy_score

pred=np.argmax(model.predict(X_test), axis=-1)
accuracy_score(y_test, pred)

"""- Menampilkan **classification report** pada model yang telah dibuat berdasarkan pengujian menggunakan data uji"""

# Calculate metrics for classification
from sklearn.metrics import classification_report

print(classification_report(y_test, pred))

