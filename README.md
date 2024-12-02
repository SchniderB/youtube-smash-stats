# Manual to extract youtube statistics from a video

## Set up Python virtual environment

### First set-up

1. Download `virtualenv`
```bash
pip install virtualenv
```
2. Create virtual environment in your folder of interest
```bash
virtualenv yt-extractor
```
3. Activate the virtual environment
```bash
source yt-extractor/bin/activate
```
4. Install the libraries of interest in the virtual environment
```bash
pip install google-api-python-client
pip install httplib2 oauth2client
```
5. Store the dependencies in a local requirement file
```bash
pip freeze > requirements.txt
```

### Deactivate the virtual environment
```bash
deactivate
```

### Re-activate virtual environment every time you need to extract data from youtube
```bash
source yt-extractor/bin/activate
```

## Perform the statistic extraction

### Extract the playlist IDs and titles of the tournaments of interest
A large number of playlist IDs and titles of the tournaments of interest were stored in the JSON file `playlists.json` in the following way:
```json
{
    "PLcMdMmtHkPpR5epLsLfAT9OgVkAHGJgat": "Splendors and Contenders 2 - Smash Ultimate",
    "PLcMdMmtHkPpQpWKUm-ieB58c4pShNU0-G": "LACS Rivals - Smash Ultimate",
    "PLcMdMmtHkPpQP8nOfrhf1rUb-K-lkfgx_": "The Throne 2 - Smash Ultimate"
}
```

### Store your API key, service name and api version into a local `.env` file

### Extract all the statistics per Youtube video
```bash
python3 get_youtube_data.py
```
The output file is `raw_video_stats.tsv`.

### Manually curate the file with all the statistics
Based on pattern recognition, the doubles, squadstrike, team matches and interviews were filtered out.

## Identify the characters used in each set

### Define all the characters' possible names in a JSON file
The file `characters.json` can be re-used for this purpose.

### Assign a character list for each video
```bash
python3 get_character_names.py
```
The output file is `character_video_stats.tsv`.

## Use a manual iterative approach to annotate all the player names
First annotate a few player names and propagate it to all their other games with the following script.
```bash
python3 get_player_names.py
```
Repeat the process until you have annotated as many player names as possible.

## Compute all the statistics based on the curated data
```bash
python3 compute_stats.py
```
