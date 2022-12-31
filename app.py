import streamlit as st
import pandas as pd
from PIL import Image
import subprocess
import os
import base64
import pickle

# Moleküler tanımlayıcı hesaplama fonksyonu
def desc_calc():
    # Tanımlayıcı hesaplamasını gerçekleştirir
    bashCommand = "java -Xms2G -Xmx2G -Djava.awt.headless=true -jar ./PaDEL-Descriptor/PaDEL-Descriptor.jar -removesalt -standardizenitro -fingerprints -descriptortypes ./PaDEL-Descriptor/PubchemFingerprinter.xml -dir ./ -file descriptors_output.csv"
    process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    os.remove('molecule.smi')

# Dosya indirme
def filedownload(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # strings <-> bytes çevirimi
    href = f'<a href="data:file/csv;base64,{b64}" download="p53Tahmin.csv">Tahmini İndirin</a>'
    return href

# Model oluşturma
def build_model(input_data):
    # regression model okuma
    load_model = pickle.load(open('p53_model.pkl', 'rb'))
    # model uygulama
    prediction = load_model.predict(input_data)
    st.header('**Tahmin Çıktısı**')
    prediction_output = pd.Series(prediction, name='pIC50')
    molecule_name = pd.Series(load_data[1], name='molecule_name')
    df = pd.concat([molecule_name, prediction_output], axis=1)
    st.write(df)
    st.markdown(filedownload(df), unsafe_allow_html=True)

# Logo resim
image = Image.open('logo.png')

st.image(image, use_column_width=True)

# sayfa başlık
st.markdown("""
# İlaç keşfinde temel web uygulama (drug discovery essential web app)
**Cellular Tumor Antigen p53**

Bu uygulama, engellemeye yönelik biyoaktiviteyi tahmin etmenizi sağlar.
(P53), insan kanserlerinde sıklıkla mutasyona uğrayan düzenleyici bir proteindir.P53 geni hasar görürse, tümör baskılanması ciddi şekilde tehlikeye girer. Tümörlerin tedavisi veya yayılmasının önlenmesi için p53 miktarının arttırılması çözüm gibi görünebilir. Bu yüzden bu protein ilaç şeklinde kullanılır ve IC50 değerine göre en verimli mutasyona sahip ilaç en verimli ilaç denilebilir.

- Amin Hashemian 
- Bursa Uludag University
---
""")

# Sidebar
with st.sidebar.header('1. CSV verilerinizi yükleyin'):
    uploaded_file = st.sidebar.file_uploader("Giriş dosyanızı yükleyin", type=['txt'])
    st.sidebar.markdown("""
[Örnek Giriş Dosyası](https://github.com/A-Hashemian/final-project/blob/main/example-p53.txt)
""")

if st.sidebar.button('Tahmin'):
    load_data = pd.read_table(uploaded_file, sep=' ', header=None)
    load_data.to_csv('molecule.smi', sep = '\t', header = False, index = False)

    st.header('**Orijinal giriş verileri**')
    st.write(load_data)

    with st.spinner("Tanımlayıcıların hesaplanması..."):
        desc_calc()

    # Hesaplanan tanımlayıcıları okuma ve veri çerçevesini görüntüleme
    st.header('**Moleküler Tanımlayıcı Hesaplanması**')
    desc = pd.read_csv('descriptors_output.csv')
    st.write(desc)
    st.write(desc.shape)

    # Önceden oluşturulmuş modelde kullanılan tanımlayıcı listesini okuyun
    st.header('**Önceden oluşturulmuş modellerden tanımlayıcıların alt kümesi**')
    Xlist = list(pd.read_csv('descriptor_list.csv').columns)
    desc_subset = desc[Xlist]
    st.write(desc_subset)
    st.write(desc_subset.shape)

    # Sorgu dizilerine tahmin yapmak için eğitilmiş modeli uygulanması
    build_model(desc_subset)
else:
    st.info('Başlamak için kenar çubuğuna giriş verilerini yükleyin!')
