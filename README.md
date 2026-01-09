# ARK RP Visualisation

A dashboard for analysing Discord roleplay data. Built to visualise engagement and trends for the *ARK: Journey Through the Realms* (2024) Dungeons and Dragons campaign.

*Not endorsed by the UNSW Tabletop Games Society.*

## Technical Highlights
- **Pattern Matching**: Uses Dash's `MATCH` and `ALL` selectors to handle dynamic filter groups.
- **Data Pipeline**: Cleans and aggregates raw Discord exports via Pandas; serves data via AWS S3 in production.

## Setup
1. `pip install -r requirements.txt`
2. Create a `.env` with your S3 credentials.
3. `python src/app.py`

## Features
- Time-series analysis with 7/30 day moving averages.
- Multi-variable scatter plots.
- Filtering by author, date, and reaction count.

## Hosting
TODO

## Packages Used
- [Dash](https://dash.plotly.com/) - Web framework.
- [Plotly](https://plotly.com/python/) - Graphing library.
- [Pandas](https://pandas.pydata.org/) - For data manipulation.
- [Dash Mantine Components](https://wwwdash-mantine-components.com/) - Convenience library for prettifying the GUI.
- [Gunicorn](https://gunicorn.org/) - HTTP server for running on Docker.
- [Boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html) - AWS SDK for Python, for getting the dataset from Amazon S3.
- [python-dotenv](https://github.com/theskumar/python-dotenv) - For easily setting enviroment variables in VSCode.
- [pytest](https://docs.pytest.org/en/stable/) - For testing.
- [Memray](https://github.com/bloomberg/memray) - For profiling memory usage.
- [Mypy](https://www.mypy-lang.org/) - For static type checking with Python.
- [Ruff](https://github.com/astral-sh/ruff) - For linting.
