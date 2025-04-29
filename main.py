from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import httpx
import json

app = FastAPI()
templates = Jinja2Templates(directory="templates")

URLS = {
    "prod": {
        "signin": "https://account-api.wavve.com/v0.9/signin/wavve",
        "products": "https://apis.wavve.com/mypurchase/products"
    },
    "qa": {
        "signin": "https://qa-account-api.wavve.com/v0.9/signin/wavve",
        "products": None  # QA는 구매 내역 없음
    },
    "dev": {
        "signin": "https://dev-account-api.wavve.com/v0.9/signin/wavve",
        "products": None  # Dev도 구매 내역 없음
    }
}

COMMON_PARAMS = {
    "apikey": "E5F3E0D30947AA5440556471321BB6D9",
    "client_version": "7.0.40",
    "device": "pc",
    "drm": "wm",
    "partner": "pooq",
    "pooqzone": "none",
    "region": "kor",
    "targetage": "all"
}

@app.get("/", response_class=HTMLResponse)
async def form_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "result1": None, "result2": None})

@app.post("/", response_class=HTMLResponse)
async def submit_form(
    request: Request,
    id: str = Form(...),
    password: str = Form(...),
    environment: str = Form(...)
):
    payload = {
        "type": "general",
        "id": id,
        "password": password,
        "pushid": "",
        "profile": "0"
    }

    signin_url = URLS[environment]["signin"]
    products_url = URLS[environment]["products"]

    async with httpx.AsyncClient() as client:
        # 1. 로그인 요청
        signin_response = await client.post(signin_url, params=COMMON_PARAMS, json=payload)
        signin_result = signin_response.json()

        credential = signin_result.get("credential")

        formatted_signin_result = json.dumps(signin_result, indent=2, ensure_ascii=False)
        formatted_products_result = "구매 내역 조회는 운영환경(Prod)에서만 가능합니다."

        # 2. 운영환경(prod) + credential이 있을 때만 구매 내역 호출
        if credential and products_url:
            headers = {"wavve-credential": credential}
            params = {
                **COMMON_PARAMS,
                "autopayment": "n",
                "enddate": "",
                "limit": "10",
                "offset": "0",
                "orderby": "new",
                "producttype": "pass",
                "startdate": ""
            }

            products_response = await client.get(products_url, params=params, headers=headers)
            products_result = products_response.json()
            formatted_products_result = json.dumps(products_result, indent=2, ensure_ascii=False)

    return templates.TemplateResponse("index.html", {
        "request": request,
        "result1": formatted_signin_result,
        "result2": formatted_products_result
    })