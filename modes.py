# modes.py

def mode_strict(votes):
    """Validation par unanimité."""
    return len(set(votes)) == 1

def mode_moyenne(votes):
    """Calcul de la moyenne des votes."""
    if all(isinstance(vote, int) for vote in votes):
        return sum(votes) / len(votes)
    return None

def mode_mediane(votes):
    """Calcul de la médiane des votes."""
    votes_triees = sorted([vote for vote in votes if isinstance(vote, int)])
    if votes_triees:
        mid = len(votes_triees) // 2
        return votes_triees[mid]
    return None

def mode_majorite_absolue(votes):
    """Majorité absolue pour valider une fonctionnalité."""
    from collections import Counter
    counts = Counter(votes)
    majorite = len(votes) // 2
    for vote, count in counts.items():
        if count > majorite:
            return vote
    return None

def mode_majorite_relative(votes):
    """Majorité relative pour valider une fonctionnalité."""
    from collections import Counter
    counts = Counter(votes)
    most_common_vote = counts.most_common(1)[0][0]
    return most_common_vote
