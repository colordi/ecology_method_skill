#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
生态学研究：本地数据摘要与质量审查（Step 1）

设计目标：
- 尽量零配置：默认扫描当前目录下的常见数据文件（csv/tsv/xlsx）。
- 可追溯：把“读了什么、怎么读的、输出到哪里”写入 run_meta.json。
- 可扩展：后续可在 Step 3（系统深入分析）复用输出的列信息与缺失模式。

输出（默认）：
analysis/00_data_summary/
  - data_summary.md
  - file_inventory.csv
  - columns.csv
  - numeric_summary.csv
  - categorical_top_values.csv
  - run_meta.json
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Optional

import pandas as pd


SUPPORTED_EXTS = {".csv", ".tsv", ".xlsx", ".xls"}


@dataclass(frozen=True)
class DatasetRef:
    dataset_id: str
    file_path: str
    file_type: str
    sheet_name: str | None


def _now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def _safe_mkdir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def _iter_data_files(root: Path, recursive: bool) -> Iterable[Path]:
    pattern = "**/*" if recursive else "*"
    for file_path in root.glob(pattern):
        if file_path.is_file() and file_path.suffix.lower() in SUPPORTED_EXTS:
            yield file_path


def _read_csv_with_fallbacks(file_path: Path) -> pd.DataFrame:
    # 先尝试 UTF-8；失败再尝试 GBK（常见于中文 Windows 环境）
    # 为减少“分隔符不一致”问题，csv/tsv分别处理；其他情况再走自动推断。
    suffix = file_path.suffix.lower()
    read_kwargs = {"dtype_backend": "numpy_nullable"}

    if suffix == ".tsv":
        read_kwargs.update({"sep": "\t"})

    encodings = ["utf-8", "utf-8-sig", "gbk"]
    last_err: Exception | None = None
    for enc in encodings:
        try:
            return pd.read_csv(file_path, encoding=enc, **read_kwargs)
        except Exception as e:  # noqa: BLE001 - 需要逐个尝试
            last_err = e

    # 兜底：尝试自动分隔符推断（可能较慢）
    try:
        return pd.read_csv(file_path, sep=None, engine="python", encoding="utf-8", **read_kwargs)
    except Exception as e:  # noqa: BLE001
        if last_err is not None:
            raise RuntimeError(f"读取失败（已尝试多种编码与分隔符）：{file_path}") from last_err
        raise RuntimeError(f"读取失败：{file_path}") from e


def _read_excel_sheets(file_path: Path, all_sheets: bool, max_sheets: int) -> list[DatasetRef]:
    xls = pd.ExcelFile(file_path)
    sheet_names = list(xls.sheet_names)
    if all_sheets:
        selected = sheet_names[: max_sheets if max_sheets > 0 else len(sheet_names)]
    else:
        selected = sheet_names[:1]

    refs: list[DatasetRef] = []
    for sheet in selected:
        dataset_id = f"{file_path.name}#{sheet}"
        refs.append(
            DatasetRef(
                dataset_id=dataset_id,
                file_path=str(file_path),
                file_type="excel",
                sheet_name=sheet,
            )
        )
    return refs


def _expand_datasets(root: Path, recursive: bool, all_sheets: bool, max_sheets: int) -> list[DatasetRef]:
    datasets: list[DatasetRef] = []
    for file_path in _iter_data_files(root, recursive=recursive):
        suffix = file_path.suffix.lower()
        if suffix in {".xlsx", ".xls"}:
            datasets.extend(_read_excel_sheets(file_path, all_sheets=all_sheets, max_sheets=max_sheets))
        elif suffix in {".csv", ".tsv"}:
            datasets.append(
                DatasetRef(
                    dataset_id=file_path.name,
                    file_path=str(file_path),
                    file_type="csv" if suffix == ".csv" else "tsv",
                    sheet_name=None,
                )
            )
    return datasets


def _maybe_sample(df: pd.DataFrame, sample_rows: int) -> tuple[pd.DataFrame, bool]:
    if sample_rows <= 0:
        return df, False
    if len(df) <= sample_rows:
        return df, False
    return df.sample(n=sample_rows, random_state=0), True


def _infer_kind(series: pd.Series) -> str:
    dtype = series.dtype
    if pd.api.types.is_bool_dtype(dtype):
        return "布尔"
    if pd.api.types.is_numeric_dtype(dtype):
        return "数值"
    if pd.api.types.is_datetime64_any_dtype(dtype):
        return "日期时间"
    return "文本/类别"


def _to_example_values(series: pd.Series, max_values: int) -> str:
    if max_values <= 0:
        return ""
    values = series.dropna().astype(str).unique().tolist()
    values = values[:max_values]
    return "｜".join(values)


def _profile_dataframe(
    dataset: DatasetRef,
    df: pd.DataFrame,
    sample_rows: int,
    max_categories: int,
    top_k: int,
) -> dict:
    df_used, sampled = _maybe_sample(df, sample_rows=sample_rows)

    rows, cols = df.shape
    duplicate_rows = int(df_used.duplicated().sum()) if cols > 0 else 0

    column_rows: list[dict] = []
    numeric_rows: list[dict] = []
    categorical_rows: list[dict] = []

    for col in df_used.columns:
        series = df_used[col]
        missing_count = int(series.isna().sum())
        non_null_count = int(series.notna().sum())
        unique_count = int(series.nunique(dropna=True))
        missing_rate = (missing_count / len(df_used)) if len(df_used) else 0.0
        kind = _infer_kind(series)

        column_rows.append(
            {
                "dataset_id": dataset.dataset_id,
                "column": str(col),
                "kind": kind,
                "dtype": str(series.dtype),
                "rows_profiled": int(len(df_used)),
                "sampled": bool(sampled),
                "non_null_count": non_null_count,
                "missing_count": missing_count,
                "missing_rate": round(missing_rate, 6),
                "unique_count": unique_count,
                "example_values": _to_example_values(series, max_values=3),
            }
        )

        if kind == "数值":
            desc = series.describe(percentiles=[0.25, 0.5, 0.75])
            numeric_rows.append(
                {
                    "dataset_id": dataset.dataset_id,
                    "column": str(col),
                    "count": float(desc.get("count", 0.0)),
                    "mean": float(desc.get("mean", float("nan"))),
                    "std": float(desc.get("std", float("nan"))),
                    "min": float(desc.get("min", float("nan"))),
                    "p25": float(desc.get("25%", float("nan"))),
                    "p50": float(desc.get("50%", float("nan"))),
                    "p75": float(desc.get("75%", float("nan"))),
                    "max": float(desc.get("max", float("nan"))),
                }
            )
        elif kind == "文本/类别" and unique_count > 0 and unique_count <= max_categories:
            vc = series.dropna().astype(str).value_counts().head(top_k)
            total = float(len(series.dropna()))
            for value, count in vc.items():
                categorical_rows.append(
                    {
                        "dataset_id": dataset.dataset_id,
                        "column": str(col),
                        "value": value,
                        "count": int(count),
                        "percent": round((float(count) / total) if total else 0.0, 6),
                    }
                )

    return {
        "dataset": dataset,
        "rows": rows,
        "cols": cols,
        "rows_profiled": len(df_used),
        "sampled": sampled,
        "duplicate_rows_in_profiled": duplicate_rows,
        "columns": column_rows,
        "numeric": numeric_rows,
        "categorical": categorical_rows,
    }


def _load_dataset(dataset: DatasetRef) -> pd.DataFrame:
    file_path = Path(dataset.file_path)
    if dataset.file_type in {"csv", "tsv"}:
        return _read_csv_with_fallbacks(file_path)
    if dataset.file_type == "excel":
        return pd.read_excel(file_path, sheet_name=dataset.sheet_name, dtype_backend="numpy_nullable")
    raise ValueError(f"不支持的文件类型：{dataset.file_type}")


def _write_markdown_report(
    output_dir: Path,
    profiles: list[dict],
    *,
    project_root: Path,
    sample_rows: int,
    max_categories: int,
    top_k: int,
) -> None:
    lines: list[str] = []
    lines.append("# 本地数据摘要报告（自动生成）")
    lines.append("")
    lines.append(f"- 生成时间：{_now_iso()}")
    lines.append(f"- 项目目录：`{project_root}`")
    lines.append(f"- 采样策略：{'不采样（全量统计）' if sample_rows <= 0 else f'若行数过大则随机抽样 {sample_rows} 行（用于画像）'}")
    lines.append(f"- 类别列Top统计：唯一值≤{max_categories} 时输出 Top {top_k}")
    lines.append("")
    lines.append("## 总览")
    lines.append("")
    if not profiles:
        lines.append("- 未在指定路径发现可读取的数据文件（csv/tsv/xlsx）。")
    else:
        lines.append(f"- 数据集数量：{len(profiles)}")
        total_rows = sum(int(p.get("rows", 0)) for p in profiles)
        lines.append(f"- 总行数（各数据集相加）：{total_rows}")
    lines.append("")

    for p in profiles:
        dataset: DatasetRef = p["dataset"]
        lines.append(f"## 数据集：{dataset.dataset_id}")
        lines.append("")
        lines.append(f"- 文件：`{dataset.file_path}`")
        if dataset.sheet_name:
            lines.append(f"- 工作表：`{dataset.sheet_name}`")
        lines.append(f"- 形状：{p['rows']} 行 × {p['cols']} 列")
        if p["sampled"]:
            lines.append(f"- 画像基于抽样：{p['rows_profiled']} 行（为速度与稳定性）")
        lines.append(f"- 画像行重复数（抽样子集）：{p['duplicate_rows_in_profiled']}")
        lines.append("")

        # 缺失率最高的列
        columns = p["columns"]
        if columns:
            sorted_by_missing = sorted(columns, key=lambda r: r["missing_rate"], reverse=True)
            top_missing = sorted_by_missing[: min(5, len(sorted_by_missing))]
            lines.append("### 缺失率最高的列（Top 5）")
            lines.append("")
            for r in top_missing:
                lines.append(
                    f"- `{r['column']}`：缺失 {r['missing_count']}/{r['rows_profiled']}（{r['missing_rate']:.2%}），类型={r['kind']}，示例={r['example_values'] or '无'}"
                )
            lines.append("")

            # 数值列概览
            numeric = p["numeric"]
            if numeric:
                lines.append("### 数值列概览（节选）")
                lines.append("")
                for r in numeric[: min(10, len(numeric))]:
                    lines.append(
                        f"- `{r['column']}`：均值={r['mean']:.4g}，SD={r['std']:.4g}，范围=[{r['min']:.4g}, {r['max']:.4g}]，n={int(r['count'])}"
                    )
                lines.append("")

        lines.append("### 输出文件")
        lines.append("")
        lines.append(f"- `file_inventory.csv`：数据集清单与读取状态")
        lines.append(f"- `columns.csv`：列画像（类型、缺失、唯一值、示例）")
        lines.append(f"- `numeric_summary.csv`：数值列描述统计")
        lines.append(f"- `categorical_top_values.csv`：类别列 Top 值（有上限）")
        lines.append("")

    (output_dir / "data_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="生态学研究：本地数据摘要与质量审查（生成可复用的数据画像与报告）",
    )
    parser.add_argument(
        "--input",
        type=str,
        default=".",
        help="输入路径：数据文件或目录（默认：当前目录）",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="analysis/00_data_summary",
        help="输出目录（默认：analysis/00_data_summary）",
    )
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="递归扫描子目录",
    )
    parser.add_argument(
        "--all-sheets",
        action="store_true",
        help="Excel 分析所有工作表（默认只分析第一个）",
    )
    parser.add_argument(
        "--max-sheets",
        type=int,
        default=20,
        help="Excel 最多分析多少个工作表（默认：20；<=0 表示不限制）",
    )
    parser.add_argument(
        "--sample-rows",
        type=int,
        default=20000,
        help="用于画像的抽样行数（<=0 表示不抽样；默认：20000）",
    )
    parser.add_argument(
        "--max-categories",
        type=int,
        default=50,
        help="类别列唯一值<=该阈值时才输出 Top 统计（默认：50）",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=10,
        help="类别列输出 Top K（默认：10）",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = _parse_args(argv)
    input_path = Path(args.input).resolve()
    output_dir = Path(args.output).resolve()
    project_root = Path.cwd().resolve()

    _safe_mkdir(output_dir)

    datasets: list[DatasetRef] = []
    if input_path.is_file():
        suffix = input_path.suffix.lower()
        if suffix not in SUPPORTED_EXTS:
            print(f"[错误] 不支持的文件扩展名：{suffix}", file=sys.stderr)
            return 2
        if suffix in {".xlsx", ".xls"}:
            datasets = _read_excel_sheets(input_path, all_sheets=args.all_sheets, max_sheets=args.max_sheets)
        else:
            datasets = [
                DatasetRef(
                    dataset_id=input_path.name,
                    file_path=str(input_path),
                    file_type="csv" if suffix == ".csv" else "tsv",
                    sheet_name=None,
                )
            ]
    elif input_path.is_dir():
        datasets = _expand_datasets(
            input_path,
            recursive=args.recursive,
            all_sheets=args.all_sheets,
            max_sheets=args.max_sheets,
        )
    else:
        print(f"[错误] 输入路径不存在：{input_path}", file=sys.stderr)
        return 2

    inventory_rows: list[dict] = []
    all_columns: list[dict] = []
    all_numeric: list[dict] = []
    all_categorical: list[dict] = []
    profiles: list[dict] = []

    for dataset in datasets:
        file_path = Path(dataset.file_path)
        file_size = file_path.stat().st_size if file_path.exists() else 0
        try:
            df = _load_dataset(dataset)
            profile = _profile_dataframe(
                dataset,
                df,
                sample_rows=args.sample_rows,
                max_categories=args.max_categories,
                top_k=args.top_k,
            )
            profiles.append(profile)
            all_columns.extend(profile["columns"])
            all_numeric.extend(profile["numeric"])
            all_categorical.extend(profile["categorical"])
            inventory_rows.append(
                {
                    "dataset_id": dataset.dataset_id,
                    "file_path": dataset.file_path,
                    "file_type": dataset.file_type,
                    "sheet_name": dataset.sheet_name or "",
                    "size_bytes": file_size,
                    "rows": profile["rows"],
                    "cols": profile["cols"],
                    "read_status": "ok",
                    "error": "",
                }
            )
        except Exception as e:  # noqa: BLE001 - 要把错误写入清单
            inventory_rows.append(
                {
                    "dataset_id": dataset.dataset_id,
                    "file_path": dataset.file_path,
                    "file_type": dataset.file_type,
                    "sheet_name": dataset.sheet_name or "",
                    "size_bytes": file_size,
                    "rows": "",
                    "cols": "",
                    "read_status": "error",
                    "error": str(e),
                }
            )

    pd.DataFrame(inventory_rows).to_csv(output_dir / "file_inventory.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(all_columns).to_csv(output_dir / "columns.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(all_numeric).to_csv(output_dir / "numeric_summary.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(all_categorical).to_csv(output_dir / "categorical_top_values.csv", index=False, encoding="utf-8-sig")

    _write_markdown_report(
        output_dir,
        profiles,
        project_root=project_root,
        sample_rows=args.sample_rows,
        max_categories=args.max_categories,
        top_k=args.top_k,
    )

    run_meta = {
        "generated_at": _now_iso(),
        "project_root": str(project_root),
        "input": str(input_path),
        "output": str(output_dir),
        "args": vars(args),
        "python": sys.version,
        "pandas": pd.__version__,
        "platform": os.name,
        "datasets_found": len(datasets),
    }
    (output_dir / "run_meta.json").write_text(json.dumps(run_meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"[OK] 已生成数据摘要：{output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

