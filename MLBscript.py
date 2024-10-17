import time
import sys

import requests
from bs4 import BeautifulSoup

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
#                                  
# RETRIEVING ODDS FROM API
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 


API_KEY = 'YOUR API_KEY'

SPORT = 'baseball_mlb' # use the sport_key from the /sports endpoint below, or use 'upcoming' to see the next 8 games across all sports

REGIONS = 'us' # uk | us | eu | au. Multiple can be specified if comma delimited

MARKETS = 'h2h' # h2h | spreads | totals. Multiple can be specified if comma delimited

ODDS_FORMAT = 'american' # decimal | american

DATE_FORMAT = 'iso' # iso | unix

# First get a list of in-season sports
# The sport 'key' from the response can be used to get odds in the next request

sports_response = requests.get(
    'https://api.the-odds-api.com/v4/sports/americanfootball_nfl/odds?regions=us&markets=h2h,spreads,totals&oddsFormat=american&apiKey=0850a8fd524916f47c63ae0a16a0de59', 
)


if sports_response.status_code != 200:
    print(f'Failed to get sports: status_code {sports_response.status_code}, response body {sports_response.text}')

#else:
    #print('List of in season sports:', sports_response.json())


# Now get a list of live & upcoming games for the sport you want, along with odds for different bookmakers
# This will deduct from the usage quota
# The usage quota cost = [number of markets specified] x [number of regions specified]
# For examples of usage quota costs, see https://the-odds-api.com/liveapi/guides/v4/#usage-quota-costs

odds_response = requests.get(
    f'https://api.the-odds-api.com/v4/sports/{SPORT}/odds',
    params={
        'api_key': API_KEY,
        'regions': REGIONS,
        'markets': MARKETS,
        'oddsFormat': ODDS_FORMAT,
        'dateFormat': DATE_FORMAT,
    }
)

if odds_response.status_code != 200:
    print(f'Failed to get odds: status_code {odds_response.status_code}, response body {odds_response.text}')

else:
    odds_json = odds_response.json()

    # Check the usage quota
    print('Remaining requests', odds_response.headers['x-requests-remaining'])
    print('Used requests', odds_response.headers['x-requests-used'])
    print("Number of events: "+ str(len(odds_json)))


# def printlist(l):
#     for data in range(l):
#         print("Game: "+ odds_json[data]["home_team"]+" vs "+ odds_json[data]["away_team"])
#         for x in range(len(odds_json[data]["bookmakers"])):
#             print()
#             print("Sportsbook: "+ odds_json[data]["bookmakers"][x]["title"])
#             print(odds_json[data]["bookmakers"][x]["markets"][0]["outcomes"][0]["name"]+ ": "+str(odds_json[data]["bookmakers"][x]["markets"][0]["outcomes"][0]["price"]))
#             print(odds_json[data]["bookmakers"][x]["markets"][0]["outcomes"][1]["name"]+ ": "+str(odds_json[data]["bookmakers"][x]["markets"][0]["outcomes"][1]["price"]))
#             print()
#         print()
#         print()


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
#                                  
# ARBITRAGE BETS CALCULATION FUNCTIONS
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 

def americanToDecimal(odd):
    if odd>0:
        return ((odd/100)+1)
    elif odd<0:
        return ((100/(abs(odd)))+1)
    else:
        print("none")

def calculate_arbitrage_bets(total_investment, odds_original, odds_hedge):
    # Calculate the implied probabilities
    prob_original = 1 / odds_original
    prob_hedge = 1 / odds_hedge

    # Calculate the arbitrage percentage
    arbitrage_percentage = prob_original + prob_hedge

    if arbitrage_percentage >= 1:
        return 1

    # Calculate the stake for the original bet and hedge bet
    stake_original = (prob_original / arbitrage_percentage) * total_investment
    stake_hedge = (prob_hedge / arbitrage_percentage) * total_investment

    return [arbitrage_percentage, stake_original, stake_hedge]

def calculate_arbitrage_bets_print(total_investment, odds_original, odds_hedge):
    # Calculate the implied probabilities
    prob_original = 1 / odds_original
    prob_hedge = 1 / odds_hedge

    # Calculate the arbitrage percentage
    arbitrage_percentage = prob_original + prob_hedge

    if arbitrage_percentage >= 1:
        return [None, arbitrage_percentage]

    # Calculate the stake for the original bet and hedge bet
    stake_original = (prob_original / arbitrage_percentage) * total_investment
    stake_hedge = (prob_hedge / arbitrage_percentage) * total_investment

    return [arbitrage_percentage, stake_original, stake_hedge]

def loading(duration):
    loading_chars = ['|', '/', '-', '\\']
    
    # Get the end time based on the duration
    end_time = time.time() + duration
    
    # Loop until the end time
    while time.time() < end_time:
        for char in loading_chars:
            sys.stdout.write(f'\rLoading... {char}')  # Use \r to overwrite the line
            sys.stdout.flush()  # Flush the output buffer
            time.sleep(0.2) 

list1 = {}
list2 = {}
listofitems = []
arb_opportunities = {}

def arbitrageAlgo(l, investment):
    for x in range(l):
        list1.clear()
        list2.clear()
        for i in range(len(odds_json[x]["bookmakers"])):
            list1[odds_json[x]["bookmakers"][i]["markets"][0]["outcomes"][0]["price"]] = odds_json[x]["bookmakers"][i]["markets"][0]["outcomes"][0]["name"]+odds_json[x]["bookmakers"][i]["title"]
            list2[odds_json[x]["bookmakers"][i]["markets"][0]["outcomes"][1]["price"]] = odds_json[x]["bookmakers"][i]["markets"][0]["outcomes"][1]["name"]+odds_json[x]["bookmakers"][i]["title"]
        for num1 in list1.keys():
            for num2 in list2.keys():
                if calculate_arbitrage_bets(investment, americanToDecimal(num1), americanToDecimal(num2)) != 1:
                    listofitems.append(arb_opportunities)
                    arb_opportunities[num1] = list1[num1]
                    arb_opportunities[num2] = list2[num2]
                    listofitems.append(arb_opportunities)
                    print()
                    print(listofitems)
                    arb_opportunities.clear()
    return listofitems


investment = float(input("Enter amount you want to bet: "))
amnt = int(input("Enter number of mlb games you want to check: "))

print()
print()
loading(1)
print()
print()

if arbitrageAlgo(amnt, investment) == {}:
    print("No arbitrage bets available")
else:
    print(arbitrageAlgo(amnt, investment))
                
        
        

        
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
#                                  
# WEBSCRAPER
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 


# def scrape_moneyline_odds(url):
#     # Send a request to the website
#     response = requests.get(url)

#     # Check if the request was successful
#     if response.status_code != 200:
#         print(f"Failed to retrieve data from {url}")
#         return []

#     # Parse the HTML content
#     soup = BeautifulSoup(response.content, 'html.parser')

#     # Find the relevant section of the page containing the moneyline odds
#     odds_section = soup.find_all('div', class_='odds-table-moneyline--0 active')  # Adjust this based on the website's structure

#     moneyline_odds = []

#     # Extract the moneyline odds
#     for odds in odds_section:
#         teams = odds.find_all('span', class_='name')  # Adjust this based on the website's structure
#         odds_values = odds.find_all('span', class_='bet-price')  # Adjust this based on the website's structure

#         for team, odds_value in zip(teams, odds_values):
#             moneyline_odds.append({
#                 'team': team.get_text(strip=True),
#                 'odds': odds_value.get_text(strip=True)
#             })

#     return moneyline_odds

# url = 'https://www.vegasinsider.com/nfl/odds/las-vegas/'

# print(scrape_moneyline_odds(url))

# print()
# print()

# original = americanToDecimal((float(input("Enter the odds of original bet: "))))
# hedge = americanToDecimal((float(input("Enter the odds of hedge bet: "))))
# amnt = float(input("Enter amount you want to bet: "))

# print()
# print()
# loading(1)
# print()
# print()
# print()

# if calculate_arbitrage_bets(amnt, original, hedge)[0] is None:
#     print("No arbitrage opportunity available.")
#     print()
#     print("This is the arbitrage percentage: ")
#     print(calculate_arbitrage_bets(amnt, original, hedge)[1])
# else:
#     print("This is the arbitrage percentage: ")
#     print(calculate_arbitrage_bets(amnt, original, hedge)[0])
#     print()
#     print("This is the amount for the original bet: ")
#     print(calculate_arbitrage_bets(amnt, original, hedge)[1])
#     print()
#     print("This is the amount for the hedge bet: ")
#     print(calculate_arbitrage_bets(amnt, original, hedge)[2])