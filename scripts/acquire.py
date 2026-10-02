"""Download only an explicitly published MoneyPuck file, with source checksum."""
import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from nhl_forecast.data import SOURCE_URL, checksum

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--accept-noncommercial-terms',action='store_true',required=True)
    args=parser.parse_args()
    path=ROOT/'data/raw/all_teams.csv'
    path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists():
        raise SystemExit('Raw snapshot exists; retain it rather than overwrite.')
    partial=path.with_suffix('.part')
    subprocess.run(['curl','--fail','--location','--retry','2','--output',str(partial),SOURCE_URL],check=True)
    partial.replace(path)
    manifest={'source':'MoneyPuck.com','url':SOURCE_URL,
        'retrieved_at_utc':datetime.now(timezone.utc).isoformat(),
        'sha256':checksum(path),'bytes':path.stat().st_size,
        'terms_url':'https://moneypuck.com/data.htm',
        'use':'Non-commercial research with MoneyPuck.com attribution',
        'redistribution':'Raw and row-level derived data excluded from repository',
        'schema':'all-team game-by-game download, situation all',
        'study_season_start_years':[2016,2024], 'reserved_season':2025}
    (ROOT/'reports/source-manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    print(json.dumps(manifest,indent=2))

if __name__=='__main__':main()
