import pandas as pd

test_data = {
    "text": [
        "thanks so much for this awesome politeness predictor @tslmy",
        "RT @tslmy: fuck you. This thing is completely garbage.",
    ]
}

want_emolex_cnts_df = {
    "Disgust": {0: 0, 1: 1},
}

want_politelex_cnts_df = {
    "you_direct": {0: 0, 1: 1},
    "gratitude": {0: 1, 1: 0},
    "taboo": {0: 0, 1: 1},
    "praise": {0: 1, 1: 0},
}

from pem import Pem


def test_pem():
    # Set up a fixture:
    pem = Pem(
        liwc_path="",
        estimator_path="english_twitter_politeness_estimator_noLiwc.joblib",
        feature_defn_path="english_twitter_additional_features.pickle",
    )
    pem.df = pd.DataFrame(test_data)
    pem.tokenize().vectorize()

    # Assertions:
    criteria = pem.emolex_cnts_df.sum() > 0
    got = pem.emolex_cnts_df.loc[:, criteria].to_dict()
    assert got == want_emolex_cnts_df

    criteria = pem.politelex_cnts_df.sum() > 0
    got = pem.politelex_cnts_df.loc[:, criteria].to_dict()
    assert got == want_politelex_cnts_df

    labels = pem.predict()
    assert labels[0] == "Neutral"
    assert labels[1] == "Neutral"
