import csv
import os
import glob
import pandas as pd

def parse_number(val):
    """将德式小数逗号替换为点；转成 float 或 int"""
    if val is None:
        return None
    s = str(val).strip()
    if s == "":
        return None
    s = s.replace(",", ".")  # 德式小数转标准
    try:
        f = float(s)
        # 如果本应是整数
        return int(f) if f.is_integer() else f
    except:
        return None

def clean_unbounce_csv(input_file, output_file):
    # 用 csv.reader 读取，避免 pandas 因列数不一致报错
    with open(input_file, "r", encoding="utf-8", errors="ignore") as f:
        rows = list(csv.reader(f))

    # === 结构说明 ===
    # 第 0 行: ,Overall,,Variant F,,Variant D,
    # 第 1 行: Date, Visitors, Conversions, Rolling Avg, Visitors, Conversions, Rolling Avg, ...
    # 第 2 行起: 数据
    if len(rows) < 3:
        print(f"⚠️ 文件 {input_file} 行数不足，跳过。")
        return

    header_variants = rows[0]
    header_metrics = rows[1]
    data_rows = rows[2:]

    # 填充 variant 名称
    variants = []
    current_variant = None
    for h in header_variants[1:]:
        if h.strip():
            current_variant = h.strip()
        variants.append(current_variant)

    # 确定每组列数 (Visitors, Conversions, Rolling Avg)
    metric_groups = [header_metrics[1 + i : 1 + i + 3] for i in range(0, len(header_metrics) - 1, 3)]
    variant_names = list(dict.fromkeys(variants[::3]))  # 每隔3列取一个变体名并去重

    tidy_rows = []
    for row in data_rows:
        if not row or not row[0].strip():
            continue
        date_val = row[0].strip()

        # 处理后续指标列
        numeric_part = row[1:]
        # 避免行尾空列
        while len(numeric_part) and (numeric_part[-1] == "" or numeric_part[-1] is None):
            numeric_part.pop()

        # 一般 pattern: 变体数 × 3
        for idx, variant in enumerate(variant_names):
            base = idx * 3
            if base + 2 >= len(numeric_part):
                continue
            visitors = parse_number(numeric_part[base])
            conversions = parse_number(numeric_part[base + 1])
            rolling = parse_number(numeric_part[base + 2])
            tidy_rows.append({
                "Date": date_val,
                "Variant": variant,
                "Visitors": visitors,
                "Conversions": conversions,
                "Rolling Avg (%)": rolling
            })

    df = pd.DataFrame(tidy_rows)
    df.to_csv(output_file, index=False, encoding="utf-8-sig")
    print(f"✅ 已清理: {input_file} → {output_file}")

if __name__ == "__main__":
    input_folder = "data"      # 📥 原始 CSV
    output_folder = "cleaned"  # 📤 输出清洗结果
    os.makedirs(output_folder, exist_ok=True)

    files = sorted(glob.glob(os.path.join(input_folder, "*.csv")))
    if not files:
        print("⚠️ data/ 文件夹中没有找到 CSV。")
    for f in files:
        base = os.path.basename(f)
        out = os.path.join(output_folder, base.replace(".csv", "_CLEAN.csv"))
        clean_unbounce_csv(f, out)
