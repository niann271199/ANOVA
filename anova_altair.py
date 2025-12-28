import streamlit as st

import numpy as np

import pandas as pd

import altair as alt

from scipy import stats



# ================= 页面配置 =================

st.set_page_config(

    page_title="极简 ANOVA 可视化",

    page_icon="✨",

    layout="wide"

)



# 自定义 CSS 让滑块和背景更协调

st.markdown("""

<style>

    .stApp { background-color: #ffffff; }

    h1 { font-family: 'Helvetica Neue', sans-serif; font-weight: 300; }

    .card {

        background-color: #f8f9fa; padding: 20px; border-radius: 10px;

        box-shadow: 0 2px 10px rgba(0,0,0,0.05);

    }

</style>

""", unsafe_allow_html=True)



# ================= 侧边栏：极简控制 =================

with st.sidebar:

    st.header("🎛️ 参数调整")



    # 均值差异

    mean_diff = st.slider("组间距离 (Cohens d):", 0.0, 4.0, 2.0, 0.1)



    # 样本量 (控制分布的平滑度)

    n = st.slider("样本量 (N):", 20, 200, 50)



    # 错误方差

    sd = st.slider("组内变异 (SD):", 0.5, 2.0, 1.0, 0.1)



    st.markdown("---")

    st.caption("提示：Altair 绘图由浏览器渲染，比 Matplotlib 更清晰流畅。")



# ================= 核心逻辑：生成密度数据 =================

# 为了模拟那个网站的丝滑曲线，我们不画直方图，而是画理论密度曲线

x = np.linspace(-5, 15, 500)



# 计算三组的概率密度 (PDF)

# 组A (基准), 组B (偏移), 组C (偏移更多或反向)

y_a = stats.norm.pdf(x, loc=0, scale=sd)

y_b = stats.norm.pdf(x, loc=mean_diff, scale=sd)

y_c = stats.norm.pdf(x, loc=-mean_diff / 2, scale=sd)  # 让C组在左边一点



# 整理成 Altair 喜欢的长格式数据

source = pd.DataFrame({

    'x': np.concatenate([x, x, x]),

    'density': np.concatenate([y_a, y_b, y_c]),

    'Group': ['Control (A)'] * 500 + ['Treatment 1 (B)'] * 500 + ['Treatment 2 (C)'] * 500

})



# ================= 主界面 =================

st.title("✨ 交互式 ANOVA 原理 (Altair 版)")

st.markdown("体验更接近 rpsychologist.com 的矢量绘图效果")



col1, col2 = st.columns([3, 1])



with col1:

    # --- Altair 绘图核心 ---

    # 定义基础图表

    base = alt.Chart(source).encode(

        x=alt.X('x', title='测量分数', axis=alt.Axis(grid=False)),

        y=alt.Y('density', title='概率密度', axis=None),

        color=alt.Color('Group', legend=alt.Legend(orient='top', title=None),

                        scale=alt.Scale(scheme='set2'))  # 使用高级配色 Set2

    )



    # 画区域图 (Area) - 带透明度

    area = base.mark_area(opacity=0.6).encode(

        tooltip=['Group', alt.Tooltip('x', format='.2f')]

    )



    # 画轮廓线 (Line) - 让边缘更清晰

    line = base.mark_line(strokeWidth=2, opacity=0.8)



    # 组合图表

    chart = (area + line).properties(

        height=450,

        title="组间分布重叠示意图"

    ).configure_view(

        stroke=None  # 去掉边框

    ).configure_axis(

        domain=False,  # 去掉轴线

        tickSize=0  # 去掉刻度

    ).interactive()  # 开启缩放和平移



    st.altair_chart(chart, use_container_width=True)



with col2:

    # 模拟计算 F 值 (基于理论参数)

    # F ≈ (均值差^2) / (方差/N)

    # 这只是一个近似演示，为了展示动态变化

    signal = mean_diff ** 2

    noise = (sd ** 2)

    f_approx = (signal * n) / noise



    st.markdown(f"""

    <div class='card'>

        <h3 style='margin:0; color:#7f8c8d; font-size:16px;'>实时 F 值 (近似)</h3>

        <h1 style='margin:5px 0; color:#2c3e50; font-size:48px;'>{f_approx:.1f}</h1>

        <hr>

        <p style='font-size:14px; color:#95a5a6;'>

        当曲线重叠越少（滑块右移），<br>

        F 值越大。<br><br>

        这就是 <b>信号(Signal)</b> 战胜了 <b>噪声(Noise)</b>。

        </p>

    </div>

    """, unsafe_allow_html=True)

