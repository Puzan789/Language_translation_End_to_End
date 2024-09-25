import torch
import torch.nn as nn
from translator.model import build_transformer
from translator.entity import ModelTrainingConfig
from translator.inference import Inference
from translator.pipeline.stage_03_datatransformation import DataTransformationPipeline
from translator.logging import logger
from pathlib import Path
import os
from torch.utils.tensorboard import SummaryWriter
from tqdm import tqdm


class Train_model:
    def __init__(self,config:ModelTrainingConfig):
        self.config=config
        self.inference=Inference(self.config)
        self.datasets=DataTransformationPipeline()

    
    def get_weights_file_path(self,epoch:str):
        model_folder=self.config.model_path # extracting model folder from the config
        model_basename=self.config.model_basename# extracting the base name for model files
        model_filename=f'{model_basename}{epoch}.pt'
        return str(Path('.')/model_folder/model_filename)
    
    def get_model(self,vocab_src_len,vocab_tgt_len):
        model=build_transformer(vocab_src_len, vocab_tgt_len, self.config.max_seq_len, self.config.max_seq_len, self.config.d_model)
        return model

    
    def trainmodel(self):
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Using device{device}")
        #model directory to store weight
        model_path = Path(self.config.model_path)
        experiment_path = Path(self.config.experiment_path)
        
        # Create directories if they do not exist
        model_path.mkdir(parents=True, exist_ok=True)
        experiment_path.mkdir(parents=True, exist_ok=True)
        
        train_dataloader,val_dataloader,tokenizer_src,tokenizer_tgt=self.datasets.main()
        model = self.get_model( tokenizer_src.get_vocab_size(), tokenizer_tgt.get_vocab_size()).to(device)
        optimizer = torch.optim.Adam(model.parameters(), lr=self.config.lr, eps=1e-9)
        initial_epoch = 0
        global_step = 0
        writer = SummaryWriter(self.config.experiment_path)
    # Check if there is a pre-trained model to load
        if self.config.preload:
            model_filename = self.get_weights_file_path(self.config.preload)
            logger.info(f"preloading model {model_filename}")
            print(f'Preloading model {model_filename}')
            state = torch.load(model_filename)
            
            # Sets epoch to the saved in the state plus one, to resume from where it stopped
            initial_epoch = state['epoch'] + 1
          
            optimizer.load_state_dict(state['optimizer_state_dict'])
            global_step = state['global_step']
        loss_fn = nn.CrossEntropyLoss(ignore_index=tokenizer_src.token_to_id('[PAD]'), label_smoothing=0.1).to(device)
        previous_model_filename = None  # Variable to track the last saved model file
        for epoch in range(initial_epoch, self.config.num_epochs):
            batch_iterator = tqdm(train_dataloader, desc=f'Processing epoch {epoch:02d}')
            for i, batch in enumerate(batch_iterator):
                model.train()
                
                # Loading input data and masks onto the GPU
                encoder_input = batch['encoder_input'].to(device)
                decoder_input = batch['decoder_input'].to(device)
                encoder_mask = batch['encoder_mask'].to(device)
                decoder_mask = batch['decoder_mask'].to(device)
                
                # Running tensors through the transformer
                encoder_output = model.encode(encoder_input, encoder_mask)
                decoder_output = model.decode(encoder_output, encoder_mask, decoder_input, decoder_mask)
                proj_output = model.project(decoder_output)
                # Loading the target labels onto the GPU
                label = batch['label'].to(device)
                # Computing loss between model's output and true labels
                loss = loss_fn(proj_output.view(-1, tokenizer_tgt.get_vocab_size()), label.view(-1))
                # Updating progress bar
                batch_iterator.set_postfix({f'loss': f'{loss.item():6.3f}'})
                writer.add_scalar('train loss', loss.item(), global_step)
                writer.flush()
                # Performing backpropagation
                loss.backward()
                optimizer.step()
                # Clearing the gradients to prepare for the next batch
                optimizer.zero_grad()
                global_step += 1  # Updating global step coun
                if global_step % 100 == 0:
                    print(f'Iteration {global_step}: loss = {loss.item():6.3f}')
                    writer.add_scalar('iteration loss', loss.item(), global_step)
                    writer.flush()
            self.inference.run_validation(model, val_dataloader, tokenizer_src, tokenizer_tgt,  device, lambda msg: batch_iterator.write(msg), global_step, writer)
        
            # Save model after every epoch
            model_filename = self.get_weights_file_path(f'epoch_{epoch+1}')
            
            # Writing current model state to the model_filename
            torch.save({
                'epoch': epoch,  # Current epoch
                'model_state_dict': model.state_dict(),  # Current model state
                'optimizer_state_dict': optimizer.state_dict(),  # Current optimizer state
                'global_step': global_step  # Current global step
            }, model_filename)
            
            print(f'Saved model for epoch {epoch+1}: {model_filename}')
            logger.info(f'Saved model for epoch {epoch+1}: {model_filename}')
            
            # Delete the model from the previous epoch
            if previous_model_filename and os.path.exists(previous_model_filename):
                os.remove(previous_model_filename)
                print(f'Deleted previous model: {previous_model_filename}')
                logger.info(f'Deleted previous model: {previous_model_filename}')

            
            # Update the previous model filename to the current one
            previous_model_filename = model_filename

        logger.info("Training complete. Calculating BLEU score on validation data...")
        print("training complete calculating Bleu score on validation data")
        avg_bleu_score = self.inference.calculate_bleu_for_validation(model, val_dataloader, tokenizer_src, tokenizer_tgt, device)
        logger.info(f"\nFinal Average BLEU score on validation data: {avg_bleu_score:.4f}")
        print(f"\nFinal Average BLEU score on validation data: {avg_bleu_score:.4f}")
                
        



    