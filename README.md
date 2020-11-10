# stock-sentiment-analysis

# Introduction

The stock market is arguably one of the most competitive environment, and every trader and institution is trying to gain an edge in this algorithmic arms race. Even though algorithmic trading computers have taken over the trading floors and now account for the majority of trades on the stock market, human psychology plays an important role in the market's movements. Stock market data is widely available and used for trading, however there are massive quantities of qualitative text data that has great influence over the market. In this project, our goal is to collect a data set of stock tweets and train a model to quantify sentiment on a given opinion about the stock market.

# Methodology

What we're trying to do is classify a given tweet as either bullish or bearish. *Bullish* meaning they think the stock is going up, *bearish* meaning they it's going down. The type of problem we are trying to solve is text classification.


This project is comprised of 4 parts:
1. Collecting a data set and understanding potential bias
2. Loading, cleaning, and embedding data
3. Initializing the model
4. Training and Evaluating the model

# Collecting a data set

In order to collect a data set, we are using Stocktwits' API. Stocktwits is a wrapper on top of Twitter for stock market related information. Stocktwits allows for users to tweet on their platform and mark their opinion as either bullish or bearish on the stock.

# BERT Model

In this project, we are finetuning the robust NLP model, BERT. BERT is a transformer model developed by Google in 2018. To our benefit, the awesome people over at <a href="https://github.com/huggingface">Hugging Face</a> have made NLP a little bit easier for us. Their `transformers` library allows us to download the BERT model and use it with PyTorch. They also have many handy utilities to encode our data for the model. We'll be finetuning the BERT model with one additional output layer for binary classification.
