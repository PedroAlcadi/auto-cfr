import ast
import asyncio
import os

from playwright.async_api import async_playwright, expect
from playwright_stealth import stealth_async

urls = ast.literal_eval(os.environ["URLS"])

user = ast.literal_eval(os.environ["USER"])

async def main():
    async with async_playwright() as p:
        browser = await p.firefox.launch()
        page = await browser.new_page()

        await stealth_async(page)
        
        await page.goto(urls["login_url"])
        await expect(
            page.get_by_text("Entre na conta"),
            "Login page not loaded",
        ).to_be_visible()

        await page.locator("id=username").fill(user["email"])
        await page.locator("id=password").fill(user["password"])
        await (
            page.get_by_role("button")
            .filter(has_text="Entrar")
            .click()
        )
        await expect(
            page.get_by_text("Bem-vindo de volta"), "not logged in"
        ).to_be_visible()


        await page.goto(urls["schedule_url"])

        await (
            page.get_by_role("link")
            .filter(has_text=user["activity"])
            .filter(has_text=(user["start_time"] + " - "))
            .filter(has_text="dispon")
            .click()
        )
        await expect(
            page.get_by_text("Detalhes do pedido"),
            "schedule not selected",
        ).to_be_visible()

        await (
            page.get_by_role("button")
            .filter(has_text="Continuar")
            .click()
        )
        await expect(
            page.get_by_text("Informações pessoais"), "Continue failed"
        ).to_be_visible()

        await (
            page.get_by_role("button")
            .filter(has_text="Criar reserva")
            .click()
        )
        await expect(
            page.get_by_text("Ótimo, você está reservado"),
            "schedule final reservation failed",
        ).to_be_visible()
        await page.screenshot(
            path="reserva-{}.png".format(
                user["start_time"].replace(":", "h"),
            )
        )

        await browser.close()

asyncio.run(main())