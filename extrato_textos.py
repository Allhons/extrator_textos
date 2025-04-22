import streamlit as st
import cv2
import numpy as np
import pytesseract
import pandas as pd
from io import BytesIO
import re

# Windows: Descomente e configure se necessário
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

st.title("🧠 Extrator de textos")
st.write("Faça upload de ou ou mais imagens, e o sistema extrai colunas (em MAIÚSCULAS com `:`) e organiza os dados em um DataFrame único.")

# Upload múltiplo
uploaded_files = st.file_uploader("📤 Envie uma ou mais imagens (PNG, JPG)", type=["png", "jpg", "jpeg"], accept_multiple_files=True)

dados_gerais = []

if uploaded_files:
    for uploaded_file in uploaded_files:
        st.subheader(f"📷 Imagem: {uploaded_file.name}")
        file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
        imagem = cv2.imdecode(file_bytes, 1)
        st.image(imagem, caption=uploaded_file.name, use_column_width=True)

        # OCR
        texto = pytesseract.image_to_string(imagem, lang="por")
        palavras = texto.strip().split()

        # Parse colunas e dados
        dados = {}
        coluna_atual = None
        linha = {}

        for palavra in palavras:
            if re.match(r"^[A-ZÇÃÕÁÉÍÓÚÜÀÊÂÔ]+:$", palavra):
                if coluna_atual:
                    dados[coluna_atual] = " ".join(linha.get(coluna_atual, []))
                coluna_atual = palavra
                linha[coluna_atual] = []
            elif coluna_atual:
                linha[coluna_atual].append(palavra)

        if coluna_atual:
            dados[coluna_atual] = " ".join(linha.get(coluna_atual, []))
            
        if not coluna_atual:
            st.warning(f"⚠️ Nenhuma coluna encontrada na imagem {uploaded_file.name}.")

            continue

        dados_limpos = {col.strip(":"): val for col, val in dados.items()}
        dados_gerais.append(dados_limpos)

    
    
        
    # Unir tudo em um DataFrame
    df_final = pd.DataFrame(dados_gerais)
    st.success("✅ Todas as imagens foram processadas com sucesso!")
    st.dataframe(df_final)

    # Baixar como Excel
    def converter_para_excel(df):
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        return output.getvalue()

    excel_bytes = converter_para_excel(df_final)
    st.download_button("⬇️ Baixar resultado como Excel", data=excel_bytes, file_name="dados_extraidos.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")