import os
import time
import csv
import requests
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

load_dotenv()

def parse_raw_cookie(cookie_string, domain="retroachievements.org"):
    cookies = []
    for item in cookie_string.split(';'):
        if '=' in item:
            name, value = item.strip().split('=', 1)
            cookies.append({
                "name": name,
                "value": value,
                "domain": domain,
                "path": "/"
            })
    return cookies

def scrape_open_ticket_ids_playwright(target_dev, raw_cookie):
    url = f"https://retroachievements.org/user/{target_dev}/tickets"
    ticket_ids = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        context.add_cookies(parse_raw_cookie(raw_cookie))
        
        page = context.new_page()
        page.goto(url)
        
        try:
            page.wait_for_selector("table", timeout=10000)
        except Exception:
            print("Error: Table failed to load. Please check the RA_COOKIE value.")
            browser.close()
            return []

        rows = page.query_selector_all("table tr")
        
        for row in rows:
            cols = row.query_selector_all("td")
            if len(cols) >= 2:
                status_text = cols[1].inner_text().strip().lower()
                if status_text == 'open':
                    id_link = cols[0].query_selector("a")
                    if id_link:
                        ticket_id = id_link.inner_text().strip()
                        if ticket_id.isdigit() and ticket_id not in ticket_ids:
                            ticket_ids.append(ticket_id)

        browser.close()
    return ticket_ids

def get_ticket_details(ticket_id, api_user, api_key):
    url = "https://retroachievements.org/API/API_GetTicketData.php"
    params = {
        'i': ticket_id,
        'z': api_user,
        'y': api_key
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error querying ticket {ticket_id}: {e}")
        return None

def export_to_csv(data_list, filename):
    if not data_list:
        return
    
    keys = data_list[0].keys()
    
    with open(filename, 'w', newline='', encoding='utf-8-sig') as output_file:
        dict_writer = csv.DictWriter(output_file, fieldnames=keys, delimiter=';')
        dict_writer.writeheader()
        dict_writer.writerows(data_list)

if __name__ == "__main__":
    RA_COOKIE = os.getenv("RA_COOKIE")
    RA_USER = os.getenv("RA_USER")
    RA_API_KEY = os.getenv("RA_API_KEY")
    
    if not all([RA_COOKIE, RA_USER, RA_API_KEY]):
        print("Error: Please verify that RA_COOKIE, RA_USER, and RA_API_KEY are configured in your .env file.")
        exit(1)

    target = input("Enter the developer's username (e.g., Salsa): ").strip()
    
    if target:
        print(f"\n[1] Scraping IDs for '{target}' (Page 1)...")
        ids = scrape_open_ticket_ids_playwright(target, RA_COOKIE)
        
        if not ids:
            print("No tickets found.")
        else:
            print(f"Success! {len(ids)} open tickets found. Starting API data extraction...\n")
            
            tickets_data = []
            
            # Loops through the ID list to fetch data from the API
            for i, t_id in enumerate(ids):
                print(f"Processing ticket {t_id} ({i+1}/{len(ids)})...")
                
                details = get_ticket_details(t_id, RA_USER, RA_API_KEY)
                
                if details:
                    reporter_name = details.get("ReportedBy", "N/A")
                    
                    link_id = f'=HIPERLINK("https://retroachievements.org/ticket/{t_id}"; "{t_id}")'
                    link_dev = f'=HIPERLINK("https://retroachievements.org/user/{target}"; "{target}")'
                    
                    if reporter_name != "N/A":
                        link_reporter = f'=HIPERLINK("https://retroachievements.org/user/{reporter_name}"; "{reporter_name}")'
                    else:
                        link_reporter = "N/A"
                    
                    # Extracts notes and replaces the <br/> HTML tag with a separator for Excel
                    raw_notes = details.get("ReportNotes", "N/A")
                    if raw_notes != "N/A" and raw_notes is not None:
                        clean_notes = str(raw_notes).replace("<br/>", " | ").replace("\r", "").replace("\n", " ")
                    else:
                        clean_notes = "N/A"
                    
                    row_data = {
                        "ID": link_id,
                        "Developer": link_dev,
                        "Game": details.get("GameTitle", "N/A"),
                        "Achievement": details.get("AchievementTitle", "N/A"),
                        "Reported By": link_reporter,
                        "Reported Date": details.get("ReportedAt", "N/A"),
                        "Notes": clean_notes
                    }
                    tickets_data.append(row_data)
                
                # Mandatory delay to prevent hitting API rate limits
                time.sleep(1)
            
            # Exports the data
            csv_filename = f"open_tickets_{target}.csv"
            export_to_csv(tickets_data, csv_filename)
            print(f"\nProcess completed! Generated file: {csv_filename}")