from app import create_app

app = create_app()

@app.route('/')
def index():
    return "✅ Backend is running. See /api/* routes."

if __name__ == '__main__':
    app.run(debug=True)
