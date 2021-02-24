"""APP
FastAPI app definition, initialization and definition of routes
"""

# # Installed # #
import uvicorn
from fastapi import FastAPI
from fastapi import status as statuscode

# # Package # #
from .models import *
from .exceptions import *
from .repositories import ChatBotRepository, LoanRepository
from .middlewares import request_handler
from .settings import api_settings as settings

__all__ = ("app", "run")


app = FastAPI(
    title=settings.title
)
app.middleware("http")(request_handler)


@app.get(
    "/chatbot",
    description="Allocate response based on actions",
    tags=["DialogFlow Chatbot"]
)
def _chatbot_actions_allocation():
    return ChatBotRepository.actions()

@app.get(
    "/getLoanAmount/{customer_id}",
    description="Based on customer profile predict loan",
    tags=["Loan"]
)
def _get_loan_amount(customer_id: str):
    return LoanRepository.getLoanAmount(customer_id)

def run():
    """Run the API using Uvicorn"""
    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        log_level=settings.log_level.lower()
    )
