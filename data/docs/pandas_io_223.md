---
doc_id: pandas_io_223
version: pandas 2.2.3
source_url: https://pandas.pydata.org/pandas-docs/version/2.2.3/user_guide/io.html
additional_source_url: https://pandas.pydata.org/pandas-docs/version/2.2.3/reference/api/pandas.read_csv.html
---

# pandas IO tools
The `read_csv()` function reads a comma-separated values (csv) file into a DataFrame. It supports a number of options to control how the data is parsed.

# pandas.read_csv
`pandas.read_csv(filepath_or_buffer, *, sep=<no_default>, delimiter=None, header='infer', names=<no_default>, index_col=None, usecols=None, dtype=None, engine=None, converters=None, skiprows=None, nrows=None, na_values=None, keep_default_na=True, na_filter=True, parse_dates=None, date_format=None, encoding=None, on_bad_lines='error', low_memory=True, memory_map=False, dtype_backend=<no_default>)`
Read a comma-separated values (csv) file into a DataFrame.

| Parameter | Meaning |
|---|---|
| `filepath_or_buffer` | Any valid string path, path-like object, or file-like object |
| `sep` | Character or regular expression used to denote the delimiter; defaults to `,` |
| `delimiter` | Alias for `sep` |
| `header` | Row number(s) to use as the column names, and the start of the data |
| `names` | List of column names to use |
| `index_col` | Column(s) to use as the row labels of the DataFrame |
| `usecols` | Return a subset of the columns |
| `dtype` | Data type for data or columns |
| `engine` | Parser engine; options include `c`, `python`, and `pyarrow` |
| `converters` | Dict of functions for converting values in specified columns |
| `skiprows` | Line numbers to skip (0-indexed) or number of lines to skip |
| `nrows` | Number of rows of file to read |
| `na_values` | Additional strings to recognize as NA/NaN |
| `keep_default_na` | Whether to include default NaN values when parsing |
| `na_filter` | Detect missing value markers; setting False can improve performance |
| `parse_dates` | Attempt to parse data into datetime |
| `encoding` | Encoding to use for UTF when reading/writing |
| `on_bad_lines` | Specifies what to do upon encountering a bad line; options include error, warn, skip, or a callable |

# pandas.read_table
`pandas.read_table(filepath_or_buffer, *, sep='\\t', delimiter=None, header='infer', names=<no_default>, index_col=None, usecols=None, dtype=None, engine=None, converters=None, skiprows=None, nrows=None, na_values=None, keep_default_na=True, na_filter=True, parse_dates=None, encoding=None, on_bad_lines='error', ...)`
Read general delimited file into DataFrame. The default delimiter is a tab (`\\t`), unlike `read_csv()`, whose default delimiter is a comma.

# pandas.DataFrame.to_csv
`DataFrame.to_csv(path_or_buf=None, sep=',', na_rep='', float_format=None, columns=None, header=True, index=True, index_label=None, mode='w', encoding=None, compression='infer', quoting=None, quotechar='"', lineterminator=None, chunksize=None, date_format=None, doublequote=True, escapechar=None, decimal='.')`
Write object to a comma-separated values (csv) file.

# pandas.read_csv version notes
In pandas 2.2.0, the `date_format` parameter was added to `read_csv()` for parsing dates. The `date_parser` parameter is deprecated; use `date_format` or parse dates after reading.
