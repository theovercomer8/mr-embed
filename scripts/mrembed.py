import modules.scripts as scripts
import gradio as gr
import os
import re

import modules.shared as shared
import modules

scripts_dir = scripts.basedir()
embeds_dir = os.path.join(scripts_dir,'embeddings')
enabled_embeds = []
hooked_func = None
hooked = False

def embeds_for_model(hash):
    positive = []
    negative = []
    general = []

    for root, dirs, fns in os.walk(os.path.join(embeds_dir,hash)):
        for fn in fns:
            if 'positive' in root:
                positive.append(os.path.splitext(fn)[0])
            elif 'negative' in root:
                negative.append(os.path.splitext(fn)[0])
            elif 'general' in root:
                general.append(os.path.splitext(fn)[0])

    return [positive,negative,general]


class Script(scripts.Script):
    def __init__(self) -> None:
         super().__init__()

         if not os.path.exists(embeds_dir):
              os.mkdir(embeds_dir)
              
         modules.sd_hijack.model_hijack.embedding_db.add_embedding_dir(embeds_dir)
         modules.sd_hijack.model_hijack.embedding_db.load_textual_inversion_embeddings(force_reload=False)


    def title(self):
        return "Mr. Embed"
    
    def show(self, is_img2img):
            return scripts.AlwaysVisible
    
    def ui(self, is_img2img):
        global enabled_embeds
        # model_ckpt = os.path.basename(shared.sd_model.sd_checkpoint_info.filename)
        model_hash = shared.opts.data["sd_checkpoint_hash"][0:10]
        ckpt_embed_dir = os.path.join(embeds_dir,model_hash)

        def create_folders():
            if not os.path.exists(ckpt_embed_dir):
                os.mkdir(ckpt_embed_dir)
                os.mkdir(os.path.join(ckpt_embed_dir,'positive'))
                os.mkdir(os.path.join(ckpt_embed_dir,'negative'))
                os.mkdir(os.path.join(ckpt_embed_dir,'general'))
                return [gr.HTML.update(f"""
                        <div>Created {ckpt_embed_dir}</div>
                        <div>Created {os.path.join(ckpt_embed_dir,'positive')}</div>
                        <div>Created {os.path.join(ckpt_embed_dir,'negative')}</div>
                        <div>Created {os.path.join(ckpt_embed_dir,'general')}</div>
                    """),gr.Button.update(visible=False)]
            else:
                return [gr.HTML.update(F"""ERR: {ckpt_embed_dir} already exists""",gr.Button.update(visible=False))]

        def update_enabled_embeds(pos,neg,gen):
            global enabled_embeds
            enabled_embeds = pos + neg + gen
           

        with gr.Group():
            with gr.Accordion('Mr. Embed', open=True):
                gr.HTML(value=f"""
                <strong>Checkpoint: </strong> {model_hash}<br/>
                <strong>Embeds dir:</strong> {embeds_dir}
                """)
                
                is_enabled = gr.Checkbox(label='Mr. Embed Enabled', value=True)

                if not os.path.exists(ckpt_embed_dir):
                    create_folders_html = gr.HTML(value='<div>No embedding folder structure found for checkpoint.</div>')
                    create_folders_btn = gr.Button('Create')
                    create_folders_btn.click(create_folders, inputs=None, outputs=[create_folders_html,create_folders_btn])

                else:

                    pos, neg, gen = embeds_for_model(model_hash)
                    
                    enabled_embeds = pos + neg + gen
                    
                    pos_cb = gr.CheckboxGroup(choices=pos,label='Positive',value=pos)
                    neg_cb = gr.CheckboxGroup(choices=neg,label='Negative',value=neg)
                    gen_cb = gr.CheckboxGroup(choices=gen,label='General',value=gen)

                    pos_cb.change(update_enabled_embeds,inputs=[pos_cb,neg_cb,gen_cb],outputs=[])
                    neg_cb.change(update_enabled_embeds,inputs=[pos_cb,neg_cb,gen_cb],outputs=[])
                    gen_cb.change(update_enabled_embeds,inputs=[pos_cb,neg_cb,gen_cb],outputs=[])


        return [is_enabled]
    
    def process(self, p, is_enabled):
        global enabled_embeds, hooked_func, hooked
        if not is_enabled:
            return

        model_hash = shared.opts.data["sd_checkpoint_hash"][0:10]
        pos, neg, gen = embeds_for_model(model_hash)
        orig_pos = pos.copy()
        orig_neg = neg.copy()
        orig_gen = gen.copy()

        for o in pos:
            if o not in enabled_embeds:
                pos.remove(o)
        for o in neg:
            if o not in enabled_embeds:
                neg.remove(o)
        for o in gen:
            if o not in enabled_embeds:
                gen.remove(o)

        def match_start(s):
            exp = '^[Ss](\d+)_.*'

            matches = re.search(exp,s)
            return True if matches is not None else False
        
        def match_end(s):
            exp = '^[Ee](\d+)_.*'

            matches = re.search(exp,s)
            return True if matches is not None else False
        
        def sort_key(s):
            if s is None:
                return 0
            exp = '^[SsEe](\d+)_.*'

            matches = re.search(exp,s)
            return float(matches.group(1)) if matches is not None else 0
            
        def new_prompt(prompt:str,start:list|None,end:list|None,other:list|None):
            prompt = f"{', '.join(start)}, {prompt}" if start is not None and len(start) > 0 else prompt
            prompt = f"{prompt}, {', '.join(other)}" if other is not None and len(other) > 0 else prompt
            prompt = f"{prompt}, {', '.join(end)}" if end is not None and len(end) > 0 else prompt
            return prompt
        
        # Add positive keywords to prompt
        start = list(filter(lambda kw: match_start(kw),pos))
        start.sort(key=sort_key)
        end = list(filter(lambda kw: match_end(kw),pos))
        end.sort(key=sort_key)
        other = list(filter(lambda kw: (start is None or kw not in start) and (end is None or kw not in end),pos))

        if start is not None or end is not None or other is not None:
            p.prompt = new_prompt(p.prompt,start,end,other)
            p.all_prompts = [new_prompt(prompt,start,end,other) for prompt in p.all_prompts]

        # Add negative keywords to prompt
        start = list(filter(lambda kw: match_start(kw),neg))
        start.sort(key=sort_key)
        end = list(filter(lambda kw: match_end(kw),neg))
        end.sort(key=sort_key)
        other = list(filter(lambda kw: (start is None or kw not in start) and (end is None or kw not in end),neg))

        if start is not None or end is not None or other is not None:
            p.negative_prompt = new_prompt(p.negative_prompt,start,end,other)
            p.all_negative_prompts = [new_prompt(prompt,start,end,other) for prompt in p.all_negative_prompts]

        # Disable any general embeds that are not active
        hooked_func = modules.sd_hijack.model_hijack.embedding_db.find_embedding_at_position
        
        def hijacked_embedding(tokens, offset):
            embedding, l = hooked_func(tokens,offset)
            if embedding is None:
                return embedding, l
            if embedding.name in orig_pos or embedding.name in orig_neg or embedding.name in orig_gen:
                if embedding.name not in enabled_embeds:
                    return None, None
            return embedding, l
                
        modules.sd_hijack.model_hijack.embedding_db.find_embedding_at_position = hijacked_embedding
        hooked = True
                
    def postprocess(self, p, processed, *args):
        if hooked and hooked_func is not None:
            modules.sd_hijack.model_hijack.embedding_db.find_embedding_at_position = hooked_func
       


        
        
        

