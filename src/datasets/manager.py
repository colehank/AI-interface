from __future__ import annotations

import os
import os.path as op

base_dir = op.dirname(op.abspath(__file__))
llm_prompts = [
    op.abspath(op.join(base_dir, 'llm_prompts', f))
    for f in os.listdir(op.join(base_dir, 'llm_prompts'))
    if f.endswith('.py')
]
vlm_prompts = [
    op.abspath(op.join(base_dir, 'vlm_prompts', f))
    for f in os.listdir(op.join(base_dir, 'vlm_prompts'))
    if f.endswith('.py')
]

llm_prompts = {
    name: op.abspath(path) for name, path in zip(
    [op.splitext(op.basename(f))[0] for f in llm_prompts], llm_prompts,
    )
}
vlm_prompts = {
    name: op.abspath(path) for name, path in zip(
    [op.splitext(op.basename(f))[0] for f in vlm_prompts], vlm_prompts,
    )
}
