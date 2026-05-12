# Semantic Analysis Textbook Information

## 1. Sentiment Analysis via BERT (Bidirectional Encoder Representations from Transformers)
**Concept:** Sentiment analysis is the computational identification and categorization of opinions expressed in a piece of text, especially in order to determine whether the writer's attitude towards a particular topic, product, etc., is positive, negative, or neutral.
**Application:** Using models like `nlptown/bert-base-multilingual-uncased-sentiment`, text can be classified on a 1-5 scale. By normalizing these scores, we can plot an "emotional arc" or "valence score" representing how the emotional tone shifts throughout a message.

## 2. Semantic Entropy (Shannon Entropy in Linguistics)
**Concept:** In information theory, entropy measures the unpredictability or information content of a message. Shannon Entropy ($H$) is calculated as:
$$ H = - \sum_{i} p_i \log_2(p_i) $$
Where $p_i$ is the probability of a token (word) occurring in a given text segment.
**Application:** High entropy indicates a higher density of unique words (a more complex, unpredictable, or "fresh" message). Low entropy indicates formulaic, repetitive, or cliché phrasing. In forensic linguistics, higher entropy during conflict resolution can imply higher cognitive load and effort, whereas low entropy may indicate "social autopilot" or standard platitudes.

## 3. Linguistic Forensic Synthesis
**Concept:** This is the practice of combining quantitative linguistic metrics (like sentiment valence and entropy) with qualitative contextual analysis to understand the hidden psychological or social dynamics of a communication event (e.g., transitioning a relationship from a Zero-Sum Conflict to a Cooperative Nash Equilibrium).
**Application:** By feeding the numerical NLP outputs into a Large Language Model (LLM), we synthesize a human-readable interpretation that highlights the strategic use of language (e.g., "Negative Face Redress").
