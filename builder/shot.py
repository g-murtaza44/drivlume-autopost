import sys
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch();pg=b.new_page(viewport={'width':1080,'height':1920})
    for d in sys.argv[1:]:
        pg.goto('file://'+d+'/p.html');pg.wait_for_timeout(400);pg.screenshot(path=d+'/post.png')
    b.close()
