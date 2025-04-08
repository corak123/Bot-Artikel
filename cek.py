import os
import base64
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import requests
from PIL import Image
from io import BytesIO
import tempfile

def generate_article_and_image(title_prompt, image_prompt):
    article = f"""<h2>{title_prompt}</h2>
<p>Artikel otomatis dari Gemini AI tentang topik <strong>{title_prompt}</strong>. Artikel ini disusun untuk SEO dan memberikan informasi mendalam kepada pembaca.</p>
<p>{title_prompt} adalah topik yang menarik untuk dibahas. Dengan pendekatan AI, kami mencoba memberikan informasi yang relevan dan terkini.</p>
<p>Simak artikel lengkap di bawah ini!</p>"""

    image_url = f"https://dummyimage.com/600x400/000/fff&text={image_prompt.replace(' ', '+')}"
    image_response = requests.get(image_url)
    image = Image.open(BytesIO(image_response.content))

    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_img:
        image.save(temp_img.name)
        image_path = temp_img.name

    img_tag = f'<img src="data:image/jpeg;base64,{base64.b64encode(image_response.content).decode()}" alt="{image_prompt}" style="width:100%;height:auto;"/>'
    full_content = img_tag + article

    return title_prompt, full_content

def create_drive_service_from_secrets():
    from google.oauth2 import service_account
    from googleapiclient.discovery import build

    SERVICE_ACCOUNT_FILE = os.getenv("SERVICE_ACCOUNT_FILE", "service_account.json")
    SCOPES = ["https://www.googleapis.com/auth/drive"]

    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)

    drive_service = build("drive", "v3", credentials=credentials)

    return credentials, drive_service

def post_to_blogger_with_creds(title, content, labels, credentials):
    try:
        service = build("blogger", "v3", credentials=credentials)
        blogs = service.blogs().listByUser(userId="self").execute()
        blog_id = blogs["items"][0]["id"]

        body = {
            "kind": "blogger#post",
            "title": title,
            "content": content,
            "labels": labels,
        }

        post = service.posts().insert(blogId=blog_id, body=body, isDraft=False).execute()
        return True, post["url"]
    except Exception as e:
        return False, str(e)
