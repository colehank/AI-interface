from ..base_lvm import BaseLVM
from PIL import Image
import base64
import io

class ConsCharacter:
    def __init__(
        self, 
        name='Lilan',
        description=None,
        ref_img=None
        ):
        self.name = name
        self.lvm = BaseLVM()
        if not (ref_img or description):
            raise ValueError("Either ref_img or description must be provided.")
        if not ref_img:
            self._make_ref_img(description)
        self.description = description
        self.ref_img = ref_img

    def _make_ref_img(self, description):
        ref_img = self.lvm.create(prompt=description) 
        self.ref_img = ref_img

    def create(
        self,
        prompt: str,
        model: str = 'gpt-image-1',
        size: str = '1024x1024',
        input_fidelity: str = 'low',

    )-> Image.Image:
        image = self.lvm.edit(
            image=self.ref_img,
            input_fidelity=input_fidelity,
            prompt=f"上传的人物图像代号为{self.name}，请对其进行如下编辑: {prompt}",
            model=model,
            size=size,
        )
        return image
    
    def _repr_html_(self):
        html = f"<h3>{self.name}</h3>"
        if self.description:
            html += f"<p>{self.description}</p>"
        if self.ref_img:
            buffer = io.BytesIO()
            self.ref_img.save(buffer, format='PNG')
            img_str = base64.b64encode(buffer.getvalue()).decode()
            html += f'<img src="data:image/png;base64,{img_str}" alt="{self.name}" style="max-width: 300px;">'
        return html