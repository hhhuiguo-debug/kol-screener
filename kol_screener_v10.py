import streamlit as st
import pandas as pd
import numpy as np

# 设置页面基础配置
st.set_page_config(
    page_title="KOL Screener v2.0 - Lymow Global Influencer Selection Tool",
    page_icon="🎯",
    layout="wide"
)

# 1. 样式美化注入
st.markdown("""
    <style>
    .main-title { font-size: 32px; font-weight: bold; color: #1E3A8A; margin-bottom: 5px; }
    .sub-title { font-size: 16px; color: #4B5563; margin-bottom: 25px; }
    .metric-card { background-color: #F3F4F6; padding: 15px; border-radius: 10px; border-left: 5px solid #3B82F6; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🎯 KOL Screener v1.0</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">基于多维匹配度、粉丝价值与真实互动率的 Lymow 割草机海外网红精准筛选系统</div>', unsafe_allow_html=True)
st.write("---")

# 2. 模拟/注入 12 位原始 KOL 核心底层数据
@st.cache_data
def load_initial_data():
    raw_data = {
        'KOL 账号': ['@LawnKingUS', '@SmartYardLife', '@TechGadgetReview', '@OutdoorLivingPro', 
                     '@HomeAutomationHub', '@GardenDesignDaily', '@WinterPrep2025', '@SuburbanDadLife', 
                     '@EUGardenLife', '@LifestyleMomUS', '@FitnessOutdoor', '@TechNewsDaily'],
        '平台': ['YouTube', 'YouTube', 'YouTube', 'Instagram', 'YouTube', 'Instagram', 'TikTok', 'YouTube', 'YouTube', 'Instagram', 'YouTube', 'YouTube'],
        '粉丝数': [1240000, 890000, 3200000, 560000, 420000, 780000, 1100000, 320000, 290000, 2100000, 1500000, 4800000],
        '互动率': [0.032, 0.048, 0.021, 0.063, 0.051, 0.042, 0.087, 0.072, 0.038, 0.018, 0.023, 0.012],
        '内容相关度原始分': [46117, 46147, 46058, 46117, 46086, 46086, 46058, 46086, 46086, 46027, 46027, 46027],
        '受众地区': ['US (Northeast)', 'US (Midwest)', 'Global (US 35%)', 'US (South)', 'US+CA', 'US (West Coast)', 'US (Snow Belt)', 'US (Midwest)', 'EU (Germany/Austria)', 'US (National)', 'US (National)', 'Global'],
        '内容形式': ['口播+官方素材', '口播+官方素材', '开箱评测', '生活场景', '智能家居测评', '园艺美化', '冬季生活vlog', '家庭生活', '园艺测评', '生活方式', '户外运动', '科技新闻'],
        '原综合得分': [78, 82, 71, 68, 62, 58, 55, 52, 48, 38, 35, 32]
    }
    return pd.DataFrame(raw_data)

df_kol = load_initial_data()

# 3. 侧边栏：交互式权重调优面板与筛选器
st.sidebar.header("⚙️ 权重与参数配置中心")

st.sidebar.markdown("### 1. 评分维度权重分配")
w_followers = st.sidebar.slider("粉丝数权重 (%)", 0, 100, 25) / 100
w_engagement = st.sidebar.slider("互动率权重 (%)", 0, 100, 25) / 100
w_relevance = st.sidebar.slider("内容相关度权重 (%)", 0, 100, 20) / 100
w_match = st.sidebar.slider("产品受众匹配度权重 (%)", 0, 100, 30) / 100

# 校验权重是否等于 100%
total_weight = w_followers + w_engagement + w_relevance + w_match
if abs(total_weight - 1.0) > 0.001:
    st.sidebar.error(f"⚠️ 当前权重总和为 {int(total_weight*100)}%，请调整至 100% 以确保计算准确！")

st.sidebar.write("---")
st.sidebar.markdown("### 2. 精准漏斗过滤器")
selected_platform = st.sidebar.multiselect("包含平台", options=['YouTube', 'Instagram', 'TikTok'], default=['YouTube', 'Instagram', 'TikTok'])
min_followers = st.sidebar.number_input("最低粉丝量限制", min_value=0, value=100000, step=50000)

# 4. 后台逻辑核心算法：受众地区与内容形式映射打分 + 标准化归一
match_scores = {
    '@LawnKingUS': 10,       # 东北部大院子 + 雪区换季刚需
    '@SmartYardLife': 10,    # 智能庭院 + 中西部典型大草坪
    '@TechGadgetReview': 6,  # 泛科技全球流量，精准度一般
    '@OutdoorLivingPro': 9,  # 美南户外庭院生活方式，极利于种草
    '@HomeAutomationHub': 7, # 北美智能家居，契合自动化卖点
    '@GardenDesignDaily': 8, # 西海岸园艺美化，极佳的视觉表现场地
    '@WinterPrep2025': 10,   # 雪区换季大刚需，互动率爆棚
    '@SuburbanDadLife': 8,   # 中西部中产爸爸，主力购买画像
    '@EUGardenLife': 8,      # 欧洲德奥高付费割草机核心细分市场
    '@LifestyleMomUS': 4,    # 大众化女性生活方式，缺乏草坪工具转化心智
    '@FitnessOutdoor': 4,    # 户外运动场景不聚焦庭院
    '@TechNewsDaily': 3      # 纯科技新闻，无草坪转化场景
}
df_kol['产品匹配度(10分制)'] = df_kol['KOL 账号'].map(match_scores)

# 数据标准化映射函数
def scale_to_hundred(series):
    if series.max() == series.min():
        return 100
    return (series - series.min()) / (series.max() - series.min()) * 100

df_kol['粉丝得分'] = scale_to_hundred(df_kol['粉丝数'])
df_kol['互动率得分'] = scale_to_hundred(df_kol['互动率'])
df_kol['相关度得分'] = scale_to_hundred(df_kol['内容相关度原始分'])
df_kol['匹配度得分'] = scale_to_hundred(df_kol['产品匹配度(10分制)'])

# 计算动态全新得分
df_kol['V1.0综合得分'] = (
    df_kol['粉丝得分'] * w_followers + 
    df_kol['互动率得分'] * w_engagement + 
    df_kol['相关度得分'] * w_relevance + 
    df_kol['匹配度得分'] * w_match
).round(1)

# 生成新旧排名对比
df_kol['新排名'] = df_kol['V1.0综合得分'].rank(ascending=False, method='min').astype(int)
df_kol['原排名'] = df_kol['原综合得分'].rank(ascending=False, method='min').astype(int)
df_kol['排名变化'] = df_kol['原排名'] - df_kol['新排名']

# 执行数据过滤器过滤
processed_df = df_kol[
    (df_kol['平台'].isin(selected_platform)) & 
    (df_kol['粉丝数'] >= min_followers)
].sort_values(by='新排名')

# 5. 主面板视图布局
col_m1, col_m2, col_m3 = st.columns(3)
with col_m1:
    st.markdown(f'<div class="metric-card"><b>🏆 当前新评分第一名</b><br><span style="font-size:20px; color:#10B981; font-weight:bold;">{processed_df.iloc[0]["KOL 账号"] if not processed_df.empty else "N/A"}</span></div>', unsafe_allow_html=True)
with col_m2:
    st.markdown(f'<div class="metric-card"><b>📊 覆盖总粉丝池</b><br><span style="font-size:20px; color:#3B82F6; font-weight:bold;">{processed_df["粉丝数"].sum():,}</span></div>', unsafe_allow_html=True)
with col_m3:
    st.markdown(f'<div class="metric-card"><b>🔥 平均互动率水平</b><br><span style="font-size:20px; color:#F59E0B; font-weight:bold;">{processed_df["互动率"].mean()*100:.2f}%</span></div>', unsafe_allow_html=True)

st.write("### 📋 实时达人计算矩阵与策略评估看板")

# 格式化展示数据输出
display_df = processed_df[[
    '新排名', '原排名', '排名变化', 'KOL 账号', '平台', '粉丝数', '互动率', 
    '受众地区', '内容形式', '产品匹配度(10分制)', 'V1.0综合得分', '原综合得分'
]].copy()

# 为排名变动加上箭头视觉效果
def format_trend(val):
    if val > 0: return f"▲ {val}"
    elif val < 0: return f"▼ {abs(val)}"
    return "—"
display_df['排名变化'] = display_df['排名变化'].apply(format_trend)
display_df['粉丝数'] = display_df['粉丝数'].apply(lambda x: f"{x/10000:.0f}万" if x>=10000 else f"{x}")
display_df['互动率'] = display_df['互动率'].apply(lambda x: f"{x*100:.1f}%")

st.dataframe(
    display_df,
    column_config={
        "新排名": st.column_config.NumberColumn("新排名", help="基于新权重规则实时重算的名次"),
        "产品匹配度(10分制)": st.column_config.ProgressColumn("产品与受众匹配度", min_value=0, max_value=10, format="%d分"),
        "V1.0综合得分": st.column_config.NumberColumn("V1.0得分 🔥", format="%.1f")
    },
    use_container_width=True,
    hide_index=True
)

# 6. 系统自动化决策分析卡
st.write("### 💡 系统智能筛选决策透视")
tab1, tab2 = st.tabs(["🚀 核心力推与黑马博主", "⚠️ 投资报酬率(ROI)风险预警"])

with tab1:
    st.success("""
    *   **首选黄金方案（智能大草坪方向）**: `@SmartYardLife` 稳居第 1 名。该账号在拥有接近百万的高价值北美本地粉丝群体的同时，匹配度极高，属于高转化基本盘。
    *   **核心心智引爆（雪区/长冬爆发点）**: `@WinterPrep2025` 从第 7 名跨越式跃升至第 2 名！得益于 **8.7% 的极高互动率** 与独特的雪区环境，极度适合推广 Lymow 割草机的换季耐寒、全地形适应性及硬核性能。
    """)

with tab2:
    st.warning("""
    *   **全球泛科技大号泡沫**: `@TechGadgetReview` (原第3) 和 `@TechNewsDaily` (原第12) 的名次在引入精准画像后显著下滑。这类达人虽然粉丝体量看似巨大，但受众散布全球且缺乏独立的私人庭院场景，盲目投放会造成大量无效预算浪费。
    *   **调性不符预警**: `@LifestyleMomUS` 虽然在女性与大众生活方式圈层粉丝量高达 210 万，但因其完全缺乏底层硬核割草工具、园艺修整的垂类受众，不建议在 V1.0 营销周期内投放。
    """)