from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route
from starlette.requests import Request
from pydantic import BaseModel
import uvicorn


# ------------------------------
# Pydantic Model for ToDo Item
# ------------------------------
class Todo(BaseModel):
    title: str
    completed: bool = False


# ------------------------------------
# In-Memory Storage (Temporary Database)
# ------------------------------------
todos = []  # This will store todo items
todo_id_counter = 1


# ------------------------------
# Handlers (Views)
# ------------------------------

# Get all todos
async def get_todos(request: Request):
    return JSONResponse({"todos": todos})


# Create a new todo
async def create_todo(request: Request):
    global todo_id_counter

    data = await request.json()
    todo = Todo(**data)

    todo_item = {
        "id": todo_id_counter,
        "title": todo.title,
        "completed": todo.completed
    }

    todos.append(todo_item)
    todo_id_counter += 1

    return JSONResponse({"message": "Todo created", "todo": todo_item})


# Get a todo by ID
async def get_todo(request: Request):
    todo_id = int(request.path_params["todo_id"])

    for t in todos:
        if t["id"] == todo_id:
            return JSONResponse(t)

    return JSONResponse({"error": "Todo not found"}, status_code=404)


# Update a todo
async def update_todo(request: Request):
    todo_id = int(request.path_params["todo_id"])
    data = await request.json()

    for t in todos:
        if t["id"] == todo_id:
            if "title" in data:
                t["title"] = data["title"]
            if "completed" in data:
                t["completed"] = data["completed"]
            return JSONResponse({"message": "Todo updated", "todo": t})

    return JSONResponse({"error": "Todo not found"}, status_code=404)


# Delete a todo
async def delete_todo(request: Request):
    todo_id = int(request.path_params["todo_id"])

    for t in todos:
        if t["id"] == todo_id:
            todos.remove(t)
            return JSONResponse({"message": "Todo deleted"})

    return JSONResponse({"error": "Todo not found"}, status_code=404)


# ------------------------------
# Starlette App Configuration
# ------------------------------

routes = [
    Route("/todos", get_todos, methods=["GET"]),
    Route("/todos", create_todo, methods=["POST"]),
    Route("/todos/{todo_id:int}", get_todo, methods=["GET"]),
    Route("/todos/{todo_id:int}", update_todo, methods=["PUT"]),
    Route("/todos/{todo_id:int}", delete_todo, methods=["DELETE"]),
]

app = Starlette(
    debug=True,
    routes=routes
)


# ------------------------------
# Run Server
# ------------------------------
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
