"""
Task 3

Collecting anniversaries from Wikipedia
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import requests
from bs4 import BeautifulSoup
import re

# Month names to submit for, from Wikipedia:Selected anniversaries namespace
months_in_namespace = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
]


def extract_anniversaries(html: str, month: str) -> list[str]:
    """Extract all the passages from the html which contain an anniversary, and save their plain text in a list.
        For the pages in the given namespace, all the relevant passages start with a month href
         <p>
            <b>
                <a href="/wiki/April_1" title="April 1">April 1</a>
            </b>
            :
            ...
        </p>

    Parameters:
        - html (str): The html to parse
        - month (str): The month in interest, the page name of the Wikipedia:Selected anniversaries namespace

    Returns:
        - ann_list (list[str]): A list of the highlighted anniversaries for a given month
                                The format of each element in the list is:
                                '{Month} {day}: Event 1 (maybe some parentheses); Event 2; Event 3, something, something\n'
                                {Month} can be any month in the namespace and {day} is a number 1-31
    """
    
    # parse the HTML
    soup = BeautifulSoup(html, "html.parser")
    paragraphs = soup.find_all("p")
    

    # Filter the passages to keep only the highlighted anniversaries
    ann_list = []

    pattern = r"<p>(<b>)?<a\shref=\"/wiki/" + month + r"_{1,2}\d|_{3}[0,1]\""

    for p in paragraphs:
        matched = re.search(pattern, str(p))
        if matched:  
            ann_list.append(p.get_text())
    return ann_list


def anniversary_list_to_df(ann_list: list[str]) -> pd.DataFrame:
    """Transform the list of anniversaries into a pandas dataframe.

    Parameters:
        ann_list (list[str]): A list of the highlighted anniversaries for a given month
                                The format of each element in the list is:
                                '{Month} {day}: Event 1 (maybe some parenthesis); Event 2; Event 3, something, something\n'
                                {Month} can be any month in months list and {day} is a number 1-31
    Returns:
        df (pd.Dataframe): A (dense) dataframe with columns ["Date"] and ["Event"] where each row represents a single event
    """
    

    # Store the split parts 
    ann_table = []
    # Headers for the dataframe
    event_pattern = re.compile(r';(?![^(]*\))')
    
    # Iempty list to store the split parts 
    for ann in ann_list:
        date_part, _, event_part = ann.partition(':')
        if event_part:
            # regex pattern to split events
            events = event_pattern.split(event_part)
            print(f"Events before stripping: {events}")  
            for event in events:
                event = event.strip() 
                if event:
                    ann_table.append([date_part.strip(), event])
                    print(f"Event after stripping: {event}") 
    
    # DataFrame from the list of lists
    df = pd.DataFrame(ann_table, columns=["Date", "Event"])
    print(df) 

    return df


def anniversary_table(
    namespace_url: str, month_list: list[str], work_dir: str | Path
) -> None:
    """Given the namespace_url and a month_list, create a markdown table of highlighted anniversaries for all of the months in list,
        from Wikipedia:Selected anniversaries namespace

    Parameters:
        - namespace_url (str):  Full url to the "Wikipedia:Selected_anniversaries/" namespace
        - month_list (list[str]) - List of months of interest, referring to the page names of the namespace
        - work_dir (str | Path) - (Absolute) path to your working directory

    Returns:
        None
    """


    # Loop through all months in month_list
    # Extract the html from the url (use one of the already defined functions from earlier)
    # Gather all highlighted anniversaries as a list of strings
    # Split into date and event
    # Render to a df dataframe with columns "Date" and "Event"
    # Save as markdown table

    work_dir = Path(work_dir)
    output_dir = work_dir/"tables_of_anniversaries"
    output_dir.mkdir(parents=True, exist_ok=True)

    for month in month_list:
        page_url = f"{namespace_url}/{month}"
        response = requests.get(page_url)
        html = response.text
        ann_list = extract_anniversaries(html, month)
        df = anniversary_list_to_df(ann_list)

        # Convert to an .md table
        table =  df.to_markdown(index=False)

        # Save the output
        output_filepath = output_dir / f"anniversaries_{month.lower()}.md"
        with open(output_filepath, "w") as file:
            file.write(table)


if __name__ == "__main__":
    # make tables for all the months
    work_dir = "/Users/ayeshaishaq/Documents/IN3110-ayeshasi/assignment4"
    print(f"Working directory set to: {work_dir}")
    namespace_url = "https://en.wikipedia.org/wiki/Wikipedia:Selected_anniversaries"
    anniversary_table(namespace_url, months_in_namespace, work_dir)
    
