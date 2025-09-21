from __future__ import annotations
import base64

def _load_image_as_base64(image_path: str) -> str:

    with open(image_path, 'rb') as img_file:
        b64_str = base64.b64encode(img_file.read()).decode('utf-8')
    return b64_str



sys_prompt = """
You are a helpful AI assistant that generates images based on character references and scene descriptions.
The upload image is a reference character that will be used to generate the final image.
reference character's name is $CharacterName.
"""

conditioned_frame = """
The output image size is $Size.
The reference character is: $Character.
The style of the image should be: $Style.
$GenPrompt
"""

prompt_template = [
    {
        'role': 'system', 'content': [
            {'type': 'input_text', 'text': sys_prompt},
            {'type': 'input_image', 'text': f"data:image/png;base64,$RefCharacter"},
        ],
    },
    {'role': 'user', 'content': conditioned_frame},
]
