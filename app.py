from flask import Flask, render_template, request
import pandas as pd
from main import BasketballRankingsParser

app = Flask(__name__)

# Initialize parser
parser = BasketballRankingsParser()

@app.route('/')
def index():
    """Home page."""
    return render_template('index.html')

@app.route('/rankings/<source>')
def rankings(source):
    """Fetch rankings from a specific source and display as a table."""
    if source == "kenpom":
        df = parser.get_kenpom_rankings()
    elif source == "ncaa":
        df = parser.get_ncaa_rankings()
    elif source == "rpi":
        df = parser.get_rpi_rankings()
    elif source == "sos":
        df = parser.get_sos_rankings()
    elif source == "espn":
        df = parser.get_espn_rankings()
    else:
        return render_template('error.html', message="Invalid source"), 400
    
    return render_template('table.html', table=df.to_html(classes='data-table', index=False), title=f"{source.upper()} Rankings")

@app.route('/combined')
def combined_rankings():
    """Combine rankings and display as a table."""
    kenpom_df = parser.get_kenpom_rankings()
    ncaa_df = parser.get_ncaa_rankings()
    rpi_df = parser.get_rpi_rankings()
    sos_df = parser.get_sos_rankings()
    espn_df = parser.get_espn_rankings()
    
    dfs = [kenpom_df, ncaa_df, rpi_df, sos_df, espn_df]
    combined_df = dfs[0]
    for df in dfs[1:]:
        combined_df = pd.merge(combined_df, df, on="Team", how="inner")
    
    return render_template('table.html', table=combined_df.to_html(classes='data-table', index=False), title="Combined Rankings")

if __name__ == '__main__':
    app.run(debug=True)
