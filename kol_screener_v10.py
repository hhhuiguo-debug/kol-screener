import streamlit as st
import pandas as pd
import numpy as np

# 设置页面基础配置
st.set_page_config(
    page_title="KOL Screener v1.0 - Lymow Global Influencer Selection Tool",
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
st.markdown('<div class="sub-title">基于多维匹配度、粉丝价值与真实互动率的 Lymow 割草机海外网红精准筛选系统（动态上传版）</div>', unsafe_allow_html=True)
st.write("---")

# 2. 内置的 12 位原始备用数据（当用户没上传文件时展示，确保页面不空白）
def load_default_data():
    raw_data = {
        'KOL 账号': ['@LawnKingUS', '@SmartYardLife', '@TechGadgetReview', '@OutdoorLivingPro', 
                     '@HomeAutomationHub', '@GardenDesignDaily', '@WinterPrep2025', '@SuburbanDadLife', 
                     '@EUGardenLife', '@LifestyleMomUS', '@FitnessOutdoor', '@TechNewsDaily'],
        '平台': ['YouTube', 'YouTube', 'YouTube', 'Instagram', 'YouTube', 'Instagram', 'TikTok', 'YouTube', 'YouTube', 'Instagram', 'YouTube', 'YouTube'],
        '粉丝数': [1240000, 890000, 3200000, 560000, 420000, 780000, 1100000, 320000, 290000, 2100000, 1500000, 4800000],
        '互动率': [0.032, 0.048, 0.021, 0.063, 0.051, 0.042, 0.087, 0.072, 0.038, 0.018, 0.023, 0.012],
        '内容相关度': [46117, 46147, 46058, 46117, 46086, 46086, 46058, 46086, 46086, 46027, 46027, 46027],
        '受众地区': ['US (Northeast)', 'US (Midwest)', 'Global (US 35%)', 'US (South)', 'US+CA', 'US (West Coast)', 'US (Snow Belt)', 'US (Midwest)', 'EU (Germany/Austria)', 'US (National)', 'US (National)', 'Global'],
        '内容形式': ['口播+官方素材', '口播+官方素材', '开箱评测', '生活场景', '智能家居测评', '园艺美化', '冬季生活vlog', '家庭生活', '园艺测评', '生活方式', '户外运动', '科技新闻'],
        '综合得分': [78, 82, 71, 68, 62, 58, 55, 52, 48, 38, 35, 32]
    }
    return pd.DataFrame(raw_data)

# 3. 顶层动态数据上传入口
st.write("### 📤 第一步：上传您的网红数据表")
uploaded_file = st.file_uploader("支持从电脑拖拽或选择现有的 Excel (.xlsx) 或 CSV 文件", type=["xlsx", "csv"])

# 初始化加载数据逻辑
if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.xlsx'):
            df_raw = pd.read_excel(uploaded_file)
        else:
            df_raw = pd.read_csv(uploaded_file)
        st.success(f"🎉 成功成功载入新文件: {uploaded_file.name}，共检测到 {len(df_raw)} 行数据！")
    except Exception as e:
        st.error(f"❌ 读取文件出错，请确保表格格式正常。错误详情: {e}")
        df_raw = load_default_data()
else:
    st.info("💡 当前正在使用系统内置的 12 位原始测试达人数据。您随时可以上传您自己的表格进行批量覆盖计算。")
    df_raw = load_default_data()

# 统一清洗和检查表格列名是否匹配，不匹配则提示错误
required_cols = ['KOL 账号', '平台', '粉丝数', '互动率', '受众地区', '内容形式']
missing_cols = [col for col in required_cols if col not in df_raw.columns]

if missing_cols:
    st.error(f"⚠️ 您上传的表格中缺少以下必要的列名，请检查表头字段: {missing_cols}")
    st.stop()

# 确保“内容相关度”存在，如果没有则默认补全
if '内容相关度' not in df_raw.columns:
    df_raw['内容相关度'] = 100 
if '综合得分' not in df_raw.columns:
    df_raw['综合得分'] = 0  # 若无原得分，则对比原排名的功能会自动忽略

# 4. 侧边栏：交互式权重调优面板与筛选器
st.sidebar.header("⚙️ 权重与参数配置中心")

st.sidebar.markdown("### 1. 评分维度权重分配")
w_followers = st.sidebar.slider("粉丝数权重 (%)", 0, 100, 25) / 100
w_engagement = st.sidebar.slider("互动率权重 (%)", 0, 100, 25) / 100
w_relevance = st.sidebar.slider("内容相关度权重 (%)", 0, 100, 20) / 100
w_match = st.sidebar.slider("产品受众匹配度权重 (%)", 0, 100, 30) / 100

total_weight = w_followers + w_engagement + w_relevance + w_match
if abs(total_weight - 1.0) > 0.001:
    st.sidebar.error(f"⚠️ 当前权重总和为 {int(total_weight*100)}%，请调整至 100% 以确保计算准确！")

st.sidebar.write("---")
st.sidebar.markdown("### 2. 精准漏斗过滤器")
platforms_available = df_raw['平台'].unique().tolist()
selected_platform = st.sidebar.multiselect("包含平台", options=platforms_available, default=platforms_available)
min_followers = st.sidebar.number_input("最低粉丝量限制", min_value=0, value=0, step=50000)

# 5. 后台动态匹配度智能映射算法
# 建立一个基于关键字模糊匹配字典，自动适应任何新上传表格里的国家/场景标签
def calculate_dynamic_match_score(row):
    region = str(row['受众地区']).lower()
    content = str(row['内容形式']).lower()
    account = str(row['KOL 账号'])
    
    # 特殊的硬编码覆盖（兼容原始12位博主）
    special_defaults = {
        '@LawnKingUS': 10, '@SmartYardLife': 10, '@TechGadgetReview': 6, '@OutdoorLivingPro': 9, 
        '@HomeAutomationHub': 7, '@GardenDesignDaily': 8, '@WinterPrep2025': 10, '@SuburbanDadLife': 8, 
        '@EUGardenLife': 8, '@LifestyleMomUS': 4, '@FitnessOutdoor': 4, '@TechNewsDaily': 3
    }
    if account in special_defaults and uploaded_file is None:
        return special_defaults[account]
        
    score = 5 # 默认基础分
    
    # 地理受众标签加减分控制 (突出雪区、大草坪和欧洲五国核心区)
    if 'snow' in region or 'northeast' in region or 'winter' in region:
        score += 3
    if 'midwest' in region or 'yard' in region or 'lawn' in region:
        score += 3
    if 'germany' in region or 'france' in region or 'italy' in region or 'spain' in region or 'netherlands' in region or 'eu' in region:
        score += 2
    if 'global' in region or 'national' in region:
        score -= 1
        
    # 内容/场景标签加减分控制
    if 'lawn' in content or 'garden' in content or '园艺' in content or '草坪' in content:
        score += 2
    if 'vlog' in content or 'lifestyle' in content or '生活' in content:
        score += 1
    if 'home' in content or 'automation' in content or '智能' in content:
        score += 1
    if 'news' in content or '新闻' in content or 'fitness' in content:
        score -= 2
        
    return int(np.clip(score, 1, 10))

df_raw['产品匹配度(10分制)'] = df_raw.apply(calculate_dynamic_match_score, axis=1)

# 数据归一化标准化映射函数
def scale_to_hundred(series):
    if series.max() == series.min():
        return 100
    return (series - series.min()) / (series.max() - series.min()) * 100

df_raw['粉丝得分'] = scale_to_hundred(df_raw['粉丝数'])
df_raw['互动率得分'] = scale_to_hundred(df_raw['互动率'])
df_raw['相关度得分'] = scale_to_hundred(df_raw['内容相关度'])
df_raw['匹配度得分'] = scale_to_hundred(df_raw['产品匹配度(10分制)'])

# 动态核心重算得分
df_raw['V1.0综合得分'] = (
    df_raw['粉丝得分'] * w_followers + 
    df_raw['互动率得分'] * w_engagement + 
    df_raw['相关度得分'] * w_relevance + 
    df_raw['匹配度得分'] * w_match
).round(1)

# 生成计算新排名
df_raw['新排名'] = df_raw['V1.0综合得分'].rank(ascending=False, method='min').astype(int)
df_raw['原排名'] = df_raw['综合得分'].rank(ascending=False, method='min').astype(int)
df_raw['排名变化'] = df_raw['原排名'] - df_raw['新排名']

# 执行数据过滤器过滤
processed_df = df_raw[
    (df_raw['平台'].isin(selected_platform)) & 
    (df_raw['粉丝数'] >= min_followers)
].sort_values(by='新排名')

# 6. 数据主大面板视图
st.write("---")
st.write("### 📋 实时达人计算矩阵与策略评估看板")

if processed_df.empty:
    st.warning("⚠️ 当前过滤限制过紧，没有符合条件的网红数据，请调整左侧漏斗范围。")
else:
    col_m1, col_m2, col_m3 = st.columns(3)
    with col_m1:
        st.markdown(f'<div class="metric-card"><b>🏆 当前计算池首选第一名</b><br><span style="font-size:20px; color:#10B981; font-weight:bold;">{processed_df.iloc[0]["KOL 账号"]}</span></div>', unsafe_allow_html=True)
    with col_m2:
        st.markdown(f'<div class="metric-card"><b>📊 覆盖总粉丝池</b><br><span style="font-size:20px; color:#3B82F6; font-weight:bold;">{processed_df["粉丝数"].sum():,}</span></div>', unsafe_allow_html=True)
    with col_m3:
        st.markdown(f'<div class="metric-card"><b>🔥 平均互动率水平</b><br><span style="font-size:20px; color:#F59E0B; font-weight:bold;">{processed_df["互动率"].mean()*100:.2f}%</span></div>', unsafe_allow_html=True)

    st.write(" ")
    
    # 格式化数据便于前端阅读
    display_df = processed_df[[
        '新排名', '原排名', '排名变化', 'KOL 账号', '平台', '粉丝数', '互动率', 
        '受众地区', '内容形式', '产品匹配度(10分制)', 'V1.0综合得分', '综合得分'
    ]].copy()

    def format_trend(val):
        if val > 100 or val < -100: return "—" # 说明没有原排名参考
        if val > 0: return f"▲ {val}"
        elif val < 0: return f"▼ {abs(val)}"
        return "—"
        
    display_df['排名变化'] = display_df['排名变化'].apply(format_trend)
    display_df['粉丝数'] = display_df['粉丝数'].apply(lambda x: f"{x/10000:.1f}万" if x>=10000 else f"{x}")
    display_df['互动率'] = display_df['互动率'].apply(lambda x: f"{x*100:.2f}%" if isinstance(x, float) else str(x))

    st.dataframe(
        display_df,
        column_config={
            "新排名": st.column_config.NumberColumn("新排名", help="基于新权重规则实时重算的名次"),
            "产品匹配度(10分制)": st.column_config.ProgressColumn("产品与受众匹配度", min_value=0, max_value=10, format="%d分"),
            "V1.0综合得分": st.column_config.NumberColumn("V1.0得分 🔥", format="%.1f"),
            "综合得分": st.column_config.NumberColumn("表格原始得分")
        },
        use_container_width=True,
        hide_index=True
    )

    # 导出结果按钮
    st.write(" ")
    csv_buffer = processed_df.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 导出当前排好名的网红计算结果 (CSV)",
        data=csv_buffer,
        file_name="Lymow_KOL_Screener_Results.csv",
        mime="text/csv"
    )
