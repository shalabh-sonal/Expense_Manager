from app import create_app

app = create_app()

if __name__ == '__main__':
    # This block only runs when you do `python run.py`
    # Won't run when using gunicorn
    app.run(host='0.0.0.0', port=5000)