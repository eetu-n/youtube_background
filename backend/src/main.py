from fastapi import FastAPI, Response, status, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import requests

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

filename = "current_id.txt"

@app.get("/id")
async def get_id():
    f = open(filename, "r")
    return { "id": f.read() }
    f.close

@app.post("/id/{new_id}", status_code = 400)
async def post_id(new_id: str, response: Response):
    with open(filename, "w") as f:
        f.write(new_id)
        response.status_code = 201

@app.get("/video", response_class=HTMLResponse)
async def get_video():
    f = open(filename, "r")
    current_id = f.read()
    f.close

    return f"""
    <html>
        <script>
            var ws = new WebSocket("ws://127.0.0.1:9004/ws");
            ws.onmessage = function(event) {{
                window.location.reload();
            }};
        </script>
        <body>
        <iframe width="1920" height="1080" src="https://www.youtube.com/embed/{current_id}?playlist={current_id}&autoplay=1&controls=0&loop=1&mute=1"></iframe>
        </body>
    </html>
    """

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        await websocket.receive_text()
        await websocket.send_text("-")

@app.get("/", response_class=HTMLResponse)
async def web_form():
    return """\
    <html>
        <script>
            var ws = new WebSocket("ws://127.0.0.1:9004/ws");
            function get_input() {
                var userInput = document.getElementById('userInput').value;
                fetch("/id/" + userInput, {
                    method: "POST"
                }).then(res => {
                    console.log("Request complete! response:", res);
                });
                ws.send("-");
            }
        </script>
        <body>
        <h1>Provide Youtube video ID</h1>
        <h1>Not the full link! I'm too lazy to fix it</h1>
        <input type='text' id='userInput'/>
        <input type='button' onclick='get_input()' value='Send'/>
        </body>
    </html>
    """