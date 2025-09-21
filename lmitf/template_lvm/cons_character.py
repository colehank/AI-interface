from ..base_lvm import BaseLVM
from PIL import Image

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
    )-> Image.Image:
        image = self.lvm.edit(
            image=self.ref_img,
            prompt=prompt,
            model=model,
            size=size,
        )
        return image