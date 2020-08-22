## Prepare EmoLex
from os import system
from os.path import isfile
import pandas as pd

if not isfile('NRC - Sentiment Lexicon - Research EULA Sept 2017 .pdf'):
    system('wget http://sentiment.nrc.ca/lexicons-for-research/NRC-Emotion-Lexicon.zip')
    system('unzip NRC-Emotion-Lexicon.zip')
    system('rm NRC-Emotion-Lexicon.zip')

original_df = pd.read_excel('NRC-Emotion-Lexicon-v0.92/NRC-Emotion-Lexicon-v0.92-In105Languages-Nov2017Translations.xlsx') # Open the downloaded Excel file

# For English:
if not isfile('english_emolex.csv'):
    df = original_df[['English (en)', 'Anger', 'Anticipation', 'Disgust', 'Fear', 'Joy', 'Sadness', 'Surprise', 'Trust']]      # Keep only the English tokens and the annotated emotions
    df = df[df[['Anger', 'Anticipation', 'Disgust', 'Fear', 'Joy', 'Sadness', 'Surprise', 'Trust']].sum(axis=1)>0]    # Drop words that does not relate to any emotion
    df.to_csv('english_emolex.csv', index=False) # Save to file

# For Mandarin Chinese:
if not isfile('chinese_emolex.csv'):
    df = original_df[['Chinese (Simplified) (zh-CN)', 'Anger', 'Anticipation', 'Disgust', 'Fear', 'Joy', 'Sadness', 'Surprise', 'Trust']]      # Keep only the Chinese tokens and the annotated emotions
    df.drop_duplicates(subset=['Chinese (Simplified) (zh-CN)'], inplace=True) # translation inbalances
    df = df[df[['Anger', 'Anticipation', 'Disgust', 'Fear', 'Joy', 'Sadness', 'Surprise', 'Trust']].sum(axis=1)>0]    # Drop words that does not relate to any emotion
    df.to_csv('chinese_emolex.csv', index=False) # Save to file

if isfile('NRC - Sentiment Lexicon - Research EULA Sept 2017 .pdf'):
    system('rm -r NRC-Emotion-Lexicon-v0.92/ "NRC - Sentiment Lexicon - Research EULA Sept 2017 .pdf"') # Remove unzipped files