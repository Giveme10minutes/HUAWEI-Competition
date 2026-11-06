# Python 数据分析：用 Python 完成数据清洗、统计与可视化

Python 数据分析指用 Python 及其数据生态完成取数、清洗、统计和图表输出的技术组合，不是某个岗位名称。它把编程语言、数据处理库和可视化库组合起来，适合处理表格数据、做探索性分析并形成可重复的脚本。

来源：主题名称取自 roadmap.sh 的 Python Data Analysis 路线索引（https://roadmap.sh/python-data-analysis）；定位说明为整理者归纳。

## Python 数据分析是什么：由哪些工具组成

这套组合通常包含数组计算、表格处理、统计与可视化几类库，它们分工不同但可以互相传递数据。pandas 的 DataFrame 是多数流程的中心结构，NumPy 提供底层数组运算，绘图库负责把结果呈现出来。

相关库（6 项）：NumPy（多维数组与数值计算）、pandas（表格数据读写与处理）、Matplotlib（基础绘图）、Seaborn（统计图表）、Plotly（交互图表）、scikit-learn（统计建模与机器学习）。

参考：pandas 官方文档（https://pandas.pydata.org/docs/getting_started/index.html）。

## Python 数据分析的典型流程

一次分析通常从明确问题开始，再读取数据、检查缺失与重复、转换字段类型、分组统计，最后用图表或表格呈现结论。每一步都应保留可重复执行的代码，避免只留下手工改过的结果文件。

来源：该流程说明由整理者归纳；主题名称取自 roadmap.sh 的 Python Data Analysis 路线索引（https://roadmap.sh/python-data-analysis）。

## Python 数据分析的数据读取与清洗

数据可能来自本地文件、数据库或网络接口，读取后要统一列名、类型和缺失值处理方式。清洗的目标是让后续统计有明确口径，而不是把所有异常值都删掉。

相关工具（6 项）：pandas（读写 CSV、Excel 与 JSON）、openpyxl（读写 Excel 文件）、requests（调用网络接口取数）、SQLAlchemy（连接数据库）、PyArrow（读写 Parquet 列式文件）、DuckDB（本地分析型 SQL 查询）。

来源：主题名称取自 roadmap.sh 的 Python Data Analysis 路线索引（https://roadmap.sh/python-data-analysis）；工具用途为整理者归纳。

## Python 数据分析的统计与可视化

统计部分关注分布、相关性和分组差异，可视化则把结果变成可比较的图。可以先画直方图和相关矩阵了解数据，再针对结论选择折线图、箱线图或交互图表。

相关工具（6 项）：Matplotlib（基础图表）、Seaborn（统计图与热力图）、Plotly（交互图表）、SciPy（统计检验）、pandas（分组聚合）、JupyterLab（交互式分析记录）。

来源：主题名称取自 roadmap.sh 的 Python Data Analysis 路线索引（https://roadmap.sh/python-data-analysis）；工具用途为整理者归纳。

## Python 数据分析的运行环境与包管理

分析代码通常在交互式笔记本或编辑器中运行，依赖用包管理工具隔离到项目环境。固定依赖版本并记录环境，能让别人重新跑出相近结果。

相关工具（6 项）：JupyterLab（笔记本式分析）、VS Code（代码编辑与调试）、pip（安装 Python 包）、conda（环境与包管理）、venv（标准库虚拟环境）、uv（快速的包与环境工具）。

来源：主题名称取自 roadmap.sh 的 Python Data Analysis 路线索引（https://roadmap.sh/python-data-analysis）；工具用途为整理者归纳。

## 如何开始练习 Python 数据分析

最小练习是取一份带缺失值的 CSV（例如公开的销售或气象数据），用 pandas 完成读取、去重、填补缺失、按类别分组求均值，再用 Matplotlib 或 Seaborn 画两张图并保存。产出是一个可重复运行的笔记本和一段结论说明。

来源：该练习由整理者归纳设计；主题名称取自 roadmap.sh 的 Python Data Analysis 路线索引（https://roadmap.sh/python-data-analysis）。
