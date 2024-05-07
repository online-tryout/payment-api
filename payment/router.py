from fastapi import APIRouter, Depends, Form, HTTPException, Response, UploadFile
from sqlalchemy.orm import Session
from supabase import Client, StorageException

from database import get_db, get_supabase
from payment import schema, crud

router = APIRouter()


@router.get("/transaction/", response_model=schema.Transaction)
async def get_transaction(transaction_id: str, db: Session = Depends(get_db)):
    transaction = crud.get_transaction(db, transaction_id)
    if transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction


@router.get("/transactions/", response_model=list[schema.Transaction])
async def get_transactions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_transactions(db, skip=skip, limit=limit)


@router.get("/transactions/user/", response_model=list[schema.Transaction])
async def get_transactions_by_user(user_id: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_transactions_by_user(db, user_id, skip=skip, limit=limit)


@router.get("/transactions/tryout/", response_model=list[schema.Transaction])
async def get_transactions_by_tryout(tryout_id: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_transactions_by_tryout(db, tryout_id, skip=skip, limit=limit)


@router.post("/transaction/", response_model=schema.Transaction)
async def create_transaction(transaction: schema.TransactionCreate, db: Session = Depends(get_db)):
    transaction = crud.create_transaction(db, transaction)


@router.put("/transaction/", response_model=schema.Transaction)
async def update_transaction(transaction_id: str, updated_transaction: schema.TransactionCreate, db: Session = Depends(get_db)):
    return crud.update_transaction(db, transaction_id, updated_transaction)


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
    
    transaction = crud.get_transaction(tid)
    if transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")

    file_bytes = await file.read()
    upload_response = supabase.storage.from_("proofs").upload(file=file_bytes, path=tid, file_options={"content-type": file.content_type})

    if upload_response.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to upload proof of payment")
    
    return tid
