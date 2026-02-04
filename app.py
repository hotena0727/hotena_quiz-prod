    st.divider()

    # ============================================================
    # ✅ 자주 틀린 단어 TOP10 (최근 50회 기준) - A안(카드+진행바)
    # ============================================================
    st.divider()
    st.markdown("### ❌ 자주 틀린 단어 TOP10 (최근 50회)")

    # ✅ A안 카드 렌더링 함수(이 블록 안에 같이 둬도 되고, 위쪽 유틸 영역으로 빼도 됨)
    def render_top_wrong_words_cards(top_items, title=None):
        """
        top_items: [(word, wrong_cnt), ...]
        """
        if not top_items:
            st.info("아직 집계된 오답 단어가 없습니다.")
            return

        max_cnt = max([cnt for _, cnt in top_items]) or 1

        if title:
            st.markdown(f"#### {title}")

        st.markdown(
            """
<style>
.weak-wrap{
  display:flex;
  flex-direction:column;
  gap:10px;
  margin-top:10px;
}
.weak-card{
  border: 1px solid rgba(120,120,120,0.20);
  border-radius: 16px;
  padding: 12px 14px;
  background: rgba(255,255,255,0.02);
}
.weak-row{
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap:12px;
}
.weak-left{
  display:flex;
  align-items:center;
  gap:10px;
  min-width: 0;
}
.rank-badge{
  width:28px;
  height:28px;
  border-radius: 999px;
  display:flex;
  align-items:center;
  justify-content:center;
  font-weight: 900;
  border: 1px solid rgba(120,120,120,0.25);
  background: rgba(255,255,255,0.03);
  flex: 0 0 auto;
}
.weak-word{
  font-weight: 900;
  font-size: 15px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.weak-meta{
  opacity: 0.8;
  font-size: 12px;
  margin-top: 2px;
}
.weak-right{
  display:flex;
  align-items:center;
  gap:8px;
  flex: 0 0 auto;
}
.weak-chip{
  padding: 6px 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 800;
  border: 1px solid rgba(120,120,120,0.25);
  background: rgba(255,255,255,0.03);
  white-space: nowrap;
}
.bar{
  width: 100%;
  height: 8px;
  border-radius: 999px;
  background: rgba(120,120,120,0.18);
  overflow: hidden;
  margin-top: 10px;
}
.bar > div{
  height: 100%;
  border-radius: 999px;
  background: rgba(3,199,90,0.55);
}
</style>
""",
            unsafe_allow_html=True,
        )

        st.markdown('<div class="weak-wrap">', unsafe_allow_html=True)

        for idx, (word, cnt) in enumerate(top_items, start=1):
            pct = int(round((cnt / max_cnt) * 100))
            st.markdown(
                f"""
<div class="weak-card">
  <div class="weak-row">
    <div class="weak-left">
      <div class="rank-badge">{idx}</div>
      <div style="min-width:0;">
        <div class="weak-word">{word}</div>
        <div class="weak-meta">자주 틀린 단어</div>
      </div>
    </div>
    <div class="weak-right">
      <div class="weak-chip">오답 {cnt}회</div>
      <div class="weak-chip">{pct}%</div>
    </div>
  </div>
  <div class="bar"><div style="width:{pct}%"></div></div>
</div>
""",
                unsafe_allow_html=True,
            )

        st.markdown("</div>", unsafe_allow_html=True)

    # quiz_attempts의 wrong_list를 펼쳐서 단어별로 카운트
    from collections import Counter
    counter = Counter()

    # res.data 원본에 wrong_list가 들어있음 (hist는 일부 컬럼만 쓰고 있어서 res.data를 사용)
    for row in (res.data or []):
        wl = row.get("wrong_list") or []
        if isinstance(wl, list):
            for w in wl:
                # w는 {"단어": "...", ...} 형태로 저장되어 있음
                word = str(w.get("단어", "")).strip()
                if word:
                    counter[word] += 1

    if not counter:
        st.caption("아직 오답 데이터가 충분하지 않습니다. 몇 번 더 풀면 TOP10이 생겨요 🙂")
        return

    top10 = counter.most_common(10)

    # ✅ (변경) 엑셀표 제거 → 카드 렌더링
    render_top_wrong_words_cards(top10)

    # 시험 보기 버튼
    if st.button(
        "❌ 이 TOP10으로 시험 보기",
        type="primary",
        use_container_width=True,
        key="btn_quiz_from_top10",
    ):
        clear_question_widget_keys()

        # build_quiz_from_wrongs가 기대하는 형태: [{"단어": "..."} , ...]
        weak_wrong_list = [{"단어": w} for w, _ in top10]

        retry_quiz = build_quiz_from_wrongs(
            weak_wrong_list,
            st.session_state.quiz_type,
        )

        start_quiz_state(retry_quiz, st.session_state.quiz_type, clear_wrongs=True)
        st.session_state["_scroll_top_once"] = True
        st.session_state.page = "quiz"
        st.rerun()

    # ============================================================
    # ✅ 최근 기록
    # ============================================================
    st.markdown("### 최근 기록")

    st.markdown(
        """
<style>
.record-card{
  border: 1px solid rgba(120,120,120,0.25);
  border-radius: 16px;
  padding: 14px 14px;
  margin-bottom: 10px;
  background: rgba(255,255,255,0.02);
}
.record-top{
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap:12px;
  margin-bottom: 8px;
}
.record-title{ font-weight: 800; font-size: 16px; }
.record-sub{ opacity: 0.75; font-size: 12px; }
.pill{
  display:inline-flex;
  align-items:center;
  gap:6px;
  padding: 6px 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
  border: 1px solid rgba(120,120,120,0.25);
  background: rgba(255,255,255,0.03);
  white-space: nowrap;
}
</style>
""",
        unsafe_allow_html=True,
    )

    for _, r in hist.head(15).iterrows():
        dt = pd.to_datetime(r["created_at"]).strftime("%Y-%m-%d %H:%M")
        mode = r["유형"]
        score_i = int(r["score"])
        total = int(r["quiz_len"])
        wrong = int(r["wrong_count"])
        pct = float(r["정답률"] * 100)

        badge = "🏆" if pct >= 90 else ("👍" if pct >= 70 else "💪")

        st.markdown(
            f"""
<div class="record-card">
  <div class="record-top">
    <div>
      <div class="record-title">{badge} {score_i} / {total}</div>
      <div class="record-sub">{dt} · {mode} · 레벨 {LEVEL}</div>
    </div>
    <div class="pill">오답 {wrong}개</div>
  </div>
</div>
""",
            unsafe_allow_html=True,
        )
        st.progress(min(max(pct / 100.0, 0.0), 1.0))
        st.caption(f"정답률 {pct:.0f}%")
        st.write("")
