import re
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class FinBertSentimentWorker:
    """
    Financial sentiment scoring engine powered by ProsusAI/finbert (BERT architecture
    fine-tuned on Financial PhraseBank).
    Processes financial news headlines and articles to produce contextual sentiment,
    confidence metrics, key takeaways, and market impact analysis with MPS/CPU acceleration.
    """

    BULLISH_KEYWORDS = [
        "growth", "surge", "climb", "profit", "gain", "expansion", "record",
        "dividend", "upgrade", "outperform", "rally", "robust", "accommodative",
        "beat", "higher", "approval", "win", "contract", "clearance", "resilient",
        "inflow", "stabilize", "accretion", "order", "eir", "turnaround", "lead",
    ]

    BEARISH_KEYWORDS = [
        "fall", "drop", "decline", "cautious", "loss", "headwind", "delay",
        "defer", "scrutiny", "inflation", "cut", "downgrade", "weak", "slump",
        "deficit", "debt", "curb", "constraint", "underperform", "volatility",
        "contraction", "warning", "slowdown", "investigation", "fine", "penalty",
    ]

    def __init__(self):
        self._model = None
        self._tokenizer = None
        self._device = None
        self._id2label = {}
        self._model_load_attempted = False

    def _load_model(self):
        if self._model_load_attempted:
            return
        self._model_load_attempted = True

        try:
            import torch
            from transformers import AutoTokenizer, AutoModelForSequenceClassification

            if torch.backends.mps.is_available():
                self._device = torch.device("mps")
            elif torch.cuda.is_available():
                self._device = torch.device("cuda")
            else:
                self._device = torch.device("cpu")

            model_name = "ProsusAI/finbert"
            try:
                self._tokenizer = AutoTokenizer.from_pretrained(model_name, local_files_only=True)
                self._model = AutoModelForSequenceClassification.from_pretrained(model_name, local_files_only=True).to(self._device)
            except Exception:
                self._tokenizer = AutoTokenizer.from_pretrained(model_name)
                self._model = AutoModelForSequenceClassification.from_pretrained(model_name).to(self._device)

            self._model.eval()
            self._id2label = {int(k): str(v).lower() for k, v in self._model.config.id2label.items()}
            logger.info("FinBERT neural model initialized on device: %s", self._device)
        except Exception as exc:
            logger.warning("FinBERT neural model load failed (%s); using lexical analyzer fallback.", exc)
            self._model = None
            self._tokenizer = None

    def analyze(self, title: str, text: str = "") -> Dict[str, Any]:
        full_text = f"{title}. {text}".strip()
        combined = full_text.lower()

        bullish_matches = [w for w in self.BULLISH_KEYWORDS if re.search(r"\b" + re.escape(w) + r"\b", combined)]
        bearish_matches = [w for w in self.BEARISH_KEYWORDS if re.search(r"\b" + re.escape(w) + r"\b", combined)]

        # Extract structured takeaways from text
        sentences = [s.strip() for s in text.replace("\n", ". ").split(".") if len(s.strip()) > 20]
        if not sentences and title:
            sentences = [title]
        key_takeaways = sentences[:3] if len(sentences) >= 3 else sentences

        # Attempt neural FinBERT inference
        self._load_model()
        if self._model is not None and self._tokenizer is not None:
            try:
                import torch

                inputs = self._tokenizer(
                    full_text,
                    return_tensors="pt",
                    truncation=True,
                    max_length=512,
                ).to(self._device)

                with torch.no_grad():
                    outputs = self._model(**inputs)
                    probs = torch.nn.functional.softmax(outputs.logits, dim=-1)[0]

                pred_idx = int(torch.argmax(probs).cpu())
                label = self._id2label.get(pred_idx, "neutral")
                sentiment = label.capitalize()
                confidence = round(float(probs[pred_idx].cpu()), 2)

                pos_idx = next((k for k, v in self._id2label.items() if v == "positive"), 0)
                neg_idx = next((k for k, v in self._id2label.items() if v == "negative"), 1)
                pos_prob = float(probs[pos_idx].cpu())
                neg_prob = float(probs[neg_idx].cpu())

                if sentiment == "Positive":
                    score = round(max(0.10, pos_prob - neg_prob), 2)
                    market_impact = (
                        f"Constructive momentum driven by {', '.join(bullish_matches[:3]) if bullish_matches else 'solid performance'}; "
                        f"supportive of equity valuations (FinBERT confidence: {int(confidence * 100)}%)."
                    )
                elif sentiment == "Negative":
                    score = round(min(-0.10, pos_prob - neg_prob), 2)
                    market_impact = (
                        f"Near-term cautious bias reflecting {', '.join(bearish_matches[:3]) if bearish_matches else 'market headwinds'}; "
                        f"potential volatility in affected sectors (FinBERT confidence: {int(confidence * 100)}%)."
                    )
                else:
                    score = round(pos_prob - neg_prob, 2)
                    market_impact = (
                        "Balanced market impact with steady baseline realizations and neutral near-term outlook "
                        f"(FinBERT confidence: {int(confidence * 100)}%)."
                    )

                return {
                    "sentiment": sentiment,
                    "sentiment_score": score,
                    "sentiment_confidence": confidence,
                    "key_takeaways": key_takeaways,
                    "market_impact": market_impact,
                }
            except Exception as e:
                logger.warning("FinBERT inference error (%s); falling back to heuristic scoring.", e)

        # Robust lexical fallback
        bullish_count = len(bullish_matches)
        bearish_count = len(bearish_matches)
        total_signals = bullish_count + bearish_count

        if total_signals == 0:
            score = 0.05
            sentiment = "Neutral"
            confidence = 0.82
        elif bullish_count > bearish_count:
            ratio = bullish_count / total_signals
            score = round(0.40 + (ratio * 0.50), 2)
            sentiment = "Positive"
            confidence = round(0.85 + (min(bullish_count, 5) * 0.02), 2)
        elif bearish_count > bullish_count:
            ratio = bearish_count / total_signals
            score = round(-0.35 - (ratio * 0.45), 2)
            sentiment = "Negative"
            confidence = round(0.84 + (min(bearish_count, 5) * 0.02), 2)
        else:
            score = 0.02
            sentiment = "Neutral"
            confidence = 0.80

        if sentiment == "Positive":
            market_impact = f"Constructive momentum driven by {', '.join(bullish_matches[:3]) if bullish_matches else 'solid performance'}; supportive of equity valuations."
        elif sentiment == "Negative":
            market_impact = f"Near-term cautious bias reflecting {', '.join(bearish_matches[:3]) if bearish_matches else 'market headwinds'}; potential volatility in affected sectors."
        else:
            market_impact = "Balanced market impact with steady baseline realizations and neutral near-term outlook."

        return {
            "sentiment": sentiment,
            "sentiment_score": score,
            "sentiment_confidence": confidence,
            "key_takeaways": key_takeaways,
            "market_impact": market_impact,
        }


finbert_worker = FinBertSentimentWorker()
