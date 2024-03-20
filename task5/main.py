import warnings
from os import path

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from vector_search import VectorSearch

templates = Jinja2Templates(directory=path.dirname(__file__) + '/templates')
app = FastAPI()
vector = VectorSearch()
warnings.filterwarnings('ignore')


@app.get('/', response_class=HTMLResponse)
async def index(request: Request, q: str = ''):
    result = []
    if q:
        result = vector.search(q)
    return templates.TemplateResponse('index.html', context={'request': request, 'result': result, 'q': q})

if __name__ == '__main__':
    uvicorn.run(app)