#!/usr/bin/env Rscript
# -*- coding: utf-8 -*-

# 生态学研究：本地数据摘要与质量审查（Step 1，默认 R）
#
# 设计目标：
# - 尽量零配置：默认扫描当前目录下的常见数据文件（csv/tsv/xlsx）。
# - 可追溯：把“读了什么、怎么读的、输出到哪里”写入 run_meta.json。
# - 可扩展：后续可在 Step 3（系统深入分析）复用输出的列信息与缺失模式。
#
# 输出（默认）：
# analysis/00_data_summary/
#   - data_summary.md
#   - file_inventory.csv
#   - columns.csv
#   - numeric_summary.csv
#   - categorical_top_values.csv
#   - run_meta.json
#
# 依赖建议：
# - 读取 Excel：readxl（必需，若存在 xlsx/xls）
# - JSON 元数据：无额外依赖（脚本内置最小 JSON 序列化）

suppressWarnings({
  options(stringsAsFactors = FALSE)
})


supported_exts <- c(".csv", ".tsv", ".xlsx", ".xls")


now_iso <- function() {
  format(Sys.time(), "%Y-%m-%dT%H:%M:%S%z")
}


json_escape <- function(x) {
  # 仅覆盖本脚本需要的最小转义：反斜杠、双引号、换行、回车、制表符
  x <- gsub("\\\\", "\\\\\\\\", x)
  x <- gsub("\"", "\\\\\"", x)
  x <- gsub("\n", "\\\\n", x)
  x <- gsub("\r", "\\\\r", x)
  x <- gsub("\t", "\\\\t", x)
  x
}


to_json <- function(x) {
  if (is.null(x)) {
    return("null")
  }
  if (length(x) == 1 && is.na(x)) {
    return("null")
  }
  if (is.logical(x)) {
    if (length(x) == 1) {
      return(ifelse(isTRUE(x), "true", "false"))
    }
    return(paste0("[", paste(vapply(x, to_json, character(1)), collapse = ","), "]"))
  }
  if (is.numeric(x)) {
    if (length(x) == 1) {
      return(ifelse(is.finite(x), format(x, scientific = FALSE, trim = TRUE), "null"))
    }
    return(paste0("[", paste(vapply(x, to_json, character(1)), collapse = ","), "]"))
  }
  if (is.character(x)) {
    if (length(x) == 1) {
      return(paste0("\"", json_escape(x), "\""))
    }
    return(paste0("[", paste(vapply(x, to_json, character(1)), collapse = ","), "]"))
  }
  if (is.list(x)) {
    nms <- names(x)
    if (!is.null(nms) && any(nms != "")) {
      parts <- character(0)
      for (i in seq_along(x)) {
        key <- nms[[i]]
        if (is.null(key) || key == "") {
          next
        }
        parts <- c(parts, paste0("\"", json_escape(key), "\":", to_json(x[[i]])))
      }
      return(paste0("{", paste(parts, collapse = ","), "}"))
    }
    return(paste0("[", paste(vapply(x, to_json, character(1)), collapse = ","), "]"))
  }
  # 兜底：转字符串
  paste0("\"", json_escape(as.character(x)), "\"")
}


write_text_utf8 <- function(path, lines) {
  con <- file(path, open = "w", encoding = "UTF-8")
  on.exit(close(con), add = TRUE)
  writeLines(lines, con = con, sep = "\n", useBytes = TRUE)
}


write_csv_utf8_bom <- function(df, path) {
  # 为 Windows Excel 兼容性写入 UTF-8 BOM
  con <- file(path, open = "wb")
  writeBin(as.raw(c(0xEF, 0xBB, 0xBF)), con)
  close(con)
  utils::write.table(
    df,
    file = path,
    sep = ",",
    row.names = FALSE,
    col.names = TRUE,
    append = TRUE,
    quote = TRUE,
    qmethod = "double",
    na = "",
    fileEncoding = "UTF-8"
  )
}


parse_args <- function(argv) {
  opts <- list(
    input = ".",
    output = "analysis/00_data_summary",
    recursive = FALSE,
    all_sheets = FALSE,
    max_sheets = 20,
    sample_rows = 20000,
    max_categories = 50,
    top_k = 10
  )

  if (length(argv) == 0) {
    return(opts)
  }

  i <- 1
  while (i <= length(argv)) {
    a <- argv[[i]]
    if (a %in% c("-h", "--help")) {
      cat(
        paste(
          "用法：Rscript scripts/data_summary.R [参数]",
          "",
          "参数：",
          "  --input <path>          输入路径：文件或目录（默认：.）",
          "  --output <dir>          输出目录（默认：analysis/00_data_summary）",
          "  --recursive             递归扫描子目录",
          "  --all-sheets            Excel 分析所有工作表（默认只分析第一个）",
          "  --max-sheets <n>         Excel 最多分析多少个工作表（默认：20；<=0 表示不限制）",
          "  --sample-rows <n>        用于画像的抽样行数（默认：20000；<=0 表示不抽样）",
          "  --max-categories <n>     类别列唯一值<=该阈值时才输出 Top（默认：50）",
          "  --top-k <n>              类别列输出 Top K（默认：10）",
          "",
          sep = "\n"
        )
      )
      quit(status = 0)
    }

    if (a == "--recursive") {
      opts$recursive <- TRUE
      i <- i + 1
      next
    }
    if (a == "--all-sheets") {
      opts$all_sheets <- TRUE
      i <- i + 1
      next
    }

    # 需要值的参数
    if (a %in% c("--input", "--output", "--max-sheets", "--sample-rows", "--max-categories", "--top-k")) {
      if (i == length(argv)) {
        stop(paste0("参数缺少取值：", a))
      }
      v <- argv[[i + 1]]
      if (a == "--input") opts$input <- v
      if (a == "--output") opts$output <- v
      if (a == "--max-sheets") opts$max_sheets <- as.integer(v)
      if (a == "--sample-rows") opts$sample_rows <- as.integer(v)
      if (a == "--max-categories") opts$max_categories <- as.integer(v)
      if (a == "--top-k") opts$top_k <- as.integer(v)
      i <- i + 2
      next
    }

    stop(paste0("不支持的参数：", a))
  }

  opts
}


infer_kind <- function(x) {
  if (is.logical(x)) return("布尔")
  if (inherits(x, "POSIXct") || inherits(x, "POSIXt") || inherits(x, "Date")) return("日期时间")
  if (is.numeric(x)) return("数值")
  "文本/类别"
}


example_values <- function(x, n = 3) {
  if (n <= 0) return("")
  v <- unique(x[!is.na(x)])
  if (length(v) == 0) return("")
  v <- as.character(v)[seq_len(min(n, length(v)))]
  v <- substr(v, 1, 80)
  paste(v, collapse = "\uFF5C") # 全角分隔符“｜”
}


read_table_with_fallbacks <- function(file_path, sep) {
  encodings <- c("UTF-8", "UTF-8-BOM", "GBK")
  last_err <- NULL
  for (enc in encodings) {
    df <- tryCatch(
      {
        utils::read.table(
          file_path,
          sep = sep,
          header = TRUE,
          check.names = FALSE,
          quote = "\"",
          stringsAsFactors = FALSE,
          fileEncoding = enc
        )
      },
      error = function(e) {
        last_err <<- e
        NULL
      }
    )
    if (!is.null(df)) return(df)
  }
  stop(paste0("读取失败（已尝试多种编码）：", file_path, "；原因：", as.character(last_err)))
}


read_dataset <- function(ref) {
  fp <- ref$file_path
  ext <- tolower(tools::file_ext(fp))
  if (ext %in% c("csv", "tsv")) {
    sep <- ifelse(ext == "tsv", "\t", ",")
    return(read_table_with_fallbacks(fp, sep = sep))
  }
  if (ext %in% c("xlsx", "xls")) {
    if (!requireNamespace("readxl", quietly = TRUE)) {
      stop("读取 Excel 需要安装 R 包 readxl（install.packages('readxl')）")
    }
    df <- readxl::read_excel(fp, sheet = ref$sheet_name)
    return(as.data.frame(df, stringsAsFactors = FALSE))
  }
  stop(paste0("不支持的文件类型：", fp))
}


expand_datasets <- function(input_path, recursive, all_sheets, max_sheets) {
  if (file.exists(input_path) && !dir.exists(input_path)) {
    # 单文件
    ext <- paste0(".", tolower(tools::file_ext(input_path)))
    if (!(ext %in% supported_exts)) {
      stop(paste0("不支持的文件扩展名：", ext))
    }
    if (ext %in% c(".xlsx", ".xls")) {
      if (!requireNamespace("readxl", quietly = TRUE)) {
        stop("读取 Excel 需要安装 R 包 readxl（install.packages('readxl')）")
      }
      sheets <- readxl::excel_sheets(input_path)
      selected <- if (isTRUE(all_sheets)) sheets else sheets[1]
      if (!is.null(max_sheets) && is.finite(max_sheets) && max_sheets > 0) {
        selected <- selected[seq_len(min(length(selected), max_sheets))]
      }
      out <- lapply(selected, function(sh) {
        list(
          dataset_id = paste0(basename(input_path), "#", sh),
          file_path = normalizePath(input_path, winslash = "/", mustWork = FALSE),
          sheet_name = sh
        )
      })
      return(out)
    }
    return(list(list(
      dataset_id = basename(input_path),
      file_path = normalizePath(input_path, winslash = "/", mustWork = FALSE),
      sheet_name = NULL
    )))
  }

  if (!dir.exists(input_path)) {
    stop(paste0("输入路径不存在：", input_path))
  }

  files <- list.files(
    input_path,
    pattern = "\\.(csv|tsv|xlsx|xls)$",
    full.names = TRUE,
    recursive = isTRUE(recursive),
    ignore.case = TRUE
  )

  refs <- list()
  for (fp in files) {
    ext <- paste0(".", tolower(tools::file_ext(fp)))
    if (!(ext %in% supported_exts)) next
    if (ext %in% c(".xlsx", ".xls")) {
      if (!requireNamespace("readxl", quietly = TRUE)) {
        # Excel 需要 readxl；若缺失则仍记录到清单中，但读取时会报错
        refs <- c(refs, list(list(
          dataset_id = paste0(basename(fp), "#", "(需要readxl)"),
          file_path = normalizePath(fp, winslash = "/", mustWork = FALSE),
          sheet_name = NULL
        )))
        next
      }
      sheets <- readxl::excel_sheets(fp)
      selected <- if (isTRUE(all_sheets)) sheets else sheets[1]
      if (!is.null(max_sheets) && is.finite(max_sheets) && max_sheets > 0) {
        selected <- selected[seq_len(min(length(selected), max_sheets))]
      }
      for (sh in selected) {
        refs <- c(refs, list(list(
          dataset_id = paste0(basename(fp), "#", sh),
          file_path = normalizePath(fp, winslash = "/", mustWork = FALSE),
          sheet_name = sh
        )))
      }
    } else {
      refs <- c(refs, list(list(
        dataset_id = basename(fp),
        file_path = normalizePath(fp, winslash = "/", mustWork = FALSE),
        sheet_name = NULL
      )))
    }
  }
  refs
}


profile_dataset <- function(ref, df, sample_rows, max_categories, top_k) {
  rows <- nrow(df)
  cols <- ncol(df)

  df_profile <- df
  sampled <- FALSE
  if (!is.null(sample_rows) && is.finite(sample_rows) && sample_rows > 0 && rows > sample_rows) {
    set.seed(0)
    idx <- sample.int(rows, size = sample_rows)
    df_profile <- df_profile[idx, , drop = FALSE]
    sampled <- TRUE
  }

  dup_rows <- if (ncol(df_profile) > 0) sum(duplicated(df_profile)) else 0

  col_rows <- list()
  num_rows <- list()
  cat_rows <- list()

  prof_rows <- nrow(df_profile)
  for (col in names(df_profile)) {
    x <- df_profile[[col]]
    miss <- sum(is.na(x))
    non_null <- sum(!is.na(x))
    uniq <- length(unique(x[!is.na(x)]))
    miss_rate <- ifelse(prof_rows > 0, miss / prof_rows, 0)
    kind <- infer_kind(x)
    dtype <- paste(class(x), collapse = "|")

    col_rows <- c(col_rows, list(data.frame(
      dataset_id = ref$dataset_id,
      column = col,
      kind = kind,
      dtype = dtype,
      rows_profiled = prof_rows,
      sampled = sampled,
      non_null_count = non_null,
      missing_count = miss,
      missing_rate = round(miss_rate, 6),
      unique_count = uniq,
      example_values = example_values(x, n = 3),
      stringsAsFactors = FALSE
    )))

    if (kind == "数值") {
      x_num <- as.numeric(x)
      x_num <- x_num[!is.na(x_num)]
      if (length(x_num) == 0) {
        num_rows <- c(num_rows, list(data.frame(
          dataset_id = ref$dataset_id,
          column = col,
          count = 0,
          mean = NA_real_,
          sd = NA_real_,
          min = NA_real_,
          p25 = NA_real_,
          p50 = NA_real_,
          p75 = NA_real_,
          max = NA_real_,
          stringsAsFactors = FALSE
        )))
      } else {
        qs <- as.numeric(stats::quantile(x_num, probs = c(0.25, 0.5, 0.75), names = FALSE))
        num_rows <- c(num_rows, list(data.frame(
          dataset_id = ref$dataset_id,
          column = col,
          count = length(x_num),
          mean = mean(x_num),
          sd = stats::sd(x_num),
          min = min(x_num),
          p25 = qs[[1]],
          p50 = qs[[2]],
          p75 = qs[[3]],
          max = max(x_num),
          stringsAsFactors = FALSE
        )))
      }
    }

    if (kind == "文本/类别" && uniq > 0 && !is.null(max_categories) && uniq <= max_categories) {
      x_chr <- as.character(x)
      x_chr <- x_chr[!is.na(x_chr)]
      total <- length(x_chr)
      if (total > 0) {
        tab <- sort(table(x_chr), decreasing = TRUE)
        tab <- head(tab, ifelse(is.null(top_k) || !is.finite(top_k) || top_k <= 0, length(tab), top_k))
        for (v in names(tab)) {
          ct <- as.integer(tab[[v]])
          cat_rows <- c(cat_rows, list(data.frame(
            dataset_id = ref$dataset_id,
            column = col,
            value = substr(v, 1, 200),
            count = ct,
            percent = round(ct / total, 6),
            stringsAsFactors = FALSE
          )))
        }
      }
    }
  }

  list(
    rows = rows,
    cols = cols,
    rows_profiled = prof_rows,
    sampled = sampled,
    duplicate_rows_in_profiled = dup_rows,
    columns = if (length(col_rows) > 0) do.call(rbind, col_rows) else data.frame(),
    numeric = if (length(num_rows) > 0) do.call(rbind, num_rows) else data.frame(),
    categorical = if (length(cat_rows) > 0) do.call(rbind, cat_rows) else data.frame()
  )
}


write_markdown_report <- function(output_dir, profiles, opts, project_root) {
  lines <- c(
    "# 本地数据摘要报告（自动生成）",
    "",
    paste0("- 生成时间：", now_iso()),
    paste0("- 项目目录：`", project_root, "`"),
    paste0(
      "- 采样策略：",
      ifelse(is.null(opts$sample_rows) || !is.finite(opts$sample_rows) || opts$sample_rows <= 0,
        "不采样（全量画像）",
        paste0("若行数过大则随机抽样 ", opts$sample_rows, " 行（用于画像）")
      )
    ),
    paste0("- 类别列Top统计：唯一值≤", opts$max_categories, " 时输出 Top ", opts$top_k),
    "",
    "## 总览",
    ""
  )

  if (length(profiles) == 0) {
    lines <- c(lines, "- 未在指定路径发现可读取的数据文件（csv/tsv/xlsx）。", "")
    write_text_utf8(file.path(output_dir, "data_summary.md"), lines)
    return(invisible(NULL))
  }

  total_rows <- sum(vapply(profiles, function(p) p$rows, integer(1)))
  lines <- c(lines, paste0("- 数据集数量：", length(profiles)))
  lines <- c(lines, paste0("- 总行数（各数据集相加）：", total_rows), "")

  for (p in profiles) {
    ref <- p$ref
    lines <- c(lines, paste0("## 数据集：", ref$dataset_id), "")
    lines <- c(lines, paste0("- 文件：`", ref$file_path, "`"))
    if (!is.null(ref$sheet_name) && nzchar(ref$sheet_name)) {
      lines <- c(lines, paste0("- 工作表：`", ref$sheet_name, "`"))
    }
    lines <- c(lines, paste0("- 形状：", p$rows, " 行 × ", p$cols, " 列"))
    if (isTRUE(p$sampled)) {
      lines <- c(lines, paste0("- 画像基于抽样：", p$rows_profiled, " 行（为速度与稳定性）"))
    }
    lines <- c(lines, paste0("- 画像行重复数（抽样子集）：", p$duplicate_rows_in_profiled), "")

    cols_df <- p$columns
    if (is.data.frame(cols_df) && nrow(cols_df) > 0) {
      cols_df <- cols_df[order(cols_df$missing_rate, decreasing = TRUE), , drop = FALSE]
      top_missing <- head(cols_df, 5)
      lines <- c(lines, "### 缺失率最高的列（Top 5）", "")
      for (i in seq_len(nrow(top_missing))) {
        r <- top_missing[i, , drop = FALSE]
        lines <- c(lines, paste0(
          "- `", r$column, "`：缺失 ", r$missing_count, "/", r$rows_profiled,
          "（", sprintf("%.2f%%", r$missing_rate * 100), "），类型=", r$kind,
          "，示例=", ifelse(nzchar(r$example_values), r$example_values, "无")
        ))
      }
      lines <- c(lines, "")
    }

    num_df <- p$numeric
    if (is.data.frame(num_df) && nrow(num_df) > 0) {
      lines <- c(lines, "### 数值列概览（节选）", "")
      num_df2 <- head(num_df, 10)
      for (i in seq_len(nrow(num_df2))) {
        r <- num_df2[i, , drop = FALSE]
        lines <- c(lines, paste0(
          "- `", r$column, "`：均值=", signif(r$mean, 4),
          "，SD=", signif(r$sd, 4),
          "，范围=[", signif(r$min, 4), ", ", signif(r$max, 4), "]",
          "，n=", as.integer(r$count)
        ))
      }
      lines <- c(lines, "")
    }

    lines <- c(lines, "### 输出文件", "")
    lines <- c(lines, "- `file_inventory.csv`：数据集清单与读取状态")
    lines <- c(lines, "- `columns.csv`：列画像（类型、缺失、唯一值、示例）")
    lines <- c(lines, "- `numeric_summary.csv`：数值列描述统计")
    lines <- c(lines, "- `categorical_top_values.csv`：类别列 Top 值（有上限）")
    lines <- c(lines, "- `run_meta.json`：本次运行元信息", "")
  }

  write_text_utf8(file.path(output_dir, "data_summary.md"), lines)
}


main <- function() {
  opts <- parse_args(commandArgs(trailingOnly = TRUE))

  input_path <- opts$input
  output_dir <- opts$output
  project_root <- normalizePath(getwd(), winslash = "/", mustWork = FALSE)

  dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)

  refs <- expand_datasets(
    input_path = input_path,
    recursive = opts$recursive,
    all_sheets = opts$all_sheets,
    max_sheets = opts$max_sheets
  )

  inventory_rows <- list()
  all_columns <- list()
  all_numeric <- list()
  all_categorical <- list()
  profiles <- list()

  for (ref in refs) {
    fp <- ref$file_path
    size_bytes <- tryCatch(as.integer(file.info(fp)$size), error = function(e) NA_integer_)

    inv <- list(
      dataset_id = ref$dataset_id,
      file_path = fp,
      file_type = tolower(tools::file_ext(fp)),
      sheet_name = ifelse(is.null(ref$sheet_name), "", ref$sheet_name),
      size_bytes = size_bytes,
      rows = "",
      cols = "",
      read_status = "ok",
      error = ""
    )

    df <- NULL
    prof <- NULL
    err <- NULL
    tryCatch(
      {
        df <- read_dataset(ref)
        prof <- profile_dataset(
          ref = ref,
          df = df,
          sample_rows = opts$sample_rows,
          max_categories = opts$max_categories,
          top_k = opts$top_k
        )
      },
      error = function(e) {
        err <<- e
      }
    )

    if (!is.null(err)) {
      inv$read_status <- "error"
      inv$error <- as.character(err)
    } else {
      inv$rows <- prof$rows
      inv$cols <- prof$cols
      profiles <- c(profiles, list(c(list(ref = ref), prof)))
      if (is.data.frame(prof$columns) && nrow(prof$columns) > 0) all_columns <- c(all_columns, list(prof$columns))
      if (is.data.frame(prof$numeric) && nrow(prof$numeric) > 0) all_numeric <- c(all_numeric, list(prof$numeric))
      if (is.data.frame(prof$categorical) && nrow(prof$categorical) > 0) all_categorical <- c(all_categorical, list(prof$categorical))
    }

    inventory_rows <- c(inventory_rows, list(as.data.frame(inv, stringsAsFactors = FALSE)))
  }

  inventory_df <- if (length(inventory_rows) > 0) do.call(rbind, inventory_rows) else data.frame()
  columns_df <- if (length(all_columns) > 0) do.call(rbind, all_columns) else data.frame()
  numeric_df <- if (length(all_numeric) > 0) do.call(rbind, all_numeric) else data.frame()
  categorical_df <- if (length(all_categorical) > 0) do.call(rbind, all_categorical) else data.frame()

  write_csv_utf8_bom(inventory_df, file.path(output_dir, "file_inventory.csv"))
  write_csv_utf8_bom(columns_df, file.path(output_dir, "columns.csv"))
  write_csv_utf8_bom(numeric_df, file.path(output_dir, "numeric_summary.csv"))
  write_csv_utf8_bom(categorical_df, file.path(output_dir, "categorical_top_values.csv"))

  write_markdown_report(output_dir, profiles, opts, project_root)

  meta <- list(
    generated_at = now_iso(),
    project_root = project_root,
    input = normalizePath(input_path, winslash = "/", mustWork = FALSE),
    output = normalizePath(output_dir, winslash = "/", mustWork = FALSE),
    args = opts,
    r_version = R.version.string,
    datasets_found = length(refs)
  )
  write_text_utf8(file.path(output_dir, "run_meta.json"), to_json(meta))

  cat(paste0("[OK] 已生成数据摘要：", normalizePath(output_dir, winslash = "/", mustWork = FALSE), "\n"))
}


main()
