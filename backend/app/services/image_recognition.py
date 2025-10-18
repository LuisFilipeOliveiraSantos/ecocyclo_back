import google.generativeai as genai

genai.configure(api_key="AIzaSyBwVzj66buIhe8NOxmMo1DGa6b45HrMJ6w")

LISTA_DE_ELETRONICOS = [
    "celular", "laptop", "tablet", "monitor", "teclado", "mouse", 
    "headset", "CPU", "Placa-mãe", "Controle remoto"
]

def predict_image(image_data: bytes):
    #base64_image = base64.b64encode(image_data).decode('utf-8')
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content([
            "Analise esta imagem e identifique se existe os objetos eletrônicos presentes nessa lista:"
            f"{', '.join(LISTA_DE_ELETRONICOS)}. "
            "Se existir, apenas devolva quais como uma lista de strings. "
            "Se não existir, devolva 'Nenhum objeto eletronico identificado.'"
            "Siga esse padrão de resposta: ['celular', 'laptop', 'teclado']." ,
            {'mime_type': 'image/jpeg', 'data': image_data}
        ])
        predicao = response.text
        return predicao

    except Exception as e:
        print(f"Erro ao analisar a imagem com a API do Gemini: {e}")
        return []