"""
MINDCARE NER – AI Cognitive Adaptive Difficulty Engine
Using scikit-learn machine learning classification combined with elderly-centered heuristics
to tailor game challenges dynamically without causing cognitive fatigue.

Non-Diagnostic Notice:
MindCare NER is a cognitive assistance and monitoring platform.
It does not replace professional medical diagnosis or treatment.
"""

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

class CognitiveAdaptiveEngine:
    DIFFICULTY_LEVELS = ['EASY', 'MEDIUM', 'HARD']
    DIFF_TO_INT = {'EASY': 1, 'MEDIUM': 2, 'HARD': 3}
    INT_TO_DIFF = {1: 'EASY', 2: 'MEDIUM', 3: 'HARD'}

    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=30, random_state=42)
        self.scaler = StandardScaler()
        self._is_trained = False
        self._train_baseline_model()

    def _train_baseline_model(self):
        """
        Train a scikit-learn classifier on representative cognitive gameplay telemetry.
        Features: [accuracy_percent, completion_time_sec, attempts, current_difficulty_int]
        Target: recommended next difficulty level (1=EASY, 2=MEDIUM, 3=HARD)
        """
        X = []
        y = []

        # Synthetic elderly gameplay profiles calibrated for confidence-building:
        # High accuracy, quick completion -> upgrade
        for acc in [85.0, 90.0, 95.0, 100.0]:
            for time_sec in [10.0, 15.0, 22.0, 30.0]:
                for attempts in [1, 2]:
                    # If currently Easy and doing well -> Medium
                    X.append([acc, time_sec, attempts, 1])
                    y.append(2)
                    # If currently Medium and doing exceptionally well -> Hard
                    if acc >= 90.0 and time_sec <= 25.0 and attempts == 1:
                        X.append([acc, time_sec, attempts, 2])
                        y.append(3)
                    else:
                        X.append([acc, time_sec, attempts, 2])
                        y.append(2)

        # Moderate accuracy (50% - 79%) -> maintain current difficulty
        for acc in [55.0, 65.0, 75.0]:
            for time_sec in [25.0, 40.0, 55.0]:
                for attempts in [1, 2, 3]:
                    X.append([acc, time_sec, attempts, 1])
                    y.append(1)
                    X.append([acc, time_sec, attempts, 2])
                    y.append(2)
                    X.append([acc, time_sec, attempts, 3])
                    y.append(2)

        # Low accuracy (<50%) or high attempts (>3) -> ease difficulty for patient encouragement
        for acc in [20.0, 35.0, 45.0]:
            for time_sec in [40.0, 60.0, 90.0]:
                for attempts in [3, 4, 5]:
                    X.append([acc, time_sec, attempts, 1])
                    y.append(1)
                    X.append([acc, time_sec, attempts, 2])
                    y.append(1)
                    X.append([acc, time_sec, attempts, 3])
                    y.append(2)

        X_arr = np.array(X)
        y_arr = np.array(y)
        X_scaled = self.scaler.fit_transform(X_arr)
        self.model.fit(X_scaled, y_arr)
        self._is_trained = True

    def evaluate(self, performance_data):
        """
        Evaluate performance data (single dict or list of historical dicts).
        Returns a dict with difficulty, confidence, and supportive message.
        """
        if not performance_data:
            return {
                'difficulty': 'EASY',
                'confidence': 1.0,
                'message': 'Starting with comfortable, friendly activities.',
                'status': 'default'
            }

        # Handle list of past attempts by taking weighted recent average
        if isinstance(performance_data, list):
            if len(performance_data) == 0:
                return {
                    'difficulty': 'EASY',
                    'confidence': 1.0,
                    'message': 'Starting with comfortable, friendly activities.',
                    'status': 'default'
                }
            # Give higher weight to most recent game results
            recent = performance_data[-5:]
            weights = np.linspace(0.5, 1.0, len(recent))
            weights /= weights.sum()

            accuracies = [float(r.get('accuracy', 70.0)) for r in recent]
            times = [float(r.get('completion_time', 30.0)) for r in recent]
            attempts_list = [int(r.get('attempts', 1)) for r in recent]

            avg_acc = float(np.average(accuracies, weights=weights))
            avg_time = float(np.average(times, weights=weights))
            avg_attempts = float(np.average(attempts_list, weights=weights))
            current_diff_str = str(recent[-1].get('difficulty', 'EASY')).upper()
        elif isinstance(performance_data, dict):
            avg_acc = float(performance_data.get('accuracy', 70.0))
            avg_time = float(performance_data.get('completion_time', 30.0))
            avg_attempts = float(performance_data.get('attempts', 1))
            current_diff_str = str(performance_data.get('difficulty', 'EASY')).upper()
        else:
            return {
                'difficulty': 'EASY',
                'confidence': 1.0,
                'message': 'Your next activity has been personalized based on your recent performance.',
                'status': 'fallback'
            }

        current_diff_int = self.DIFF_TO_INT.get(current_diff_str, 1)

        # 1. Scikit-learn ML prediction
        try:
            features = np.array([[avg_acc, avg_time, avg_attempts, current_diff_int]])
            features_scaled = self.scaler.transform(features)
            pred_int = int(self.model.predict(features_scaled)[0])
            probabilities = self.model.predict_proba(features_scaled)[0]
            confidence = float(np.max(probabilities))
        except Exception:
            pred_int = current_diff_int
            confidence = 0.75

        # 2. Heuristic safety rules for elderly dementia care:
        # Prevent sudden difficulty spikes; always prioritize patient confidence
        if avg_acc >= 85.0 and avg_attempts <= 2:
            final_int = min(current_diff_int + 1, 3)
            trend_note = 'Great progress! Gently increasing challenge.'
        elif avg_acc < 50.0 or avg_attempts >= 3 or avg_time > 75.0:
            final_int = max(current_diff_int - 1, 1)
            trend_note = 'Easing the pace for a relaxing, supportive experience.'
        else:
            final_int = pred_int
            trend_note = 'Keeping activities comfortable and balanced.'

        final_difficulty = self.INT_TO_DIFF.get(final_int, 'EASY')

        return {
            'difficulty': final_difficulty,
            'confidence': round(confidence, 2),
            'trend': trend_note,
            'message': 'Your next activity has been personalized based on your recent performance.',
            'metrics_evaluated': {
                'average_accuracy': round(avg_acc, 1),
                'average_time_sec': round(avg_time, 1),
                'attempts': round(avg_attempts, 1),
                'previous_difficulty': current_diff_str
            }
        }


# Singleton engine instance
_engine = None

def get_ai_engine():
    global _engine
    if _engine is None:
        _engine = CognitiveAdaptiveEngine()
    return _engine

def calculate_next_difficulty(performance_data):
    """
    Main entry point function required by specification.
    Accepts performance_data and returns difficulty string or rich dictionary.
    """
    engine = get_ai_engine()
    res = engine.evaluate(performance_data)
    return res.get('difficulty', 'EASY')
