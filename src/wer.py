import re

def normalize_text(text):
    """Normalize text by converting to lowercase and removing punctuation."""
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)
    return text

def wer(reference, hypothesis):
    """Calculating the Word Error Rate (WER) between reference and hypothesis texts."""
    ref_words = normalize_text(reference).split()
    hyp_words = normalize_text(hypothesis).split()

    # Initializing the matrix
    d = [[0] * (len(hyp_words) + 1) for _ in range(len(ref_words) + 1)]

    # Filling the first row and column
    for i in range(len(ref_words) + 1):
        d[i][0] = i
    for j in range(len(hyp_words) + 1):
        d[0][j] = j

    # Compute the edit distance
    for i in range(1, len(ref_words) + 1):
        for j in range(1, len(hyp_words) + 1):
            if ref_words[i - 1] == hyp_words[j - 1]:
                cost = 0
            else:
                cost = 1
            d[i][j] = min(d[i - 1][j] + 1,      # Deletion
                           d[i][j - 1] + 1,      # Insertion
                           d[i - 1][j - 1] + cost)  # Substitution

    # The WER is the edit distance divided by the number of words in the reference
    wer_value = d[len(ref_words)][len(hyp_words)] / len(ref_words) if ref_words else float('inf')
    return wer_value


if __name__ == "__main__":
    ref = "this is a test"
    hyp = "this is test"
    print(wer(ref, hyp))