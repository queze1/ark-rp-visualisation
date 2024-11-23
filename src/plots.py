import subprocess

import plotly.express as px

VIEWCMD = "wslview"
OUTPUT_PATH = "output/output.html"

fig = px.line(x=["a", "b", "c"], y=[1, 3, 2], title="sample figure")
fig.write_html(OUTPUT_PATH)
subprocess.run([VIEWCMD, OUTPUT_PATH])
