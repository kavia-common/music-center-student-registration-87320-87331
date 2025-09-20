from app import app

# PUBLIC_INTERFACE
def main():
    """Entrypoint to run the Flask development server."""
    app.run(host="0.0.0.0", port=5000, debug=True)


if __name__ == "__main__":
    main()
