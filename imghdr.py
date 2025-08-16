import mimetypes

def what(file, h=None):
    # Minimal stub to satisfy Streamlit <1.14
    if isinstance(file, (str, bytes)):
        return mimetypes.guess_type(str(file))[0]
    return None
