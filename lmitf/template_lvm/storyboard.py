from ..base_lvm import BaseLVM
from PIL import Image
import base64
import io
from tqdm.auto import tqdm
from PIL import ImageOps


def make_sequence(
    image_list: list,
    border_width=10,
    border_color='white',
) -> Image:
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



class StoryBoard:
    def __init__(
        self, 
        cha_name:str='Lilan',
        description:str=None,
        ref_img:Image.Image=None
        ):
        self.cha_name = cha_name
        self.lvm = BaseLVM()
        if not (ref_img or description):
            raise ValueError("Either ref_img or description must be provided.")
        self.ref_img = ref_img
        self.description = description

    def _make_ref_img(self, description):
        return self.lvm.create(prompt=description) 

    def create(
        self,
        story_prompts:list,
        model:str='gpt-image-1',
        verbose:bool=True,
        **kwargs
        )-> Image.Image:
        """Generate a sequence of images telling a story in a tram."""
        
        results = []
       
        prefix = f"""这是角色{self.cha_name}的参考图以及前序事件。注意保持场景与角色的一致性\n"""

        # If no ref image, include an extra tqdm step for generating it
        missing_ref = not self.ref_img
        total_steps = len(story_prompts) + (1 if missing_ref else 0)

        # Initialize context depending on whether ref image exists
        context = [self.ref_img] if self.ref_img else []

        pbar = tqdm(
            total=total_steps,
            desc=kwargs.get('desc', 'T2I'),
            disable=not verbose,
            leave=kwargs.get('leave', False),
        )
        try:
            # Step 1: create reference image if needed
            if missing_ref:
                pbar.set_postfix_str('Drawing ref-character')
                self.ref_img = self._make_ref_img(self.description)
                context = [self.ref_img]
                pbar.update(1)

            # Following steps: iterate through story prompts
            for prompt_idx, prompt in enumerate(story_prompts):
                # Clear or override postfix for normal steps
                pbar.set_postfix_str(f'Drawing panels')

                # First prompt doesn't need previous context
                current_prompt = (
                    prefix if prompt_idx > 0 else f"这是角色{self.cha_name}的参考图。\n"
                )
                current_prompt += prompt

                # Generate the image
                img = self.lvm.edit(context, current_prompt, model=model)
                results.append(img)

                # Add to context for next iteration and advance progress
                context.append(img)
                pbar.update(1)
        finally:
            pbar.close()
        
        return make_sequence(results), results
    
    def _repr_html_(self):
        html = f"<h3>{self.cha_name}</h3>"
        if self.ref_img:
            buffer = io.BytesIO()
            self.ref_img.save(buffer, format='PNG')
            img_str = base64.b64encode(buffer.getvalue()).decode()
            html += f'<img src="data:image/png;base64,{img_str}" alt="{self.cha_name}" style="max-width: 300px;">'
        return html
