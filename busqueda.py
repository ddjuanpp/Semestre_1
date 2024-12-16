# busqueda.py

import boto3
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class ClaudeAPI:
    def __init__(self):
        # Cliente de Bedrock
        self.bedrock_client = boto3.client('bedrock-runtime', region_name='us-east-1')
        self.vectorizer = TfidfVectorizer()
        self.embeddings = None
        self.documents = []

    def process_documents(self, documents):
        """
        Procesa los textos de documentos y genera embeddings TF-IDF.
        """
        self.documents = documents
        self.embeddings = self.vectorizer.fit_transform(documents)

    def search_documents(self, query, number_of_results=5):
        """
        Busca documentos relevantes usando similitud coseno con TF-IDF.
        """
        if not self.embeddings:
            raise ValueError("No hay documentos procesados para buscar.")

        query_embedding = self.vectorizer.transform([query])
        similarities = cosine_similarity(query_embedding, self.embeddings).flatten()
        sorted_indices = similarities.argsort()[::-1][:number_of_results]

        return [self.documents[idx] for idx in sorted_indices]

    def generar_preguntas(self, full_text, tema, tipo):
        """
        Genera preguntas y respuestas usando Claude en Bedrock.
        """
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1000,
            "messages": [
                {
                    "role": "user",
                    "content": (
                        f"Quiero que generes preguntas de tipo '{tipo}' sobre '{tema}' "
                        f"usando el siguiente contenido: {full_text[:10000]}."
                    ),
                }
            ]
        }

        try:
            response = self.bedrock_client.invoke_model(
                modelId="anthropic.claude-3-5-sonnet-20240620-v1:0",
                accept="application/json",
                contentType="application/json",
                body=json.dumps(body)
            )

            if 'body' not in response:
                return [], []

            response_body = json.loads(response['body'].read())
            content = response_body.get('completion', "")

            # Suponemos que las preguntas y respuestas están separadas en el contenido
            questions, answers = self._parse_questions_and_answers(content)
            return questions, answers

        except Exception as e:
            print(f"Error al invocar a Claude: {e}")
            return [], []

    def _parse_questions_and_answers(self, content):
        """
        Procesa el texto generado por Claude para dividir preguntas y respuestas.
        """
        lines = content.split('\n')
        questions = []
        answers = []

        for line in lines:
            if line.startswith("Pregunta:"):
                questions.append(line.replace("Pregunta:", "").strip())
            elif line.startswith("Respuesta:"):
                answers.append(line.replace("Respuesta:", "").strip())

        return questions, answers
