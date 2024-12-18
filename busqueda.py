import json
import boto3

class ClaudeAPI:
    def __init__(self):
        # Cliente de Bedrock
        self.bedrock_client = boto3.client('bedrock-runtime', region_name='us-east-1')
        print("Cliente de Bedrock inicializado.")

    def generar_preguntas(self, full_text, tema, tipo):
        """
        Genera preguntas y respuestas usando Claude en Bedrock.
        """
        # Generar prompt
        prompt = (
            f"Genera preguntas del tipo '{tipo}' sobre el tema '{tema}' utilizando el siguiente contenido:\n\n"
            f"{full_text[:8000]}\n\n"
            "Formato de salida:\n"
            "Pregunta: [Aquí va la pregunta]\n"
            "Respuesta: [Aquí va la respuesta]"
        )
        print(f"\n### PROMPT ENVIADO A CLAUDE ###\n")

        # Construir la solicitud para Bedrock
        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1000,
            "temperature": 0.7,
            "messages": [{"role": "user", "content": prompt}]
        })
        print(f"Payload enviado a Bedrock: {body}")

        try:
            # Invocar el modelo
            print("Invocando a Claude...")
            response = self.bedrock_client.invoke_model(
                modelId="anthropic.claude-3-5-sonnet-20240620-v1:0",
                accept="application/json",
                contentType="application/json",
                body=body
            )

            # Leer respuesta
            response_body = json.loads(response['body'].read())
            content = response_body.get('content', '')
            print(f"\n### RESPUESTA RECIBIDA DE CLAUDE ###\n{content}\n")

            # Procesar preguntas y respuestas
            questions, answers = self._parse_questions_and_answers(content)
            print(f"Preguntas generadas: {questions}")
            print(f"Respuestas generadas: {answers}")

            return questions, answers

        except Exception as e:
            print(f"Error al invocar a Claude: {e}")
            return [], []

    def _parse_questions_and_answers(self, content):
        """
        Procesa el texto generado por Claude para dividir preguntas y respuestas completas.
        """
        print("Procesando la respuesta para extraer preguntas y respuestas...")
        questions, answers = [], []
        current_answer = []
        capturing_answer = False

        # Si el contenido es una lista, convertirlo en un string
        if isinstance(content, list):
            content = "\n".join([item['text'] for item in content if isinstance(item, dict) and 'text' in item])

        # Procesar línea por línea
        for line in content.split("\n"):
            if line.startswith("Pregunta:"):
                if capturing_answer and current_answer:
                    answers.append(" ".join(current_answer).strip())  # Guardar la respuesta completa
                    current_answer = []  # Reiniciar la respuesta actual
                questions.append(line.replace("Pregunta:", "").strip())
                capturing_answer = True  # La siguiente sección será la respuesta

            elif line.startswith("Respuesta:"):
                current_answer = [line.replace("Respuesta:", "").strip()]  # Empezar la respuesta

            elif capturing_answer:  # Acumular líneas adicionales hasta que encuentre otra pregunta
                current_answer.append(line.strip())

        # Capturar la última respuesta si existe
        if capturing_answer and current_answer:
            answers.append(" ".join(current_answer).strip())

        print(f"Preguntas extraídas: {questions}")
        print(f"Respuestas extraídas: {answers}")
        return questions, answers


    def process_documents(self, documents):
        """
        Procesa documentos y genera embeddings usando Cohere Embed Multilingual.
        """
        print("Generando embeddings para los documentos...")
        self.documents = documents
        truncated_texts = [doc[:2048] for doc in documents]

        body = json.dumps({
            "texts": truncated_texts,
            "input_type": "search_document",
            "truncate": "END"
        })
        print(f"Payload enviado a Bedrock para embeddings: {body}")

        try:
            response = self.bedrock_client.invoke_model(
                modelId="cohere.embed-multilingual-v3",
                body=body
            )
            response_body = json.loads(response['body'].read())
            self.embeddings = response_body['embeddings']
            print("Embeddings generados correctamente.")
        except Exception as e:
            print(f"Error al generar embeddings: {e}")
            self.embeddings = None

    def search_documents(self, query, number_of_results=5):
        """
        Busca documentos relevantes utilizando similitud coseno entre embeddings.
        """
        if not self.embeddings or not self.documents:
            raise ValueError("No hay documentos procesados para buscar.")

        print(f"Generando embedding para la consulta: '{query}'")
        body = json.dumps({
            "texts": [query[:2048]],
            "input_type": "search_query",
            "truncate": "END"
        })

        try:
            response = self.bedrock_client.invoke_model(
                modelId="cohere.embed-multilingual-v3",
                body=body
            )
            response_body = json.loads(response['body'].read())
            query_embedding = response_body['embeddings'][0]
            print(f"Embedding de la consulta generado: {query_embedding}")

            # Calcular similitud coseno
            from numpy import dot
            from numpy.linalg import norm

            similarities = [
                dot(query_embedding, doc_emb) / (norm(query_embedding) * norm(doc_emb))
                for doc_emb in self.embeddings
            ]

            # Ordenar por relevancia
            sorted_indices = sorted(range(len(similarities)), key=lambda i: similarities[i], reverse=True)
            results = [self.documents[i] for i in sorted_indices[:number_of_results]]
            print(f"Documentos más relevantes encontrados: {results}")

            return results

        except Exception as e:
            print(f"Error al buscar documentos: {e}")
            return []
