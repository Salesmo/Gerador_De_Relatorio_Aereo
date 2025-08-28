from selenium import webdriver as gs
import chromedriver_autoinstaller
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import re
import json
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor

print("Programa iniciado.")
print("Otimizando configurações do navegador...")

# Configurações otimizadas do Chrome
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--blink-settings=imagesEnabled=false')
chrome_options.add_argument('--disable-extensions')
chrome_options.add_argument('--disable-javascript')
chrome_options.page_load_strategy = "eager"  # Carrega quando DOM estiver pronto

# Instalação automática do driver
chromedriver_autoinstaller.install()
print("Driver do Google configurado com sucesso!")

def get_flight_data(driver, emit=None):
    emit('message', {'type': 'alert', 'text': 'Carregando voos...'})
    
    for _ in range(3):
        try:
            driver.execute_script("""
                var btn = document.querySelector('.btn-flights-load');
                if (btn) btn.click();
            """)
            time.sleep(1.5)
        except Exception as e:
            print(f"Erro ao cargar voos: {str(e)}")
            break

    flights_data = driver.execute_script("""
        function getFlightData() {
            const flights = [];
            
            const rows = document.querySelectorAll('tr.hidden-xs.hidden-sm.ng-scope');
            
            rows.forEach((row, index)=> {
                const tds = row.querySelectorAll('td');
                if (tds.length < 7) return;
                
                const dateAttr = row.getAttribute('data-date') || '';
                const [weekDay, month, day] = dateAttr.replace(',', '').split(' ');
                
                const statusText = tds[6].textContent.trim();
                const statusParts = statusText.split(/(\d{2}:\d{2})/);
                
                flights.push({
                    date: { weekDay, month, day: parseInt(day) },
                    time: tds[0].textContent.trim(),
                    flight: tds[1].textContent.trim(),
                    from: tds[2].querySelector('.hide-mobile-only')?.textContent.trim() || '',
                    airport: (tds[2].querySelector('a')?.textContent || '').replace(/[()]/g, '').trim(),
                    airline: tds[3].textContent.trim(),
                    aircraft: tds[4].querySelector('span')?.textContent.trim() || '-',
                    aircraftName: (tds[4].querySelector('a')?.textContent || '').replace(/[()]/g, '').trim(),
                    status: statusParts[0].trim(),
                    timeStatus: statusParts[1] || ''
                });
            });
            
            return flights;
        }
        return getFlightData();
    """)
    
    agrupados = defaultdict(list)
    count = 100/len(flights_data)
    for c, flight in enumerate(flights_data):
        
        if flight['date']['day']:
            emit('message', {'type': 'alert', 'text': f'{c*count}%'})
            chave_data = f"{flight['date']['weekDay']}, {flight['date']['month']} {flight['date']['day']}"
            agrupados[chave_data].append(flight)
    emit('message', {'type': 'alert', 'text': f'100%'})
    return agrupados

def get_info(cod, emit=None):
    driver = None
    try:
        driver = gs.Chrome(options=chrome_options)
        driver.set_page_load_timeout(30)

        url = f'https://www.flightradar24.com/data/airports/{cod}/arrivals'
        emit('message', {'type': 'alert', 'text': 'Acessando aeroporto...'})
        driver.get(url)
        
        if driver.find_elements(By.ID, 'cnt-subpage-title'):
            emit('message', {'type': 'error', 'text': 'Aeroporto não encontrado!'})
            return None
        
        nome_aeroporto = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'airport-name'))
        ).text
        
        emit('message', {
            'type': 'alert',
            'text': f'Aeroporto "{nome_aeroporto}" ({cod}) encontrado!'
        })
        
        agrupados = get_flight_data(driver, emit)

        arrivals = []
        for chave_data, voos in agrupados.items():
            week_day, month_day = chave_data.split(', ')
            month, day = month_day.split()
            arrivals.append({
                "date": {"month": month, "week-day": week_day, "day": int(day)},
                "info": voos
            })
        
        voos_formatados = {
            "Airport": nome_aeroporto,
            "Arrivals": arrivals
        }

        with open('voos.json', 'w', encoding='utf-8') as f:
            json.dump(voos_formatados, f, ensure_ascii=False, indent=4)
            
        emit('message', {'type': 'success', 'text': 'Dados salvos em voos.json!'})
        return json.dumps(voos_formatados, ensure_ascii=False, indent=4)
        
    except Exception as e:
        emit('message', {'type': 'error', 'text': f'Erro: {str(e)}'})
        print(f"Erro: {str(e)}")
        return None
        
    finally:
        if driver:
            driver.quit()