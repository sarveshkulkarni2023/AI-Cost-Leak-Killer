"""API routes for file upload."""
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Transaction
from app.services.data_validator import DataValidator
from app.schemas import FileUploadResponse
from app.utils.helpers import FileHandler
import os

router = APIRouter(prefix="/api", tags=["upload"])


@router.post("/upload", response_model=FileUploadResponse)
async def upload_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload and process a CSV file containing cost transactions.
    
    Expected CSV columns: vendor, amount, category, date, description
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV")

    # Save uploaded file
    FileHandler.ensure_upload_dir()
    filepath = os.path.join(FileHandler.UPLOAD_DIR, file.filename)
    
    try:
        content = await file.read()
        with open(filepath, 'wb') as f:
            f.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving file: {str(e)}")

    # Validate CSV
    records, errors = DataValidator.validate_csv(filepath)

    # Store valid records in database
    uploaded_count = 0
    for record in records:
        try:
            transaction = Transaction(
                vendor=record['vendor'],
                amount=record['amount'],
                category=record['category'],
                date=record['date'],
                description=record['description'],
                currency=record.get('currency', 'USD')
            )
            db.add(transaction)
            uploaded_count += 1
        except Exception as e:
            errors.append(f"Error storing record: {str(e)}")

    db.commit()

    # Clean up uploaded file
    try:
        os.remove(filepath)
    except:
        pass

    return FileUploadResponse(
        filename=file.filename,
        records_uploaded=uploaded_count,
        records_rejected=len(records) - uploaded_count,
        validation_errors=errors,
        message=f"Successfully uploaded {uploaded_count} records. {len(errors)} errors encountered."
    )
