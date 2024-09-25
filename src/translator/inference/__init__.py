import torch 
from translator.entity import ModelTrainingConfig
from translator.utils.common import causal_mask
from nltk.translate.bleu_score import sentence_bleu
from tqdm import tqdm

class Inference:
    def __init__(self,config:ModelTrainingConfig) :
        self.config=config
    
    def greedy_decode(self,model,source,source_mask,tokenizer_src,tokenizer_tgt,device):
        sos_idx=tokenizer_tgt.token_to_id('[SOS]')
        eos_idx=tokenizer_tgt.token_to_id('[EOS]')

    # computing the output of the encoder 
        encoder_output=model.encode(source,source_mask)
        decoder_input=torch.empty(1,1).fill_(sos_idx).type_as(source).to(device) #tensor type is like source
        while True:
            if decoder_input.size(1)==self.config.max_seq_len:
                break
            #building a mask for decoder input 
            decoder_mask=causal_mask(decoder_input.size(1)).type_as(source_mask).to(device)
            #calculating the output of the decoder
            out=model.decode(encoder_output,source_mask,decoder_input,decoder_mask)
            prob=model.project(out[:,-1])

            # Select token with the highest probability 
            _,next_word=torch.max(prob,dim=1)
            decoder_input=torch.cat([decoder_input,torch.empty(1,1).type_as(source).fill_(next_word.item()).to(device)],dim=1)
            if next_word==eos_idx:
                break
        return decoder_input.squeeze(0)
        
    def run_validation(self,model,validation_ds,tokenizer_src,tokenizer_tgt,device,print_msg, global_state, writer, num_examples=2):
        model.eval()
        count=0
        console_width=0
        #evaluation loop
        with torch.no_grad():
            for batch in validation_ds:
                count+=1
                encoder_input=batch['encoder_input'].to(device)
                encoder_mask=batch['encoder_mask'].to(device)
                assert encoder_input.size(0)==1, 'Batch size must be 1 for validation.'
                model_out=self.greedy_decode(model,encoder_input,encoder_mask,tokenizer_src,tokenizer_tgt,device)
                source_text=batch['src_text'][0]
                target_text=batch['tgt_text'][0] # true translation
                # token_ids = model_out.argmax(dim=-1).squeeze().tolist() # Convert tensor to a list of token IDs
                # model_out_text = tokenizer_tgt.decode(token_ids) 
                model_out_text=tokenizer_tgt.decode(model_out.detach().cpu().numpy()) # decoded, human-readable model ouptut
                
                # printing results
                print_msg('-'*console_width)
                print_msg(f'SOURCE: {source_text}')
                print_msg(f'TARGET: {target_text}')
                print_msg(f'PREDICTED: {model_out_text}')
                
                # After two examples, we break the loop
                if count >= num_examples:
                    break
    def compute_bleu(self,reference, candidate):
        return sentence_bleu([reference], candidate)
    def calculate_bleu_for_validation(self,model, val_dataloader, tokenizer_src, tokenizer_tgt, device):
        model.eval()  # Set the model to evaluation mode
        total_bleu_score = 0
        total_examples = 0
        example_printed = False 

        with torch.no_grad():  # No gradients needed during validation
            for batch in tqdm(val_dataloader, desc="Calculating BLEU for validation"):
                # Get source (input) and reference (target) texts
                encoder_input = batch['encoder_input'].to(device)
                encoder_mask = batch['encoder_mask'].to(device)
                target_texts = batch['tgt_text']  # Ground truth translations (list of strings)
                # Predict translations using the greedy decoding function
                model_output =self.greedy_decode(model, encoder_input, encoder_mask, tokenizer_src, tokenizer_tgt, device)
            
                # Decode predicted token IDs to text
                predicted_text = tokenizer_tgt.decode(model_output.tolist(), skip_special_tokens=True)
                
                # Iterate over each example in the batch
                for i, target_text in enumerate(target_texts):
                    reference = target_text.split()  # Tokenize the reference (true) sentence
                    candidate = predicted_text.split()  # Tokenize the predicted sentence
                    
                    # Calculate BLEU score for this example
                    bleu_score = self.compute_bleu(reference, candidate)
                    total_bleu_score += bleu_score
                    total_examples += 1
                    if not example_printed:
                        print("\n--- Sample Validation Output ---")
                        print(f"Real: {target_text}")
                        print(f"Predicted: {predicted_text}")
                        print(f"BLEU score for this example: {bleu_score:.4f}")
                        example_printed = True
                    
        
        # Calculate and return the average BLEU score across all validation examples
        avg_bleu_score = total_bleu_score / total_examples if total_examples > 0 else 0
        return avg_bleu_score
        


        