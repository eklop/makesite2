makesite.py
===========
Check [sunainapai/makesite]() for the main documentation.

## Added
- Parameter `output_dir` to define the output folder.
- Parameter `theme` to support themes. See [Themes](#themes) for more information.
- Parameter `pretty_date_format`: define the format of the dates shown on the website.

## Removed
- Content type News
- Unittests
- Makefile

## Quickstart
```
python -m venv env
source env/bin/activate //Windows: env\Scripts\activate
pip install commonmark
python makesite.py
```

## Themes
`themes/default` contains the default theme.

### Create a theme
1. Create a copy of `themes/default` in the same directory, and rename it.
1. Customize it to your liking.
1. Open `makesite.py` (or `params.json` if you created one) and change the `theme` parameter in the `params` object.