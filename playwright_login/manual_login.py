from playwright.sync_api import sync_playwright

from config.settings import Env, get_bool, get_env, get_int

URL = "https://dart-blu.onrender.com/login"

USERNAME = get_env(Env.USERNAME, "testuser")
PASSWORD = get_env(Env.PASSWORD, "testpass")
HEADLESS = get_bool(Env.HEADLESS, True)
TIMEOUT = get_int(Env.TIMEOUT, 30000)


def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=HEADLESS)
        page = browser.new_page()
        page.goto(URL)

        # Inspect inputs in page and pick username + password fields by heuristic
        inputs = page.evaluate("""
            () => Array.from(document.querySelectorAll('input')).map(i => ({
                type: i.type || '',
                name: i.name || '',
                id: i.id || '',
                placeholder: i.placeholder || ''
            }))
        """)

        pwd_index = None
        user_index = None

        for idx, info in enumerate(inputs):
            t = (info.get('type') or '').lower()
            name = (info.get('name') or '').lower()
            ph = (info.get('placeholder') or '').lower()

            if pwd_index is None and (t == 'password' or 'password' in name or 'password' in ph):
                pwd_index = idx
                continue

        for idx, info in enumerate(inputs):
            if idx == pwd_index:
                continue
            t = (info.get('type') or '').lower()
            name = (info.get('name') or '').lower()
            ph = (info.get('placeholder') or '').lower()

            if user_index is None:
                if t in ('email', 'text') and ('user' in name or 'email' in name or 'user' in ph or 'email' in ph or name in ('username', 'email')):
                    user_index = idx
                    break

        # fallback: first non-password input
        if user_index is None:
            for idx, info in enumerate(inputs):
                if idx == pwd_index:
                    continue
                t = (info.get('type') or '').lower()
                if t != 'hidden' and t != 'submit':
                    user_index = idx
                    break

        if user_index is None or pwd_index is None:
            print('Could not reliably detect username/password inputs. Inputs found:')
            for i, info in enumerate(inputs):
                print(i, info)
            browser.close()
            return

        # Fill inputs by index using locators
        page.locator('input').nth(user_index).fill(USERNAME)
        page.locator('input').nth(pwd_index).fill(PASSWORD)

        # Try clicking submit button with several fallbacks
        clicked = False
        try:
            if page.locator('button[type="submit"]').count() > 0:
                page.locator('button[type="submit"]').first.click()
                clicked = True
        except Exception:
            pass

        if not clicked:
            try:
                if page.locator('input[type="submit"]').count() > 0:
                    page.locator('input[type="submit"]').first.click()
                    clicked = True
            except Exception:
                pass

        if not clicked:
            # try buttons with common text
            for text in ('Accedi', 'Login', 'Sign in', 'Submit'):
                btn = page.get_by_role('button', name=text)
                try:
                    if btn.count() > 0:
                        btn.first.click()
                        clicked = True
                        break
                except Exception:
                    pass

        # Wait for navigation or network idle and print result
        try:
            page.wait_for_load_state('networkidle', timeout=TIMEOUT)
        except Exception:
            pass

        print('Current page:', page.url)

        browser.close()


if __name__ == '__main__':
    run()
