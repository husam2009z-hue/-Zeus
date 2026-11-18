import time, logging, json
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')
log = logging.getLogger('job')
STATE_DIR = Path('/home/runner/work/state')
STATE_DIR.mkdir(parents=True, exist_ok=True)
def build_driver():
    o = Options()
    o.add_argument('--headless=new')
    o.add_argument('--no-sandbox')
    o.add_argument('--disable-dev-shm-usage')
    return webdriver.Chrome(options=o)
def main():
    log.info('boot')
    d = build_driver()
    while True:
        try:
            d.get('https://example.com')
            log.info('tick - working')
            (STATE_DIR / 'last_state.json').write_text(json.dumps({'url': d.current_url, 'ts': time.time()}))
        except Exception as e:
            log.error('error: %s' % e)
            try: d.quit()
            except: pass
            time.sleep(10)
            d = build_driver()
        time.sleep(30)
if __name__ == '__main__': main()