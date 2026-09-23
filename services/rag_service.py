"""
RAG Orchestration Service for TourAI.
Integrates Question Analyzer, Tour Retriever, Context Builder, Prompt Builder,
and Gemini Service into a seamless, hallucination-free pipeline.
"""

import json
from services.question_analyzer import QuestionAnalyzer
from services.tour_retriever import TourRetriever
from services.context_builder import ContextBuilder
from services.prompt_builder import PromptBuilder
from services.gemini_service import GeminiService
from database.db import execute_query

class RAGService:
    @staticmethod
    def answer_question(question: str, session_id: str = "guest") -> dict:
        """
        Executes the full RAG pipeline:
        question -> analyze -> retrieve -> context -> prompt -> gemini -> answer + cards
        """
        if not question or not question.strip():
            return {
                "answer": "Vui lòng nhập câu hỏi của bạn để TourAI tư vấn nhé!",
                "tours": [],
                "intent": {}
            }

        clean_q = question.strip()

        # Step 1: Question Analysis
        intent = QuestionAnalyzer.analyze_question(clean_q)

        # Step 2: Tour Retrieval
        tours = TourRetriever.retrieve_tours(intent)
        alternatives = []
        if not tours:
            alternatives = TourRetriever.retrieve_alternative_tours(intent)

        # Step 3: Context Building
        context = ContextBuilder.build_context(tours, alternatives)

        # Step 4: Prompt Construction
        prompt = PromptBuilder.build_prompt(clean_q, context)

        # Step 5: Gemini AI Generation
        answer = GeminiService.generate_content(prompt)

        # Step 6: Log chat interaction for analytics and auditing
        try:
            tour_ids_str = ",".join([str(t["id"]) for t in (tours or alternatives)])
            execute_query(
                """INSERT INTO chat_logs 
                (session_id, user_message, intent_json, retrieved_tour_ids, bot_response)
                VALUES (?, ?, ?, ?, ?);""",
                (session_id, clean_q, json.dumps(intent, ensure_ascii=False), tour_ids_str, answer),
                commit=True
            )
        except Exception:
            pass # Non-blocking logging

        displayed_tours = tours if tours else alternatives
        return {
            "answer": answer,
            "tours": displayed_tours,
            "intent": intent
        }

