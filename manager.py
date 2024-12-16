# manager.py

class ExamManager:
    def __init__(self, agent_rag):
        self.agent_rag = agent_rag
        self.questions = []
        self.answers = []

    def resolver_ticket(self, description):
        """
        Resuelve un ticket utilizando Claude y procesa la solución.
        """
        # Obtener datos de solución desde Claude
        solution_data = self.agent_rag.resolver_ticket(description)

        if isinstance(solution_data, str):
            return f"Error resolving ticket: {solution_data}"

        # Procesar los datos de solución y asegurarse de que sea un string único
        solution_text = ""
        if isinstance(solution_data.get('content'), list):
            # Concatenar todos los textos en un único string si es una lista
            solution_text = " ".join(
                item.get('text', '') for item in solution_data['content'] if item.get('type') == 'text'
            )
        else:
            solution_text = solution_data.get('content', 'No resolution found')

        return solution_text

    def create_random_questions(self, full_text):
        """
        Genera preguntas aleatorias basadas en el texto completo.
        """
        from random import sample

        sentences = full_text.split('.')
        sentences = [s.strip() for s in sentences if len(s.strip()) > 20]

        for sentence in sample(sentences, min(5, len(sentences))):
            words = sentence.split()
            if len(words) > 4:
                answer = words.pop(2)  # Elegir una palabra al azar como respuesta
                question = sentence.replace(answer, "_____")
                self.questions.append(question)
                self.answers.append(answer)

        return self.questions, self.answers

    def create_topic_specific_questions(self, full_text, topic):
        """
        Genera preguntas sobre un tema específico.
        """
        sentences = [s for s in full_text.split('.') if topic.lower() in s.lower()]
        if not sentences:
            return [], []

        for sentence in sentences[:10]:  # Máximo 10 preguntas
            words = sentence.split()
            if len(words) > 4:
                answer = words.pop(2)
                question = sentence.replace(answer, "_____")
                self.questions.append(question)
                self.answers.append(answer)

        return self.questions, self.answers

    def combine_claude_and_random(self, description):
        """
        Combina preguntas de Claude con preguntas generadas aleatoriamente.
        """
        # Resolver ticket con Claude para obtener contenido relevante
        full_text = self.resolver_ticket(description)

        if "Error" in full_text:
            return [], [], full_text  # Devuelve el error si algo falla

        # Generar preguntas aleatorias y sobre el texto de Claude
        random_questions, random_answers = self.create_random_questions(full_text)
        self.questions = random_questions
        self.answers = random_answers

        return self.questions, self.answers, "Preguntas generadas exitosamente."
