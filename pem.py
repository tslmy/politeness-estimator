import pandas as pd
import joblib
import re
from ekphrasis.classes.preprocessor import TextPreProcessor
from ekphrasis.classes.tokenizer import SocialTokenizer
from collections import Counter

# The following are for specifying typing information:
from pandas.core.series import Series
from typing import Set, Union, List
from re import Pattern

# This shortcut performs faster than `pd.concat`:
concat = pd.np.concatenate


class Pem:
    '''
    Politeness Estimator for Microblogs.
    Typing information was done via:

    ```shell
    monkeytype run __init__.py
    monkeytype apply pem
    ```
    '''
    
    threshold = 0.5
    use_liwc = False
    use_cntVec = False
    def __init__(self,
                 liwc_path: str='',
                 emolex_path: str='english_emolex.csv',
                 estimator_path: str='english_twitter_politeness_estimator.joblib',
                 feature_defn_path: str='english_twitter_additional_features.pickle',
                 countVectorizer_path: str='') -> None:
        # Preload LIWC dictionary:
        if liwc_path:
            liwc_df = pd.read_csv(liwc_path)
            liwc_df['*'] = liwc_df['term'].str.endswith('*')
            liwc_df['t'] = liwc_df['term'].str.rstrip('*')
            self.liwc_prefx = liwc_df[liwc_df['*']
                                      ].groupby('category')['t'].apply(set)
            self.liwc_whole = liwc_df[~liwc_df['*']
                                      ].groupby('category')['t'].apply(set)
            self.use_liwc = True

        # Preload EmoLex dictionary:
        emolex_df = pd.read_csv(emolex_path, index_col=0)
        self.emolex = emolex_df.apply(lambda s: set(s[s == 1].index))

        # Preload additional feature rules:
        pltlex = pd.read_pickle(feature_defn_path)
        types = pltlex.apply(type)
        self.pltlex_ptn = pltlex[types == re.Pattern].to_dict()
        self.pltlex_set = pltlex[types == set].to_dict()

        # Initialize Tokenizer:
        self.text_processor = TextPreProcessor(
            # terms that will be normalized:
            normalize=['url', 'email', 'percent', 'money', 'phone', 'user',
                       'time', 'url', 'date', 'number'],
            # terms that will be annotated:
            annotate={"hashtag", "allcaps", "elongated", "repeated",
                      'emphasis', 'censored'},
            # perform word segmentation on hashtags:
            unpack_hashtags=False,
            # Unpack contractions (can't -> can not):
            unpack_contractions=True,
            tokenizer=SocialTokenizer(lowercase=True).tokenize,)
        # preload classifier:
        self.clf = joblib.load(estimator_path)
        
        if countVectorizer_path:
            self.counter = joblib.load(countVectorizer_path)
            self.use_cntVec = True

    def load(self, filepath: str='tweets.csv'):
        self.df = pd.read_csv(filepath)
        return self

    def _tokenizeString(self, s: str) -> List[str]:
        '''
        _tokenizeString tokenizes a string.
        Interestingly, it is faster to put this call into a separate method like this.
        '''
        return self.text_processor.pre_process_doc(s)

    def tokenize(self):
        self.df['token'] = self.df['text'].apply(self._tokenizeString)
        self.df['token_cnts'] = self.df['token'].apply(Counter)
        return self

    def vectorizeByLiwc(self, cnts: dict, liwc_whole: dict, liwc_prefx: dict) -> Series:
        '''Vectorize by LIWC'''
        result = self.countAcrossDicts(cnts, liwc_whole)

        for category, tokens in liwc_prefx.items():
            for j, n_appearance in cnts.items():
                n_prefixes = sum(map(j.startswith, tokens))
                result[category] += n_appearance * n_prefixes

        return pd.Series(result)

    def vectorizeByEmolex(self, cnts: dict, lex: dict) -> Series:
        '''Vectorize by EmoLex'''
        result = self.countAcrossDicts(cnts, lex)
        return pd.Series(result)

    def vectorizeByPoliteLex(self, r: Series, patterns: dict, sets: dict) -> Series:
        '''Vectorize by PoliteLex'''
        result = self.countAcrossDicts(r['token_cnts'], sets)

        text = r['text']
        for feature_name, pattern in patterns.items():
            # Slightly faster than `sum(1 for m in pattern.finditer(text))`.
            result[feature_name] = len(pattern.findall(text))

        return pd.Series(result)

    @staticmethod
    def countAcrossDicts(cnts: dict, sets: dict) -> dict:
        result = {}
        # This native-Python implementation is faster than DataFrame multiplication.
        for feature_name, tokens in sets.items():
            tokens_seen = tokens.intersection(cnts)
            result[feature_name] = sum(cnts[token] for token in tokens_seen)
        return result

    def vectorize(self, debug=True):
        '''
        This function extracts features from the provided texts.
        It requires that `self.df` is already prepared.
        It writes the prepared features to `self.X`.
        '''
        if self.use_liwc:
            liwc_cnts_df = self.df['token_cnts'].apply(
                self.vectorizeByLiwc, liwc_whole=self.liwc_whole, liwc_prefx=self.liwc_prefx)
        emolex_cnts_df = self.df['token_cnts'].apply(
            self.vectorizeByEmolex, lex=self.emolex)
        politelex_cnts_df = self.df.apply(
            self.vectorizeByPoliteLex, patterns=self.pltlex_ptn, sets=self.pltlex_set, axis=1)

        if self.use_cntVec:
            # Unigrams:
            space_separated_texts = self.df['token'].apply(' '.join)
            unigram_matrix = self.counter.transform(space_separated_texts)
            unigram_matrix = unigram_matrix.todense()

        if debug:
            if self.use_liwc: self.liwc_cnts_df = liwc_cnts_df
            self.emolex_cnts_df = emolex_cnts_df.astype(int)
            self.politelex_cnts_df = politelex_cnts_df
            if self.use_cntVec: 
                self.space_separated_texts = space_separated_texts
                self.unigram_df = pd.DataFrame(unigram_matrix, index=self.df.index)

        # Combine all feature sets into one table:
        all_feats = [
            emolex_cnts_df,
            politelex_cnts_df, 
        ]
        if self.use_liwc:
            all_feats.insert(0, liwc_cnts_df)
        if self.use_cntVec:
            all_feats.append(unigram_matrix)
        self.X = concat(all_feats, axis=1)
        return self

    def predict(self) -> Series:
        def scoreToLabel(score):
            if score<-self.threshold:
                return 'Rude'
            if score>self.threshold:
                return 'Polite'
            return 'Neutral'
        scores = self.predict_proba()
        labels = scores.apply(scoreToLabel).rename('label')
        return labels
    def predict_proba(self) -> Series:
        probs = self.clf.predict_proba(self.X)
        probs_df = pd.DataFrame(probs)
        scores = probs_df.loc[:,1]-probs_df.loc[:,0]
        
        # Zero out scores that is too insignificant:
        scores = scores.apply(lambda x: 0 if -self.threshold<x<self.threshold else x)
        
        return scores.rename('score')
