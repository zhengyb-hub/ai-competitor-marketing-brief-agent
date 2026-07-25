from datetime import date
import json
import os
from pathlib import Path

import pandas as pd
import streamlit as st

from brief_generator import (
    REQUIRED_COLUMNS,
    generate_ai_brief_sections,
    validate_competitor_data,
)


st.set_page_config(
    page_title="AI-Powered Competitor Marketing Brief Agent",
    page_icon="📊",
    layout="wide",
)


APP_DIR = Path(__file__).resolve().parent
DATA_PATH = APP_DIR / "data" / "sample_competitor_data.csv"
DEFAULT_MODEL = "gpt-5.6"


@st.cache_data
def load_data(file_path: Path) -> pd.DataFrame:
    """Read the bundled portfolio sample."""
    return pd.read_csv(file_path)


def get_runtime_setting(name: str, default: str = "") -> str:
    """Read a setting from the environment or Streamlit secrets."""
    environment_value = os.getenv(name, "").strip()
    if environment_value:
        return environment_value

    try:
        secret_value = st.secrets.get(name, default)
    except Exception:
        secret_value = default
    return str(secret_value).strip()


def add_report_metadata(
    sections: dict[str, str],
    data: pd.DataFrame,
    selected_competitors: list[str],
    brand_name: str,
    industry: str,
    generation_mode: str,
    model: str,
) -> dict[str, str]:
    """Add transparent provenance metadata to any generated report."""
    enriched = dict(sections)
    source_labels = sorted(data["source"].dropna().astype(str).unique().tolist())
    metadata_lines = [
        f"Brand: {brand_name}",
        f"Industry: {industry}",
        f"Selected Competitors: {', '.join(selected_competitors)}",
        f"Records Used: {len(data)}",
        f"Sources: {', '.join(source_labels) or 'Not provided'}",
        f"Generation Mode: {generation_mode}",
    ]
    if generation_mode == "AI-powered":
        metadata_lines.append(f"Model: {model}")
    metadata_lines.append(f"Generated On: {date.today().isoformat()}")
    enriched["Report Metadata"] = "\n\n".join(metadata_lines)
    return enriched


def add_custom_css() -> None:
    """添加页面自定义 CSS，让 Streamlit 页面更像专业作品集工具。"""
    st.markdown(
        """
        <style>
        .stApp {
            background: #f6f8fb;
            color: #172033;
        }

        .block-container {
            max-width: 1220px;
            padding-top: 2rem;
            padding-bottom: 3rem;
        }

        section[data-testid="stSidebar"] {
            background: #ffffff;
            border-right: 1px solid #e5eaf2;
        }

        .hero-card {
            background: linear-gradient(135deg, #ffffff 0%, #eef5ff 100%);
            border: 1px solid #dbe7f3;
            border-radius: 18px;
            padding: 34px 38px;
            margin-bottom: 24px;
            box-shadow: 0 18px 42px rgba(20, 37, 63, 0.08);
        }

        .hero-label {
            color: #2563eb;
            font-size: 0.82rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            margin-bottom: 10px;
        }

        .hero-title {
            color: #0f172a;
            font-size: 2.45rem;
            font-weight: 760;
            line-height: 1.15;
            margin-bottom: 12px;
        }

        .hero-subtitle {
            color: #1d4ed8;
            font-size: 1.14rem;
            font-weight: 650;
            margin-bottom: 10px;
        }

        .hero-copy {
            color: #475569;
            font-size: 1rem;
            line-height: 1.65;
            max-width: 860px;
        }

        div[data-testid="stMetric"] {
            background: #ffffff;
            border: 1px solid #e5eaf2;
            border-radius: 14px;
            padding: 18px 20px;
            box-shadow: 0 10px 28px rgba(15, 23, 42, 0.05);
        }

        div[data-testid="stMetricLabel"] {
            color: #64748b;
        }

        .step-card {
            background: #ffffff;
            border: 1px solid #e5eaf2;
            border-radius: 14px;
            padding: 20px;
            min-height: 150px;
            box-shadow: 0 10px 28px rgba(15, 23, 42, 0.04);
        }

        .step-number {
            width: 34px;
            height: 34px;
            border-radius: 50%;
            background: #2563eb;
            color: #ffffff;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            margin-bottom: 12px;
        }

        .step-title {
            color: #0f172a;
            font-size: 1.04rem;
            font-weight: 700;
            margin-bottom: 8px;
        }

        .step-copy {
            color: #64748b;
            line-height: 1.55;
        }

        .section-note {
            background: #ffffff;
            border: 1px solid #e5eaf2;
            border-left: 5px solid #2563eb;
            border-radius: 14px;
            padding: 18px 20px;
            color: #475569;
            margin-bottom: 18px;
        }

        .stButton > button {
            border-radius: 12px;
            font-weight: 700;
            min-height: 44px;
        }

        .stDownloadButton > button {
            border-radius: 12px;
            font-weight: 700;
            min-height: 44px;
        }

        div[data-testid="stTabs"] button {
            font-weight: 650;
        }

        h2, h3, h4 {
            color: #0f172a;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def format_bullets(items: list[str], fallback: str) -> str:
    """把列表转换成 Markdown 项目符号。"""
    if not items:
        return f"- {fallback}"

    return "\n".join([f"- {item}" for item in items])


def make_row_bullets(data: pd.DataFrame, limit: int, output_language: str) -> str:
    """把 CSV 中的 title、content、category 整理成报告里的证据点。"""
    bullets = []

    for _, row in data.head(limit).iterrows():
        if output_language == "Chinese":
            bullet = (
                f"{row['competitor']} | {row['category']}："
                f"{row['title']} - {row['content']}"
            )
        else:
            bullet = (
                f"{row['competitor']} | {row['category']}: "
                f"{row['title']} - {row['content']}"
            )
        bullets.append(bullet)

    fallback = (
        "所选数据中没有找到清晰样例。"
        if output_language == "Chinese"
        else "No clear examples found in the selected data."
    )
    return format_bullets(bullets, fallback)


def clean_file_name(text: str) -> str:
    """把品牌名转换成适合文件名的格式。"""
    cleaned = "".join(char.lower() if char.isalnum() else "_" for char in text)
    cleaned = "_".join(cleaned.split("_"))
    return cleaned.strip("_") or "brand"


def build_marketing_brief_sections(
    data: pd.DataFrame,
    selected_competitors: list[str],
    brand_name: str,
    industry: str,
    output_language: str,
) -> dict[str, str]:
    """根据用户选择和本地 CSV 数据，生成报告的各个区块。"""
    filtered_data = data[data["competitor"].isin(selected_competitors)].copy()

    total_records = len(filtered_data)
    category_counts = filtered_data["category"].value_counts()
    competitor_counts = filtered_data["competitor"].value_counts()

    top_category = category_counts.index[0] if not category_counts.empty else "N/A"
    top_category_count = int(category_counts.iloc[0]) if not category_counts.empty else 0
    most_active_competitor = (
        competitor_counts.index[0] if not competitor_counts.empty else "N/A"
    )

    date_min = filtered_data["date"].min() if total_records else "N/A"
    date_max = filtered_data["date"].max() if total_records else "N/A"
    category_list = ", ".join(category_counts.index.tolist()) or "N/A"

    competitor_overview = []
    for competitor in selected_competitors:
        competitor_data = filtered_data[filtered_data["competitor"] == competitor]
        competitor_categories = competitor_data["category"].value_counts()
        category_text = ", ".join(competitor_categories.index.tolist()) or "N/A"

        if output_language == "Chinese":
            competitor_overview.append(
                f"{competitor}：包含 {len(competitor_data)} 条记录，覆盖 {category_text}。"
            )
        else:
            competitor_overview.append(
                f"{competitor}: {len(competitor_data)} records, covering {category_text}."
            )

    strategy_data = filtered_data[
        filtered_data["category"].isin(["Content Strategy", "Product Feature"])
    ]
    positioning_data = filtered_data[
        filtered_data["category"].isin(["Brand Positioning", "User Engagement"])
    ]
    opportunity_data = filtered_data[
        filtered_data["category"] == "Marketing Opportunity"
    ]

    if output_language == "Chinese":
        insight_items = [
            (
                f"最明显的主题是 {top_category}，共有 {top_category_count} 条记录，"
                "说明这是当前样本中最强的竞争信号。"
            ),
            (
                f"{most_active_competitor} 在所选数据中记录最多，"
                "因此对本次分析结论影响最大。"
            ),
            (
                "标题和内容显示，新闻客户端之间的竞争重点集中在内容发现、可信度、"
                "用户参与和产品便利性。"
            ),
        ]

        recommendations = [
            f"围绕 {brand_name} 提炼一句清晰的差异化品牌主张。",
            f"优先关注 {top_category}，因为它是所选数据里最突出的竞争主题。",
            "把产品功能转化为用户能理解的营销卖点，而不只是功能描述。",
            "持续向 CSV 中添加新样本，让这个分析流程变成可复用的竞品研究工具。",
        ]

        limitations = [
            "本分析只使用作品集模拟数据，不能当作真实官方市场数据。",
            "报告由简单规则生成，没有调用真实 AI 模型或外部 API。",
            "项目只分析本地 CSV 文件，不追踪实时竞品活动。",
        ]

        if total_records < 8:
            limitations.append("所选数据量较小，因此结论更适合作为方向性参考。")
        if len(selected_competitors) < 2:
            limitations.append("当前只选择了一个竞品，因此横向对比能力有限。")

        sections = {
            "Executive Summary": (
                f"本报告分析 **{industry}** 领域中 {len(selected_competitors)} 个竞品的本地 CSV 样本数据。"
                f"当前共分析 **{total_records}** 条记录，数据时间范围为 **{date_min} 至 {date_max}**。"
                f"样本中最突出的主题是 **{top_category}**。对 **{brand_name}** 来说，"
                "这些信号可以帮助团队优化品牌定位、内容策略和营销沟通重点。"
            ),
            "Competitor Activity Overview": format_bullets(
                competitor_overview,
                "所选数据中没有竞品活动记录。",
            ),
            "Content Strategy Analysis": (
                "以下内容和产品信号来自 CSV 中的 title、content 和 category 字段：\n\n"
                f"{make_row_bullets(strategy_data, 6, output_language)}\n\n"
                "这些样本说明，竞品正在通过更快的内容发现、更清晰的新闻包装和更实用的产品入口来争夺用户注意力。"
            ),
            "Audience and Positioning": (
                "以下样本更接近用户认知、品牌调性和参与方式：\n\n"
                f"{make_row_bullets(positioning_data, 6, output_language)}\n\n"
                f"对 **{brand_name}** 来说，这些信息可以帮助判断竞品是在强调可信度、社区感、便利性还是差异化编辑风格。"
            ),
            "Key Marketing Insights": (
                f"{format_bullets(insight_items, '暂未发现明确洞察。')}\n\n"
                "机会相关样本：\n\n"
                f"{make_row_bullets(opportunity_data, 5, output_language)}"
            ),
            "Recommendations": format_bullets(
                recommendations,
                "暂未生成建议。",
            ),
            "Limitations": format_bullets(
                limitations,
                "暂未发现限制说明。",
            ),
        }
    else:
        insight_items = [
            (
                f"The strongest visible theme is {top_category} "
                f"({top_category_count} records), making it the clearest signal "
                "in the selected sample."
            ),
            (
                f"{most_active_competitor} has the largest number of selected records, "
                "so it has the strongest influence on this brief."
            ),
            (
                "The selected titles and content suggest that news apps compete through "
                "content discovery, trust, user participation, and product convenience."
            ),
        ]

        recommendations = [
            f"Clarify one differentiated brand promise for {brand_name}.",
            f"Prioritize {top_category}, because it is the most visible competitive theme in the selected data.",
            "Translate product features into user-facing marketing benefits, not only feature descriptions.",
            "Keep adding rows to the CSV so this workflow becomes a reusable competitor research system.",
        ]

        limitations = [
            "This analysis uses sample portfolio data only and should not be treated as official market data.",
            "The brief is generated with simple rule-based logic, not a real AI model or external API.",
            "The project only analyzes the local CSV file and does not track live competitor activity.",
        ]

        if total_records < 8:
            limitations.append(
                "The selected dataset is small, so the findings should be read as directional signals."
            )
        if len(selected_competitors) < 2:
            limitations.append(
                "Only one competitor is selected, so cross-competitor comparison is limited."
            )

        sections = {
            "Executive Summary": (
                f"This report analyzes local CSV sample data for {len(selected_competitors)} competitor(s) "
                f"in the **{industry}** space. It reviews **{total_records}** records from "
                f"**{date_min} to {date_max}** and identifies **{top_category}** as the strongest theme. "
                f"For **{brand_name}**, these signals can support sharper positioning, clearer content priorities, "
                "and more focused marketing decisions."
            ),
            "Competitor Activity Overview": format_bullets(
                competitor_overview,
                "No competitor activity records were found in the selected data.",
            ),
            "Content Strategy Analysis": (
                "The strongest content and product signals from the CSV fields are:\n\n"
                f"{make_row_bullets(strategy_data, 6, output_language)}\n\n"
                "These examples suggest that competitors are trying to win attention through faster discovery, "
                "clearer news packaging, and more useful product surfaces."
            ),
            "Audience and Positioning": (
                "Audience and positioning signals from the selected data include:\n\n"
                f"{make_row_bullets(positioning_data, 6, output_language)}\n\n"
                f"For **{brand_name}**, these signals help reveal whether competitors are emphasizing trust, "
                "community, convenience, or a distinctive editorial voice."
            ),
            "Key Marketing Insights": (
                f"{format_bullets(insight_items, 'No clear insights were found.')}\n\n"
                "Opportunity-focused rows in the dataset:\n\n"
                f"{make_row_bullets(opportunity_data, 5, output_language)}"
            ),
            "Recommendations": format_bullets(
                recommendations,
                "No recommendations were generated.",
            ),
            "Limitations": format_bullets(
                limitations,
                "No limitations were identified.",
            ),
        }

    sections["Report Metadata"] = (
        f"Brand: {brand_name}\n\n"
        f"Industry: {industry}\n\n"
        f"Selected Competitors: {', '.join(selected_competitors)}\n\n"
        f"Categories Covered: {category_list}\n\n"
        f"Generated On: {date.today().isoformat()}"
    )

    return sections


def build_markdown_report(sections: dict[str, str], brand_name: str) -> str:
    """把报告区块转换成可下载的 Markdown 文本。"""
    markdown_parts = [f"# AI-Powered Competitor Marketing Brief for {brand_name}"]

    for section_title, section_content in sections.items():
        markdown_parts.append(f"## {section_title}\n{section_content}")

    return "\n\n".join(markdown_parts)


def show_report_card(title: str, content: str) -> None:
    """用卡片样式展示单个报告区块。"""
    with st.container(border=True):
        st.markdown(f"#### {title}")
        st.markdown(content)


add_custom_css()


st.sidebar.header("Analysis Settings")
st.sidebar.caption("Configure the evidence, target brand, and generation mode.")

uploaded_file = st.sidebar.file_uploader(
    "Competitor observations (CSV)",
    type=["csv"],
    help=(
        "Required columns: competitor, date, source, title, content, category. "
        "Maximum upload size is 10 MB."
    ),
)

try:
    raw_df = pd.read_csv(uploaded_file) if uploaded_file is not None else load_data(DATA_PATH)
    df = validate_competitor_data(raw_df)
except (FileNotFoundError, pd.errors.ParserError, UnicodeDecodeError, ValueError) as exc:
    st.error(f"Unable to load competitor data: {exc}")
    st.stop()

data_source_label = (
    f"Uploaded file: {uploaded_file.name}"
    if uploaded_file is not None
    else "Bundled sample portfolio dataset"
)
st.sidebar.caption(data_source_label)

brand_name = st.sidebar.text_input("Brand Name", value="Sohu News")
industry = st.sidebar.text_input("Industry", value="China news apps")

competitor_options = sorted(df["competitor"].unique().tolist())
selected_competitors = st.sidebar.multiselect(
    "Competitor Selection",
    options=competitor_options,
    default=competitor_options,
)

category_options = sorted(df["category"].unique().tolist())
selected_categories = st.sidebar.multiselect(
    "Category Filter",
    options=category_options,
    default=category_options,
)

output_language = st.sidebar.selectbox(
    "Output Language",
    options=["English", "Chinese"],
    index=0,
)

api_key = get_runtime_setting("OPENAI_API_KEY")
model_name = get_runtime_setting("OPENAI_MODEL", DEFAULT_MODEL)

if api_key:
    generation_mode = st.sidebar.radio(
        "Generation Mode",
        options=["AI-powered", "Rule-based portfolio demo"],
        index=0,
        help=(
            "AI-powered mode uses the OpenAI Responses API. Rule-based mode "
            "provides a deterministic and auditable portfolio demonstration."
        ),
    )
    st.sidebar.success(f"OpenAI configured · {model_name}")
else:
    generation_mode = "Rule-based portfolio demo"
    st.sidebar.info(
        "Public portfolio demo · No external API calls · No user data is sent "
        "to a third-party model."
    )

generate_button = st.sidebar.button(
    "Generate Brief",
    type="primary",
    width="stretch",
)


if selected_competitors and selected_categories:
    filtered_df = df[
        df["competitor"].isin(selected_competitors)
        & df["category"].isin(selected_categories)
    ].copy()
else:
    filtered_df = df.iloc[0:0].copy()


# Hero Section：展示项目定位和作品集价值
st.markdown(
    """
    <div class="hero-card">
        <div class="hero-label">AI Marketing Intelligence Portfolio</div>
        <div class="hero-title">AI-Powered Competitor Marketing Brief Agent</div>
        <div class="hero-subtitle">From structured evidence to decision-ready marketing strategy.</div>
        <div class="hero-copy">
            Upload competitor observations, explore activity patterns, and generate a grounded
            marketing brief with the OpenAI Responses API or a transparent rule-based fallback.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# 点击按钮后生成简报，并把结果保存到 session_state
if generate_button:
    if not brand_name.strip():
        st.warning("Please enter a brand name in the sidebar.")
    elif not industry.strip():
        st.warning("Please enter an industry in the sidebar.")
    elif not selected_competitors:
        st.warning("Please select at least one competitor before generating the brief.")
    elif not selected_categories:
        st.warning("Please select at least one category before generating the brief.")
    elif filtered_df.empty:
        st.warning("The selected data is empty. Please select at least one competitor with records.")
    else:
        try:
            with st.spinner(
                "Generating an evidence-grounded marketing brief..."
                if generation_mode == "AI-powered"
                else "Generating the rule-based portfolio brief..."
            ):
                if generation_mode == "AI-powered":
                    brief_sections = generate_ai_brief_sections(
                        data=filtered_df,
                        brand_name=brand_name.strip(),
                        industry=industry.strip(),
                        output_language=output_language,
                        api_key=api_key,
                        model=model_name,
                    )
                else:
                    brief_sections = build_marketing_brief_sections(
                        data=filtered_df,
                        selected_competitors=selected_competitors,
                        brand_name=brand_name.strip(),
                        industry=industry.strip(),
                        output_language=output_language,
                    )

                brief_sections = add_report_metadata(
                    sections=brief_sections,
                    data=filtered_df,
                    selected_competitors=selected_competitors,
                    brand_name=brand_name.strip(),
                    industry=industry.strip(),
                    generation_mode=generation_mode,
                    model=model_name,
                )

            st.session_state["brief_sections"] = brief_sections
            st.session_state["brief_markdown"] = build_markdown_report(
                brief_sections,
                brand_name.strip(),
            )
            st.session_state["brief_json"] = json.dumps(
                brief_sections,
                ensure_ascii=False,
                indent=2,
            )
            st.session_state["brief_file_name"] = (
                f"{clean_file_name(brand_name)}_competitor_marketing_brief_"
                f"{date.today().isoformat()}"
            )
            st.session_state["brief_language"] = output_language
            st.session_state["generation_mode"] = generation_mode
            st.session_state["evidence_csv"] = filtered_df.to_csv(
                index=False
            ).encode("utf-8-sig")
            st.success(f"Marketing brief generated with {generation_mode}.")
        except Exception as exc:
            st.error(f"Brief generation failed: {exc}")


# 主页面分成 4 个标签页，避免所有内容堆在一个页面里
overview_tab, data_tab, brief_tab, export_tab = st.tabs(
    ["Overview", "Data Analysis", "Marketing Brief", "Export"]
)


with overview_tab:
    # Overview：说明项目用途和使用流程
    st.subheader("Project Overview")
    st.markdown(
        """
        <div class="section-note">
            This app turns auditable competitor observations into a structured marketing
            brief. Every conclusion is grounded in the selected CSV rows, and the report
            exposes its source, record count, generation mode, and limitations.
        </div>
        """,
        unsafe_allow_html=True,
    )

    step_col_1, step_col_2, step_col_3 = st.columns(3)

    with step_col_1:
        st.markdown(
            """
            <div class="step-card">
                <div class="step-number">1</div>
                <div class="step-title">Load evidence</div>
                <div class="step-copy">Use the sample dataset or upload a CSV with your own competitor observations.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with step_col_2:
        st.markdown(
            """
            <div class="step-card">
                <div class="step-number">2</div>
                <div class="step-title">Filter and analyze</div>
                <div class="step-copy">Select competitors and categories, then review activity and content patterns.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with step_col_3:
        st.markdown(
            """
            <div class="step-card">
                <div class="step-number">3</div>
                <div class="step-title">Generate and export</div>
                <div class="step-copy">Create a grounded AI brief or rule-based fallback in Markdown and JSON.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")

    # Overview 指标卡片：快速展示当前分析范围
    metric_col_1, metric_col_2, metric_col_3, metric_col_4, metric_col_5 = st.columns(5)
    metric_col_1.metric("Selected Competitors", len(selected_competitors))
    metric_col_2.metric("Records Analyzed", len(filtered_df))
    metric_col_3.metric("Categories Covered", filtered_df["category"].nunique())
    metric_col_4.metric("Target Brand", brand_name.strip() or "Not set")
    metric_col_5.metric("Generation", generation_mode)

    if not selected_competitors:
        st.warning("No competitors selected. Use the sidebar to choose at least one competitor.")
    st.caption(
        f"Data source: {data_source_label} · "
        f"Date range: {df['date'].min()} to {df['date'].max()}"
    )


with data_tab:
    # Data Analysis：展示筛选后的数据、竞品数量统计和类别分布
    st.subheader("Data Analysis")

    if filtered_df.empty:
        st.warning("No data to analyze. Please select at least one competitor in the sidebar.")
    else:
        chart_col_1, chart_col_2 = st.columns(2)

        competitor_count_data = (
            filtered_df["competitor"]
            .value_counts()
            .rename_axis("competitor")
            .reset_index(name="records")
        )

        category_count_data = (
            filtered_df["category"]
            .value_counts()
            .rename_axis("category")
            .reset_index(name="records")
        )

        with chart_col_1:
            with st.container(border=True):
                st.markdown("#### Competitor Record Count")
                st.bar_chart(competitor_count_data.set_index("competitor"))
                st.dataframe(competitor_count_data, width="stretch", hide_index=True)

        with chart_col_2:
            with st.container(border=True):
                st.markdown("#### Category Distribution")
                st.bar_chart(category_count_data.set_index("category"))
                st.dataframe(category_count_data, width="stretch", hide_index=True)

        with st.expander("Filtered data preview", expanded=False):
            st.dataframe(
                filtered_df[REQUIRED_COLUMNS],
                width="stretch",
                hide_index=True,
            )

    with st.expander("Full source data", expanded=False):
        st.dataframe(df[REQUIRED_COLUMNS], width="stretch", hide_index=True)


with brief_tab:
    # Marketing Brief：用卡片区块展示报告，不再只堆 Markdown 文本
    st.subheader("Marketing Brief")

    if "brief_sections" not in st.session_state:
        st.info("Use the sidebar settings, then click Generate Brief.")
    else:
        st.caption(
            f"Generated with {st.session_state.get('generation_mode', 'unknown mode')} · "
            "Review the evidence and limitations before using the recommendations."
        )
        sections_to_show = [
            "Executive Summary",
            "Competitor Activity Overview",
            "Content Strategy Analysis",
            "Audience and Positioning",
            "Key Marketing Insights",
            "Recommendations",
            "Limitations",
        ]

        for section_name in sections_to_show:
            show_report_card(section_name, st.session_state["brief_sections"][section_name])


with export_tab:
    # Export：集中放置文件名和 Markdown 下载按钮
    st.subheader("Export Report")
    st.markdown(
        """
        <div class="section-note">
            This report can be included in a marketing analytics portfolio or GitHub project documentation.
        </div>
        """,
        unsafe_allow_html=True,
    )

    if "brief_markdown" not in st.session_state:
        st.info("Generate a brief first, then return here to download the Markdown file.")
    else:
        st.markdown("#### Current report file name")
        st.code(f"{st.session_state['brief_file_name']}.md", language="text")

        export_col_1, export_col_2, export_col_3 = st.columns(3)
        with export_col_1:
            st.download_button(
                label="Download Markdown",
                data=st.session_state["brief_markdown"],
                file_name=f"{st.session_state['brief_file_name']}.md",
                mime="text/markdown",
                width="stretch",
            )
        with export_col_2:
            st.download_button(
                label="Download JSON",
                data=st.session_state["brief_json"],
                file_name=f"{st.session_state['brief_file_name']}.json",
                mime="application/json",
                width="stretch",
            )
        with export_col_3:
            st.download_button(
                label="Download Filtered Evidence",
                data=st.session_state["evidence_csv"],
                file_name=(
                    f"{clean_file_name(brand_name)}_filtered_evidence_"
                    f"{date.today().isoformat()}.csv"
                ),
                mime="text/csv",
                width="stretch",
            )
