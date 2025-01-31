from fastapi import FastAPI
from app.models import Film, QueryRequest, Critique
from app.core import MySQLManager

# Initialize FastAPI app
app = FastAPI()
mySQLManager = MySQLManager()

@app.get("/health_check")
async def health_check():
    """
    Checks the health of the API and returns a status message.
    
    This endpoint can be used to ensure the API is operational. It is helpful 
    for basic monitoring and to confirm that the service is running correctly.
    """
    return {
        "status": "success",
        "message": "Health check."
    }


@app.post("/query")
async def query(request: QueryRequest):
    # Access the SQL query from the request body
    sql_query = request.sql_query
    
    # Execute the query using the freeQuery method
    result = mySQLManager.freeQuery(sql_query=sql_query)
    
    # Return the result (for example, as JSON)
    return {"result": result}

@app.post("/execution")
async def execution(request: QueryRequest):
    # Access the SQL query from the request body
    sql_query = request.sql_query

    # Execute the query using the freeQuery method
    result = mySQLManager.freeExecution(sql_query=sql_query)

    # Return the result (for example, as JSON)
    return {"result": result}