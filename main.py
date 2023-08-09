import requests
from bs4 import BeautifulSoup

def retrieve_scores(month, day, year):

    #maps numerical month to string version to construct URL
    month_names = {
        1: "january", 2: "february", 3: "march", 4: "april", 5: "may", 6: "june",
        7: "july", 8: "august", 9: "september", 10: "october", 11: "november", 12: "december"
    }

    #adjusts year for url because the year in url corresponds to the second year in a season
    #i.e. the year 2023 would correspond to the 2022-2023 season
    if 10 <= month <= 12:
        year_url = year + 1
    else:
        year_url = year

    #construct the url to scrape based on year and month
    url = f"https://www.basketball-reference.com/leagues/NBA_{year_url}_games-{month_names[month]}.html"

    #parse page content
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    body = soup.find_all("tbody")

    #checks if no games are played during this month
    if not body:
        return ["No NBA games played this day"]
    
    #extract dates from table and match row to date
    dates = body[0].find_all("th")
    rowvals = [rownum for rownum, date in enumerate(dates, start=1) if f"{day}, {year}" in date.get_text()]

    #checks if no games are played on this day
    if not rowvals:
        return ["No NBA games played this day"]

    #collect rows from table
    rows = soup.find_all("tr")

    #all scores will be added to this list which will be returned
    scores = []

    #extract scores from selected rows
    for rownum in rowvals:
        #basketball-reference changed its website formatting for seasons after 1984-1985   
        if year <= 1984:
            row_cells = rows[rownum].find_all("td")
            visitor, visitor_score, home, home_score = [cell.get_text() for cell in row_cells[0:4]]
        else:
            row_cells = rows[rownum + 1].find_all("td")
            visitor, visitor_score, home, home_score = [cell.get_text() for cell in row_cells[1:5]]
        scores.append(f"{visitor}: {visitor_score} | {home}: {home_score}")

    return scores

def main():
    date = input("Enter a date (MM/DD/YYYY): ")
    month, day, year = map(int, date.split('/'))

    scores = retrieve_scores(month, day, year)

    for score in scores:
        print(score)

if __name__ == "__main__":
    main()
