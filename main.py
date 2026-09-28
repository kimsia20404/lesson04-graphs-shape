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
# 이후 그래프를 추가할 자리
# --------------------------------------------------
# st.divider()
# st.header("그래프 3. ...")
# ...
