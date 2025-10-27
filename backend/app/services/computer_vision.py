import google.generativeai as genai
from dotenv import load_dotenv
import os
load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=str(gemini_api_key))

LISTA_DE_ELETRONICOS = [
    "celular", "laptop", "tablet", "monitor", "teclado", "mouse", 
    "Fone de ouvido", "CPU", "Placa-mãe", "Controle remoto", "Televisão"
]



def predict_image(image_data: bytes):

    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content([
            "Analise esta imagem e identifique se existe os objetos eletrônicos presentes nessa lista:"
            f"{', '.join(LISTA_DE_ELETRONICOS)}. "
            "Se existir, apenas devolva quais e a quantidade desse objeto. "
            "Siga esse padrão de resposta, porém com aspas duplas: {'celular': 1, 'laptop': 3, 'teclado': 1}."
             "Se não existir, devolva 'Nenhum objeto eletronico identificado.'" ,
            {'mime_type': 'image/jpeg', 'data': image_data}
        ])
        predicao = response.text
        return predicao

    except Exception as e:
        print(f"Erro ao analisar a imagem com a API do Gemini: {e}")
        return []