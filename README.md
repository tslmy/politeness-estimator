# Politeness Estimator for Microblogs (Pem)

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/tslmy/politeness-estimator/HEAD?labpath=demo.ipynb)

Pem is a set of pre-trained machine-learning models that predict (im-)politeness scores in texts. The models are trained on annotated microblogs and packaged into a simple Python class for easy use. Currently, two language-microblog pairs are supported:

- English Twitter
- Mandarin Chinese Weibo

The description of the data and training process is part of our paper published at CSCW 2020. 
Preprint: https://arxiv.org/pdf/2008.02449.pdf 

**Looking for source code of analyses, and/or PoliteLex itself? See `src/`.**

**The annotated corpora is available upon request.**

## Installation

1. Install requirements: `pip install -r requirements.txt`
2. If you wish to use LIWC (highly recommended for increased accuracy), 
   1. Put your English LIWC `.dic` file to the same directory as `LIWC2015_Dictionary.dic`.
   2. Convert LIWC dictionary to long form `liwc15.csv` by running `python prepare_liwc.py`.
   3. Rename `liwc15.csv` to `english_liwc15.csv` and repeat this for other languages, if needed.
3. Prepare also the EmoLex lexicon by `python prepare_emolex.py`. Both `english_emolex.csv` and `chinese_emolex.csv` should be generated.

Notice that, due to license concerns, we are unable to provide LIWC in this repository.

## Usage

1. Put microblogs in a CSV file as a column `text`. I have included two toy examples, `tweets.csv` for English Twitter and `weibo.csv` for Mandarin Weibo. **If Chinese, please pre-segment/pre-tokenize posts by whitespace.**
2. In your code:

   ```python
    from pem import Pem # `Pem` is short for "Politeness Estimator for Microblogs".
    pem = Pem(
        liwc_path           ='english_liwc15.csv', # or '' if LIWC is unavailable
        emolex_path         ='english_emolex.csv', 
        estimator_path      ='english_twitter_politeness_estimator.joblib', # or 'english_twitter_politeness_estimator_noLiwc.joblib' if LIWC is unavailable
        feature_defn_path   ='english_twitter_additional_features.pickle')
    pem.load('tweets.csv')
    pem.tokenize()
    pem.vectorize()
    print(pem.predict())
   ```
   
   or, for Mandarin Weibo posts:
   
   ```python
    from pem import Pem # `Pem` is short for "Politeness Estimator for Microblogs".
    pem = Pem(
        liwc_path           ='chinese_liwc15.csv', # or '' if LIWC is unavailable
        emolex_path         ='chinese_emolex.csv', 
        estimator_path      ='chinese_weibo_politeness_estimator.joblib', # or 'chinese_weibo_politeness_estimator_noLiwc.joblib' if LIWC is unavailable
        feature_defn_path   ='chinese_weibo_additional_features.pickle')
    pem.load('weibo.csv')
    pem.tokenize()
    pem.vectorize()
    print(pem.predict())
   ```

We are actively working on understanding sources of bias in classifiers and currently, estimates between -0.5 and 0.5 are treated as neutral. Would love your feedback on how to make this classifer better. Reach out at myli at alumni dot upenn dot edu or sharathg at cis dot upenn dot edu.

## Citation

```
@article{li2020cscw,
  title={Studying Politeness across Cultures Using English Twitter and Mandarin Weibo},
  author={Li, Mingyang and Hickman, Louis and Tay, Louis and Ungar, Lyle and Guntuku, Sharath Chandra},
  journal={Proceedings of the ACM on Human-Computer Interaction},
  number={CSCW},  
  year={2020}
}
```

```
APA
Li, M., Hickman, L., Tay, L., Ungar, L., & Guntuku, S. C. (2020). Studying Politeness across Cultures Using English Twitter and Mandarin Weibo. Proceedings of the ACM on Human-Computer Interaction (CSCW)
```
 
