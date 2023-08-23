from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    scores = None
    if request.method == 'POST':
        date = request.form['date']
        month, day, year = map(int, date.split('/'))
        scores = retrieve_scores(month, day, year)
    return render_template('index.html', scores=scores)

def retrieve_scores(month, day, year):

    #maps numerical month to string version to construct URL
    month_names = {
        1: "january", 2: "february", 3: "march", 4: "april", 5: "may", 6: "june",
        7: "july", 8: "august", 9: "september", 10: "october", 11: "november", 12: "december"
    }

    #maps numerical month to shorthand 
    month_shorthand = {
        1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May", 6: "Jun",
        7: "Jul", 8: "Aug", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec"
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
    rowvals = [rownum for rownum, date in enumerate(dates, start=1) if f"{month_shorthand[month]} {day}, {year}" in date.get_text()]

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
            row_cells = rows[rownum].find_all("td")
            visitor, visitor_score, home, home_score = [cell.get_text() for cell in row_cells[1:5]]
        scores.append(f"{visitor}: {visitor_score} | {home}: {home_score}")

    return scores
if __name__ == '__main__':
    app.run(debug=True)
