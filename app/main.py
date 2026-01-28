from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException
from starlette.middleware.cors import CORSMiddleware

from app.api.errors.http_error import http_error_handler
from app.api.errors.validation_error import http422_error_handler
from app.api.routes.api import router as api_router
from app.core.config import get_app_settings
from app.core.events import create_start_app_handler, create_stop_app_handler


def get_application() -> FastAPI:
    settings = get_app_settings()

    settings.configure_logging()
# ここで、大まかなな設定をしている（空の箱を作っていき、そこに部品をつけていくイメージがわかりやすい）

# FastAPI()は箱のイメージ
    application = FastAPI(**settings.fastapi_kwargs)

    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_hosts,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
# evet_handlerはイベント発生（処理開始時）の動きを決める
    application.add_event_handler(
        "startup",
        create_start_app_handler(application, settings),
    )
    application.add_event_handler(
        "shutdown",
        create_stop_app_handler(application),
    )
# エラー発生時の処理方法を決定する
    application.add_exception_handler(HTTPException, http_error_handler)
    application.add_exception_handler(RequestValidationError, http422_error_handler)
    
    
# ルーティングの設定（どのURLにどの処理を割り当てるか）
    application.include_router(api_router, prefix=settings.api_prefix)

    return application


app = get_application()
