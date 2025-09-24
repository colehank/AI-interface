# %%
from lmitf.template_lvm import ConsCharacter
from PIL import Image

prompts = {'E': "Create a 1024x1024 realistic image of Lilan and his friend seated on a tram. Scene's description: Lilan is seated next to his friend in a moderately crowded urban tram with neutral tones and metallic interiors. The atmosphere is calm and mundane, with soft ambient lighting filtering through tram windows and passengers casually sitting. Lilan and his friend appear engaged in a casual conversation. Lilan's expression is neutral and relaxed, and his posture is upright but informal, with hands loosely resting on his lap. Meanwhile, his friend is slightly turned toward him, showing an animated expression, gesture, or motion as part of their interaction.",
 'I': "Create a 1024x1024 realistic image of an attractive woman stepping onto the tram at a station. Scene's description: Focus on her entrance from the tram doors at the center or edge of the frame, capturing her figure in motion as she steps in. Her facial expression is neutral but calm, conveying confidence and poise. Her attire is modern and stylish, drawing subtle attention, while her posture is upright and elegant. The tram station is visible through the windows, with passengers sitting inside and faint sunlight casting gentle shadows over her. The color palette is soft and understated, emphasizing urban tones like silvers, grays, and light blues.",
 'Pr': "Create a 1024x1024 realistic image of Lilan's friend whistling at the attractive woman inside the tram. Scene's description: Lilan's friend leans slightly forward in his seat, his lips pursed as he whistles in a playful or provocative manner. His expression is animated, with raised eyebrows and eyes subtly glancing toward the woman. Lilan is visible alongside him, turning his head slightly toward his friend in confused or surprised awareness, but his expression remains neutral or slightly discomforted at this stage. The attractive woman is shown mid-motion further down the aisle, with her back partially turned toward the camera, unaware of the whistle for now. Lighting remains soft and ambient, while colors and composition stay consistent with the tram's interior aesthetic.",
 'P': "Create a 1024x1024 realistic image of Lilan seated uncomfortably in a tense environment as the attractive woman sharply turns toward him. Scene's description: The focus is on Lilan and the woman, capturing the charged and uncomfortable interaction. Lilan's facial expression: Eyes widen noticeably, eyebrows raised and slightly drawn together, lips parted slightly with a tense demeanor, showing discomfort and unease. Lilan's gesture: His body stiffens, hands gripping the edge of his seat tightly, shoulders slightly hunched, and legs pressed together, attempting to shrink away. His gaze avoids making direct contact. The attractive woman's posture is tense, and her body slightly leans forward. One hand rests on her hip while the other gestures toward Lilan in a pointed manner. Her facial expression: Eyebrows furrowed and drawn tightly together, eyes narrowed with an intense gaze, lips pressed in a thin line, jaw clenched, and face slightly flushed, conveying irritation. Background details: Other passengers sitting nearby subtly glance at the scene with varied levels of awareness or discomfort. Lighting intensifies slightly around the woman to emphasize her irritation, while shadows and muted colors underline the tense atmosphere."}

ref_img = Image.open(
    'lmitf/datasets/lvm_prompts/character_ref.png')

lilan = ConsCharacter(
    name='Lilan',
    ref_img=ref_img
)

res = {}
for k, v in prompts.items():
    print(f'正在生成 {k} 图像...')
    res[k] = lilan.create(v)
    print(f'{k} 图像生成完毕。')
# %%
from openai import OpenAI

client = OpenAI()
resp = client.responses.create(
    model="gpt-5",  # 或你账户里确认支持的
    input=[{"role":"user", "content":[{"type":"input_text","text":"生成一张猫在森林里的插画"}]}],
    tools=[{"type":"image_generation"}],
    tool_choice="required",
)
print(resp)
#%%
from PIL import Image, ImageOps
def make_sequence(image_list, border_width=10, border_color='white'):
    """
    Concatenate images horizontally.

    Parameters:
    -----------
    image_list: list
        A list of images to concatenate.
    border_width: int
        The width of the border.
    border_color: str
        The color of the border.

    Returns:
    --------
    new_im: Image
        The concatenated image.
    """
    bordered_images = [
        ImageOps.expand(im, border=border_width, fill=border_color) for im in image_list
    ]

    total_width = sum(im.width for im in bordered_images)
    max_height = max(im.height for im in bordered_images)

    new_im = Image.new('RGBA', (total_width, max_height), border_color)

    x_offset = 0
    for im in bordered_images:
        new_im.paste(im, (x_offset, 0))
        x_offset += im.width

    return new_im

vngs = make_sequence([res['E'], res['I'], res['Pr'], res['P']])
vngs
#%%
from openai import OpenAI
import base64

# 初始化客户端
client = OpenAI()

# 调用 response 接口生成图像
response = client.responses.create(
    model="gpt-4o",   # 专门用于生成图像的模型
    input=[
        {"role": "user", "content": "生成一只在月球上打篮球的猫咪的卡通图像"},
    ],    # 可选：控制生成图像的大小
)

# 从 response 中取出 base64 编码的图像
image_base64 = response.output[0].content[0].image.b64_json
image_bytes = base64.b64decode(image_base64)

# 保存到本地文件
with open("cat_on_moon.png", "wb") as f:
    f.write(image_bytes)

print("图像已保存为 cat_on_moon.png")
#%%
