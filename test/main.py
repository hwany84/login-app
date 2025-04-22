from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import httpx
import json

app = FastAPI()
templates = Jinja2Templates(directory="templates")

SIGNIN_URL = "https://account-api.wavve.com/v0.9/signin/wavve"
PRODUCTS_URL = "https://apis.wavve.com/mypurchase/products"

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
async def submit_form(request: Request, id: str = Form(...), password: str = Form(...)):
    payload = {
        "type": "general",
        "id": id,
        "password": password,
        "pushid": "",
        "profile": "0"
    }

    async with httpx.AsyncClient() as client:
        # 1. 로그인 요청
        signin_response = await client.post(SIGNIN_URL, params=COMMON_PARAMS, json=payload)
        signin_result = signin_response.json()

        # credential 추출
        credential = signin_result.get("credential")

        # 기본 JSON 포맷
        formatted_signin_result = json.dumps(signin_result, indent=2, ensure_ascii=False)
        formatted_products_result = "로그인 실패 또는 credential 없음"

        # 2. credential이 있으면 구매 상품 조회
        if credential:
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

            products_response = await client.get(PRODUCTS_URL, params=params, headers=headers)
            products_result = products_response.json()
            formatted_products_result = json.dumps(products_result, indent=2, ensure_ascii=False)

    return templates.TemplateResponse("index.html", {
        "request": request,
        "result1": formatted_signin_result,
        "result2": formatted_products_result
    })