makesite.py
===========
A lite version of [sunainapai/makesite](https://github.com/sunainapai/makesite).
Check that repo for the main documentation.

## Features
- Parameter `output_dir` to define the output folder.
- Parameter `theme` to support themes. See [Themes](#themes) for more information.
- Parameter `pretty_date_format`: define the format of the dates shown on the website.

## Removed
- Content type News
- Unittests
- Makefile

## Quickstart
```shell
python -m venv env
source env/bin/activate # Windows: .\env\Scripts\activate
pip install commonmark
python makesite.py
```

## Themes
`themes/default` contains the default theme. Copy that folder and change it to your liking.
Then change the `theme` parameter in `makesite.py` or `config.json` to the folder name to use this theme.