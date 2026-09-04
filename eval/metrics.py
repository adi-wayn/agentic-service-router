from typing import List, Dict, Any


def compute_confusion_matrix(y_true: List[str], y_pred: List[str]) -> Dict[str, Any]:
    classes = ["CONFIDENT_RECOMMENDATION", "NEEDS_CLARIFICATION", "ROUTE_TO_HUMAN"]

    tp = {c: 0 for c in classes}
    fp = {c: 0 for c in classes}
    fn = {c: 0 for c in classes}

    for t, p in zip(y_true, y_pred):
        if t == p:
            if t in tp:
                tp[t] += 1
        else:
            if p in fp:
                fp[p] += 1
            if t in fn:
                fn[t] += 1

    metrics = {}
    f1_scores = []

    for c in classes:
        precision = tp[c] / (tp[c] + fp[c]) if (tp[c] + fp[c]) > 0 else 0.0
        recall = tp[c] / (tp[c] + fn[c]) if (tp[c] + fn[c]) > 0 else 0.0
        f1 = (
            2 * (precision * recall) / (precision + recall)
            if (precision + recall) > 0
            else 0.0
        )

        metrics[c] = {"precision": precision, "recall": recall, "f1": f1}
        f1_scores.append(f1)

    metrics["macro_f1"] = sum(f1_scores) / len(classes)

    # Weighted F1
    total_true = len(y_true)
    weighted_f1 = (
        sum(metrics[c]["f1"] * ((tp[c] + fn[c]) / total_true) for c in classes)
        if total_true > 0
        else 0.0
    )
    metrics["weighted_f1"] = weighted_f1

    return metrics


def compute_safety_metrics(
    y_true_urgency: List[str], y_pred_urgency: List[str]
) -> Dict[str, Any]:
    tp_p1 = 0
    fn_p1 = 0
    fp_p1 = 0
    tn_p1 = 0

    for t, p in zip(y_true_urgency, y_pred_urgency):
        is_true_p1 = t == "P1"
        is_pred_p1 = p == "P1"

        if is_true_p1 and is_pred_p1:
            tp_p1 += 1
        elif is_true_p1 and not is_pred_p1:
            fn_p1 += 1
        elif not is_true_p1 and is_pred_p1:
            fp_p1 += 1
        else:
            tn_p1 += 1

    recall_p1 = tp_p1 / (tp_p1 + fn_p1) if (tp_p1 + fn_p1) > 0 else 1.0
    fnr_p1 = fn_p1 / (tp_p1 + fn_p1) if (tp_p1 + fn_p1) > 0 else 0.0

    standard_errors = fp_p1  # Simplified for cost
    cost_safety = (100 * fn_p1) + (5 * fp_p1) + (1 * standard_errors)

    return {"p1_recall": recall_p1, "p1_fnr": fnr_p1, "cost_safety": cost_safety}


def compute_jaccard_iou(
    expected_missing: List[str], actual_missing: List[str]
) -> float:
    set_expected = set(expected_missing)
    set_actual = set(actual_missing)

    intersection = set_expected.intersection(set_actual)
    union = set_expected.union(set_actual)

    if len(union) == 0:
        return 1.0  # Both empty -> perfect match

    return len(intersection) / len(union)


def compute_calibration(
    y_true_binary: List[int], y_prob: List[float], n_bins: int = 10
) -> Dict[str, float]:
    if not y_prob:
        return {"brier_score": 0.0, "ece": 0.0}

    # Brier Score
    brier = sum((p - t) ** 2 for t, p in zip(y_true_binary, y_prob)) / len(y_prob)

    # ECE
    bins = [[] for _ in range(n_bins)]
    for t, p in zip(y_true_binary, y_prob):
        bin_idx = min(int(p * n_bins), n_bins - 1)
        bins[bin_idx].append((t, p))

    ece = 0.0
    for b in bins:
        if not b:
            continue
        bin_acc = sum(t for t, p in b) / len(b)
        bin_conf = sum(p for t, p in b) / len(b)
        ece += (len(b) / len(y_prob)) * abs(bin_acc - bin_conf)

    return {"brier_score": brier, "ece": ece}


def compute_template_accuracy(y_true_temp: List[str], y_pred_temp: List[str]) -> float:
    if not y_true_temp:
        return 0.0
    correct = sum(1 for t, p in zip(y_true_temp, y_pred_temp) if t == p)
    return correct / len(y_true_temp)


def compute_clarification_metrics(
    loop_counts: List[int],
    expected_missing_list: List[List[str]],
    generated_questions_list: List[List[str]],
) -> Dict[str, Any]:
    """
    Computes CR, MTTR, Question Specificity, and Redundancy Index for cases requiring clarification.
    """
    if not loop_counts:
        return {
            "convergence_rate": 0.0,
            "mttr": 0.0,
            "specificity": 0.0,
            "redundancy": 0.0,
        }

    resolved_count = sum(1 for lc in loop_counts if lc <= 2)
    convergence_rate = resolved_count / len(loop_counts)
    mttr = sum(loop_counts) / len(loop_counts)

    total_questions = 0
    specific_questions = 0
    redundant_questions = 0

    for expected_missing, generated_questions in zip(
        expected_missing_list, generated_questions_list
    ):
        total_questions += len(generated_questions)
        # Simplified specificity/redundancy estimation
        # Specific: targets an expected missing field.
        # Redundant: asks about something already present (i.e. not in expected missing).
        for q in generated_questions:
            # We assume q is mapped to a target_field in the evaluation runner
            if q in expected_missing:
                specific_questions += 1
            else:
                redundant_questions += 1

    specificity = specific_questions / total_questions if total_questions > 0 else 0.0
    redundancy_index = (
        redundant_questions / total_questions if total_questions > 0 else 0.0
    )

    return {
        "loop_convergence_rate": convergence_rate,
        "mean_turns_to_resolution": mttr,
        "question_specificity": specificity,
        "redundancy_index": redundancy_index,
    }
