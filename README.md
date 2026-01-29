# ARK RP Visualisation
> *This project is unofficial and not endorsed by the UNSW Tabletop Games Society.*

A dashboard for analysing Discord message metadata from the *ARK: Journey Through the Realms* (2024) Dungeons and Dragons campaign.

**Link:** https://ark-rp-visualisation.fly.dev/ (may take >30s for a cold start)

<details>
<summary>Screenshots</summary>
<br>

|                               Time Series                            |                               Bar                          |                               Scatter                      | 
| :------------------------------------------------------------------- | :--------------------------------------------------------: | :--------------------------------------------------------: |
| <img src="docs/images/time_series.png" title="Time Series" width="100%"> | <img src="docs/images/bar.png" title="Bar" width="100%"> | <img src="docs/images/scatter.png" title="Scatter" width="100%"> |

</details>

## Built With

* [![Dash][Dash-badge]][Dash-url]
* [![Plotly][Plotly-badge]][Plotly-url]
* [![Pandas][Pandas-badge]][Pandas-url]
* [![Dash Mantine Components][DMC-badge]][DMC-url]
* [![Boto3][Boto3-badge]][Boto3-url]
* [![Docker][Docker-badge]][Docker-url]

## Getting Started

### Prerequisites
- [uv](https://docs.astral.sh/uv/)
- Your [Discord exports](https://github.com/Tyrrrz/DiscordChatExporter) (CSV format)
- [Docker](https://www.docker.com/) (optional)
- An [S3 bucket](https://aws.amazon.com/s3/) (if using S3)

### Installation
*As the ARK dataset is private, this guide assumes you already have access to it, or intend to fork this repo.*
1. Run the following commands:
```bash
git clone https://github.com/queze1/ark-rp-visualisation.git
cd ark-rp-visualisation
uv sync
```
2. Create a `/data` directory if it does not exist, and place your Discord CSV exports in there.
3. Create an `.env` file based on `.env.example`.
4. Replace path constants in `src/core/data_loader.py`.

### Usage
1. `uv run src/app.py`
    - This will create a file in `.cache`. To use S3, upload this file into your S3 bucket.

### Usage (Docker)
1. `docker compose up --build`

## Features
TODO

## Roadmap
- [ ] Add tooltips & help icons
- [ ] Add GIF of usage
- [ ] Add preset graphs to website

## License

This project is licensed under the **MIT license**.

See [LICENSE](LICENSE) for more information.

<!-- MARKDOWN LINKS & IMAGES -->
[Dash-badge]: https://img.shields.io/badge/dash-008DE4.svg?style=for-the-badge&logo=plotly&logoColor=white
[Dash-url]: https://dash.plotly.com/
[Plotly-badge]: https://img.shields.io/badge/plotly-7A76FF.svg?style=for-the-badge&logo=plotly&logoColor=white
[Plotly-url]: https://plotly.com/python/
[Pandas-badge]: https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white
[Pandas-url]: https://pandas.pydata.org/
[DMC-badge]: https://img.shields.io/badge/Dash_Mantine_Components-339af0?style=for-the-badge&logo=mantine&logoColor=white
[DMC-url]: https://www.dash-mantine-components.com/
[Boto3-badge]: https://img.shields.io/badge/boto3-%23FF9900.svg?style=for-the-badge&logoColor=white
[Boto3-url]: https://aws.amazon.com/s3/
[Docker-badge]: https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white
[Docker-url]: https://www.docker.com/
