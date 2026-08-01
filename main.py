import os
from fastapi import FastAPI, Request, Response
from fastapi.responses import PlainTextResponse
from openai import OpenAI

app = FastAPI()

# Inicializamos el cliente de OpenAI usando variables de entorno
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Prompt del Sistema: Define la personalidad y reglas de negocio de la IA
SYSTEM_PROMPT = """
Eres un asistente de voz amigable y eficiente para un negocio de comida rápida en Montevideo.
Tu objetivo es tomar el pedido del cliente de forma clara, natural y conversacional.
Debes recopilar:
1. Nombre del cliente.
2. Qué productos desea del menú (Hamburguesas, Papas fritas, Refrescos).
3. Dirección de entrega o si retira en local.
4. Método de pago (Efectivo o Mercado Pago).
Mantén tus respuestas breves, cordiales y adaptadas para ser leídas por un sintetizador de voz.
"""

@app.get("/")
def read_root():
    return {"status": "El sistema de llamadas y pedidos está activo en la nube 🚀"}

@app.post("/webhook/voice")
async def handle_voice_call(request: Request):
    """
    Endpoint que recibe las peticiones de la llamada (por ejemplo, desde Twilio o un webhook de voz).
    Aquí procesamos la entrada y respondemos con las instrucciones de voz o texto.
    """
    form_data = await request.form()
    user_speech = form_data.get("SpeechResult", "Hola")

    # Generamos la respuesta conversacional usando la IA
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_speech}
        ]
    )
    
    ai_reply = response.choices[0].message.content

    # Retornamos una respuesta en formato TwiML o texto plano para que el sistema de llamadas la reproduzca
    twiml_response = f"""
    <Response>
        <Say language="es-UY" voice="alice">{ai_reply}</Say>
        <Gather input="speech" action="/webhook/voice" method="POST" language="es-UY" timeout="3"/>
    </Response>
    """
    return Response(content=twiml_response, media_type="application/xml")
