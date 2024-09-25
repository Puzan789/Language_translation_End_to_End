from tokenizers import Tokenizer
from tokenizers.models import WordLevel
from tokenizers.trainers import WordLevelTrainer
from tokenizers.pre_tokenizers import Whitespace
from datasets import load_dataset
from torch.utils.data import Dataset,random_split,DataLoader
import torch
from typing import Any
from translator.logging import logger
from translator.entity import DataTransformConfig
from pathlib import Path
from translator.utils.common import casual_mask

class DataTransformation:
    def __init__(self,config:DataTransformConfig):
        self.config=config
        
    
    def get_all_sentences(self,ds,lang):
        for pair in ds:
            yield pair['translation'][lang]
    
    def build_tokenizer(self,ds,lang):
        tokenizer_path=Path(str(self.config.tokenizer_file).format(lang))
        if not Path.exists(tokenizer_path):
            tokenizer=Tokenizer(WordLevel(unk_token='[UNK]'))
            tokenizer.pre_tokenizer=Whitespace() # we will spilt the text into tokens based ont hte whitespace

            # creating a trainer for the new tokenizer 
            trainer=WordLevelTrainer(special_tokens=['[UNK]','[PAD]','[SOS]','[EOS]'])
            tokenizer.train_from_iterator(self.get_all_sentences(ds,lang),trainer=trainer)
            tokenizer.save(str(tokenizer_path))
            logger.info(f"Tokenizer saved")
        else:
            tokenizer=Tokenizer.from_file(str(tokenizer_path))
            logger.info("Tokenizer retrieved from file")
        return tokenizer

class BilingualDataset(Dataset):
    def __init__(self,ds,tokenizer_src,tokenizer_tgt,config:DataTransformConfig,) :
        super().__init__()
        self.config=config
        self.seq_len=self.config.max_seq_len
        self.ds=ds
        self.tokenizer_src=tokenizer_src
        self.tokenizer_tgt=tokenizer_tgt
        self.src_lang=self.config.src_lang
        self.tgt_lang=self.config.tgt_lang
        self.sos_token=torch.tensor([tokenizer_tgt.token_to_id('[SOS]')],dtype=torch.int64)
        self.eos_token=torch.tensor([tokenizer_tgt.token_to_id('[EOS]')], dtype=torch.int64)
        self.pad_token=torch.tensor([tokenizer_tgt.token_to_id('[PAD]')], dtype=torch.int64)
    def __len__(self):
        return len(self.ds)
    
    
    def __getitem__(self,index:Any):
        src_target_pair=self.ds[index]
        src_text=src_target_pair['translation'][self.src_lang]
        tgt_text=src_target_pair['translation'][self.tgt_lang]

        #tokenizationgthe source and target text 
        enc_input_tokens=self.tokenizer_src.encode(src_text).ids
        dec_input_tokens=self.tokenizer_tgt.encode(tgt_text).ids

        # sentence ma hamlai aktiota pad token chainxa 
        enc_num_padding_tokens=self.seq_len-len(enc_input_tokens) -2 # -2 for eos and sos

        #target tokens 
        dec_num_padding_tokens=self.seq_len-len(dec_input_tokens)-1 # euta chai for sos

        if enc_num_padding_tokens<0 or dec_num_padding_tokens<0:
            logger.error("Sentences are long")
            raise ValueError("Sentences seem to be long")#yedi maxtokens 10 xa aani tokens 9 ota xa bhaney eos ra sos nai bhayena jaha -1 aauxa tei bahyera
        
        #suruma sos tokens last ma eos token ani padding tokens
        encoder_input=torch.cat(
            [
                self.sos_token,
                torch.tensor(enc_input_tokens,dtype=torch.int64),
                self.eos_token,
                torch.tensor([self.pad_token]*enc_num_padding_tokens,dtype=torch.int64)#padding tokens add gareko jastai list[0]*5 huda list[0,0,0,0,0]

            ]
        )

        #building decoder input tensor
        decoder_input=torch.cat([
            self.sos_token, # inserting the '[SOS]' token
            torch.tensor(dec_input_tokens, dtype=torch.int64), # indersting the tokenized target text
            torch.tensor([self.pad_token] * dec_num_padding_tokens, dtype=torch.int64) # adding padding tokens
        ])

        # yo bhaneko label target yo sanga comaper garera loss nikalxa
        # creating a label tensor, the expected output for training the model
        label=torch.cat([
            torch.tensor(dec_input_tokens, dtype=torch.int64), # inserting the tokenized targate text
            self.eos_token, # inserting the '[EOS]' token
            torch.tensor([self.pad_token] * dec_num_padding_tokens, dtype=torch.int64) # adding padding tokens
        ])
        # Ensuring that the length of each tensor above is equal to the defined `seq_len`
        assert encoder_input.size(0)==self.seq_len,'Encoder input doesnt match with sequencelength'
        assert decoder_input.size(0)==self.seq_len,'Edecoder input doesnt match with sequencelength'
        assert label.size(0)==self.seq_len,'label  doesnt match with sequencelength'

        return {
            'encoder_input':encoder_input,
            'decoder_input':decoder_input,
            'encoder_mask': (encoder_input!=self.pad_token).unsqueeze(0).unsqueeze(0).int(),
            'decoder_mask': (decoder_input!=self.pad_token).unsqueeze(0).unsqueeze(0).int() & casual_mask(decoder_input.size(0)),
            'label':label,
            'src_text': src_text,
            'tgt_text': tgt_text
        }


class GetDataset:
    def __init__(self,config:DataTransformConfig):
        self.config=config
        self.data_transformer=DataTransformation(config)

    def read_text_files(self):
        with open(self.config.src_file,'r',encoding='utf-8') as src_f ,open(self.config.tgt_file,"r",encoding='utf-8') as tgt_f :
            src_lines=src_f.readlines()
            tgt_lines=tgt_f.readlines()
        
        assert len(src_lines) ==len(tgt_lines) ,"Source and target files must have the same number of lines and lengths"
        dataset=[{'translation':{'src':src.strip(),'tgt':tgt.strip()}} for src,tgt in zip(src_lines,tgt_lines)]
        return dataset
    def get_ds(self):
        #read dataset form text file
        ds_raw=self.read_text_files()
        # building and loading tokenizer for source and target file
        tokenizer_src=self.data_transformer.build_tokenizer(ds_raw,self.config.src_lang)
        tokenizer_tgt=self.data_transformer.build_tokenizer(ds_raw,self.config.tgt_lang)

        #splitting the dataset for training and validation
        train_ds_size=int(0.9 * len (ds_raw))
        val_ds_size=len(ds_raw) -train_ds_size
        train_ds_raw,val_ds_raw=random_split(ds_raw,[train_ds_size,val_ds_size])

        #processing dataset with bilingualdataset 
        train_ds=BilingualDataset(ds=train_ds_raw,tokenizer_src=tokenizer_src,tokenizer_tgt=tokenizer_tgt,config=self.config)
        val_ds=BilingualDataset(ds=val_ds_raw,tokenizer_src=tokenizer_src,tokenizer_tgt=tokenizer_tgt,config=self.config)

        #finding the maximum length in the dataset 
        max_len_src=0
        max_len_tgt=0
        for pair in ds_raw:
            src_ids=tokenizer_src.encode(pair['translation'][self.config.src_lang]).ids
            tgt_ids=tokenizer_tgt.encode(pair['translation'][self.config.tgt_lang]).ids

            max_len_src=max(max_len_src,len(src_ids))
            max_len_tgt=max(max_len_tgt,len(tgt_ids))

        print(f"Max Length of source Sentence: {max_len_src}")
        print(f"Max Length of target Sentence: {max_len_tgt}")
        logger.info(f"The  max length of source sentence is {max_len_src}")
        logger.info(f"The  max length of target sentence is {max_len_tgt}")


        train_dataloader=DataLoader(train_ds,batch_size=self.config.batch_size,shuffle=True)
        val_dataloader=DataLoader(val_ds,batch_size=1,shuffle=True)

        return train_dataloader,val_dataloader,tokenizer_src,tokenizer_tgt
