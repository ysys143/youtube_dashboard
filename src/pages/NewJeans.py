from utils import *
from carousel_component import *
import unicodedata

st.set_page_config(page_title="TrendPop", initial_sidebar_state="collapsed", layout="wide")
conn = st.connection('trendpop_db', type='sql', url="mysql+pymysql://trendpop:1234@localhost:3306/trendpop_db")

# session state 선언
page_path = "pages/"
st.session_state['idol_group'] = "NewJeans"
selected_group = st.session_state['idol_group']
def main():
    main_css = """
        <style>
            html, body, [class*="css"] {
                font-size: 20px;
            }
            .main > div {
                padding-left: 12%;
                padding-right: 12%;
            }
        </style>
    """
    st.markdown(main_css, unsafe_allow_html=True)

    # 페이지 타이틀
    st.title('🎩Trend  Pop')
    st.subheader("아티스트")

    artist_widget(1)
    st.divider()

    # 현재 선택된 아이돌 그룹(헤더):
    st.header(selected_group)

    st.subheader("아티스트 감정 지표") # TO-DO: 관심도 지표 만들기
    all_data = fetch_all_data(conn, selected_group)
    group_df = all_data['group_comments']

    with st.container():
        min_date, max_date = get_date_range(group_df[['date']])
        freq_fig = create_frequency_chart(group_df[['Group', 'Title', 'date', 'predicted_label']], date_range=[min_date, max_date])
        sentiment_plot(freq_fig, key= "frequency_chart")
        fig = create_sentiment_chart(group_df[['Group', 'Title', 'date', 'predicted_label']], date_range=[min_date, max_date])
        selected_point = sentiment_plot(fig, key="sentiment_chart")

    st.subheader("Ask Gemini! 이슈 분석")
    if selected_point:
        st.chat_message("assistant").write(
        f"Gemini-1.5-Flash: {selected_group}에게 {selected_point[0]['x']} 기간에 있던 일을 찾아볼까요?")
        ask_button = st.button("Ask Gemini!")
        if ask_button:
            chatbot_response = get_chatbot_response(selected_group, selected_point[0]['x'])
            st.markdown(chatbot_response)
    else:
        st.chat_message("assistant").write(
        f"Gemini-1.5-Flash: 그래프를 클릭해서 {selected_group}에 대해 물어보세요!")

    st.subheader("뮤직비디오")

    mv_info = carousel_component(data=all_data['mv_thumbnail'], layout='default', key='mv_carousel')

    if mv_info is None:
        comment_df = group_df
        st.write("확인할 뮤직비디오를 선택해 주세요")
    else:
        _, col2, _ = st.columns([1, 4, 1])
        col2.video(mv_info['link'])
        encoded_title = unicodedata.normalize('NFD', mv_info['title'])
        mv_df = group_df[group_df['Title'] == encoded_title]
        comment_df = mv_df
        if mv_df.empty:
            st.write(f"No data available for the selected music video: {mv_info['title']}")
        else:
            fig = create_sentiment_chart(mv_df)
            sentiment_plot(fig, key="mv_analysis", click_event=False)

    st.header("그룹/멤버 별 분석")
    if mv_info is None:
        member_thumbnail = all_data['member_thumbnail'][all_data['member_thumbnail']['title'] == 'All']
    else:
        member_thumbnail = all_data['member_thumbnail'][all_data['member_thumbnail']['title'] == encoded_title]

    # 기본 값 설정 (없을 시 오류)
    default_selected_member = {'title': 'All', 'description': "#노래, #류진, #한국인, #사랑해, #채령"}
    selected_member = carousel_component(data=member_thumbnail, layout='alternate', key="member_carousel") or default_selected_member

    filter_col, comment_col = st.columns([1,6])
    with filter_col:
        st.markdown("**필터**")
        key_list = ["없음"]

        if selected_member is not None and 'description' in selected_member:

            member_keys = selected_member['description'].strip('[]').replace("'", "").split(', ')
            key_list.extend(member_keys)

        selected_keyword = st.radio(
            "키워드 필터",
            key_list,
            key="keyword",
            # label_visibility="collapsed"
        )

        selected_sentiment = st.radio(
            "감정 필터",
            ["없음", "긍정", "중립", "부정"],
            key="selected_sentiment",
        )

    with comment_col:
        st.markdown(f"선택된 필터| &ensp;&ensp; 키워드: {selected_keyword} &ensp;&ensp; 감정: {selected_sentiment}")

        if mv_info is None:
            filtered_comments = filter_kpop_comments(
                comment_df,
                member_filter='All' if selected_member['title'] == 'All' else selected_member['title'],
                keyword_filter=selected_keyword[1:],
                sentiment_filter=selected_sentiment
            )
        else:
            filtered_comments = filter_kpop_comments(
                comment_df,
                member_filter='All' if selected_member['title'] == mv_info['title'] else selected_member['title'],
                keyword_filter=selected_keyword[1:],
                sentiment_filter=selected_sentiment
            )

        # shown_comments = shown_comments[['comment', 'likes', 'date']]
        st.dataframe(filtered_comments,use_container_width=True)

if __name__ == '__main__':
    main()