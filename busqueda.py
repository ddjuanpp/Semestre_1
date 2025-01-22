# busqueda.py

import json
import boto3
from faiss_manager import FAISSManager

class ClaudeAPI:
    def __init__(self):
        self.bedrock_client = boto3.client('bedrock-runtime', region_name='us-east-1')
        print("Cliente de Bedrock inicializado.")
        
        self.faiss_manager = FAISSManager()
        self.index_created = False

    def generar_preguntas(self, full_text, tema, tipo):
        """
        Genera preguntas y respuestas usando Claude en Bedrock.
        """
        # Si no hemos creado el índice FAISS aún
        if not self.index_created:
            # Pasamos la lista de documentos. En tu caso, solo uno concatenado,
            # pero podrías usar varios si así lo deseas.
            self.faiss_manager.create_faiss_index([full_text])
            self.index_created = True

        # Tomamos un chunk aleatorio
        random_chunk = self.faiss_manager.get_random_chunk()
        if not random_chunk:
            print("No se pudo obtener un chunk aleatorio. Usando fallback de 8000 chars.")
            random_chunk = full_text[:8000]

        # Construimos el prompt con ese chunk
        prompt = (
            f"Genera preguntas del tipo '{tipo}' sobre el tema '{tema}' utilizando el siguiente contenido:\n\n"
            f"{random_chunk}\n\n"
            "Formato de salida:\n"
            "Pregunta: [Aquí va la pregunta]\n"
            "Respuesta: [Aquí va la respuesta]"
        )

        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1000,
            "temperature": 0.7,
            "messages": [{"role": "user", "content": prompt}]
        })

        try:
            response = self.bedrock_client.invoke_model(
                modelId="anthropic.claude-3-5-sonnet-20240620-v1:0",
                accept="application/json",
                contentType="application/json",
                body=body
            )

            response_body = json.loads(response['body'].read())
            content = response_body.get('content', '')

            # Procesar preguntas y respuestas
            questions, answers = self._parse_questions_and_answers(content)
            return questions, answers

        except Exception as e:
            print(f"Error al invocar a Claude: {e}")
            return [], []

    def _parse_questions_and_answers(self, content):
        # Igual que antes
        questions, answers = [], []
        current_answer = []
        capturing_answer = False

        if isinstance(content, list):
            content = "\n".join([item['text'] for item in content if isinstance(item, dict) and 'text' in item])

        for line in content.split("\n"):
            if line.startswith("Pregunta:"):
                if capturing_answer and current_answer:
                    answers.append(" ".join(current_answer).strip()) 
                    current_answer = []
                questions.append(line.replace("Pregunta:", "").strip())
                capturing_answer = True 

            elif line.startswith("Respuesta:"):
                current_answer = [line.replace("Respuesta:", "").strip()]

            elif capturing_answer:
                current_answer.append(line.strip())

        if capturing_answer and current_answer:
            answers.append(" ".join(current_answer).strip())

        return questions, answers
