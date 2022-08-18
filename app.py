import time
import streamlit as st
from db_service import DbService
import random
import plotly.express as px
import pandas as pd

##############  PAGE SETUP
st.set_page_config(
    page_title="Tweets Analyzer",
    page_icon="📊",
    layout="wide",
)
##############

dbService = DbService()
dbService.initConnect()


def get_data():
    print(f"New data")
    return dbService.fetch()


def increase():
    global count
    count += 1


# dashboard title
st.title("Real-Time / Live Twitter Analysis")

# filters

# new_filter_placeholder = st.empty()
# new_filter_input = new_filter_placeholder.text_input('Apply new Filter', key=1)
# reset = st.button('Reset Filters', key=3)
# if reset:
#     new_filter_input = new_filter_placeholder.text_input('Apply new Filter', value='', key=2)
#
# if new_filter_input:
#     st.write(new_filter_input)
# else:
#     st.write("No Filters", color='red')
st.write("Showing results for filters: 'India' | 'Inflation' | 'Recession' | 'China' | 'Jobs'")
# creating a single-element container
placeholder = st.empty()

# near real-time / live feed simulation
for seconds in range(200):
    data = []
    if seconds % 2 == 0:
        data = get_data()
        print(f"Rebuilt----- {len(data)}")

    if len(data) > 0:
        total = len(data) if data is not None else 0
        likes = 0
        retweets = 0
        replies = 0
        ref = []
        retweet_list = []
        like_list = []
        tweeted_from_list = []
        sentiments = {}
        languages = {}
        named_entities = {}
        named_entities_num = {}
        ########
        recent_texts = []
        recent_senti = []
        recent_ref = []
        recent_source = []

        recent_data = data[-5:] if len(data) > 5 else data
        for item in recent_data:
            recent_texts.append(item['text'])
            recent_senti.append(item['senti'])
            recent_ref.append(item['ref'])
            recent_source.append(item['source'])

        recent_df = pd.DataFrame(list(zip(recent_texts, recent_ref, recent_senti, recent_source)),
                                 columns=['Tweet', 'Type', 'Sentiment', 'Tweeted from'])

        last_50_data = data[-20:] if len(data) > 20 else data
        for item in last_50_data:
            for key, value in item['ner'].items():
                if len(value) > 0:
                    for val in value:
                        if val not in named_entities:
                            named_entities[val] = 1
                        else:
                            named_entities[val] += 1

        for item in data:
            if item['like'] > 0:
                likes += item['like']
            if item['retweet'] > 0:
                retweets += item['retweet']
            if item['reply'] > 0:
                replies += item['reply']

            ref.append(item['ref'])
            retweet_list.append(item['retweet'] if item['retweet'] > 0 else 0)
            like_list.append(item['like'] if item['like'] > 0 else 0)
            tweeted_from_list.append(item['source'])

            if item['senti'] not in sentiments:
                sentiments[item['senti']] = 1
            else:
                sentiments[item['senti']] += 1

            if item['lang'] not in languages:
                languages[item['lang']] = 1
            else:
                languages[item['lang']] += 1

            for key, value in item['ner'].items():
                if len(value) > 0:
                    if key not in named_entities_num:
                        named_entities_num[key] = len(value)
                    else:
                        named_entities_num[key] += len(value)

        df = pd.DataFrame(list(zip(ref, retweet_list, like_list, tweeted_from_list)),
                          columns=['References', 'Retweets', 'Likes', 'TweetedFrom'])
        with placeholder.container():
            kpi1, kpi2, kpi3, kpi4 = st.columns(4)

            kpi1.metric(
                label="Total",
                value=total,
            )

            kpi2.metric(
                label="Likes",
                value=likes,
            )

            kpi3.metric(
                label="Retweets",
                value=retweets,
                # delta=-round(balance / count_married) * 100,
            )

            kpi4.metric(
                label="Replies",
                value=replies,
                # delta=-round(balance / count_married) * 100,
            )

            # Create two columns for charts
            fig_col1, fig_col2 = st.columns(2)
            with fig_col1:
                st.markdown("### Retweets per tweet type")
                fig = px.density_heatmap(
                    data_frame=df, y="Retweets", x="References"
                )
                st.write(fig)

            with fig_col2:
                st.markdown("### Recently mentioned")
                fig2 = px.bar(x=named_entities.keys(),y=named_entities.values())
                st.write(fig2)

            fig_col3, fig_col4 = st.columns(2)
            with fig_col3:
                st.markdown("### Sentiment distribution")
                fig3 = px.pie(
                    data_frame=df, values=sentiments.values(), names=sentiments.keys(), hole=.3,
                    color_discrete_sequence=px.colors.sequential.RdBu
                )
                st.write(fig3)

            with fig_col4:
                st.markdown("### Language distribution")
                fig4 = px.pie(
                    data_frame=df, values=languages.values(), names=languages.keys(), hole=.3,
                    color_discrete_sequence=px.colors.sequential.Aggrnyl
                )
                st.write(fig4)

            fig_col5, fig_col6 = st.columns(2)
            with fig_col5:
                st.markdown("### Tweet source distribution")
                fig5 = px.density_heatmap(
                    data_frame=df, y="Retweets", x="TweetedFrom"
                )
                st.write(fig5)

            with fig_col6:
                st.markdown("### Talked about Subjects")
                fig6 = px.pie(
                    data_frame=df, values=named_entities_num.values(), names=named_entities_num.keys(), hole=.3,
                    color_discrete_sequence=px.colors.sequential.Viridis
                )
                st.write(fig6)

            # Recent Tweets
            st.subheader('Recent tweets:')

            # CSS to inject contained in a string
            hide_dataframe_row_index = """
                        <style>
                        .row_heading.level0 {display:none}
                        .blank {display:none}
                        </style>
                        """

            # Inject CSS with Markdown
            st.markdown(hide_dataframe_row_index, unsafe_allow_html=True)
            if recent_df is not None:
                st.table(recent_df)
            ### sleep
            time.sleep(5)
