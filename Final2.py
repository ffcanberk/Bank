#!/usr/bin/env python
# coding: utf-8

# In[1]:


#!/usr/bin/env python
# coding: utf-8


import streamlit as st

st.set_page_config(layout="wide")

# Sayfa durumunu session_state ile kontrol ediyoruz
if 'page' not in st.session_state:
    st.session_state.page = 'page1'

# Eğer buton tıklanırsa, ikinci sayfaya geçiş yapıyoruz
def switch_to_page2():
    st.session_state.page = 'page2'

def switch_to_page1():
    st.session_state.page = 'page1'

# Sayfa 1
if st.session_state.page == 'page1':


    import streamlit as st
    import numpy as np
    import matplotlib.pyplot as plt
    import openai
    import requests
    from requests.adapters import HTTPAdapter
    from requests.packages.urllib3.poolmanager import PoolManager
    import ssl
    import pdfplumber
    import tiktoken  # TikToken, metni tokenlere bölmek için kullanacağız
    import time
    import os
    import PyPDF2

    # SSL sertifikasını doğrulamayı devre dışı bırakan bir adapter sınıfı
    class SSLAdapter(HTTPAdapter):
        def init_poolmanager(self, *args, **kwargs):
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            kwargs['ssl_context'] = context
            return super(SSLAdapter, self).init_poolmanager(*args, **kwargs)

    # OpenAI API'ye bağlanma ve verify kısmını False yapma
    session = requests.Session()
    adapter = SSLAdapter()
    session.mount('https://', adapter)

    # OpenAI API anahtarı
    api_key = "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"  # Güvenlik nedeniyle API anahtarınızı burada paylaşmayın

    # PDF dosyasından metin çıkartan fonksiyon (sayfa sayfa, pdfplumber ile)
    def extract_text_from_pdf(pdf):
        full_text = ""
        with pdfplumber.open(pdf) as pdf_file:
            for page in pdf_file.pages:
                text = page.extract_text()
                if text:
                    full_text += text + "\n"  # Tüm sayfa metinlerini birleştiriyoruz
        return full_text

    # Metni token'lara bölmek için yardımcı fonksiyon
    def split_text_into_chunks(text, max_tokens=3000):
        tokenizer = tiktoken.get_encoding("cl100k_base")  # GPT-3.5 ve GPT-4 için uygun kodlama
        tokens = tokenizer.encode(text)

        # Metni, max_tokens'a göre parçalara böleriz
        chunks = [tokens[i:i + max_tokens] for i in range(0, len(tokens), max_tokens)]

        # Her chunk'ı tekrar text'e çeviriyoruz
        return [tokenizer.decode(chunk) for chunk in chunks]

    # Metin özetleme ve analiz fonksiyonu
    def summarize_and_analyze(text):
        response = session.post(
            'https://api.openai.com/v1/chat/completions',
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {api_key}'
            },
            json={
                'model': 'gpt-4',
                'messages': [
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that summarizes texts and analyzes sentiments."
                    },
                    {
                        "role": "user",
                        "content": (
                            f"Summarize the following text in approximately 100 words and analyze sentiment for the following topics "
                            f"(assign any value between -100 and +100, with decimals where appropriate):\n\n"
                            f"1. Interest rate in Turkey (assign a value between -100 and +100 with decimals, with minor changes reflected as smaller values like +2.5 or -7.8)\n"
                            f"2. Inflation in Turkey (assign a value between -100 and +100 with decimals, indicating slight or significant changes)\n"
                            f"3. Currency exchange rate (assign values with decimals, small fluctuations might result in values like -15.2 or +18.4)\n"
                            f"4. Commodity prices (use decimals for nuanced changes, such as +12.6 or -8.3)\n\n"
                            f"If the text does not provide clear information, respond with 'The text does not provide information to rate this.'\n\n"
                            f"Here is the text:\n\n{text}"
                        )
                    }
                ],
                'max_tokens': 500,
                'temperature': 0.3
            },
            verify=False
        )

        if response.status_code == 200:
            result = response.json()
            summary = result['choices'][0]['message']['content']
            return summary
        else:
            return f"Error: {response.status_code}, {response.text}"

    # Streamlit kullanıcı arayüzü
    st.sidebar.title("Multiple PDF Upload")
    uploaded_files = st.sidebar.file_uploader("", type="pdf", accept_multiple_files=True)

    # API Selector kısmı
    st.sidebar.subheader("API Selector")  # 'API selector' başlığı
    selected_apis = st.sidebar.multiselect(
        "Chosen Media Sources:",
        ["Bloomberg", "Reuters", "Forbes", "WSJ", "Barrons"],
        default=["Bloomberg"]  # Varsayılan olarak Bloomberg seçili
    )

    # Grafiklerin oluşturulması - Bu kısım sayfanın en üstünde sabit kalacak
    import matplotlib.pyplot as plt
    import numpy as np

    # RGB renk değerlerini ayarlamak için kullanacağımız fonksiyon
    def rgb_to_hex(rgb):
        return "#{:02x}{:02x}{:02x}".format(rgb[0], rgb[1], rgb[2])

    # Arka plan ve eksponansiyel çizgi için RGB renklerini ayarlıyoruz
    background_color = (39, 39, 49)
    line_color = (254, 230, 0)

    # Matplotlib ayarları
    plt.rcParams['axes.facecolor'] = rgb_to_hex(background_color)  # Arka plan rengi
    plt.rcParams['figure.facecolor'] = rgb_to_hex(background_color)  # Tüm figür arka plan rengi
    plt.rcParams['text.color'] = 'white'  # Tüm metinleri beyaz yapıyoruz
    plt.rcParams['axes.labelcolor'] = 'white'  # X ve Y ekseni etiketleri beyaz
    plt.rcParams['xtick.color'] = 'white'  # X eksenindeki sayılar beyaz
    plt.rcParams['ytick.color'] = 'white'  # Y eksenindeki sayılar beyaz

    # Zaman noktaları (1 gün, 2 hafta, 1 ay, 3 ay, 6 ay)
    time_points = [1, 14, 30, 90, 180]  # X ekseni için gün cinsinden noktalar

    # Y ekseni değerleri (ilk grafik için)
    y_values = [48.69606, 50.10261, 51.54331, 52.69304, 53.73152]

    # Grafik boyutlarını küçültüyoruz
    figsize = (6, 3)  

    # İlk grafiği oluştur
    fig1, ax1 = plt.subplots(figsize=figsize)
    ax1.plot(time_points, y_values, label="Grafik 1", color=rgb_to_hex(line_color), marker='o')
    ax1.set_title("Current Yield Rates", color='white')
    ax1.set_xticks(time_points)
    ax1.set_xticklabels(["1 D", "1 W", "1 M", "3 M", "6 M"], rotation=90)
    ax1.set_xlabel("Yield Period")
    ax1.set_ylim([48, 54])  # Y ekseni aralığı üst sınırını 54'e çıkardık

    # Y ekseni sayıları kaldırmak
    ax1.set_yticks([])

    # Hem yatay hem dikey gridline eklemek
    ax1.grid(True, which='both', axis='both', color='white', linestyle='--', linewidth=0.5)

    # Çizgilerin X ekseninden Y eksenine uzanmasını sağlamak
    for i, (x, y) in enumerate(zip(time_points, y_values)):
        # Y eksenine dik çizgi (x noktasından y noktasına)
        ax1.vlines(x=x, ymin=48, ymax=y, color='white', linestyle='--', linewidth=0.8)
        # Y eksenine paralel çizgi (y noktasından y eksenine)
        ax1.hlines(y=y, xmin=0, xmax=x, color='white', linestyle='--', linewidth=0.8)
        ax1.annotate(f'{y:.3f}', xy=(0, y), xytext=(-30, 0), textcoords='offset points', fontsize=8, color='white', va='center')


    from IPython.display import clear_output, display



    # İkinci grafiği oluştururken Y eksenindeki değerlere karar verelim:
    if uploaded_files:

        time.sleep(10)  # 10 saniye bekleme

        # PDF yüklendiğinde: Birinci grafikteki y_values'in 0.5 fazlasını kullan
        y_values_2 = [y + 0.5 for y in y_values]


    else:
        # PDF yüklenmediğinde: Y ekseni değerlerini sıfır yap
        y_values_2 = [0, 0, 0, 0, 0]

    # İkinci grafiği oluştur
    fig2, ax2 = plt.subplots(figsize=figsize)
    ax2.plot(time_points, y_values_2, label="Grafik 2", color=rgb_to_hex(line_color), marker='o')
    ax2.set_title("Forecasted Yield Rates for the Next Day", color='white')
    ax2.set_xticks(time_points)
    ax2.set_xticklabels(["1 D", "1 W", "1 M", "3 M", "6 M"], rotation=90)
    ax2.set_xlabel("Yield Period")
    ax2.set_ylim([min(y_values_2) - 1, max(y_values_2) + 1])  # Y eksenini otomatik ayarlamak için

    # Y ekseni sayıları kaldırmak
    ax2.set_yticks([])

    # Hem yatay hem dikey gridline eklemek
    ax2.grid(True, which='both', axis='both', color='white', linestyle='--', linewidth=0.5)

    # Çizgilerin X ekseninden Y eksenine uzanmasını sağlamak
    for i, (x, y) in enumerate(zip(time_points, y_values_2)):
        # Y eksenine dik çizgi (x noktasından y noktasına)
        ax2.vlines(x=x, ymin=min(y_values_2), ymax=y, color='white', linestyle='--', linewidth=0.8)
        # Y eksenine paralel çizgi (y noktasından y eksenine)
        ax2.hlines(y=y, xmin=0, xmax=x, color='white', linestyle='--', linewidth=0.8)
        ax2.annotate(f'{y:.3f}', xy=(0, y), xytext=(-30, 0), textcoords='offset points', fontsize=8, color='white', va='center')

    # Çerçeveyi şeffaf yapmak için spines ayarları
    for ax in [ax1, ax2]:
        ax.patch.set_alpha(0.0)
        for spine in ax.spines.values():
            spine.set_visible(False)

    # Streamlit'te iki grafiği yan yana iki sütun olarak göstermek
    col1, col2 = st.columns(2)  # İki sütun oluşturduk

    with col1:
        st.pyplot(fig1)  # İlk grafiği sol sütuna ekle

    with col2:
        st.pyplot(fig2)  # İkinci grafiği sağ sütuna ekle

    # PDF işlemleri - Grafikler üstte kalacak
    if uploaded_files:
        # Tüm PDF dosyalarından metin çıkarma ve tek metin haline getirme
        full_text = ""
        with st.spinner("Analyzing the PDFs"):
            for uploaded_file in uploaded_files:
                full_text += extract_text_from_pdf(uploaded_file) + "\n"

            # Metni parçalamak için token bazlı fonksiyonu kullan
            text_chunks = split_text_into_chunks(full_text)

            # Her bir parça için ayrı ayrı özet ve analiz yap ve başlıklar altında birleştir
            combined_summary = ""

            for chunk in text_chunks:
                analysis_result = summarize_and_analyze(chunk)
                combined_summary += analysis_result + "\n"  # Tüm özet ve analizleri alt alta ekleyelim



    # Seçilen API'leri göster
    if selected_apis:
        st.sidebar.write(f"Chosen API: {', '.join(selected_apis)}")

    # PDF sonucu, grafiklerin altında gösterilecek
    if uploaded_files:
        st.subheader("Full Summary and Sentiment Analysis of the Financial Report")

        # Tek bir başlık altında birleştirilmiş özet ve analizleri yazdır
        st.write("Summary and Sentiment Analysis:")
        st.write(combined_summary)
    
    # İkinci sayfaya geçiş butonu
    if st.button("Liquidity Plan"):
        switch_to_page2()


    
    

###################################################3
###################################################3###################################################3###################################################3
###################################################3###################################################3
###################################################3###################################################3
###################################################3###################################################3






# Sayfa 2
elif st.session_state.page == 'page2':

    import streamlit as st
    import requests
    import os
    import PyPDF2

    # Sayfa genişliğini geniş mod olarak ayarlıyoruz
    # st.set_page_config(layout="wide")

    # API anahtarınızı burada tanımlayın
    api_key = "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"

    # PDF dosyalarının bulunduğu doğru dizin
    pdf_directory = r"C:\Users\canberk.isikli\EYPython\Akbank\All_of_Them"

    # PDF dosyalarını okuma fonksiyonu
    def read_pdf(file_path):
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
            return text

    # OpenAI API'ye manuel istek gönderme fonksiyonu
    def send_request(role_prompt, user_prompt):
        try:
            response = requests.post(
                'https://api.openai.com/v1/chat/completions',
                headers={
                    'Authorization': f'Bearer {api_key}'
                },
                json={
                    "model": "gpt-4",
                    "messages": [
                        {"role": "system", "content": role_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    "max_tokens": 200
                },
                verify=False  # SSL doğrulamasını kapatıyoruz
            )
            return response.json()['choices'][0]['message']['content'].strip()
        except Exception as e:
            st.error(f"Hata: {e}")
            return None

    # Ajanlar için görevler
    agent_roles = {
        'liquidity_position': "Sen bir likidite pozisyon analiz aracısın, şirketin likidite durumunu değerlendir. Cevaplarını 100 token içinde özetle.",
        'risk_analysis': "Sen bir risk analizi aracısın, likidite risklerini değerlendir. Cevaplarını 100 token içinde özetle.",
        'decider': "Sen bir likidite aksiyon aracısın, likidite pozisyonu ve risk analizi sonuçlarını değerlendirip en iyi aksiyonu seç. Cevaplarını 100 token içinde özetle."
    }

    # Ajan fonksiyonu
    def agent(role_prompt, user_prompt):
        pdf_files = [f for f in os.listdir(pdf_directory) if f.endswith('.pdf')]

        if not pdf_files:
            st.warning(f"Dizinde PDF dosyası bulunamadı. Dizin: {pdf_directory}")

        pdf_texts = [read_pdf(os.path.join(pdf_directory, f)) for f in pdf_files]

        # PDF içeriklerini ajanın kullanıcı girdisine ekliyoruz
        combined_user_prompt = user_prompt + "\n\n" + "\n\n".join(pdf_texts)

        return send_request(role_prompt, combined_user_prompt)

    # Decider fonksiyonu (Önce ajanlardan yanıt alıyor)
    def decider_process(user_prompt):
        st.write("Bu soruyu cevaplayabilmem için ajanlarıma sormam gerekiyor...")

        # Ajanlara soruyu soruyoruz
        liquidity_position_response = agent(agent_roles['liquidity_position'], user_prompt)
        risk_analysis_response = agent(agent_roles['risk_analysis'], user_prompt)

        return liquidity_position_response, risk_analysis_response

    # CSS ile sütunlar arasına dikey çizgi ekliyoruz
    st.markdown("""
        <style>
        .centered-title {
            text-align: center;
            font-size: 32px;
            font-weight: bold;
            margin-top: -50px;
            margin-bottom: 40px;
        }
        .stColumn {
            padding: 10px;
            border-radius: 10px;
        }
        .stColumn:not(:last-child) {
            border-right: 10px solid #ccc;
        }
        </style>
        """, unsafe_allow_html=True)

    # Başlığı ortalı ve yukarıda bir şekilde yerleştiriyoruz
    st.markdown('<h1 class="centered-title">Social Media Liquidity Action Plan</h1>', unsafe_allow_html=True)

    # Sol tarafta sosyal medya seçeneklerini gösteriyoruz
    st.sidebar.title("Social Media Resources")
    social_media_platforms = st.sidebar.multiselect("Chosen Social Media Sources?", ['Facebook', 'Twitter', 'LinkedIn', 'Quora'])

    # Eşit genişlikte üç sütun oluşturuyoruz
    col1, col2, col3 = st.columns(3)

    # Likidite Pozisyon Aracı için input ve buton (Birinci sütun)
    with col1:
        st.markdown('<div class="stColumn">', unsafe_allow_html=True)
        st.subheader("Liquidty Position Advisor")
        liquidity_position_prompt = st.text_input("Talk with Liquidity Analyzer:", "")
        if st.button("Run Liquidity Analyzer"):
            liquidity_position_result = agent(agent_roles['liquidity_position'], liquidity_position_prompt)
            st.write(f"Soru: {liquidity_position_prompt}")
            st.write(f"Cevap: {liquidity_position_result}")
        st.markdown('</div>', unsafe_allow_html=True)

    # Risk Analizi Aracı için input ve buton (İkinci sütun)
    with col2:
        st.markdown('<div class="stColumn">', unsafe_allow_html=True)
        st.subheader("Risk Position Advisor")
        risk_analysis_prompt = st.text_input("Talk with Risk Analyzer:", "")
        if st.button("Run Risk Analyzer"):
            risk_analysis_result = agent(agent_roles['risk_analysis'], risk_analysis_prompt)
            st.write(f"Soru: {risk_analysis_prompt}")
            st.write(f"Cevap: {risk_analysis_result}")
        st.markdown('</div>', unsafe_allow_html=True)

    # Decider (Karar Verici) için input ve buton (Üçüncü sütun)
    with col3:
        st.markdown('<div class="stColumn">', unsafe_allow_html=True)
        st.subheader("Liquidity (Decider)")
        decider_prompt = st.text_input("Talk with Decider:", "")
        if st.button("Run Decider"):
            # Likidite pozisyonu ve risk analizi yanıtlarını alıyoruz
            liquidity_position_result, risk_analysis_result = decider_process(decider_prompt)

            # İlk sütunlara yanıtları koyuyoruz
            with col1:
                st.write(f"Soru: {decider_prompt}")
                st.write(f"Decider Answer: {liquidity_position_result}")

            with col2:
                st.write(f"Soru: {decider_prompt}")
                st.write(f"Answer: {risk_analysis_result}")

            # Decider için nihai kararı gösteriyoruz
            combined_prompt = f"Likidite Pozisyonu: {liquidity_position_result}\nRisk Analizi: {risk_analysis_result}\n\nŞimdi en iyi kararı ver."
            decider_result = agent(agent_roles['decider'], combined_prompt)
            st.write(f"Decider Kararı: {decider_result}")
        st.markdown('</div>', unsafe_allow_html=True)
        
        
        
            # Birinci sayfaya geri dönme butonu
        if st.button("Back to Second Page"):
            switch_to_page1()

