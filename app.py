import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import re
import plotly.express as px
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from streamlit import columns

st.set_page_config(layout="wide",page_title="Startup Analysis")



df = pd.read_csv("cleanest_startup(1).csv")
df["Investor"] = df["Investor"].str.replace(r'[\\]+','',regex=True)
df["Investor"] = df["Investor"].str.split(r"and|&").explode().reset_index(drop=True)
df = df[df["Investor"] != ""]
df["Investor"] = df["Investor"].fillna("Undisclosed")



def load_investor(investors):
    st.markdown(f"<h1 style='text-align: center;'>{investors}</h1>", unsafe_allow_html=True)
    st.markdown("##### Most recent investment")
    st.dataframe(df[df["Investor"].str.contains(investors)].head()[
        ["Date", "Startup", "Vertical","City","Type", "Amount in cr"]])
    col1, col2 = st.columns(2)

    with (col1):
        st.markdown("#### Biggest investment")
        big = df[df["Investor"].str.contains(investors)].groupby("Startup")["Amount in cr"
            ].sum().sort_values(ascending=False).head()
        fig = px.bar(big,x=big.index,y=big.values,labels={"y":"Amount in cr"})
        event = st.plotly_chart(fig,on_select="rerun")

    with (col2):
        st.markdown("#### Sector invested in")
        sector = df[df["Investor"].str.contains(investors)].groupby("Vertical")["Amount in cr"
            ].sum().sort_values(ascending=False)
        fig1 = px.pie(sector,values=sector.values,hover_name=sector.index
                        ,color_discrete_sequence=px.colors.sequential.RdBu)
        fig1.update_traces(textfont_size=8)
        st.plotly_chart(fig1)

    col3, col4 = st.columns(2)

    with (col3):
        st.markdown("#### Stage of investment")
        stage = df[df["Investor"].str.contains(investors)].groupby("Type")["Amount in cr"
            ].sum().sort_values(ascending=False)
        fig2 = px.pie(stage,values=stage.values,hover_name=stage.index)
        st.plotly_chart(fig2)

    with (col4):
        st.markdown("#### City where invested")
        city = df[df["Investor"].str.contains(investors)].groupby("City")["Amount in cr"
            ].sum().sort_values(ascending=False)
        fig3 = px.bar(city,x=city.index,y=city.values,labels={"y":"Amount in cr"})
        st.plotly_chart(fig3)

    st.markdown("#### Year on Year Investment")
    yoy = df[df["Investor"].str.contains(investors)].groupby("year")["Amount in cr"].sum()
    fig4 = px.line(yoy,x=yoy.index,y=yoy.values,labels={"y":"Amount in cr"})
    st.plotly_chart(fig4)

    investor_profiles = df.groupby("Investor").agg({
        "Startup": lambda x: " ".join(x),
        "Vertical": lambda x: " ".join(x)
    }).reset_index()
    investor_profiles["profile_text"] = investor_profiles["Startup"] + " " + investor_profiles["Vertical"]
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(investor_profiles["profile_text"])
    cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)
    indices = pd.Series(investor_profiles.index, index=investor_profiles["Investor"]).drop_duplicates()
    def get_similar_investors(investor, top_n=5):
        if investor not in indices:
            return f"Investor '{investor}' not found."
        idx = indices[investor]
        sim_scores = list(enumerate(cosine_sim[idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        sim_scores = sim_scores[1:top_n + 1]
        investor_indices = [i[0] for i in sim_scores]
        return investor_profiles.iloc[investor_indices]["Investor"].tolist()
    target_investor = investors
    similar_investors = get_similar_investors(target_investor, top_n=3)
    st.markdown("#### Top 3 similar investors:")
    for inv in similar_investors:
       st.write(inv)




def load_startup(startup):
    st.markdown(f"<h1 style='text-align: center;'>{startup}</h1>", unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown("##### Founding Investor:")
        date = df[df["Startup"].str.contains(startup)]["Date"].tail(1).iloc[0]
        filtered_df = df[df["Startup"].str.contains(startup) & (df["Date"] == date)]
        st.dataframe(filtered_df["Investor"].values)
    with col3:
        st.markdown("##### SubVertical:")
        st.dataframe(df[df["Startup"].str.contains(startup)]["SubVertical"].dropna().unique())
    with col2:
        st.markdown("##### Industry Vertical:")
        st.dataframe(df[df["Startup"].str.contains(startup)]["SubVertical"].dropna().unique())
    with col4:
        st.markdown("##### City Location:")
        st.dataframe(df[df["Startup"].str.contains(startup)]["City"].dropna().unique())

    funding_rounds = df.groupby("Startup").agg({"Type": list, "Investor": list,"Date": lambda x:
                                                    [pd.to_datetime(d).strftime('%Y-%m-%d') for d in
                                                     sorted(x.dropna())]}).reset_index()
    funding_rounds["Funding Details"] = funding_rounds.apply(
                                                    lambda row: sorted(zip(row["Date"],
                                                    row["Type"], row["Investor"])), axis=1)
    funding_rounds["Total_funding_round"] = funding_rounds["Date"].apply(len)
    st.markdown("### Funding Round")
    st.dataframe(funding_rounds[funding_rounds["Startup"].isin([startup])].explode(["Investor","Date","Type",
                                                         "Funding Details"])[["Investor","Date","Type","Funding "
                                                        "Details"]].reset_index(drop=True))
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("##### Total Funding:")
        money = df.groupby("Startup")["Amount in cr"].sum()[startup]
        st.markdown(f"######  {money} crore")
    with col2:
        st.markdown("##### Total Funding Round:")
        st.markdown(f"###### {funding_rounds[funding_rounds["Startup"].isin([startup])]["Total_funding_round"].values}")
    with col3:
        st.markdown("##### Funding Types:")
        st.markdown(f"###### {str(df.groupby("Startup").agg({"Type":lambda x : set(x)}).loc[startup,:].values)}")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("##### Year On Year Funding:")
        yoy = df[df["Startup"].str.contains(startup)].groupby("year")["Amount in cr"].sum()
        fig = px.line(yoy,x=yoy.index,y=yoy.values,labels={"y":"Amount in cr"})
        st.plotly_chart(fig)
    with col2:
        st.markdown("##### Top Investors:")
        top = df[df["Startup"] == startup].groupby("Investor")["Amount in cr"].sum()
        fig1 = px.bar(top,x=top.index,y=top.values,labels={"y":"Amount in cr"})
        st.plotly_chart(fig1)



def load_overall_analysis():
    title = "General  Analysis"
    st.markdown(f"<h1 style='text-align: center;'>{title}</h1>", unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown("#### Total Funding:")
        st.markdown(f"###### {round(df["Amount in cr"].unique().sum())} crore")
    with col2:
        st.markdown("#### Max Funding:")
        st.markdown(f"###### {round(df.drop_duplicates(subset=["Startup","Amount in cr"]).
                                    groupby("Startup")["Amount in cr"].max().sort_values
                                    (ascending=False).values[0])} crore")
    with col3:
        st.markdown("#### Average Funding:")
        st.markdown(f"###### {round(df.drop_duplicates(subset=["Startup","Amount in cr"])
                                    .groupby("Startup")["Amount in cr"].sum().mean())} crore")
    with col4:
        st.markdown("#### Total Startup:")
        st.markdown(f"{df["Startup"].nunique()}")

    st.markdown("#### Month On Month Chart:")
    typ = st.selectbox("Select Type",["Total investment","Total Startup"],key="selectbox1")
    if typ=="Total Startup":
        start = df.groupby(["month", "year"])["Startup"].count().reset_index().sort_values(["year", "month"],
                                                                                           ascending=False)
        start["x-axis"] = start["month"].astype(str) + "-" + start["year"].astype(str)
        fig = px.line(start, x="x-axis", y="Startup")
        st.plotly_chart(fig)
    else:
        start = df.groupby(["month", "year"])["Amount in cr"].sum().reset_index().sort_values(["year", "month"],
                                                                                            ascending=False)
        start["x-axis"] = start["month"].astype(str) + "-" + start["year"].astype(str)
        fig = px.line(start,x="x-axis",y="Amount in cr")
        st.plotly_chart(fig)

    st.markdown("#### Stage Type Analysis:")
    alpha = st.selectbox("Select Type",["Total investment","Total Startup","Investment Types"],key="selectbox2")
    if alpha=="Total investment":
        sector = (df.drop_duplicates(subset=["Startup","Amount in cr"]).groupby("Type")["Amount in cr"].sum()
                  .sort_values(ascending=False))
        fig2 = px.pie(sector,values=sector.values,names=sector.index,labels={"values":"Amount in cr"},title="Total Investment Stage wise")
        st.plotly_chart(fig2)
    elif alpha=="Investment Types":
        sector = df.drop_duplicates(subset=["Startup", "Amount in cr"])["Type"].value_counts()
        fig2 = px.bar(sector, y=sector.values, x=sector.index, labels={"y": "count"},
                      title="Distribution of Investment Types",log_y=True,color=sector.index)
        st.plotly_chart(fig2)
    else:
        sector = (df.drop_duplicates(subset=["Startup", "Amount in cr"]).groupby("Type")["Startup"].count()
                  .sort_values(ascending=False))
        fig2 = px.pie(sector, values=sector.values, names=sector.index, labels={"values": "Number of Startup"}
                      ,color_discrete_sequence=px.colors.sequential.RdBu,title="Total Startup Stage wise")
        st.plotly_chart(fig2)

    st.markdown("### Top 20 City Funding Wise :")
    city = (df.drop_duplicates(subset=["Startup","Amount in cr"]).groupby("City")["Amount in cr"]
            .sum().sort_values(ascending=False).head(20))
    fig3 = px.bar(city,x=city.index,y=city.values,labels={"y":"Amount in cr"},log_y=True)
    st.plotly_chart(fig3)

    st.markdown("### Overall Top 20 Startup Funding Wise:")
    startup = (df.drop_duplicates(subset=["Startup","Amount in cr"]).groupby("Startup")["Amount in cr"]
               .sum().sort_values(ascending=False)).head(20)
    fig4 = px.bar(startup, x=startup.index, y=startup.values, labels={"y": "Amount in cr"}, log_y=True)
    st.plotly_chart(fig4)

    st.markdown("### Top Startup Year Wise:")
    starter = (df.drop_duplicates(subset=["Startup","Amount in cr"]).groupby(["Startup","year"])["Amount in cr"]
               .sum().reset_index().sort_values(ascending=[False,False], by=["year","Amount in cr"],axis=0)
               .drop_duplicates(subset="year",keep="first"))
    fig5 = px.pie(starter,values="Amount in cr",names="year")
    st.plotly_chart(fig5)

    st.markdown("### Top 20 Investors:")
    invest = (df.drop_duplicates(subset=["Startup","Amount in cr"]).groupby("Investor")["Amount in cr"]
              .sum().sort_values(ascending=False).reset_index()).head(20)
    fig6 = px.bar(invest, x="Investor", y="Amount in cr")
    st.plotly_chart(fig6)

    st.markdown("### Top Investor Year Wise:")
    investment = (df.drop_duplicates(subset=["Investor", "Amount in cr"]).groupby(["Investor", "year"])["Amount in cr"]
     .sum().reset_index().sort_values(ascending=[False, False], by=["year", "Amount in cr"], axis=0)
     .drop_duplicates(subset="year", keep="first"))
    fig7 = px.pie(investment, names="Investor", values="Amount in cr",color_discrete_sequence=px.colors.sequential.RdBu)
    st.plotly_chart(fig7)

st.sidebar.title("Startup Funding Analysis")
option = st.sidebar.selectbox("Select one",["Overall Analysis","Startup","Investor"])

if option == "Startup":
    startups = st.sidebar.selectbox("Select one",sorted(df["Startup"].unique().tolist()))
    btn1 = st.sidebar.button("Startup Details")
    if btn1:
        load_startup(startups)

elif option == "Investor":
    investor = st.sidebar.selectbox("Select one",sorted(set(df["Investor"].fillna("Undisclosed"))))
    btn2 = st.sidebar.button("Investor detail")
    if btn2:
        load_investor(investor)

else:
    load_overall_analysis()