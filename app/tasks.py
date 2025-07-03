import itertools
from typing import Optional
from urllib.parse import urlparse
import asyncio, random, uuid, os, boto3, logging
from botocore.exceptions import NoCredentialsError
from playwright.async_api import async_playwright
from playwright_stealth import Stealth


logger = logging.getLogger(__name__)
SCREENSHOT_SEMAPHORE = asyncio.Semaphore(3)
SCREEN_DIR = "screens"
os.makedirs(SCREEN_DIR, exist_ok=True)


# def scrape_and_screenshot(url: str) -> Dict[str, Any]:
#     """Celery task to scrape a webpage and capture its screenshot.
    
#     Args:
#         url (str): The URL of the webpage to scrape and screenshot.
        
#     Returns:
#         Dict[str, Any]: A dictionary containing:
#             - url: The original URL that was scraped
#             - screenshot_path: The S3 URL of the uploaded screenshot
#             - error: Error message if the scraping failed
#     """
#     return asyncio.run(_go(url))

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION")

def upload_to_s3(
        file_obj, 
        object_name=None, 
        bucket="oracle-fpl-bot-predictions",
        metadata: Optional[dict] = {}
    ):
    """
    Upload a file to S3.

    Args:
        file_obj: The file object to upload.
        object_name: The name of the object to upload.
        bucket: The name of the bucket to upload the file to.

    Returns:
        The URL of the uploaded file.       
    """
    s3_client = boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION
    )

    try:
        s3_client.upload_fileobj(file_obj, bucket, object_name, ExtraArgs=metadata)
        
        file_url = f"https://{bucket}.s3.amazonaws.com/{object_name}"
        logger.info(f"Uploaded image to S3: {file_url}")
        return file_url
    except NoCredentialsError:
        logger.error("Credentials not available")
        return None

# async def _go(url: str):
#     """Internal async function to handle the actual scraping and screenshot process.
    
#     Args:
#         url (str): The URL of the webpage to scrape and screenshot.
        
#     Returns:
#         Dict[str, Any]: A dictionary containing:
#             - url: The original URL that was scraped
#             - screenshot_path: The S3 URL of the uploaded screenshot
#             - error: Error message if the scraping failed
            
#     Note:
#         This function handles:
#         - Browser initialization with custom user agent
#         - Cookie consent popup handling
#         - Random scrolling behavior
#         - Screenshot capture
#         - S3 upload
#     """
#     async with SCREENSHOT_SEMAPHORE:
#         async with async_playwright() as p:
#             browser = await p.chromium.launch(headless=True)

#             context = await browser.new_context(
#                 user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
#                 viewport={"width": 1280, "height": 800}
#             )
#             await context.add_init_script("""
#     Object.defineProperty(navigator, 'webdriver', {
#     get: () => false
#     });
#     """)

#             page = await context.new_page()

#             try:
#                 await page.goto(url, wait_until="domcontentloaded",timeout=150000)
                

            
#                 await page.mouse.wheel(0, random.randint(200, 600))
#                 await page.wait_for_timeout(random.randint(1000, 3000))

#             except Exception as e:

#                 return {"url": url, "error": str(e)}

#             filename = f"{uuid.uuid4()}.png"
#             path = os.path.join(SCREEN_DIR, filename)
        
#             await page.screenshot(
#             path=path,
#             full_page=True
#         )

#             abs_path = os.path.abspath(path)
            
#             with open(abs_path, 'rb') as file_obj:
#                 file_url = upload_to_s3(
#                     file_obj=file_obj,
#                     object_name=filename,
#                     metadata={"ContentType": "image/png"}
#                 )
            
#             await browser.close()

#         return file_url
    

# PROXIES = [
#     # {"server": "156.248.83.224:3129"},
#     # {"server": "45.201.10.182:3129"},
#     # {"server": "156.248.87.112:3129"},
#     # {"server": "154.213.195.24:3129"},

#     # # {"server": "156.233.75.88:3129"},
#     # {"server": "156.228.182.16:3129"},
#     # # {"server": "5.151.198.139:3129"},
#     # {"server": "5.151.198.139"},
#     {"server": "http://5.151.198.139"},
# ]

# cookie_string = """PHPSESSID=3o4tid2opqbtc9puidc07ffvc2; cf_clearance=qwras5VwgbHszMF42kukE8K7.Oq4hN1284Xd79rL.aA-1751123543-1.2.1.1-2KwJGifZezpbvMuY8yDcsX05bEVXDDbivZn2m4M9tO58N7wTUsBt6Vba9iKPSXeK3kbbb4cj8clMZRN3Lji7SQjcxL3A4iyTA1Xv8M0WzIFxklXr64bVALoa_pE_Ywhb7d.v1OGIqsPQQ6gfRNdQuKygW8yQKt7Ayqhyx5R3216mlBlS_oQvbut2zGj25e0I6E4hEIDOYx7Dl2U9YnepVS6CDkQuRc8hSoGGz1oS7CnUMm98oV1dcks3.trB4fOVcfC83fmpCw7LIeRqpHPS4QzwFyNj.KJLSdEo73m4GLz5eJ4pw8fl.KUhDskSSJa_h7j7pWfCQvgUs8c7wY4Clpkzkob74RDNBzNaQXfefnE; __cf_bm=lx8TOxLipuBUNExyEe4.CTjj_zovdZidVwCn_7nVXNA-1751127287-1.0.1.1-qLn8kgqhQP6LdRnMOvxu9vkP7o8HTZVlWOhQkhLVp9HwY8Vq6plCGGhVPFnVm60m6.P0i4Lj7ta6GIsuCWHQcKbOfCvQTYN1w0wlYtbuRSE"""

cookie_string = "handlID=92852469965; handl_ref_domain=; handl_landing_page_base=https://www.freightos.com/; traffic_source=Direct; first_traffic_source=Direct; server-version-cookie=y25w24-release.1749630721000|; i18next=en; handl_original_ref=https%3A%2F%2Fship.freightos.com%2F; handl_landing_page=https%3A%2F%2Fwww.freightos.com%2Fwp-content%2Fuploads%2F2018%2F04%2Fcropped-favicon-512x512-Freighots-32x32.png; handl_ref=https%3A%2F%2Fship.freightos.com%2F; handl_url_base=https%3A%2F%2Fwww.freightos.com%2Fwp-content%2Fuploads%2F2018%2F04%2Fcropped-favicon-512x512-Freighots-32x32.png; handl_url=https%3A%2F%2Fwww.freightos.com%2Fwp-content%2Fuploads%2F2018%2F04%2Fcropped-favicon-512x512-Freighots-32x32.png; user_agent=Mozilla%2F5.0%20%28Macintosh%3B%20Intel%20Mac%20OS%20X%2010_15_7%29%20AppleWebKit%2F537.36%20%28KHTML%2C%20like%20Gecko%29%20Chrome%2F137.0.0.0%20Safari%2F537.36; organic_source=https%3A%2F%2Fship.freightos.com%2F; organic_source_str=Other; intercom-id-hwrb8vsu=84d5dfdf-01de-4610-ac59-2cceb47a176d; intercom-device-id-hwrb8vsu=49d67dd8-4587-4c5d-bcb2-17d430cda0b8; HandLtestDomainNameServer=HandLtestDomainValueServer; handl_ip=5.151.198.139; prefs=en|null|GBP|true|GB|0|kg|cm|cbm|cm3_kg|days||W48|YES|false|Freight||cbm|kg|false|false; intercom-session-hwrb8vsu=emlmUmdWR2E5c2xBYjZrRGRxKzZmM1Z3d0UxWE9QeG50ZUR5RE9FVHprWmpBTnI1cUNDSXRLd2ZtaDVPM1VleklsakYxR0FCWmI2R1hYOTZLSGQvTkYzem1DWFY5akpyK3RNUmUveDlmejQ9LS1Zc1JjRHFzdW1ISkdEeVRkaHBRdCtRPT0=--d9843bc58cd8bbe1a1a4ee6c9adf7c4f77cb06a1; session=okafor%40thecozm.com|agpzfnRyYWRlb3Mxch0LEhB1c2VyL0xlZ2FsRW50aXR5GICA6vCFiaoLDA|Okafor+Okafor||1750517761132|1753109761132|yT_32N3EdG4Tvn16XsqHMUfTciA|true|false||false|BuyQuotes+MarketplaceShipper+Buying|BusinessAdmin||||7204968168%3AagpzfnRyYWRlb3Mxch0LEhB1c2VyL0xlZ2FsRW50aXR5GICA6rCyp-kLDA%2CBuyQuotes%2BBuying%2BMarketplaceShipper|V2|v-qdF8g9ijcq1QqmMEa_6-i9Q_k"

def parse_cookies(cookie_str, url):
    domain = urlparse(url).netloc
    cookies = []
    for part in cookie_str.split(";"):
        if "=" in part:
            name, value = part.strip().split("=", 1)
            cookies.append({
                "name": name,
                "value": value,
                "domain": domain,
                "path": "/"
            })
    return cookies

USER_AGENTS = [
    # Desktop Chrome/Edge/Safari/Firefox
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edg/119.0.0.0 Safari/537.36",
    # Mobile: iPhone, iPad
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Mobile/15E148 Safari/605.1",
    "Mozilla/5.0 (iPad; CPU OS 17_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Mobile/15E148 Safari/605.1",
    # Android
    "Mozilla/5.0 (Linux; Android 13; SM-S901B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 14; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Mobile Safari/537.36",
    # Tablets
    "Mozilla/5.0 (Linux; Android 12; Nexus 9) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    # Older browsers
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0",
    "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.5938.62 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Safari/605.1.15",
    # Linux desktop
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:122.0) Gecko/20100101 Firefox/122.0",
    # Edge Mac
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_4) AppleWebKit/537.36 (KHTML, like Gecko) Edg/121.0.0.0 Safari/537.36",
    # Opera
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 OPR/90.0.4560.40",
    # Samsung Browser
    "Mozilla/5.0 (Linux; Android 13; SAMSUNG SM-G990B) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/21.0 Chrome/114.0.0.0 Mobile Safari/537.36",
    # Old mobile Android
    "Mozilla/5.0 (Linux; Android 8.1; Nexus 5X Build/OPM6.171019.030.E1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.98 Mobile Safari/537.36",
    # Tablet old Android
    "Mozilla/5.0 (Linux; Android 9; SM-T860) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
    # ...
]
random.shuffle(USER_AGENTS)
user_agent_iter = itertools.cycle(USER_AGENTS)

# RANDOM_SITES = [
#     "https://www.bbc.com",
#     "https://www.cnn.com",
#     "https://www.wikipedia.org",
#     "https://www.nytimes.com",
#     "https://www.bloomberg.com",
#     "https://www.theguardian.com",
#     "https://www.reddit.com",
#     "https://www.amazon.com",
#     "https://www.twitter.com",
#     "https://www.youtube.com",
#     "https://www.medium.com",
#     "https://www.forbes.com",
#     "https://www.techcrunch.com",
# ]

# LOCALES = ["en-GB", "en-US", "fr-FR", "de-DE", "es-ES", "pt-BR", "zh-CN", "ja-JP"]
LOCALES = ["en-GB", "en-US"]
TIMEZONES = ["Europe/London", "Europe/Berlin"]
# TIMEZONES = [
#     "Europe/London", "America/New_York", "Europe/Berlin",
#     "Asia/Tokyo", "Australia/Sydney", "America/Sao_Paulo",
#     "Europe/Paris", "Europe/Madrid", "Asia/Shanghai"
# ]
async def _go(url: str, accept_cookies: bool = False):
    async with SCREENSHOT_SEMAPHORE:
        stealth = Stealth(
            navigator_languages_override=("en-GB", "en"),
            init_scripts_only=False
        )
        async with stealth.use_async(async_playwright()) as p:
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    '--disable-features=IsolateOrigins,site-per-process',
                    '--tls-fingerprint-randomization=enabled'
                ]
            )
            # Get a "new" user-agent on each call
            user_agent = next(user_agent_iter)
            width = random.choice([1280, 1366, 1440, 1600, 1920])
            height = random.choice([720, 900, 1080])
            locale = random.choice(LOCALES)
            timezone = random.choice(TIMEZONES)
            device_scale_factor = random.choice([1, 1.25, 1.5, 2])
            
            context = await browser.new_context(
                user_agent=user_agent,
                viewport={"width": width, "height": height},
                locale=locale,
                timezone_id=timezone,
                device_scale_factor=device_scale_factor,
                # is_mobile=random.choice([True, False])
            )
            await stealth.apply_stealth_async(context)
            page = await context.new_page()

            cookies = parse_cookies(cookie_string, url)
            await context.add_cookies(cookies)

            # More spoofing for fingerprint evasion (unchanged)
            await page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', { get: () => false });
                const origToDataURL = HTMLCanvasElement.prototype.toDataURL;
                HTMLCanvasElement.prototype.toDataURL = function(t) {
                    const ctx = this.getContext('2d');
                    ctx.fillStyle = 'rgba(0,0,0,0.01)';
                    ctx.fillRect(0,0,this.width,this.height);
                    return origToDataURL.apply(this, arguments);
                };
                const origGetParam = WebGLRenderingContext.prototype.getParameter;
                WebGLRenderingContext.prototype.getParameter = function(p) {
                    if (p === 37445) return 'Intel Inc.';
                    return origGetParam.apply(this, arguments);
                };
            """)

            # await page.set_extra_http_headers({
            #     "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            #     "accept-language": "en-US,en;q=0.9",
            #     "cache-control": "max-age=0",
            #     "upgrade-insecure-requests": "1",
            #     "sec-ch-ua": '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
            #     "sec-ch-ua-mobile": "?0",
            #     "sec-ch-ua-platform": '"macOS"',
            # })

            try:
                # --- HISTORY MANIPULATION: Optionally visit random site first ---
                # if random.random() < 0.7:  # 70% of the time, visit random site first
                #     pre_site = random.choice(RANDOM_SITES)
                #     await page.goto(pre_site, wait_until="domcontentloaded", timeout=45000)
                #     await page.wait_for_timeout(random.randint(10000, 30000))  # 10-30s

                
                # if random.random() < 0.3:
                #     await context.close()
                #     context = await browser.new_context()
                #     page = await context.new_page()

                # Now go to your real target
                await page.goto(url, wait_until="domcontentloaded", timeout=150000)

                if accept_cookies:
                    print("[INFO] Waiting for cookie popup...")
                    await page.wait_for_selector("button[data-test='CookiesPopup-Accept']", timeout=12000)
                    print("[INFO] Accept button found. Clicking it...")
                    await page.click("button[data-test='CookiesPopup-Accept']")
                    await page.wait_for_timeout(1000)

                # Human-like mouse movement
                for _ in range(random.randint(2, 5)):
                    await page.mouse.move(random.randint(100, width - 100),
                                         random.randint(100, height - 100), steps=10)
                    await page.wait_for_timeout(random.randint(500, 1500))
                await page.mouse.wheel(0, random.randint(300, 800))
                await page.wait_for_timeout(random.randint(1000, 3000))
            except Exception as e:
                await browser.close()
                return {"url": url, "error": str(e)}

            filename = f"freightos_shipping/{uuid.uuid4()}.png"
            path = os.path.join(SCREEN_DIR, filename)
            await page.screenshot(path=path, full_page=True)
            await context.close()
            await browser.close()

            with open(path, "rb") as f:
                file_url = upload_to_s3(f, filename, metadata={"ContentType": "image/png"})
            return {"url": url, "screenshot_url": file_url}



def scrape_and_screenshot(url: str):
    return asyncio.run(_go(url))


# if __name__ == "__main__":
#     url = "https://ship.freightos.com/results/agpzfnRyYWRlb3Mxch0LEhBjb21tZXJjZURvY3MvUkZRGICA6sz-5aoLDA/"
#     print(scrape_and_screenshot(url))

# # python3 -m app.tasks