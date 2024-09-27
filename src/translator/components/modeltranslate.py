import torch
from tokenizers import Tokenizer
from translator.model.mytranslatormodel import build_transformer # only for my trained 6hrs model
from translator.entity import ModelTranslateConfig
from pathlib import Path
import os

class Load_model:
    def __init__(self,config:ModelTranslateConfig):
        self.config=config
        self.model=None
        self.tokenizer_src=None
        self.tokenizer_tgt=None
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    def get_weights_file_path(self,epoch:str):
        model_folder=self.config.model_path # extracting model folder from the config
        model_basename=self.config.model_basename# extracting the base name for model files
        model_filename=f'{model_basename}{epoch}.pt'
        return str(Path('.')/model_folder/model_filename)
    
    #only performed this because i have to load previouslty trained model
  
    
    def load_model(self):
        
        self.tokenizer_src = Tokenizer.from_file(self.config.tokenizer_file.format(self.config.src_lang))
        self.tokenizer_tgt = Tokenizer.from_file(self.config.tokenizer_file.format(self.config.tgt_lang))
        vocab_src_len = self.tokenizer_src.get_vocab_size()
        vocab_tgt_len = self.tokenizer_tgt.get_vocab_size()
        self.model = build_transformer(vocab_src_len, vocab_tgt_len, self.config.max_seq_len, self.config.max_seq_len)
        self.model = self.model.to(self.device)
        
        model_filename = self.get_weights_file_path(f"epoch_{self.config.epoch_name}")
        state = torch.load(model_filename, map_location=self.device,weights_only=True)
        self.model.load_state_dict(state['model_state_dict'])
        
        
    def preprocess_sentence(self,sentence, tokenizer, seq_len, sos_token, eos_token, pad_token):
        tokens = tokenizer.encode(sentence).ids
        num_padding_tokens = seq_len - len(tokens) - 2

        if num_padding_tokens < 0:
            raise ValueError("Sentence is too long")

        input_tensor = torch.cat([
            torch.tensor([sos_token], dtype=torch.int64),
            torch.tensor(tokens, dtype=torch.int64),
            torch.tensor([eos_token], dtype=torch.int64),
            torch.tensor([pad_token] * num_padding_tokens, dtype=torch.int64)
        ])

        return input_tensor.unsqueeze(0)

    def translate_sentence(self,sentence):
        sos_token = self.tokenizer_tgt.token_to_id('[SOS]')
        eos_token = self.tokenizer_tgt.token_to_id('[EOS]')
        pad_token = self.tokenizer_tgt.token_to_id('[PAD]')

        encoder_input = self.preprocess_sentence(sentence, self.tokenizer_src, self.config.max_seq_len, sos_token, eos_token, pad_token).to(self.device)
        encoder_mask = (encoder_input != pad_token).unsqueeze(1).unsqueeze(2).int().to(self.device)

        encoder_output = self.model.encode(encoder_input, encoder_mask)
        decoder_input = torch.tensor([[sos_token]], dtype=torch.int64).to(self.device)

        for _ in range(self.config.max_seq_len):
            decoder_mask = torch.triu(torch.ones((1, decoder_input.size(1), decoder_input.size(1))), diagonal=1).type_as(encoder_mask).to(self.device)
            decoder_output = self.model.decode(encoder_output, encoder_mask, decoder_input, decoder_mask)
            proj_output = self.model.project(decoder_output[:, -1])

            _, next_word = torch.max(proj_output, dim=1)
            decoder_input = torch.cat([decoder_input, next_word.unsqueeze(0)], dim=1)

            if next_word.item() == eos_token:
                break

        translated_tokens = decoder_input.squeeze(0).tolist()
        translated_text = self.tokenizer_tgt.decode(translated_tokens)
        return translated_text


        

        