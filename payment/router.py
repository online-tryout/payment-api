from fastapi import APIRouter, Depends, Form, HTTPException, Response, UploadFile
from supabase import Client, StorageException

from database import get_supabase, post, get
from payment import schema

router = APIRouter()


@router.get("/transaction/", response_model=schema.Transaction)
async def get_transaction(transaction_id: str):
    try:
        return get("transaction", {"transaction_id": transaction_id})
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.get("/transaction/detail/", response_model=schema.TransactionDetail)
async def get_transaction_detail(transaction_id: str):
    try:
        transaction = get("transaction", {"transaction_id": transaction_id})
        tryout = get("tryout/tryout", {"tryout_id": str(transaction["tryout_id"])})

        transaction["transaction_id"] = transaction["id"]
        transaction["tryout_name"] = tryout["title"]
        transaction["bank"] = "BCA"
        transaction["account_number"] = "1234567890"

        return transaction
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/transactions/", response_model=list[schema.Transaction])
async def get_transactions(skip: int = 0, limit: int = 100):
    try:
        return get("transactions", {"skip": skip, "limit": limit})
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/transactions/user/", response_model=list[schema.Transaction])
async def get_transactions_by_user(user_id: str, skip: int = 0, limit: int = 100):
    try:
        return get("transactions/user", {"user_id": user_id, "skip": skip, "limit": limit})
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/transactions/tryout/", response_model=list[schema.Transaction])
async def get_transactions_by_tryout(tryout_id: str, skip: int = 0, limit: int = 100):
    try:
        return get("transactions/tryout", {"tryout_id": tryout_id, "skip": skip, "limit": limit})
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/transaction/", response_model=schema.Transaction)
async def create_transaction(transaction: schema.TransactionCreate):
    try:
        data = transaction.model_dump()
        data["tryout_id"] = str(data["tryout_id"])
        data["user_id"] = str(data["user_id"])
        return post("transaction", data)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/transaction/", response_model=schema.Transaction)
async def update_transaction(transaction_id: str, updated_transaction: schema.TransactionCreate):
    try:
        return post(f"transaction/{transaction_id}", updated_transaction.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/proof/", responses={200: {"content": {"image/png": {}}}})
async def get_proof_of_payment(tid: str, supabase: Client = Depends(get_supabase)):
    try:
        response: bytes = supabase.storage.from_("proofs").download(path=tid)
        return Response(content=response, media_type="image/png")
    except StorageException:
        raise HTTPException(status_code=404, detail="Proof of payment not found")


@router.post("/proof/", response_model=str)
async def upload_proof_of_payment(file: UploadFile, tid: str = Form(...), supabase: Client = Depends(get_supabase)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload an image file")
    
    transaction = await get("transaction", {"transaction_id": tid})
    if transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")

    file_bytes = await file.read()
    upload_response = supabase.storage.from_("proofs").upload(file=file_bytes, path=tid, file_options={"content-type": file.content_type})

    if upload_response.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to upload proof of payment")
    
    return tid
