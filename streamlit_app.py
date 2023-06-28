import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import re
from upsetplot import UpSet
from upsetplot import from_contents, from_memberships
import collections
from itertools import chain
def heat_map(matrix, threshold=1):
    map_counts = matrix.sum(axis=0)
    map_masks = map_counts <= threshold

    # Drop the columns that have counts less than or equal to the threshold
    matrix = matrix.loc[:, ~map_masks]
    # Compute the correlation matrix
    corr = matrix.corr()

    # Generate a mask for the upper triangle
    masks = np.triu(np.ones_like(corr, dtype=bool))

    # Set up the matplotlib figure
    f, ax = plt.subplots(figsize=(11, 9))

    # Generate a custom diverging colormap
    cmap = sns.diverging_palette(230, 20, as_cmap=True)

    # Draw the heatmap with the mask and correct aspect ratio
    sns.heatmap(corr, mask=masks, cmap=cmap, vmax=.3, center=0,
                square=True, linewidths=.5, cbar_kws={"shrink": .5})


def upset_plot(lists, threshold=1):
    counter = collections.Counter(chain.from_iterable(lists))
    filtered_lists = [[item for item in sublist if counter[item] > threshold] for sublist in lists]
    data = from_memberships(filtered_lists)
    upset = UpSet(data, subset_size="count", show_counts=True)
    upset.plot()

def add_numbers_on_bars(plot):
    for p in plot.patches:
        width = p.get_width()
        plot.text(width+1, p.get_y()+0.55*p.get_height(),
             '{:1.0f}'.format(width),
             ha='left', va='center')



st.title("Application Analyize Dashboard")


# uploaded_file = st.file_uploader("Choose a file", type="xlsx")
# if uploaded_file is not None:
df = pd.read_excel("Application Data analysis .xlsx", engine='openpyxl')


st.markdown("# 1. Analyzing Applicants' Interests")
interest_column = df["Which track(s) of work will you be interested in? (Select as many as you are interested in)."]
interests_matrix = pd.DataFrame()
interests_lists = []
for i, interests in interest_column.iterrows():
    interests = re.sub(r'\(.*?\)', '', interests)
    interests = interests.split(",")
    temp = []
    for interest in interests:
        interest = interest.strip()
        if "video editing" in interest.lower() or "video" in interest.lower():
            interest = "Video editing"
        interests_matrix.loc[i, interest] = 1
        temp.append(interest)
    interests_lists.append(temp)
# fill NaN with 0
interest_counts = interests_matrix.sum(axis=0).sort_values(ascending=False)
THRESHOLD = 1
masks = interest_counts <= THRESHOLD
interest_counts.index = np.where(masks, "Others", interest_counts.index)
interest_counts = interest_counts.groupby(interest_counts.index).sum().sort_values(ascending=False)


st.markdown("## 1.1. UpSet Plot of Interests")
plt.figure(figsize=(15, 15))
upset_plot(interests_lists, threshold=1)
st.pyplot(plt)

st.markdown("## 1.2. Pie Plot of Interests")
plt.figure(figsize=(10, 10))
plt.pie(interest_counts, labels=interest_counts.index, autopct='%1.1f%%')
plt.title("Interests of the applicants")
st.pyplot(plt)


st.markdown("# 2. Analyzing Applicants' Status")
status_column = df["What are the following statements can describe you status?"]
status_matrix = pd.DataFrame()
status_lists = []
for i, status in status_column.iterrows():
    status = re.sub(r'\(.*?\)', '', status)
    temp = []
    if ", I am currently working " in status:
        status = status.split(",")
        for s in status:
            s = s.replace("I am currently working ", "")
            s = s.replace("I am currently a ", "")
            s = s.replace("i am a ", "")
            s = s.replace("I am", "")
            s = s.strip()
            status_matrix.loc[i, s] = 1
            temp.append(s)
    else:
        status = status.replace("I am currently working ", "")
        status = status.replace("I am currently a ", "")
        status = status.replace("i am a ", "")
        status = status.replace("I am", "")
        status = status = status.strip()
        status_matrix.loc[i, status] = 1
        temp.append(status)
    status_lists.append(temp)
# fill NaN with 0
status_matrix = status_matrix.fillna(0)
status_counts = status_matrix.sum(axis=0).sort_values(ascending=False)
status_threshold = st.slider("Status Threshold", 0, 10, 1)
masks = status_counts <= status_threshold
status_counts.index = np.where(masks, "Others", status_counts.index)
status_counts = status_counts.groupby(status_counts.index).sum().sort_values(ascending=False)

st.markdown("## 2.1. Bar Plot of Status")
plt.figure(figsize=(10, 8))
sns_plot = sns.barplot(x=status_counts.values, y=status_counts.index, orient='h')
plt.title("Status Counts")
plt.xlabel("Count")
plt.ylabel("Status")
add_numbers_on_bars(sns_plot)
st.pyplot(plt)

st.markdown("## 2.2. _UpSet_ of Status")

plt.figure(figsize=(15, 15))
upset_plot(status_lists, threshold=status_threshold)
st.pyplot(plt)

st.markdown("# 3. Analyzing Applicants' Demographic Indicators")
indicators_column = df["[Optional] To comply with government reporting requirements, please indicate which demographic indicators apply to you by checking the appropriate boxes below."]
indicators_column = indicators_column.astype(str)
indicators_matrix = pd.DataFrame()
indicators_lists = []
for i, indicators in indicators_column.iterrows():
    indicators = indicators.split(",")
    temp = []
    for indicator in indicators:
        # # Fix some typos
        if "Landed in Canada or become a Canadian Canadian Citizen in the past 5 years" in indicator:
            indicator = "Landed in Canada or become a Canadian Citizen in the past 5 years"
        if "Landed in Canada or become a Canadian Citizen in the past 5 years" in indicator:
            indicator = "Landed in Canada or become a Canadian citizen in the past 5 years"
        if indicator == "nan":
            indicator = "No Entry"
        # if "Foreign student" in category:
        #     indicator = "International student"
        indicator = indicator.strip()
        indicators_matrix.loc[i, indicator] = 1
        temp.append(indicator)
    indicators_lists.append(temp)
# fill NaN with 0
indicators_matrix = indicators_matrix.fillna(0)
indicators_counts = indicators_matrix.sum(axis=0).sort_values(ascending=False)
indicators_threshold = st.slider("Indicators Threshold", 0, 10, 1)
masks = indicators_counts <= indicators_threshold
indicators_counts.index = np.where(masks, "Other Indicators", indicators_counts.index)
indicators_counts = indicators_counts.groupby(indicators_counts.index).sum().sort_values(ascending=False)

st.markdown("## 3.1. Bar Plot of Indicators")
plt.figure(figsize=(10,8))
sns_plot = sns.barplot(x=indicators_counts.values, y=indicators_counts.index, orient='h')
plt.title("Indicators Counts")
plt.xlabel("Count")
plt.ylabel("Indicators")
add_numbers_on_bars(sns_plot)
st.pyplot(plt)

# the heat_map becomes:
st.markdown("## 3.2. Heat Map of Indicators")
plt.figure(figsize=(10,10))
heat_map(indicators_matrix)
st.pyplot(plt)


# Wordcloud
st.markdown("# 4. Analyzing Applicants' Goals")
import nltk
from nltk.corpus import stopwords
from wordcloud import WordCloud
# download modules from nltk
nltk.download('stopwords')
nltk.download('punkt')
# code goes as before
stop_words = set(stopwords.words('english')) 
# extend the stop words
extra_stop_words = ['please', "canada", 'would', 'like', 'also', "get", 'could', "new", 'may', 'thank', 'thanks', 'much', 'really', 'many', "want", "able", "use", "well", "different", "make", "understanding"]
stop_words= stop_words.union(extra_stop_words)
# join all the responses and lower the case
text = ' '.join(df['What are the goals you hope to achieve or skills you want to develop through National Youth Service Network? '].str.lower())
# tokenize the text
tokens = nltk.word_tokenize(text)
# remove stopwords and non-alphabetic tokens
words = [word for word in tokens if word.isalpha() and word not in stop_words]
freq_dist = nltk.FreqDist(words)
number_of_words = st.slider("Number of Words", 0, 100, 50)
st.markdown("## Word Frequency")
freq_df = pd.DataFrame(freq_dist.most_common(number_of_words), columns=['Word', 'Count'])
st.dataframe(freq_df)

# create a word cloud
wordcloud = WordCloud(width=800, height=500, random_state=21, max_font_size=110, background_color='white').generate_from_frequencies(dict(freq_dist.most_common(number_of_words)))
# the word cloud becomes:
plt.figure(figsize=(10, 7))
plt.imshow(wordcloud, interpolation="bilinear")
plt.axis('off')
st.pyplot(plt)