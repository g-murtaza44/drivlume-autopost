import sys
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch();pg=b.new_page(viewport={'width':1080,'height':1350},device_scale_factor=2)
    pg.goto('file://'+sys.argv[1]);pg.wait_for_timeout(500)
    pg.screenshot(path=sys.argv[2],omit_background=True,clip={'x':0,'y':0,'width':1080,'height':1350});b.close()
