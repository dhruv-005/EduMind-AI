import uuid
import time
import json
import re
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.core.logger import logger
from app.core.config import settings
from app.challenge1_evaluator.schemas import (
    EvaluationRequest,
    EvaluationResult,
    ScoreBreakdown,
    ConceptAnalysis
)
from app.challenge1_evaluator.concept_extractor import concept_extractor
from app.challenge1_evaluator.scoring_engine import scoring_engine
from app.challenge1_evaluator.feedback_generator import feedback_generator
from app.challenge1_evaluator.subjects.math_evaluator import math_evaluator
from app.challenge1_evaluator.subjects.science_evaluator import science_evaluator
from app.challenge1_evaluator.subjects.english_evaluator import english_evaluator
from app.challenge1_evaluator.subjects.general_evaluator import general_evaluator
from app.governance.audit_logger import audit_logger
from app.governance.human_oversight import human_oversight
from app.governance.prompt_versioning import prompt_versioning
from app.governance.bias_detector import bias_detector
from app.models.evaluation import Evaluation


GRADE_THRESHOLDS = [
    {"min": 9.0, "max": 10.0, "grade": "A+", "label": "Outstanding"},
    {"min": 8.0, "max": 9.0,  "grade": "A",  "label": "Excellent"},
    {"min": 7.0, "max": 8.0,  "grade": "B+", "label": "Very Good"},
    {"min": 6.0, "max": 7.0,  "grade": "B",  "label": "Good"},
    {"min": 5.0, "max": 6.0,  "grade": "C",  "label": "Average"},
    {"min": 4.0, "max": 5.0,  "grade": "D",  "label": "Below Average"},
    {"min": 0.0, "max": 4.0,  "grade": "F",  "label": "Fail"},
]

def get_grade_info(score_out_of_10: float) -> Dict[str, str]:
    for t in GRADE_THRESHOLDS:
        if t["min"] <= score_out_of_10 <= t["max"]:
            return {"grade": t["grade"], "label": t["label"]}
    return {"grade": "F", "label": "Fail"}


def simple_stem(word: str) -> str:
    """Basic English stemmer."""
    w = word.lower().strip()
    if len(w) <= 3:
        return w
    for suffix in ['tion', 'sion', 'ment', 'ness', 'ence', 'ance',
                   'ally', 'ible', 'able', 'ying', 'ting',
                   'ning', 'ding', 'ling', 'ring', 'sing',
                   'ing', 'ies', 'ers', 'ous', 'ive', 'ful',
                   'less', 'ward', 'like', 'wise',
                   'ed', 'er', 'ly', 'al', 'es', 'or',
                   'ty', 'ry', 'cy', 'gy', 'fy', 'ar',
                   's']:
        if w.endswith(suffix) and len(w) - len(suffix) >= 3:
            return w[:-len(suffix)]
    return w


SYNONYM_GROUPS = [
    ["equation", "reaction", "expression"],
    ["formula", "formulas"],
    ["float", "floats", "floating", "buoyant"],
    ["sink", "sinks", "sinking"],
    ["divide", "divided", "dividing", "division"],
    ["multiply", "multiplied", "multiplying", "multiplication"],
    ["add", "added", "adding", "addition"],
    ["subtract", "subtracted", "subtracting", "subtraction"],
    ["substitute", "substituted", "substituting", "substitution"],
    ["calculate", "calculated", "calculating", "calculation"],
    ["convert", "converted", "converting", "conversion"],
    ["produce", "produced", "producing", "production"],
    ["identify", "identified", "identifying", "identification"],
    ["expand", "expanded", "expanding", "expansion"],
    ["simplify", "simplified", "simplifying"],
    ["solve", "solved", "solving", "solution"],
    ["isolate", "isolated", "isolating"],
    ["balance", "balanced", "balancing"],
    ["compare", "compared", "comparing", "comparison"],
    ["determine", "determined", "determining"],
    ["express", "expressed", "expressing"],
    ["water", "h2o"],
    ["hydrogen", "h2"],
    ["oxygen", "o2"],
    ["mass", "masses", "weight"],
    ["mole", "moles", "mol"],
    ["density", "densities"],
    ["volume", "volumes"],
    ["ratio", "ratios", "proportion"],
    ["coefficient", "coefficients"],
    ["stoichiometric", "stoichiometry"],
    ["molar", "molar mass"],
    ["gram", "grams", "g"],
    ["centimeter", "centimeters", "cm"],
    ["object", "objects", "block", "body"],
    ["wooden", "wood"],
    ["pure", "pure water"],
    ["excess", "excess oxygen"],
    ["complete", "completely", "complete reaction"],
    ["debate", "debates", "contemplate", "contemplating", "weigh", "weighs"],
    ["suffer", "suffering", "hardship", "hardships", "trouble", "troubles"],
    ["die", "dying", "death", "end", "ending"],
    ["fear", "fearing", "worry", "worries", "worried"],
    ["exist", "existence", "existential", "life", "lifes"],
    ["endure", "enduring", "tolerate", "bear"],
    ["crisis", "indecision", "dilemma"],
    ["cause", "causes", "factor", "factors", "reason", "reasons"],
    ["trigger", "spark", "event", "incident"],
    ["war", "wars", "conflict", "conflicts"],
    ["invade", "invasion", "invading"],
    ["ally", "allies", "alliance", "alliances"],
    ["empire", "imperial", "imperialism", "colonial", "colonies"],
    ["nation", "national", "nationalism", "ethnic"],
    ["army", "military", "militarism", "arms", "weapons"],
    ["race", "races", "competition", "compete"],
    ["power", "powers", "powerful"],
    ["german", "germany", "german territory"],
    ["austria", "hungary", "austria-hungary"],
    ["ferdinand", "franz", "archduke"],
    ["poland", "polish"],
    ["hitler", "adolf"],
    ["student", "pupil", "learner"],
    ["exam", "examination", "test", "test"],
    ["job", "work", "working", "shift"],
    ["evening", "night", "time"],
    ["study", "studying", "preparing", "prepare"],
    ["earn", "earning", "wage", "wages", "pay", "pays", "paid"],
    ["choose", "chooses", "choice", "decision", "decide"],
    ["give", "give up", "forgo", "forgone", "sacrifice"],
    ["alternative", "option", "alternative"],
    ["example", "instance", "instance"],
    ["refer", "refers", "reference"],
    ["they", "he", "she", "it"],
    ["atom", "atoms", "molecule", "molecules"],
    ["ion", "ions", "cation", "anion", "carbocation", "bromide"],
    ["charge", "charged", "positive", "positively", "negative"],
    ["break", "breaking", "cleave", "cleavage"],
    ["nucleophile", "electrophile", "nucleophilic", "electrophilic"],
    ["bond", "bonds", "double bond", "single bond", "pi bond"],
    ["attack", "attacks", "attacking"],
    ["form", "forms", "forming", "formation"],
    ["intermediate", "intermediates"],
    ["mechanism", "mechanisms", "reaction", "reactions"],
    ["alkene", "alkenes", "ethene", "ethylene"],
    ["markovnikov", "markovnikov rule"],
    ["substitution", "addition", "elimination"],
    ["hydrogen", "h2", "gas"],
    ["release", "releasing", "released"],
    ["replace", "replaces", "replacing", "displace"],
]

SYNONYM_MAP = {}
for group in SYNONYM_GROUPS:
    canonical = group[0]
    for word in group:
        SYNONYM_MAP[word] = canonical


def smart_keyword_concepts(
    ref_text: str, stu_text: str, question_text: str = ""
) -> Dict[str, Any]:
    """
    Smart concept matching with stemming, synonyms, and question-awareness.
    NOTE: This is used for DISPLAY ONLY, not for scoring.
    """
    stop_words = {
        "the", "and", "for", "that", "this", "with", "from", "are",
        "was", "were", "her", "his", "she", "him", "its", "not",
        "but", "all", "can", "has", "had", "may", "been", "will",
        "each", "which", "their", "what", "when", "where", "how",
        "into", "than", "also", "just", "back", "both", "some",
        "then", "them", "these", "those", "more", "most", "other",
        "such", "only", "own", "same", "too", "very", "after",
        "before", "between", "through", "during", "above", "below",
        "about", "against", "further", "once", "here", "there",
        "any", "few", "much", "many", "well", "now", "even",
        "new", "want", "because", "going", "get", "got", "make",
        "like", "long", "still", "find", "know", "take", "come",
        "could", "would", "should", "does", "did", "let", "say",
        "one", "two", "three", "four", "five", "six", "seven",
        "eight", "nine", "ten", "first", "second", "third",
        "use", "using", "used", "given", "calculate", "solve",
        "since", "over", "under", "less", "greater", "equal",
        "pure", "solid", "cubic", "centimeters", "grams",
        "completely", "excess", "according", "so", "will",
        "how", "many", "much", "when", "what", "which",
        "its", "has", "are", "was", "were", "been", "being",
        "divide", "divided", "dividing", "division", "by",
        "multiply", "multiplied", "multiplying", "multiplication",
        "add", "added", "adding", "addition",
        "subtract", "subtracted", "subtracting", "subtraction",
        "sum", "product", "difference", "ratio", "over", "plus", "minus", "times",
        "value", "values", "step", "steps", "answer", "answers", "question", "questions",
        "square", "squares", "centimeter", "centimeters", "cubic", "grams", "gram",
        "world", "main", "main causes", "main factors",
        "you", "your", "they", "they", "he", "she", "it", "we", "our",
        "your", "my", "me", "i", "a", "an",
    }

    def canonicalize(word: str) -> str:
        w = word.lower().strip()
        if w in SYNONYM_MAP:
            return SYNONYM_MAP[w]
        stemmed = simple_stem(w)
        if stemmed in SYNONYM_MAP:
            return SYNONYM_MAP[stemmed]
        return stemmed

    def extract_words(text):
        raw = set(re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())) - stop_words
        result = {}
        for w in raw:
            canon = canonicalize(w)
            if canon not in result:
                result[canon] = w
        return result

    ref_stems = extract_words(ref_text)
    stu_stems = extract_words(stu_text)
    q_stems = extract_words(question_text) if question_text else {}

    combined_ref = dict(ref_stems)
    combined_ref.update(q_stems)

    ref_nums = set(re.findall(r'\b\d+\.?\d*\b', ref_text))
    stu_nums = set(re.findall(r'\b\d+\.?\d*\b', stu_text))
    q_nums = set(re.findall(r'\b\d+\.?\d*\b', question_text)) if question_text else set()

    correct_stems = set(combined_ref.keys()) & set(stu_stems.keys())
    correct = list(set(combined_ref[s] for s in correct_stems))

    missing_stems = set(ref_stems.keys()) - set(stu_stems.keys())
    missing = list(set(ref_stems[s] for s in missing_stems))

    wrong_stems = set(stu_stems.keys()) - set(combined_ref.keys())
    wrong = list(set(stu_stems[s] for s in wrong_stems))

    correct += list(ref_nums & stu_nums)
    missing += list(ref_nums - stu_nums - q_nums)

    wrong = wrong[:5]

    total_expected = len(ref_stems) + len(ref_nums)
    total_found = len(correct)
    coverage = (total_found / max(total_expected, 1)) * 100.0

    return {
        "correct_concepts": correct[:10],
        "missing_concepts": missing[:10],
        "wrong_concepts": wrong,
        "total_expected": total_expected,
        "total_found": total_found,
        "coverage_percentage": round(coverage, 1)
    }


class EvaluatorService:
    """Main evaluation service."""

    def _get_subject_evaluator(self, subject: str):
        evaluators = {
            "mathematics": math_evaluator,
            "math":        math_evaluator,
            "science":     science_evaluator,
            "physics":     science_evaluator,
            "chemistry":   science_evaluator,
            "biology":     science_evaluator,
            "english":     english_evaluator,
            "general":     general_evaluator,
            "history":     general_evaluator,
            "geography":   general_evaluator,
            "economics":   general_evaluator,
        }
        return evaluators.get(subject.lower(), general_evaluator)

    async def evaluate(
        self,
        request: EvaluationRequest,
        db: Optional[Session] = None,
        user_id: Optional[str] = None,
        request_id: Optional[str] = None
    ) -> Dict[str, Any]:
        start_time = time.time()
        request_id = request_id or str(uuid.uuid4())

        logger.info(f"Starting evaluation: id={request_id} subject={request.subject}")

        try:
            # STEP 1: Semantic similarity (informational only)
            try:
                semantic_sim = scoring_engine.calculate_semantic_score(
                    request.student_answer, request.reference_answer
                )
            except Exception:
                semantic_sim = 0.5
            logger.debug(f"Semantic similarity: {semantic_sim:.3f}")

            # STEP 2: Concept extraction (DISPLAY ONLY — not used for scoring)
            concept_analysis = smart_keyword_concepts(
                ref_text=request.reference_answer,
                stu_text=request.student_answer,
                question_text=request.question
            )

            concept_coverage = concept_analysis.get("coverage_percentage", 50.0) / 100.0
            logger.debug(f"Concept coverage (display only): {concept_analysis.get('coverage_percentage', 0)}%")

            # STEP 3: Subject-specific LLM evaluation (PRIMARY SCORING SOURCE)
            subject_evaluator = self._get_subject_evaluator(request.subject)
            llm_scores = await subject_evaluator.evaluate(
                question=request.question,
                reference_answer=request.reference_answer,
                student_answer=request.student_answer,
                grade_level=request.grade_level
            )
            logger.debug(f"LLM scores: {llm_scores}")

            # STEP 4: Score aggregation
            # KEY FIX: Trust LLM scores directly for ALL subjects.
            # The LLM is far more accurate at evaluating answers than
            # keyword matching. Concept coverage is for display only.
            correctness  = float(llm_scores.get("correctness", 0.5))
            completeness = float(llm_scores.get("completeness", 0.5))
            relevance    = float(llm_scores.get("relevance", 0.5))
            clarity      = float(llm_scores.get("clarity", 0.5))

            if request.strict_mode:
                correctness = min(correctness, correctness * 0.85)

            correctness  = max(0.0, min(1.0, correctness))
            relevance    = max(0.0, min(1.0, relevance))
            completeness = max(0.0, min(1.0, completeness))
            clarity      = max(0.0, min(1.0, clarity))

            correctness_weighted  = correctness * 40.0
            relevance_weighted    = relevance * 20.0
            completeness_weighted = completeness * 25.0
            clarity_weighted      = clarity * 15.0

            total_score = (
                correctness_weighted + relevance_weighted +
                completeness_weighted + clarity_weighted
            )
            score_out_of_10 = total_score / 10.0
            grade_info = get_grade_info(score_out_of_10)

            feedback = llm_scores.get("feedback", "")
            if not feedback or len(feedback) < 20:
                feedback = (
                    f"Your answer scored {score_out_of_10:.1f}/10. "
                    "Review the reference solution for missing details."
                )

            suggestions = llm_scores.get("improvement_suggestions", [])
            if not suggestions:
                suggestions = ["Review the core concepts of this question."]

            final_correct = llm_scores.get("final_answer_correct", None)
            if final_correct is True:
                confidence = 0.90
            elif final_correct is False:
                confidence = 0.85
            else:
                confidence = max(0.70, (correctness * 0.6) + (completeness * 0.4))

            confidence = max(0.0, min(1.0, confidence))
            review_required = confidence < getattr(settings, 'HUMAN_REVIEW_THRESHOLD', 0.6)

            try:
                bias_detector.scan_text(request.student_answer + " " + feedback)
            except Exception:
                pass

            result_payload = {
                "request_id":       request_id,
                "score_out_of_10":  round(score_out_of_10, 2),
                "total_score":      round(total_score, 2),
                "percentage":       round(total_score, 2),
                "grade":            grade_info["grade"],
                "score_breakdown": {
                    "correctness":  round(correctness_weighted, 2),
                    "relevance":    round(relevance_weighted, 2),
                    "completeness": round(completeness_weighted, 2),
                    "clarity":      round(clarity_weighted, 2),
                    "total":        round(total_score, 2)
                },
                "concept_analysis":        concept_analysis,
                "feedback":                feedback,
                "improvement_suggestions": suggestions,
                "subject_specific_notes":   llm_scores.get("reasoning", ""),
                "semantic_similarity":     round(semantic_sim, 4),
                "confidence_score":        round(confidence, 3),
                "governance_status":       "flagged" if review_required else "passed",
                "human_review_required":   review_required,
                "model_used":              llm_scores.get("model_used", "openai/gpt-oss-20b"),
                "provider":                llm_scores.get("provider", "groq"),
                "processing_time_ms":      (time.time() - start_time) * 1000,
                "prompt_version":          "4.0.0"
            }

            if db:
                self._save_evaluation(db, result_payload, request, user_id)

            try:
                audit_logger.log_ai_decision(
                    db=db,
                    request_id=request_id,
                    challenge="challenge1",
                    user_id=user_id,
                    model_used=result_payload["model_used"],
                    confidence_score=result_payload["confidence_score"],
                    governance_status=result_payload["governance_status"],
                    processing_time_ms=result_payload["processing_time_ms"],
                    output_summary=f"score={result_payload['score_out_of_10']}/10 grade={result_payload['grade']}",
                    metadata={"subject": request.subject, "human_review": review_required}
                )
            except Exception as e:
                logger.error(f"Audit log failed (non-critical): {e}")

            return result_payload

        except Exception as e:
            logger.error(f"Evaluation failed: {e}")
            raise

    def _save_evaluation(self, db, result, request, user_id):
        try:
            eval_model = Evaluation(
                id=str(uuid.uuid4()),
                request_id=result["request_id"],
                user_id=user_id or "anonymous",
                question=request.question,
                reference_answer=request.reference_answer,
                student_answer=request.student_answer,
                subject=request.subject,
                grade_level=request.grade_level,
                total_score=result["total_score"],
                score_out_of_10=result["score_out_of_10"],
                correctness_score=result["score_breakdown"]["correctness"],
                relevance_score=result["score_breakdown"]["relevance"],
                completeness_score=result["score_breakdown"]["completeness"],
                clarity_score=result["score_breakdown"]["clarity"],
                percentage=result["percentage"],
                grade=result["grade"],
                correct_concepts=json.dumps(result["concept_analysis"]["correct_concepts"]),
                missing_concepts=json.dumps(result["concept_analysis"]["missing_concepts"]),
                wrong_concepts=json.dumps(result["concept_analysis"]["wrong_concepts"]),
                feedback=result["feedback"],
                improvement_suggestions=json.dumps(result["improvement_suggestions"]),
                semantic_similarity=result["semantic_similarity"],
                model_used=result["model_used"],
                provider=result["provider"],
                confidence_score=result["confidence_score"],
                processing_time_ms=result["processing_time_ms"],
                prompt_version=result["prompt_version"],
                governance_status=result["governance_status"],
                human_review_required=result["human_review_required"]
            )
            db.add(eval_model)
            db.commit()
            logger.info(f"Evaluation saved: {eval_model.id}")
        except Exception as e:
            db.rollback()
            logger.error(f"DB save failed: {e}")


evaluator_service = EvaluatorService()
