from fastapi import Query, Response, status, HTTPException, Depends, APIRouter
from ..database import get_db
from .. import schemas
from sqlalchemy.orm import Session
import mysql.connector
import pdb
router = APIRouter(
    prefix = "/query",
    tags = ["query"]
)

@router.post("/")
def post_query(QueryObject: schemas.QueryRequest, db: Session = Depends(get_db)):
    if QueryObject.query == "" or any([word in QueryObject.query.lower() for word in ["delete", "insert", "alter", "drop", "truncate"]]):
        return HTTPException(status_code = status.HTTP_406_NOT_ACCEPTABLE, detail = "You need to enter a valid sql request.")
    try:
        result = db.execute(QueryObject.query)
    except Exception as e:
        return HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = f"The query is not cannot be executed by the server. {e}")
    entries = result.fetchall()
    return {"data": entries} 

@router.post("/outdated_post", response_model=schemas.QueryResult)
def post_top(QueryObject: schemas.CategoryQuery, db: Session = Depends(get_db)):
    if QueryObject.category == "":
        return HTTPException(status_code = status.HTTP_406_NOT_ACCEPTABLE, detail = "You need to enter a valid category.")
    try: 
        category = QueryObject.category
        result = db.execute(f"""SELECT * FROM mostoutdatedpage WHERE category = '{category}'""")
        entry = result.fetchall()
        if len(entry) == 0:
            return HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = f"No such category")
        return {"category": QueryObject.category, "page": entry[0][0].decode("utf-8")}
    except Exception as e:
        return HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = f"The query is not cannot be executed by the server. {e}")
        