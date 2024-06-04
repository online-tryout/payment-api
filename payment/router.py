import json
from fastapi import APIRouter, Depends, HTTPException, Response, UploadFile
from supabase import Client, StorageException

from database import get_supabase, post, get, put
from payment import schema
from payment.websocket import manager

router = APIRouter()
BANK = "BCA"
ACCOUNT_NUMBER = "1234567890"

@router.get("/transaction/{transaction_id}", response_model=schema.Transaction)
async def get_transaction(transaction_id: str):
    try:
        return get("payment/transaction", {"transaction_id": transaction_id})
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.get("/transaction/detail/{transaction_id}", response_model=schema.TransactionDetail)
async def get_transaction_detail(transaction_id: str):
    try:
        transaction = get(f"payment/transaction/{transaction_id}")

        tryout_id = str(transaction["tryout_id"])
        tryout = get(f"tryout/{tryout_id}")

        if transaction is None or tryout is None:
            raise HTTPException(status_code=404, detail="Transaction or tryout not found")

        transaction["transaction_id"] = transaction["id"]
        transaction["tryout_name"] = tryout["title"]
        transaction["bank"] = BANK
        transaction["account_number"] = ACCOUNT_NUMBER

        return transaction
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/intent/{tryout_id}", response_model=schema.TransactionIntent)
async def get_transaction_intent(tryout_id: str):
    try:
        tryout = get(f"tryout/{tryout_id}")
        if tryout is None:
            raise HTTPException(status_code=404, detail="Tryout not found")
        
        return {
            "tryout_id": tryout_id,
            "tryout_name": tryout["title"],
            "amount": tryout["price"],
            "bank": BANK,
            "account_number": ACCOUNT_NUMBER
        }
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/transactions/", response_model=list[schema.Transaction])
async def get_transactions(skip: int = 0, limit: int = 100):
    try:
        return get("payment/transactions", {"skip": skip, "limit": limit})
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/transactions/user/{user_id}", response_model=list[schema.Transaction])
async def get_transactions_by_user(user_id: str, skip: int = 0, limit: int = 100):
    try:
        return get(f"payment/transactions/user/{user_id}", {"skip": skip, "limit": limit})
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/transactions/tryout/{tryout_id}", response_model=list[schema.Transaction])
async def get_transactions_by_tryout(tryout_id: str, skip: int = 0, limit: int = 100):
    try:
        return get(f"payment/transactions/tryout/{tryout_id}", {"skip": skip, "limit": limit})
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/transaction/", response_model=schema.Transaction)
async def create_transaction(transaction: schema.TransactionCreate):
    try:
        data = transaction.model_dump()
        data["tryout_id"] = str(data["tryout_id"])
        data["user_id"] = str(data["user_id"])
        response = post("payment/transaction", data)
        if response is None:
            raise HTTPException(status_code=400, detail="Failed to create transaction")
        
        tryout = get(f"tryout/{data['tryout_id']}")
        response["tryout_name"] = tryout["title"]
        response["bank"] = BANK
        response["account_number"] = ACCOUNT_NUMBER
        
        await manager.send_message(json.dumps(response))
        return response
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/approve/{transaction_id}", response_model=schema.Transaction)
async def approve_transaction(transaction_id: str):
    try:
        transaction = get(f"payment/transaction/{transaction_id}")
        if transaction is None:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        transaction["status"] = "approved"
        return put(f"payment/transaction/{transaction_id}", transaction)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.post("/reject/{transaction_id}", response_model=schema.Transaction)
async def reject_transaction(transaction_id: str):
    try:
        transaction = get(f"payment/transaction/{transaction_id}")
        if transaction is None:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        transaction["status"] = "rejected"
        return put(f"payment/transaction/{transaction_id}", transaction)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/proof/{transaction_id}", responses={200: {"content": {"image/png": {}}}})
async def get_proof_of_payment(transaction_id: str, supabase: Client = Depends(get_supabase)):
    try:
        response: bytes = supabase.storage.from_("proofs").download(path=transaction_id)
        return Response(content=response, media_type="image/png")
    except StorageException:
        raise HTTPException(status_code=404, detail="Proof of payment not found")


@router.post("/proof/{transaction_id}", response_model=str)
async def upload_proof_of_payment(file: UploadFile, transaction_id: str, supabase: Client = Depends(get_supabase)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload an image file")
    
    transaction = get(f"payment/transaction/{transaction_id}")
    if transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")

    file_bytes = await file.read()
    try:
        upload_response = supabase.storage.from_("proofs").upload(file=file_bytes, path=transaction_id, file_options={"content-type": file.content_type})

        if upload_response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to upload proof of payment")
    except StorageException as e:
        error_dict = json.loads(str(e).replace("'", "\""))
        raise HTTPException(status_code=error_dict["statusCode"], detail=error_dict["message"])
    
    return transaction_id
