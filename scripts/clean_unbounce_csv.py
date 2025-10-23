
import pandas as pd
import os
import glob

def clean_unbounce_csv(input_file, output_file):
    """
    清洗 Unbounce 导出的多变体报表 CSV
    把 “一行多个变体” 的数据转换成 “每行一个变体” 的整洁结构
    """
    # 读取原始文件（无表头）
    df = pd.read_csv(input_file, header=None)

    # 第 1 行：Variant 名称，如 Overall, Variant I, Variant H
    variants_row = df.iloc[0].fillna(method='ffill')
    variants = variants_row.tolist()[1:]  # 去掉日期列

    # 第 2 行：指标，如 Visitors, Conversions, 7 Day Rolling Average (%)
    metrics_row = df.iloc[1].tolist()[1:]

    # 数据部分（从第 3 行开始）
    data = df.iloc[2:].reset_index(drop=True)
    col_count = len(metrics_row)

    clean_rows = []
    for i in range(len(data)):
        date_value = data.iloc[i, 0]  # 第一列是日期

        # 每 3 列代表一个 variant
        for j in range(0, col_count, 3):
            variant_name = variants[j]
            visitors = data.iloc[i, j + 1]
            conversions = data.iloc[i, j + 2]
            rolling_avg = data.iloc[i, j + 3]

            clean_rows.append({
                "Date": date_value,
                "Variant": variant_name,
                "Visitors": visitors,
                "Conversions": conversions,
                "Rolling Avg (%)": rolling_avg
            })

    clean_df = pd.DataFrame(clean_rows)

    # 输出 UTF-8 带 BOM，避免 Excel 乱码
    clean_df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"✅ 已清理: {input_file} → {output_file}")

# 入口
if __name__ == "__main__":
    input_folder = "data"         # 📥 原始 CSV 文件夹
    output_folder = "cleaned"     # 📤 清理后文件输出文件夹

    os.makedirs(output_folder, exist_ok=True)

    for file in glob.glob(os.path.join(input_folder, "*.csv")):
        filename = os.path.basename(file)
        output_file = os.path.join(output_folder, filename.replace(".csv", "_CLEAN.csv"))
        clean_unbounce_csv(file, output_file)
