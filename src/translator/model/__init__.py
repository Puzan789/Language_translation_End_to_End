#Model 
# embeddings
import torch
import torch.nn as nn
import math
from typing import Any


class Inputembedding(nn.Module):
    def __init__(self,d_model:int,vocab_size:int):
        super().__init__()
        self.d_model=d_model
        self.vocab_size=vocab_size
        self.embedding=nn.Embedding(vocab_size,d_model)
    def forward(self,x):
        return self.embedding(x)*math.sqrt(self.d_model)

class PositionalEncoding(nn.Module):
    def __init__(self,d_model:int,max_seq_len:int,dropout:float):
        super().__init__()
        self.d_model=d_model
        self.max_seq_len=max_seq_len
        self.dropout=nn.Dropout(dropout)
        #positional encoding filled with  zeroes
        pe=torch.zeros(max_seq_len,d_model)
        # creating a position
        position=torch.arange(0,max_seq_len,dtype=torch.float).unsqueeze(1)
        dividend_term=torch.exp(torch.arange(0,d_model,2).float()*(-math.log(10000)/d_model))
        #applying sine to even indices
        pe[:,0::2]=torch.sin(position*dividend_term)
        #applying cosine to odd indices
        pe[:,1::2]=torch.cos(position*dividend_term)
        #apply one dimension more for the batch_size
        pe=pe.unsqueeze(0)
        self.register_buffer("pe",pe)
        print(pe.shape)
    def forward(self,x):
        x=x+(self.pe[:,:x.shape[1],:]) # all bach size 0 to maxseqlen-1,dimension 
        return self.dropout(x)
class LayerNormalization(nn.Module):
    def __init__(self,eps:float=10**-6):
        super().__init__()
        self.eps=eps
        self.alpha=nn.Parameter(torch.ones(1))
        self.bias=nn.Parameter(torch.zeros(1))
    
    def forward(self,x):
        mean=x.mean(dim=-1,keepdim=True)
        std=x.std(dim=-1,keepdim=True)
        return self.alpha*(x-mean)/(std+self.eps)+self.bias

class FeedForwardNeuralNetwork(nn.Module):
    def __init__(self,d_model:int,d_ff:int,dropout:float):
        super().__init__()
        self.firstlayer=nn.Linear(d_model,d_ff)
        self.dropout=nn.Dropout(dropout)
        self.secondlayer=nn.Linear(d_ff,d_model)
    
    def forward(self,x):
        return self.secondlayer(self.dropout(torch.relu(self.firstlayer(x))))

class MultiHeadAttention(nn.Module):
    def __init__(self,d_model:int,num_heads:int,dropout:float):
        super().__init__()
        self.d_model=d_model
        self.num_heads=num_heads
        assert d_model%num_heads==0,'Dimension of model should be divisible by no of heads'
        self.d_k=d_model//num_heads

        # for the  weight metrices
        self.w_q=nn.Linear(d_model,d_model)# Weighted query
        self.w_k=nn.Linear(d_model,d_model)# weighted key
        self.w_v=nn.Linear(d_model,d_model)# weighted value
        self.w_o=nn.Linear(d_model,d_model) #weight of the concatenated layer
        self.dropout=nn.Dropout(dropout)  #last dropoutlayer
    @staticmethod
    def attention(query,key,value,mask,dropout=nn.Dropout):
        d_k=query.shape[-1]
        attention_scores=(query@key.transpose(-2,-1))/math.sqrt(d_k)
        if mask is not None:
            attention_scores.masked_fill_(mask==0,-1e9)# In-place: mask out positions with a large negative value to ignore them in softmax
        attention_scores=attention_scores.softmax(dim=-1) # applied at the last dimension that is max_selenght
        if dropout is not None:
            attention_scores=dropout(attention_scores)
        return (attention_scores@value) ,attention_scores

    def forward(self,q,k,v,mask):
        query=self.w_q(q)
        key=self.w_k(k)
        value=self.w_v(v)
        query=query.view(query.shape[0],query.shape[1],self.num_heads,self.d_k).transpose(1,2) #batchsize sequencelength number of head,d_k #transpose chai aaba independently head lai train garxam so batchsize,oofheads,max_seq_len,d_k hunxa
        key=key.view(key.shape[0],key.shape[1],self.num_heads,self.d_k).transpose(1,2)
        value=value.view(value.shape[0],value.shape[1],self.num_heads,self.d_k).transpose(1,2)
        #obtain output and attention scores
        x,self.attention_scores=MultiHeadAttention.attention(query,key,value,mask,self.dropout)
        # create  a concatenated matrix
        x=x.transpose(1,2).contiguous().view(x.shape[0],-1,self.num_heads*self.d_k)#
        return self.w_o(x)
    
class ResidualConnection(nn.Module):
    def __init__(self, dropout: float) -> None:
        super().__init__()
        # we use a dropout layer to prevent overfitting
        self.dropout=nn.Dropout(dropout)
        # we use a normalization layer
        self.norm=LayerNormalization()
        
    def forward(self, x, sublayer):
        # we normalize the input and add it to the original input x`. This creates the residual connection process
        return x+self.dropout(sublayer(self.norm(x)))

# Building Encoder Block
class EncoderBlock(nn.Module):
    def __init__(self,self_attention_block:MultiHeadAttention,ffn:FeedForwardNeuralNetwork,dropout:float):
        super().__init__()
        self.self_attention_block=self_attention_block
        self.ffn=ffn
        self.residual_connections=nn.ModuleList([ResidualConnection(dropout) for _ in range(2)])
    def forward(self,x,src_mask):
        x=self.residual_connections[0](x,lambda x : self.self_attention_block(x,x,x,src_mask)) 
        x=self.residual_connections[1](x,self.ffn) # x+x.self.ffn(x)
        # output tensor with applying feedforward selfattention feedforward 
        return x

class Encoder(nn.Module):
    def __init__(self, layers: nn.ModuleList)-> None:
        super().__init__()
        self.layers=layers # storing the EncoderBlocks
        # layer for the normalization of the output of the encoder layers
        self.norm=LayerNormalization()
    
    def forward(self, x, mask):
        # Iterating over each EncoderBlock stored in self.layers
        for layer in self.layers:
            # Applying each EncoderBlock to the input tensor x
            x=layer(x, mask)
        return self.norm(x) # Normalizing output After running all n layers

# Decoderblock #it takes multihead attention and crossattention
class DecoderBlock(nn.Module):
    def __init__(self,self_attention_block:MultiHeadAttention,crossattentionblock:MultiHeadAttention,ffn:FeedForwardNeuralNetwork,dropout:float):
        super().__init__()
        self.self_attention_block=self_attention_block
        self.cross_attention_block=crossattentionblock
        self.ffn=ffn
        self.residual_connection=nn.ModuleList([ResidualConnection(dropout) for _ in range(3)])
    
    def forward(self,x,encoderoutput,src_mask,tgt_mask):
        x=self.residual_connection[0](x,lambda x :self.self_attention_block(x,x,x,tgt_mask))
        x=self.residual_connection[1](x,lambda x : self.cross_attention_block(x,encoderoutput,encoderoutput,src_mask))
        x=self.residual_connection[2](x,self.ffn)
        return x


class Decoder(nn.Module):
    def __init__(self,layers:nn.ModuleList):
        super().__init__()
        self.layers=layers
        self.norm=LayerNormalization()
    
    def forward(self,x,encoder_output,src_mask,tgt_mask):
        for layer in self.layers:
            x=layer(x,encoder_output,src_mask,tgt_mask)
        return self.norm(x)
# Projection layer

class ProjectionLayer(nn.Module):
    def __init__(self,d_model:int,vocab_size:int):
        super().__init__()
        self.projection=nn.Linear(d_model,vocab_size)
    def forward(self,x):
        return torch.log_softmax(self.projection(x),dim=-1)

# The Transformer Architecture
# Contains all the Encoder Decoder Embeddings
class Transformer(nn.Module):
    def __init__(self,encoder:Encoder,decoder:Decoder,src_embeding:Inputembedding,tgt_embedding:Inputembedding,src_position:PositionalEncoding,tgt_position:PositionalEncoding,projection_layer:ProjectionLayer) -> None:
        super().__init__()
        self.encoder=encoder
        self.decoder=decoder
        self.src_embedding=src_embeding
        self.tgt_embedding=tgt_embedding
        self.src_position=src_position
        self.tgt_position=tgt_position
        self.projection_layer=projection_layer
    
    def encode(self,source,src_mask):
        #applying embedding to the input source language
        source=self.src_embedding(source)
        #applying positionalencoding to the source language
        source=self.src_position(source)
        return self.encoder(source,src_mask)

    def decode(self,encoder_output,src_mask,target,tgt_mask):
        target=self.tgt_embedding(target)
        target=self.tgt_position(target)
        return self.decoder(target,encoder_output,src_mask,tgt_mask)
        
    #applying projection with softmax
    def project(self,x):
        return self.projection_layer(x)
def build_transformer(src_vocab_size:int,tgt_vocab_size:int,src_seq_len:int,tgt_seq_len:int,d_model:int=512,N:int=6,h:int=8,dropout:float=0.2,d_ff:int=2048) -> Transformer:
    # Creating Embedding Layers
    src_embed=Inputembedding(d_model,src_vocab_size)
    tgt_embed=Inputembedding(d_model,tgt_vocab_size)
    #Creating Positional Encoding Layers
    src_pos=PositionalEncoding(d_model,src_seq_len,dropout)
    tgt_pos=PositionalEncoding(d_model,tgt_seq_len,dropout)

    # Encoders Blocks
    encoder_blocks=[]
    for _ in range (N) :
        encoder_self_attention_block=MultiHeadAttention(d_model,h,dropout)
        feed_forward_block=FeedForwardNeuralNetwork(d_model,d_ff,dropout)
        # one layer encoder block
        encoder_block=EncoderBlock(encoder_self_attention_block,feed_forward_block,dropout)
        encoder_blocks.append(encoder_block)
    
    # creating decoder blocks
    decoder_blocks=[]
    for _ in range(N):
        decoder_self_attention_block=MultiHeadAttention(d_model,h,dropout)
        decoder_cross_attention_block=MultiHeadAttention(d_model,h,dropout)
        feed_forward_block=FeedForwardNeuralNetwork(d_model,d_ff,dropout)

        # decoder block
        decoder_block=DecoderBlock(decoder_self_attention_block,decoder_cross_attention_block,feed_forward_block,dropout)
        decoder_blocks.append(decoder_block)
    
    # Encoder and decoder 
    encoder=Encoder(nn.ModuleList(encoder_blocks))
    decoder=Decoder(nn.ModuleList(decoder_blocks))

    #projection layer
    projection_layer=ProjectionLayer(d_model,tgt_vocab_size)
    # Fulltransforer
    transformer=Transformer(encoder,decoder,src_embed,tgt_embed,src_pos,tgt_pos,projection_layer)
    #initializing all the parameters
    for p in transformer.parameters():
        if p.dim()>1:
            nn.init.xavier_uniform_(p)
    
    return transformer

