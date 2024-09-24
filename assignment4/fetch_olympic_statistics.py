"""
Task 4

collecting olympic statistics from wikipedia
"""

from __future__ import annotations

from pathlib import Path
import requests
from bs4 import BeautifulSoup
import re
import matplotlib.pyplot as plt
from pathlib import Path
from typing import List
import numpy as np


# Countries to submit statistics for
scandinavian_countries = ["Norway", "Sweden", "Denmark"]

# Summer sports to submit statistics for
summer_sports = ["Sailing", "Athletics", "Handball", "Football", "Cycling", "Archery"]


def report_scandi_stats(url: str, sports_list: list[str], work_dir: str | Path) -> None:
    """
    Given the url, extract and display following statistics for the Scandinavian countries:

      -  Total number of gold medals for for summer and winter Olympics
      -  Total number of gold, silver and bronze medals in the selected summer sports from sport_list
      -  The best country in number of gold medals in each of the selected summer sports from sport_list

    Display the first two as bar charts, and the last as an md. table and save in a separate directory.

    Parameters:
        url (str) : url to the 'All-time Olympic Games medal table' wiki page
        sports_list (list[str]) : list of summer Olympic games sports to display statistics for
        work_dir (str | Path) : (absolute) path to your current working directory

    Returns:
        None
    """

    # Make a call to get_scandi_stats
    # Plot the summer/winter gold medal stats
    # Iterate through each sport and make a call to get_sport_stats
    # Plot the sport specific stats
    # Make a call to find_best_country_in_sport for each sport
    # Create and save the md table of best in each sport stats
    work_dir = Path(work_dir)
    stats_dir = work_dir / "olympic_games_results"
    stats_dir.mkdir(parents=True, exist_ok=True)

    country_dict = get_scandi_stats(url)

    # Plot 
    plot_scandi_stats(country_dict, stats_dir)

    best_in_sport = []

    for sport in sports_list:
        results = {}
        for country in scandinavian_countries:
            country_url = country_dict[country]['url']
            results[country] = get_sport_stats(country_url, sport)
        
        plot_medal_stats(scandinavian_countries, results, sport, stats_dir)

        # Find the best country in sport by Gold
        best_country = find_best_country_in_sport(results)
        best_in_sport.append((sport, best_country))

    md_table_path = stats_dir / "best_of_sport_by_Gold.md"
    with md_table_path.open('w') as f:
        f.write('Best Scandinavian country in Summer Olympic sports, based on most number of Gold medals\n')
        f.write('| Sport | Best Country |\n')
        f.write('|:------|:-------------|\n')
        for sport, best_country in best_in_sport:
            f.write(f'| {sport} | {best_country} |\n')


def get_scandi_stats(
    url: str,
) -> dict[str, dict[str, str | dict[str, int]]]:
    """Given the url, extract the urls for the Scandinavian countries,
       as well as number of gold medals acquired in summer and winter Olympic games
       from 'List of NOCs with medals' table.

    Parameters:
      url (str): url to the 'All-time Olympic Games medal table' wiki page

    Returns:
      country_dict: dictionary of the form:
        {
            "country": {
                "url": "https://...",
                "medals": {
                    "Summer": 0,
                    "Winter": 0,
                },
            },
        }

        with the tree keys "Norway", "Denmark", "Sweden".
    """

    response = requests.get(url)
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find('table', {'class': 'wikitable'})
    base_url = "https://en.wikipedia.org"

    rows = table.find_all('tr')

    country_dict = {}

    for row in rows:
        cols = row.find_all('td')
        if cols:
            country_name_match = re.match(r"([^\(\[]+)", cols[0].text)
            if country_name_match:
                country_name = country_name_match.group(1).strip()
                if country_name in scandinavian_countries:
                    print(f"Country_name in scandinavian_countries : {country_name}:")
                    country_url = base_url + cols[0].find('a')['href']
                    print(f"URL for {country_name}: {country_url}")

                    country_response = requests.get(country_url)
                    country_html = country_response.text
                    country_soup = BeautifulSoup(country_html, 'html.parser')

                    # Find the table with summer gold medals count
                    summer_sport_section_id = 'Medals_by_summer_sport' if country_name != 'Sweden' else 'Medals_by_Summer_Sport'
                    summer_sport_section = country_soup.find('span', id=summer_sport_section_id)
                    print(f"summer_sport_section {summer_sport_section}")
                    summer_gold = 0
                    if summer_sport_section:
                        summer_table = summer_sport_section.find_next('table')
                        summer_gold_row = summer_table.find('tr', class_='sortbottom')
                        if summer_gold_row:
                            summer_gold = int(summer_gold_row.find_all('td')[0].text.strip())
                    print(f"summer_gold {summer_gold}")

                    # Find for winter sport medals
                    winter_sport_section_id = 'Medals_by_winter_sport' if country_name != 'Sweden' else 'Medals_by_Winter_Sport'
                    winter_sport_section = country_soup.find('span', id=winter_sport_section_id)
                    winter_gold = 0
                    if winter_sport_section:
                        winter_table = winter_sport_section.find_next('table')
                        winter_gold_row = winter_table.find('tr', class_='sortbottom')
                        if winter_gold_row:
                            winter_gold = int(winter_gold_row.find_all('td')[0].text.strip())
                    print(f"winter_gold {winter_gold}")

                    country_dict[country_name] = {
                        "url": country_url,
                        "medals": {
                            "Summer": summer_gold,
                            "Winter": winter_gold,
                        },
                    }

    return country_dict



def get_sport_stats(country_url: str, sport: str) -> dict[str, int]:
    """Given the url to country specific performance page, get the number of gold, silver, and bronze medals
      the given country has acquired in the requested sport in summer Olympic games.

    Parameters:
        - country_url (str) : url to the country specific Olympic performance wiki page
        - sport (str) : name of the summer Olympic sport in interest. Should be used to filter rows in the table.

    Returns:
        - medals (dict[str, int]) : dictionary of number of medal acquired in the given sport by the country
                          Format:
                          {"Gold" : x, "Silver" : y, "Bronze" : z}
    """
    response = requests.get(country_url)
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')

    # Using regex
    table_headers = soup.find_all('span', string=re.compile('Medals by summer sport', re.I))
    print(f"table_headers {table_headers}")
    
    if not table_headers:
        return {"Gold": 0, "Silver": 0, "Bronze": 0}
    
    medals = {"Gold": 0, "Silver": 0, "Bronze": 0}
    sport_found = False
    
    for header in table_headers:
        table = header.find_parent().find_next_sibling('table')
        if table:
            rows = table.find_all('tr')
            sport_pattern = re.compile(re.escape(sport), re.I)
            print(f"sport_pattern {sport_pattern}")
            for row in rows[1:]:  
                header_cell = row.find('th')
                if not header_cell:
                    continue
                sport_link = header_cell.find('a')
                if sport_link and sport_pattern.search(sport_link.text):
                    sport_found = True
                    # td
                    medals_cells = header_cell.find_next_siblings('td')
                    medals["Gold"] = int(medals_cells[0].text.strip() if medals_cells[0].text.strip().isdigit() else 0)
                    medals["Silver"] = int(medals_cells[1].text.strip() if medals_cells[1].text.strip().isdigit() else 0)
                    medals["Bronze"] = int(medals_cells[2].text.strip() if medals_cells[2].text.strip().isdigit() else 0)
                    break
    
    if not sport_found:
        return {"Gold": 0, "Silver": 0, "Bronze": 0}
    
    return medals


def find_best_country_in_sport(
    results: dict[str, dict[str, int]], medal: str = "Gold"
) -> str:
    """Given a dictionary with medal stats in a given sport for the Scandinavian countries, return the country
        that has received the most of the given `medal`.

    Parameters:
        - results (dict) : a dictionary of country specific medal results in a given sport. The format is:
                        {"Norway" : {"Gold" : 1, "Silver" : 2, "Bronze" : 3},
                         "Sweden" : {"Gold" : 1, ....},
                         "Denmark" : ...
                        }
        - medal (str) : medal type to compare for. Valid parameters: ["Gold" | "Silver" |"Bronze"]. Should be used as a key
                          to the medal dictionary.
    Returns:
        - best (str) : name of the country(ies) leading in number of gold medals in the given sport
                       If one country leads only, return its name, like for instance 'Norway'
                       If two countries lead return their names separated with '/' like 'Norway/Sweden'
                       If all or none of the countries lead, return string 'None'
    """
    valid_medals = {"Gold", "Silver", "Bronze"}
    if medal not in valid_medals:
        raise ValueError(f"{medal} is invalid parameter for ranking, must be in {valid_medals}")

    best_countries = []
    highest_medal_count = 0

    #  each country and their medal count
    for country, medals in results.items():
        if medals[medal] > highest_medal_count:
            # Found a new best
            best_countries = [country]
            highest_medal_count = medals[medal]
        elif medals[medal] == highest_medal_count:
            # Found a country as the current best
            best_countries.append(country)

    # best country 
    if len(best_countries) == 0:
        return "None"
    elif len(best_countries) == 1:
        return best_countries[0]
    elif len(best_countries) == len(results):
        return "None"
    else:
        # If tie 
        return "/".join(sorted(best_countries))  




def plot_scandi_stats(
    country_dict: dict[str, dict[str, str | dict[str, int]]],
    output_parent: str | Path | None = None,
) -> None:
    """Plot the number of gold medals in summer and winter games for each of the scandi countries as bars.

    Parameters:
      results (dict[str, dict[str, int]]) : a nested dictionary of country names and the corresponding number of summer and winter
                            gold medals from 'List of NOCs with medals' table.
                            Format:
                            {"country_name": {"Summer" : x, "Winter" : y}}
      output_parent (str | Path) : parent file path to save the plot in
    Returns:
      None
    """
    bar_width = 0.35
    countries = list(country_dict.keys())
    summer_gold = [country_dict[country]['medals']['Summer'] for country in countries]
    winter_gold = [country_dict[country]['medals']['Winter'] for country in countries]

    index = range(len(countries))

    plt.figure(figsize=(10, 6))
    plt.bar(index, summer_gold, bar_width, label='Summer Gold')
    plt.bar([i + bar_width for i in index], winter_gold, bar_width, label='Winter Gold')

    plt.xlabel('Countries')
    plt.ylabel('Gold Medals')
    plt.title('Gold Medals in Summer and Winter Olympics')
    plt.xticks([i + bar_width / 2 for i in index], countries)
    plt.legend()

    plt.tight_layout()
    # Save the figure using the output_parent parameter
    if output_parent is not None:
        output_file = Path(output_parent) / 'total_medal_ranking.png'
        plt.savefig(output_file)
    plt.close()

#Helper function for medal stats
def plot_medal_stats(
    countries: List[str],
    medals: dict[str, dict[str, int]],
    sport: str,
    output_parent: str | Path
) -> None:
    """Plot the number of gold, silver, and bronze medals for a specific sport for each country as bars.

    Parameters:
      countries (list[str]): List of country names.
      medals (dict[str, dict[str, int]]): Dictionary of medals for each country.
      sport (str): The name of the sport.
      output_parent (str | Path): Directory to save the plot in.
    Returns:
      None
    """
    bar_width = 0.25  
    index = np.arange(len(countries))  

    gold_counts = [medals[country]['Gold'] for country in countries]
    silver_counts = [medals[country]['Silver'] for country in countries]
    bronze_counts = [medals[country]['Bronze'] for country in countries]

    plt.figure(figsize=(10, 6))

    plt.bar(index, gold_counts, bar_width, label='Gold', color='#3e4574')
    plt.bar(index + bar_width, silver_counts, bar_width, label='Silver', color='#00a9ff')
    plt.bar(index + 2 * bar_width, bronze_counts, bar_width, label='Bronze', color='#581120')

    plt.xlabel('Countries')
    plt.ylabel('Medals')
    plt.title(f'{sport} Medals by Scandinavian Countries')
    plt.xticks(index + bar_width, countries)
    plt.legend()

    plt.tight_layout()
    output_file = Path(output_parent) / f'{sport}_medal_ranking.png'
    plt.savefig(output_file)
    plt.close()


# run the whole thing if called as a script, for quick testing
if __name__ == "__main__":
    url = "https://en.wikipedia.org/wiki/All-time_Olympic_Games_medal_table"
    work_dir = "/Users/ayeshaishaq/Documents/IN3110-ayeshasi/assignment4"
    report_scandi_stats(url, summer_sports, work_dir)
