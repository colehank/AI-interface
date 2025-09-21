# %%
from lmitf.template_lvm import ConsCharacter
from PIL import Image

ref_img = Image.open('/Users/zgh/Desktop/workingdir/AI-interface/lmitf/datasets/lvm_prompts/character_ref.png')

lilan = ConsCharacter(
    name='Lilan',
    ref_img=ref_img
)

#%%
lilan.create(
    'dancing in a burning room'
)
#%%
from openai import OpenAI
import base64
import io
from PIL import Image
name = "Lilan"
def _encode_img(image: Image.Image) -> str:
    img_buf = io.BytesIO()
    image.save(img_buf, format='PNG')
    img_buf.seek(0)
    return base64.b64encode(img_buf.read()).decode('utf-8')

client = OpenAI()
response = client.responses.create(
    model="gpt-4o",
    input=[
        {
            "role": "system",
            "content": [
                { "type": "input_text", "text": f"请你作为一个图像生成专家，这张图片的人物叫做{name}。在后续用户的生图要求中若提到图像主体为{name}，请务必基于上传图片的人物特征进行生图。" },
                {
                    "type": "input_image",
                    "image_url": "data:image/png;base64," + _encode_img(ref_img),
                }
            ]
        },
        {
            "role": "user",
            "content": [
                { "type": "input_text", "text": f"生成一张{name}在火焰中跳舞的图片。" }
            ]
        }
    ]
)
#%%
