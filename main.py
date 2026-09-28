import pandas as pd
import plotly.express as px
import streamlit as st

# --------------------------------------------------
# 기본 설정
# --------------------------------------------------
st.set_page_config(
    page_title="영화 데이터 그래프 도감 2 - 분포와 관계",
    page_icon="🎬",
    layout="wide",
)

st.title("영화 데이터 그래프 도감 2 - 분포와 관계")
st.write(
    "1년간 박스오피스 10위권에 든 영화 가운데, "
    "이 기간에 개봉한 216편의 요약 데이터를 살펴봅니다."
)

DATA_URL = "https://raw.githubusercontent.com/happykth/data/main/kobis_movies.csv"


# --------------------------------------------------
# 데이터 불러오기
# --------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL)

    # 장르가 여러 개 있으면 첫 번째 장르만 사용
    df["genre"] = (
        df["genre"]
        .fillna("미분류")
        .astype(str)
        .str.split("|")
        .str[0]
        .str.strip()
    )

    # 장르가 비어 있는 경우 표시할 이름
    df.loc[df["genre"].isin(["", "nan", "None"]), "genre"] = "미분류"

    # 총 관객 수를 숫자로 변환
    df["total_audi"] = (
        df["total_audi"]
        .astype(str)
        .str.replace(",", "", regex=False)
        .str.strip()
    )
    df["total_audi"] = pd.to_numeric(df["total_audi"], errors="coerce").fillna(0)

    # 개봉일 스크린 수를 숫자로 변환
    df["first_scrn"] = (
        df["first_scrn"]
        .astype(str)
        .str.replace(",", "", regex=False)
        .str.strip()
    )
    df["first_scrn"] = pd.to_numeric(df["first_scrn"], errors="coerce").fillna(0)

    # 개봉 첫 주 관객 수를 숫자로 변환
    df["first_week_audi"] = (
        df["first_week_audi"]
        .astype(str)
        .str.replace(",", "", regex=False)
        .str.strip()
    )
    df["first_week_audi"] = pd.to_numeric(
        df["first_week_audi"], errors="coerce"
    ).fillna(0)

    return df


try:
    df = load_data()
except Exception as e:
    st.error("데이터를 불러오지 못했습니다.")
    st.info(
        "인터넷 연결 상태와 데이터 주소를 확인한 뒤 다시 실행해 주세요."
    )
    st.caption(f"오류 내용: {e}")
    st.stop()


# --------------------------------------------------
# 그래프 1. 장르별 영화 편수
# --------------------------------------------------
st.divider()
st.header("그래프 1. 장르별 영화 편수")

genre_counts = (
    df["genre"]
    .value_counts()
    .rename_axis("장르")
    .reset_index(name="편수")
)

fig1 = px.pie(
    genre_counts,
    names="장르",
    values="편수",
    hole=0.55,
    title="장르별 영화 편수",
)

fig1.update_traces(
    hovertemplate=(
        "<b>%{label}</b><br>"
        "편수: %{value}편<br>"
        "비율: %{percent}"
        "<extra></extra>"
    )
)

fig1.update_layout(
    legend_title_text="장르",
    margin=dict(t=60, b=20, l=20, r=20),
)

st.plotly_chart(fig1, use_container_width=True)

st.text_input(
    "이 그래프로 알 수 있는 것",
    placeholder="한 문장으로 적어 보세요.",
    key="graph1_caption",
)

st.caption("💡 여러 장르가 적힌 영화는 첫 번째 장르만 집계했습니다.")


# --------------------------------------------------
# 그래프 2. 장르 안의 영화 트리맵
# --------------------------------------------------
st.divider()
st.header("그래프 2. 장르 안에 들어 있는 영화")

fig2 = px.treemap(
    df,
    path=["genre", "movieNm"],
    values="total_audi",
    title="장르별 영화 총 관객 트리맵",
)

fig2.update_traces(
    hovertemplate=(
        "영화명: %{label}<br>"
        "총 관객: %{value:,.0f}명"
        "<extra></extra>"
    )
)

fig2.update_layout(
    margin=dict(t=60, b=20, l=20, r=20),
)

st.plotly_chart(fig2, use_container_width=True)

st.text_input(
    "이 그래프로 알 수 있는 것",
    placeholder="한 문장으로 적어 보세요.",
    key="graph2_caption",
)




# --------------------------------------------------
# 그래프 3. 총 관객 히스토그램
# --------------------------------------------------
st.divider()
st.header("그래프 3. 총 관객 분포")

fig3 = px.histogram(
    df,
    x="total_audi",
    nbins=20,
    title="영화별 총 관객 분포",
    labels={"total_audi": "총 관객", "count": "영화 편수"},
)

fig3.update_traces(
    hovertemplate=(
        "총 관객 구간: %{x}<br>"
        "영화 편수: %{y}편"
        "<extra></extra>"
    )
)

fig3.update_layout(
    xaxis_title="총 관객",
    yaxis_title="영화 편수",
    margin=dict(t=60, b=20, l=20, r=20),
)

st.plotly_chart(fig3, use_container_width=True)

# 가장 많은 영화가 속한 구간 계산
hist_counts, bin_edges = pd.cut(
    df["total_audi"],
    bins=20,
    include_lowest=True,
    retbins=True,
)
bin_counts = hist_counts.value_counts().sort_index()
most_common_bin = bin_counts.idxmax()

# 총 관객이 가장 많은 영화 계산
top_movie = df.loc[df["total_audi"].idxmax(), "movieNm"]
top_audi = int(df["total_audi"].max())

st.markdown(
    f"""
**이 그래프로 알 수 있는 것**  
대부분의 영화는 **{most_common_bin.left:,.0f}명 ~ {most_common_bin.right:,.0f}명**의 총 관객 구간에 몰려 있습니다.

가장 관객이 많은 영화는 **{top_movie}**으로, 총 관객은 **{top_audi:,}명**입니다.
"""
)




# --------------------------------------------------
# 그래프 4. 개봉일 스크린 수와 총 관객의 관계
# --------------------------------------------------
st.divider()
st.header("그래프 4. 개봉일 스크린 수와 총 관객")

fig4 = px.scatter(
    df,
    x="first_scrn",
    y="total_audi",
    color="genre",
    hover_name="movieNm",
    title="개봉일 스크린 수와 총 관객의 관계",
    labels={
        "first_scrn": "개봉일 스크린수",
        "total_audi": "총 관객",
        "genre": "장르",
    },
)

fig4.update_traces(
    hovertemplate=(
        "영화명: %{hovertext}<br>"
        "개봉일 스크린수: %{x:,}개<br>"
        "총 관객: %{y:,}명"
        "<extra></extra>"
    )
)

fig4.update_layout(
    xaxis_title="개봉일 스크린수",
    yaxis_title="총 관객",
    margin=dict(t=60, b=20, l=20, r=20),
)

st.plotly_chart(fig4, use_container_width=True)

st.text_input(
    "이 그래프로 알 수 있는 것",
    placeholder="한 문장으로 적어 보세요.",
    key="graph4_caption",
)




# --------------------------------------------------
# 그래프 5. 장르별 총 관객 상자 그림
# --------------------------------------------------
st.divider()
st.header("그래프 5. 장르별 총 관객 분포")

# 영화가 10편 이상인 장르만 선택
genre_movie_counts = df["genre"].value_counts()
selected_genres = genre_movie_counts[genre_movie_counts >= 10].index
box_df = df[df["genre"].isin(selected_genres)].copy()

fig5 = px.box(
    box_df,
    x="genre",
    y="total_audi",
    points="outliers",
    custom_data=["movieNm"],
    title="영화가 10편 이상인 장르의 총 관객 분포",
    labels={
        "genre": "장르",
        "total_audi": "총 관객",
    },
)

# 상자 밖의 이상치 점에 영화명이 표시되도록 설정
fig5.update_traces(
    hovertemplate=(
        "영화명: %{customdata[0]}<br>"
        "총 관객: %{y:,}명"
        "<extra></extra>"
    )
)

fig5.update_layout(
    xaxis_title="장르",
    yaxis_title="총 관객",
    margin=dict(t=60, b=20, l=20, r=20),
)

st.plotly_chart(fig5, use_container_width=True)

st.text_input(
    "이 그래프로 알 수 있는 것",
    placeholder="한 문장으로 적어 보세요.",
    key="graph5_caption",
)




# --------------------------------------------------
# 그래프 6. 개봉일 스크린 수와 총 관객의 버블 그래프
# --------------------------------------------------
st.divider()
st.header("그래프 6. 개봉일 스크린 수와 총 관객 - 버블 그래프")

fig6 = px.scatter(
    df,
    x="first_scrn",
    y="total_audi",
    size="first_week_audi",
    color="genre",
    hover_name="movieNm",
    custom_data=["movieNm", "first_scrn", "total_audi", "first_week_audi"],
    size_max=55,
    title="개봉일 스크린 수와 총 관객의 관계",
    labels={
        "first_scrn": "개봉일 스크린수",
        "total_audi": "총 관객",
        "first_week_audi": "첫 주 관객",
        "genre": "장르",
    },
)

fig6.update_traces(
    hovertemplate=(
        "영화명: %{customdata[0]}<br>"
        "개봉일 스크린수: %{customdata[1]:,}개<br>"
        "총 관객: %{customdata[2]:,}명<br>"
        "첫 주 관객: %{customdata[3]:,}명"
        "<extra></extra>"
    )
)

fig6.update_layout(
    xaxis_title="개봉일 스크린수",
    yaxis_title="총 관객",
    margin=dict(t=60, b=20, l=20, r=20),
)

st.plotly_chart(fig6, use_container_width=True)

st.text_input(
    "이 그래프로 알 수 있는 것",
    placeholder="한 문장으로 적어 보세요.",
    key="graph6_caption",
)




# --------------------------------------------------
# 그래프 7. 제작 국가 → 장르 선버스트
# --------------------------------------------------
st.divider()
st.header("그래프 7. 제작 국가에서 장르로 내려가는 영화 분포")

# 국가·장르별 영화 편수 계산
sunburst_df = (
    df.assign(편수=1)
    .groupby(["nation", "genre"], as_index=False)["편수"]
    .sum()
)

# 비어 있는 제작 국가는 미분류로 표시
sunburst_df["nation"] = (
    sunburst_df["nation"]
    .fillna("미분류")
    .astype(str)
    .str.strip()
    .replace("", "미분류")
)

# 비어 있는 장르는 미분류로 표시
sunburst_df["genre"] = (
    sunburst_df["genre"]
    .fillna("미분류")
    .astype(str)
    .str.strip()
    .replace("", "미분류")
)

fig7 = px.sunburst(
    sunburst_df,
    path=["nation", "genre"],
    values="편수",
    title="제작 국가 → 장르별 영화 편수",
)

fig7.update_traces(
    hovertemplate=(
        "<b>%{label}</b><br>"
        "영화 편수: %{value}편"
        "<extra></extra>"
    )
)

fig7.update_layout(
    margin=dict(t=60, b=20, l=20, r=20),
)

st.plotly_chart(fig7, use_container_width=True)

st.text_input(
    "이 그래프로 알 수 있는 것",
    placeholder="한 문장으로 적어 보세요.",
    key="graph7_caption",
)


# --------------------------------------------------
# 이후 그래프를 추가할 자리
# --------------------------------------------------
# st.divider()
# st.header("그래프 3. ...")
# ...
